# -*- coding: utf-8 -*-
"""hunt-deserialization hunt 阶段：对落点值做序列化格式指纹，标注疑似反序列化点。

安全默认：只做**格式识别**（对 recon 抓到的 cookie/参数值做指纹），不自动投放 gadget。
带外/gadget PoC 请在 validate 阶段按 scope 手工做（gadget 直达 RCE，不宜自动化）。

用法:
  python hunt_deser.py --input recon/endpoints.json --output candidates.json [--oast <域名>]
"""
import argparse
import base64
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log, load_json, save_json  # noqa: E402

# (名称, 对原始值的正则, 对 base64 解码后的字节前缀)
TEXT_SIGS = [
    ("php-serialize", re.compile(r'^(O:\d+:"|a:\d+:\{|s:\d+:")')),
    ("yaml-object", re.compile(r'!ruby/object:|!!python/object|!!java')),
    ("json-typed", re.compile(r'"@type"\s*:')),
    ("viewstate", re.compile(r'__VIEWSTATE|ViewState', re.I)),
]
B64_SIGS = [
    ("java", b"\xac\xed\x00"),
    (".net-binaryformatter", b"\x00\x01\x00\x00\x00\xff\xff\xff\xff"),
    ("ruby-marshal", b"\x04\x08"),
    ("python-pickle", b"\x80"),
]


def fingerprint(value):
    if not isinstance(value, str) or not value:
        return None
    for name, pat in TEXT_SIGS:
        if pat.search(value):
            return name
    # 尝试 base64 解码看二进制魔数
    s = value.strip()
    if re.fullmatch(r'[A-Za-z0-9+/=_-]{8,}', s):
        try:
            raw = base64.b64decode(s + "=" * (-len(s) % 4), validate=False)
        except Exception:
            raw = b""
        for name, magic in B64_SIGS:
            if raw.startswith(magic):
                return name
        # rO0AB / gASV 等 base64 文本前缀
        if s.startswith("rO0"):
            return "java"
        if s.startswith(("gASV", "gAJ", "gAN")):
            return "python-pickle"
        if s.startswith("AAEAAAD"):
            return ".net-binaryformatter"
        if s.startswith("BAh"):
            return "ruby-marshal"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--oast", default="")
    args = ap.parse_args()

    data = load_json(args.input)
    if not data:
        sys.exit("读不到 %s，先跑 recon.sh" % args.input)
    cands = []
    # recon 的 endpoints 可能带 sample 值；也扫 cookie 字段名
    for ep in data.get("endpoints", []):
        val = ep.get("sample") or ep.get("value") or ""
        fmt = fingerprint(val)
        name = ep.get("param")
        # 名字启发：cookie/token/viewstate 类即使没取到值也标疑似
        name_hint = bool(name and re.search(r'cookie|token|session|viewstate|serial|state|auth|jwt', str(name), re.I))
        if fmt or name_hint:
            cands.append({
                "endpoint": ep.get("url"), "param": name,
                "format": fmt or "unknown(名称疑似)",
                "signal": (["格式指纹命中: %s" % fmt] if fmt
                           else ["参数名疑似序列化落点，需人工取值确认"]),
                "suspected": bool(fmt),
                "next": "按 reference.md 该语言 gadget，用最小带外 payload（如 phar/URI 打 %s）验证可达"
                        % (args.oast or "<OAST>"),
            })
    save_json(args.output, {"target": data.get("target"), "oast": args.oast, "candidates": cands})
    log("疑似反序列化落点 %d（指纹确认 %d）-> %s（gadget PoC 请人工按 scope 做）"
        % (len(cands), sum(1 for c in cands if c["suspected"]), args.output))


if __name__ == "__main__":
    main()
