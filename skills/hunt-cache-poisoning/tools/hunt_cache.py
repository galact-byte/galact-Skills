# -*- coding: utf-8 -*-
"""hunt-cache-poisoning hunt 阶段：对可缓存页发 unkeyed header 探针，判反射+是否被缓存。

两步法（带唯一 cache-buster 限制影响到自控条目）：
  1) 带恶意 header + ?cb=<uniq> 请求（尝试写缓存）；看标记是否反射。
  2) 不带 header、同 URL+同 cb 请求；若仍见标记且 X-Cache=HIT → 投毒成功。
只投无害标记；共享缓存投毒的深度验证请按 scope 谨慎做。

用法:
  python hunt_cache.py --target <url> --output candidates.json [--dry-run]
"""
import argparse
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log, save_json  # noqa: E402

MARK = "hcp9f3a2b"
UNKEYED = ["X-Forwarded-Host", "X-Host", "X-Forwarded-Server",
           "X-Forwarded-Scheme", "X-Original-URL", "X-Rewrite-URL"]


def req(url, extra_headers, max_time=10):
    cmd = ["curl", "-sS", "-i", "--max-time", str(max_time)]
    for h, v in extra_headers.items():
        cmd += ["-H", "%s: %s" % (h, v)]
    cmd.append(url)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=max_time + 3)
        return (p.stdout or "") + (p.stderr or "")
    except Exception as e:
        return "ERR:%s" % e


def cache_status(resp):
    import re
    m = re.search(r'(?im)^(x-cache|cf-cache-status|x-drupal-cache|cache-status):\s*([^\r\n]+)$', resp)
    age = re.search(r'(?im)^age:\s*(\d+)', resp)
    return (m.group(2).strip() if m else "?"), (age.group(1) if age else "?")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cands = []
    for hname in UNKEYED:
        uniq = "%s%d" % (MARK, int(time.time()) % 100000)
        sep = "&" if "?" in args.target else "?"
        url = "%s%scb=%s" % (args.target, sep, uniq)
        payload = "%s.example" % MARK
        if args.dry_run:
            print("[dry-run] %s: %s -> %s" % (hname, payload, url)); continue
        # step1 写缓存
        r1 = req(url, {hname: payload})
        reflected = MARK in r1
        st1, age1 = cache_status(r1)
        # step2 干净请求命中
        time.sleep(0.5)
        r2 = req(url, {})
        poisoned = MARK in r2
        st2, age2 = cache_status(r2)
        signal = []
        if reflected:
            signal.append("header 反射进响应")
        if reflected and poisoned:
            signal.append("干净请求仍见标记(X-Cache=%s) → 投毒成功" % st2)
        if not reflected:
            signal.append("未反射(该 header 可能进键或未用)")
        cands.append({"endpoint": args.target, "variant": hname, "header": hname,
                      "payload": payload, "probe_url": url,
                      "reflected": reflected, "cached_poison": bool(reflected and poisoned),
                      "cache_status_step1": st1, "cache_status_step2": st2,
                      "signal": signal, "suspected": bool(reflected and poisoned)})
    if args.dry_run:
        return
    save_json(args.output, {"target": args.target, "marker": MARK, "candidates": cands})
    hit = sum(1 for c in cands if c["suspected"])
    log("缓存投毒候选 %d（%d 确认被缓存）-> %s（缓存欺骗/私有页请按 reference 人工试）"
        % (len(cands), hit, args.output))


if __name__ == "__main__":
    main()
