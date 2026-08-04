# -*- coding: utf-8 -*-
"""
诊断脚本：对 batch_0000 发一次原始请求，打印完整响应结构，
用于判断 v4-flash 是否开 thinking / 是否截断 / 是否支持 response_format。

用法（PowerShell 已设好 OPENAI_API_KEY / OPENAI_BASE_URL）：
  python probe.py
  python probe.py --no-json-format      # 试不带 response_format
  python probe.py --max-tokens 60000    # 试给足预算
"""
import argparse
import json
import os
import urllib.request
import urllib.error

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", ""))
    ap.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL", "https://api.deepseek.com/v1"))
    ap.add_argument("--model", default="deepseek-v4-flash")
    ap.add_argument("--batch", default="batches/batch_0000.json")
    ap.add_argument("--prompt", default="score_prompt.md")
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--no-json-format", action="store_true")
    ap.add_argument("--disable-thinking", action="store_true", help="关闭 v4 thinking")
    args = ap.parse_args()

    system = open(args.prompt, encoding="utf-8").read()
    user = open(args.batch, encoding="utf-8").read()

    body = {
        "model": args.model,
        "temperature": 0.0,
        "max_tokens": args.max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    if not args.no_json_format:
        body["response_format"] = {"type": "json_object"}
    if args.disable_thinking:
        body["thinking"] = {"type": "disabled"}

    url = args.base_url.rstrip("/") + "/chat/completions"
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + args.api_key)

    print("POST", url, "| model", args.model, "| json_format", not args.no_json_format,
          "| max_tokens", args.max_tokens)
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, e.read().decode("utf-8", "replace")[:1000])
        return

    ch = data.get("choices", [{}])[0]
    msg = ch.get("message", {})
    content = msg.get("content") or ""
    reasoning = msg.get("reasoning_content") or ""
    print("\n=== 关键诊断 ===")
    print("finish_reason :", ch.get("finish_reason"))
    print("usage         :", data.get("usage"))
    print("message keys  :", list(msg.keys()))
    print("content 长度   :", len(content))
    print("reasoning 长度 :", len(reasoning), "(有值=开了thinking)")
    print("\n=== content 前 400 字 ===")
    print(content[:400])
    if reasoning:
        print("\n=== reasoning_content 前 300 字 ===")
        print(reasoning[:300])
    # 存全量响应备查
    with open("probe_response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("\n完整响应已存 probe_response.json")

    # 尝试解析 content 为 JSON
    if content:
        try:
            json.loads(content)
            print("content 是合法 JSON ✓")
        except Exception as e:
            print("content 解析失败:", e)

if __name__ == "__main__":
    main()
