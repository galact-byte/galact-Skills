# -*- coding: utf-8 -*-
"""hunt-auth-bypass hunt 阶段：识别鉴权机制并产出"已知模式待验证"清单。

认证绕过高度依赖业务流程，脚本不做自动利用（会触碰账户），而是：
按 recon 指纹圈定机制，输出该机制下应人工验证的已知模式检查项（含具体篡改点），
并对可无害探测的项（如 redirect_uri 宽松匹配的响应差异）给出提示。

用法:
  python hunt_authbypass.py --input recon/endpoints.json --output candidates.json
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log, load_json, save_json  # noqa: E402

# 机制 -> 待人工验证的已知模式检查项
CHECKS = {
    "saml": [
        "删除/篡改 <Signature> 后重放，看是否仍接受（签名未校验）",
        "entityId/NameID 加尾随空格或改大小写，冒充其他身份",
        "XSW 签名包裹 / XML 注释切断 NameID",
        "SAMLResponse 作为 XML 试 XXE（转 hunt-xxe）",
    ],
    "oauth": [
        "response_type 改 'code id_token' + response_mode=fragment，配合页面 XSS 偷 token",
        "redirect_uri 试 //attacker、子域后缀、路径追加、@ 绕宽松匹配",
        "去掉 state，尝试强制关联/登录 CSRF",
        "code 复用 / 无 PKCE / implicit token 回显",
    ],
    "2fa": [
        "直接请求 2FA 之后的端点，看是否可跳过",
        "响应里的 2fa_passed/verified 标志是否可改",
        "验证码是否可预测（时间种子/MD5）或无速率限制可爆破",
    ],
    "email-verify": [
        "邮箱规范化差异：尾随空格 / +tag / 大小写 / unicode",
        "SCIM/API 建用户是否可直接标记邮箱已验证",
    ],
    "session": [
        "切换登录方式看会话类型是否混淆、cookie 是否可手工构造冒充",
    ],
    "password-reset": [
        "重置 token 是否可预测/不失效；Host 头投毒改重置链接；响应是否泄露 token",
    ],
}

FP = [
    ("saml", re.compile(r'saml|SAMLResponse|entityID|assertion', re.I)),
    ("oauth", re.compile(r'oauth|response_type|redirect_uri|id_token|client_id|/authorize', re.I)),
    ("2fa", re.compile(r'2fa|mfa|otp|totp|verify.*code|two.?factor', re.I)),
    ("email-verify", re.compile(r'verify.*email|email.*verif|confirm|scim', re.I)),
    ("session", re.compile(r'session|cookie|remember', re.I)),
    ("password-reset", re.compile(r'reset|forgot', re.I)),
]


def detect_mechanisms(data):
    blob = " ".join(str(e.get("param") or "") + " " + str(e.get("url") or "")
                    for e in data.get("endpoints", []))
    blob += " " + str(data.get("target") or "")
    found = [name for name, pat in FP if pat.search(blob)]
    return found or ["oauth", "session"]  # 默认给最常见两类的检查清单


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    data = load_json(args.input)
    if not data:
        sys.exit("读不到 %s，先跑 recon.sh" % args.input)
    mechs = detect_mechanisms(data)
    cands = []
    for m in mechs:
        for chk in CHECKS.get(m, []):
            cands.append({"mechanism": m, "variant": m, "check": chk,
                          "signal": ["待人工用两个测试账户验证越权"],
                          "suspected": False})
    save_json(args.output, {"target": data.get("target"),
                            "mechanisms": mechs, "candidates": cands})
    log("识别机制 %s，产出待验证检查项 %d 条 -> %s（用测试账户间验证越权）"
        % (mechs, len(cands), args.output))


if __name__ == "__main__":
    main()
