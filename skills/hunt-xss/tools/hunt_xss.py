# -*- coding: utf-8 -*-
"""hunt-xss hunt 阶段：注入唯一标记+上下文探针，抓响应判反射上下文与编码强度。

判活：标记原样出现且关键字符（< " '）未被实体化 → 疑似可执行；据落点定上下文。
只做反射探测；真正的 alert 执行确认在 validate 阶段用无头浏览器做（脚本不弹窗）。

用法:
  python hunt_xss.py --input recon/endpoints.json --output candidates.json [--dry-run]
"""
import argparse
import os
import re
import subprocess
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log, load_json, save_json  # noqa: E402

MARK = "hxss9f3a2b"
# 探针：标记 + 各种特殊字符，用于判编码
PROBE = MARK + "<>\"'"


def build_url(ep):
    base, param = ep.get("url"), ep.get("param")
    if not param or str(param).startswith("<"):
        return None
    sep = "&" if "?" in base else "?"
    return "%s%s%s=%s" % (base, sep, param, quote(PROBE, safe=""))


def fetch(url, max_time=8):
    try:
        p = subprocess.run(["curl", "-sS", "--max-time", str(max_time), url],
                           capture_output=True, text=True, timeout=max_time + 3)
        return p.stdout or ""
    except Exception as e:
        return "ERR:%s" % e


def analyze(body):
    """返回 (reflected, raw_chars, context)。"""
    if MARK not in body:
        return False, [], None
    # 找标记周围片段判上下文
    idx = body.find(MARK)
    around = body[max(0, idx - 40):idx + 40]
    raw = [c for c in ('<', '>', '"', "'") if (MARK + PROBE[len(MARK):]).replace(MARK, "") and c in body[idx:idx + 8]]
    # 更稳的判定：看标记后紧跟的原始特殊字符是否保留
    tail = body[idx + len(MARK): idx + len(MARK) + 6]
    raw_chars = [c for c in ('<', '>', '"', "'") if c in tail]
    context = "unknown"
    low = around.lower()
    if "<script" in low or re.search(r'=\s*["\']?[^<>]*%s' % re.escape(MARK), low):
        context = "js-or-attr"
    if "<" in tail:
        context = "html-body(< 未编码)"
    elif '"' in tail or "'" in tail:
        context = "attribute(引号未编码)"
    return True, raw_chars, context


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = load_json(args.input)
    if not data:
        sys.exit("读不到 %s，先跑 recon.sh" % args.input)
    eps = [e for e in data.get("endpoints", []) if e.get("controllable")]
    cands = []
    for ep in eps:
        url = build_url(ep)
        if not url:
            continue
        if args.dry_run:
            print("[dry-run] %s | %s" % (ep.get("param"), url)); continue
        body = fetch(url)
        reflected, raw_chars, context = analyze(body)
        exploitable = reflected and raw_chars  # 有原始特殊字符未编码
        signal = []
        if reflected:
            signal.append("标记反射，上下文=%s，未编码字符=%s" % (context, raw_chars or "无(可能已编码)"))
        else:
            signal.append("未反射")
        cands.append({"endpoint": ep.get("url"), "param": ep.get("param"),
                      "probe_url": url, "context": context if reflected else None,
                      "raw_chars": raw_chars, "signal": signal,
                      "suspected": bool(exploitable)})
    if args.dry_run:
        return
    save_json(args.output, {"target": data.get("target"), "marker": MARK, "candidates": cands})
    log("反射探测候选 %d（%d 疑似可执行）-> %s（用无头浏览器确认 alert 执行）"
        % (len(cands), sum(1 for c in cands if c["suspected"]), args.output))


if __name__ == "__main__":
    main()
