# -*- coding: utf-8 -*-
"""第三轮：把第二轮 592 个"单例"候选做语义归并 + 路由到现有 skill / 新 skill / 丢弃。

输入: candidate_shortlist.jsonl 中 size==1 的条目（字符串聚类合不动的单例）。
用 DeepSeek 按主题归并，并为每条判定 action∈{fold,new-skill,drop} + target（现有 hunt skill 名）。
产出决策单 singleton_routing.md + routing_all.jsonl，供人工验证与后续回填。

key 运行时从 C:\\Users\\g1582\\.pi\\agent\\auth.json 读（不写入代码/仓库）。

用法:
  python route_singletons.py --concurrency 12 --max-tokens 12000        # 全量（可续跑）
  python route_singletons.py --aggregate                                 # 仅汇总决策单
"""
import argparse
import glob
import json
import os
import sys
import time
import threading
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

SKILLS = ["hunt-ssrf", "hunt-request-smuggling", "hunt-command-injection",
          "hunt-path-traversal", "hunt-nodejs-permission-bypass", "hunt-deserialization",
          "hunt-prototype-pollution", "hunt-auth-bypass", "hunt-xss", "hunt-xxe",
          "hunt-sqli", "hunt-csrf", "hunt-cache-poisoning", "hunt-open-redirect",
          "recognize-attack-surface"]
ACTIONS = {"fold", "new-skill", "drop"}
_lock = threading.Lock()


def log(m):
    with _lock:
        print(m, flush=True)


def read_key():
    p = os.path.join(os.environ.get("USERPROFILE", "C:/Users/g1582"), ".pi", "agent", "auth.json")
    p = os.environ.get("PI_AUTH_JSON", p)
    with open(p, encoding="utf-8") as f:
        return json.load(f)["deepseek"]["key"]


SYSTEM = """你是渗透测试知识策展专家。输入是一批"值得固化但零散的漏洞知识点"，每条含 id、一轮类别、知识点描述。
已有的渗透 skill 库如下（fold 时 target 必须从中选）：
- hunt-ssrf / hunt-request-smuggling / hunt-command-injection / hunt-path-traversal
- hunt-nodejs-permission-bypass / hunt-deserialization / hunt-prototype-pollution
- hunt-auth-bypass / hunt-xss / hunt-xxe / hunt-sqli / hunt-csrf
- hunt-cache-poisoning / hunt-open-redirect
- recognize-attack-surface（方法论总线，收纳跨组件攻击链/业务逻辑/配置错误/信息泄露等无专用 skill 的横切类）

对每条判定：
- action="fold"：该知识点属于某现有 skill 的一个绕过变体 → target 填该 skill 名。绝大多数应是这类。
- action="new-skill"：确属现有 14 类都不覆盖的全新独立主题 → target 填建议的 skill slug（hunt-xxx）。从严，别轻易新建。
- action="drop"：太窄/高度依赖单一环境/或属内存破坏等非本 web 库范围 → target="" 并在 reason 说明。
- theme：把同类知识点归到同一主题名（跨批可能重复，没关系）。
- reason：一句话中文依据。

严格输出 JSON（不要 markdown 代码块）：
{"detailed": [{"id": 123, "theme": "...", "action": "fold", "target": "hunt-ssrf", "reason": "..."}, ...]}
输出 id 集合必须与输入完全一致。"""


def call(base_url, key, model, user, max_tokens, temperature=0.0, timeout=300):
    body = {"model": model, "temperature": temperature, "max_tokens": max_tokens,
            "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
            "response_format": {"type": "json_object"}, "thinking": {"type": "disabled"}}
    req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions",
                                 data=json.dumps(body).encode("utf-8"), method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + key)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))["choices"][0]["message"]["content"]


def strip_fences(s):
    s = s.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else s
        if s.rstrip().endswith("```"):
            s = s.rstrip()[:-3]
    return s.strip()


def validate(parsed, ids):
    evs = parsed.get("detailed")
    if not isinstance(evs, list):
        return "缺 detailed"
    out = {int(e["id"]) for e in evs if "id" in e}
    if out != set(ids):
        return "id 不匹配 缺=%s 多=%s" % (sorted(set(ids) - out)[:5], sorted(out - set(ids))[:5])
    for e in evs:
        if e.get("action") not in ACTIONS:
            return "id=%s 非法 action %r" % (e.get("id"), e.get("action"))
        if e["action"] == "fold" and e.get("target") not in SKILLS:
            return "id=%s fold target 非法 %r" % (e.get("id"), e.get("target"))
    return None


def load_singletons(path):
    out = []
    for line in open(path, encoding="utf-8"):
        c = json.loads(line)
        if c.get("size") == 1:
            out.append({"id": c["rep_id"], "category": c.get("category"),
                        "knowledge_point": c.get("knowledge_point"),
                        "report_url": c.get("report_url")})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="candidate_shortlist.jsonl")
    ap.add_argument("--base-url", default="https://api.deepseek.com/v1")
    ap.add_argument("--model", default="deepseek-v4-flash")
    ap.add_argument("--size", type=int, default=20)
    ap.add_argument("--out", default="routed")
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--max-tokens", type=int, default=12000)
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--aggregate", action="store_true")
    args = ap.parse_args()

    singles = load_singletons(args.src)
    batches = [singles[i:i + args.size] for i in range(0, len(singles), args.size)]
    os.makedirs(args.out, exist_ok=True)

    if not args.aggregate:
        key = read_key()
        counters = {"ok": 0, "skip": 0, "fail": 0}
        t0 = time.time()
        log("[start] 单例 %d 条 -> %d 批 | 并发 %d" % (len(singles), len(batches), args.concurrency))

        def work(idx_batch):
            idx, batch = idx_batch
            outp = os.path.join(args.out, "batch_%04d.json" % idx)
            if os.path.exists(outp):
                with _lock:
                    counters["skip"] += 1
                return
            ids = [b["id"] for b in batch]
            user = json.dumps({"items": batch}, ensure_ascii=False)
            for attempt in range(1, args.retries + 1):
                try:
                    parsed = json.loads(strip_fences(call(args.base_url, key, args.model, user, args.max_tokens)))
                    err = validate(parsed, ids)
                    if err:
                        raise ValueError(err)
                    tmp = outp + ".tmp"
                    json.dump(parsed, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                    os.replace(tmp, outp)
                    with _lock:
                        counters["ok"] += 1
                        done = counters["ok"] + counters["skip"]
                        log("[ok] batch_%04d %d条 | %d/%d 用时%ds" % (idx, len(ids), done, len(batches), time.time() - t0))
                    return
                except (urllib.error.URLError, urllib.error.HTTPError) as e:
                    log("[net] batch_%04d %d/%d %s" % (idx, attempt, args.retries, e)); time.sleep(min(2 ** attempt, 20))
                except Exception as e:
                    log("[err] batch_%04d %d/%d %s" % (idx, attempt, args.retries, e)); time.sleep(1)
            with _lock:
                counters["fail"] += 1

        with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
            for _ in as_completed([ex.submit(work, (i, b)) for i, b in enumerate(batches)]):
                pass
        log("[done] ok=%d skip=%d fail=%d" % (counters["ok"], counters["skip"], counters["fail"]))

    # 汇总
    rows = []
    for f in sorted(glob.glob(os.path.join(args.out, "batch_*.json"))):
        for e in json.load(open(f, encoding="utf-8")).get("detailed", []):
            rows.append(e)
    by_id = {b["id"]: b for b in singles}
    for r in rows:
        meta = by_id.get(r["id"], {})
        r["knowledge_point"] = meta.get("knowledge_point")
        r["report_url"] = meta.get("report_url")
        r["category"] = meta.get("category")
    json.dump(rows, open("routing_all.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # 决策单：按 action + target 分组
    from collections import defaultdict
    groups = defaultdict(list)
    for r in rows:
        key = "%s → %s" % (r["action"], r.get("target") or "-")
        groups[key].append(r)
    lines = ["# 第三轮 单例路由决策单\n",
             "592 个单例经语义归并 + 路由。每行你只需标：保留建议 / 改路由 / 丢弃。\n",
             "已路由 %d 条，分 %d 组。\n" % (len(rows), len(groups))]
    order = sorted(groups, key=lambda k: (-len(groups[k]), k))
    lines.append("## 概览\n\n| 动作→目标 | 条数 |\n|---|---|")
    for k in order:
        lines.append("| %s | %d |" % (k, len(groups[k])))
    for k in order:
        lines.append("\n## %s （%d）\n" % (k, len(groups[k])))
        # 按 theme 再聚
        by_theme = defaultdict(list)
        for r in groups[k]:
            by_theme[r.get("theme") or "-"].append(r)
        for theme, items in sorted(by_theme.items(), key=lambda x: -len(x[1])):
            ids = ", ".join(str(i["id"]) for i in items)
            lines.append("- **%s**（%d）: %s" % (theme, len(items), ids))
    open("singleton_routing.md", "w", encoding="utf-8").write("\n".join(lines))
    print("输出: singleton_routing.md / routing_all.json（%d 条, %d 组）" % (len(rows), len(groups)))


if __name__ == "__main__":
    main()
