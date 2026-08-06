# -*- coding: utf-8 -*-
"""hunt-ssrf 共享工具：load/save/log/curl。

刻意零第三方依赖（标准库），任何装了 Python3 的机器直接跑。
所有出站探测统一走 http_probe，方便集中限速与留存证据。
"""
import json
import os
import subprocess
import sys
import time


def log(msg, level="INFO"):
    ts = time.strftime("%H:%M:%S")
    print("[%s][%s] %s" % (ts, level, msg), file=sys.stderr, flush=True)


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, obj):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    tmp = "%s.tmp" % path
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def save_text(path, text):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def http_probe(url, method="GET", headers=None, max_time=8, follow_redirects=False,
               extra_curl=None):
    """用 curl 发一次探测，返回 {status, size, time, headers, ok, cmd, stderr}。

    默认不跟随重定向（SSRF 里重定向本身是要观测/控制的行为）。
    -sS 静默但报错，-D - 输出响应头，-o 丢弃 body 到临时以量长度。
    """
    cmd = ["curl", "-sS", "-o", os.devnull, "-D", "-",
           "-w", "\n__STATUS__%{http_code}__SIZE__%{size_download}__TIME__%{time_total}",
           "--max-time", str(max_time), "-X", method]
    if follow_redirects:
        cmd.append("-L")
    for k, v in (headers or {}).items():
        cmd += ["-H", "%s: %s" % (k, v)]
    if extra_curl:
        cmd += list(extra_curl)
    cmd.append(url)
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=max_time + 3)
        out = p.stdout or ""
        status, size, dur = "0", "0", str(round(time.time() - t0, 3))
        if "__STATUS__" in out:
            tail = out.rsplit("\n__STATUS__", 1)[1]
            try:
                status = tail.split("__STATUS__")[0].split("__SIZE__")[0]
                size = tail.split("__SIZE__")[1].split("__TIME__")[0]
                dur = tail.split("__TIME__")[1]
            except IndexError:
                pass
        resp_headers = out.rsplit("\n__STATUS__", 1)[0]
        return {"url": url, "status": status, "size": size, "time": dur,
                "headers": resp_headers, "ok": p.returncode == 0,
                "cmd": " ".join(cmd), "stderr": (p.stderr or "").strip()}
    except subprocess.TimeoutExpired:
        return {"url": url, "status": "0", "size": "0",
                "time": str(round(time.time() - t0, 3)), "headers": "",
                "ok": False, "cmd": " ".join(cmd), "stderr": "TIMEOUT"}
