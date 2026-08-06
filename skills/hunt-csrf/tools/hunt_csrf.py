# -*- coding: utf-8 -*-
"""hunt-csrf hunt 阶段：对状态变更端点检查防护三要素（token / SameSite / preflight）。

安全默认：只**观测防护**（抓 Set-Cookie 的 SameSite、检测请求是否带 token、试无 token 重放
是否被拒），不自动触发真实状态变更——真正的跨站 PoC 在 validate 阶段按 scope 在测试账户上做。
需要测试账户 cookie 才能看已登录态的防护。

用法:
  python hunt_csrf.py --input recon/endpoints.json --output candidates.json [--cookie "<cookie>"] [--dry-run]
"""
import argparse
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log, load_json, save_json  # noqa: E402


def headers(url, cookie, max_time=10):
    cmd = ["curl", "-sS", "-D", "-", "-o", os.devnull, "--max-time", str(max_time), url]
    if cookie:
        cmd += ["-H", "Cookie: " + cookie]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=max_time + 3)
        return (p.stdout or "") + (p.stderr or "")
    except Exception as e:
        return "ERR:%s" % e


def samesite_of(setcookie_block):
    vals = re.findall(r'(?im)^set-cookie:\s*([^\r\n]+)$', setcookie_block)
    out = []
    for v in vals:
        name = v.split("=", 1)[0]
        m = re.search(r'SameSite\s*=\s*(\w+)', v, re.I)
        ss = m.group(1) if m else "未指定(默认按浏览器, 多为 Lax)"
        if re.search(r'session|sess|auth|token|sid|jwt', name, re.I):
            out.append("%s: SameSite=%s" % (name, ss))
    return out or [("未见会话 cookie（可能未登录或 HttpOnly 未回显名）")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--cookie", default="")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = load_json(args.input)
    if not data:
        sys.exit("读不到 %s，先跑 recon.sh" % args.input)
    # recon 抓到的页面里 token 字段名/表单
    forms = data.get("forms", 0)
    eps = data.get("endpoints", [])
    token_params = [e.get("param") for e in eps
                    if e.get("param") and re.search(r'token|csrf|state|nonce', str(e.get("param")), re.I)]
    target = data.get("target")

    cands = []
    if args.dry_run:
        print("[dry-run] 将检查 SameSite 与 token 存在性: %s" % target); return
    hdr = headers(target, args.cookie)
    ss = samesite_of(hdr)
    # 汇总为一个"防护画像"候选 + 逐操作提示
    lacks_token = (forms > 0 and not token_params)
    signal = ["SameSite: %s" % "; ".join(ss)]
    if token_params:
        signal.append("检测到疑似 token 字段: %s（需人工验证是否真校验：删掉重放）" % token_params)
    else:
        signal.append("页面表单未见 CSRF token 字段（forms=%d）→ 疑似缺防护，重点验证" % forms)
    suspected = lacks_token or any("None" in s or "未指定" in s or "Lax" in s for s in ss)

    cands.append({"endpoint": target, "variant": "protection-profile",
                  "forms": forms, "token_params": token_params, "samesite": ss,
                  "signal": signal, "suspected": suspected,
                  "next": "对每个状态变更操作：①删/改 token 重放看是否仍成功 "
                          "②按 SameSite 选向量（Lax→顶层GET/子域）③JSON API 试 text/plain 避 preflight"})
    save_json(args.output, {"target": target, "candidates": cands})
    log("CSRF 防护画像已出（SameSite/token）-> %s（跨站 PoC 在 validate 用测试账户做）" % args.output)


if __name__ == "__main__":
    main()
