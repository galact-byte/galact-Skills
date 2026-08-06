# -*- coding: utf-8 -*-
"""
第二轮筛选运行器：在一轮高分案例上判断"是否值得写成 Skill"。

口径见 round2_prompt.md（忠于 Prompt2.md：稀缺性/高频性/可迁移性/来源质量 → worth_skill），
只在其外面套上和第一轮一致的"批量 + id + 校验 + 续跑"骨架，以便自动化跑完 2605 条。

数据流：
  scored_all.parquet (value_score>=--min-score，默认7 → 2605 条)
    └─(自动 in-memory 分批)→ batches2/batch_*.json
        └─ run_round2.py (LLM, round2_prompt.md) → scored2/batch_*.json
            └─ run_round2.py --aggregate → round2_all.parquet/.jsonl + skill_candidates.md

复用第一轮同款能力：可续跑（跳过已完成批）、逐批校验（输出 id 集合==输入、字段齐全、枚举合法）、
失败存 failed2/、--concurrency 并发、--shards/--shard 多终端分片、默认关 thinking。

用法：
  # 试跑 3 批（人工抽查判断是否符合 Prompt2 口径）
  python run_round2.py --model deepseek-v4-flash --concurrency 3 --max-tokens 16000 --limit 3
  # 全量（可续跑，中断再跑只补未完成批）
  python run_round2.py --model deepseek-v4-flash --concurrency 16 --max-tokens 16000
  # 汇总
  D:\\Tools\\Python\\Anaconda3\\python.exe run_round2.py --aggregate
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

_print_lock = threading.Lock()


def log(msg):
    with _print_lock:
        print(msg, flush=True)


def fmt_dur(sec):
    sec = int(sec)
    if sec < 60:
        return "%ds" % sec
    if sec < 3600:
        return "%dm%02ds" % (sec // 60, sec % 60)
    return "%dh%02dm" % (sec // 3600, (sec % 3600) // 60)


def atomic_write_json(path, obj):
    tmp = "%s.tmp.%d" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


# ---- 第二轮 schema 校验 ----
CASE_FIELDS = ["id", "title", "category", "value_score", "weakness_name",
               "attack_chain", "bypass_technique", "defensive_insight", "reasoning"]
REQUIRED_EVAL_FIELDS = {"id", "knowledge_point", "is_ai_likely_known", "reason",
                        "scene_frequency", "migration_potential", "source_quality",
                        "worth_skill", "suggested_handling", "skill_framework"}
FREQ = {"高频", "中频", "低频"}
SRC_Q = {"高", "中", "通用"}


def load_prompt(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def call_model(base_url, api_key, model, system, user, temperature, max_tokens,
               disable_thinking=True, timeout=300):
    url = base_url.rstrip("/") + "/chat/completions"
    body = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "response_format": {"type": "json_object"},
    }
    if disable_thinking:
        body["thinking"] = {"type": "disabled"}
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + api_key)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return payload["choices"][0]["message"]["content"]


def strip_fences(s):
    s = s.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else s
        if s.rstrip().endswith("```"):
            s = s.rstrip()[:-3]
    return s.strip()


def as_bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        if v.strip().lower() in ("true", "是", "yes"):
            return True
        if v.strip().lower() in ("false", "否", "no"):
            return False
    return None


def normalize_eval(e):
    """把模型偶发的字符串布尔/多余空白规范化，减少无谓重试。"""
    for k in ("is_ai_likely_known", "worth_skill"):
        b = as_bool(e.get(k))
        if b is not None:
            e[k] = b
    if isinstance(e.get("scene_frequency"), str):
        e["scene_frequency"] = e["scene_frequency"].strip()
    if isinstance(e.get("source_quality"), str):
        e["source_quality"] = e["source_quality"].strip()
    # worth_skill=false 但给了框架 → 置空，保持口径一致
    if e.get("worth_skill") is False:
        e["skill_framework"] = None


def validate(parsed, input_ids):
    if "detailed_evaluations" not in parsed:
        return "缺少 detailed_evaluations"
    evs = parsed["detailed_evaluations"]
    out_ids = {int(e.get("id")) for e in evs if "id" in e}
    if out_ids != set(input_ids):
        miss = set(input_ids) - out_ids
        extra = out_ids - set(input_ids)
        return "id 集合不匹配 缺失=%s 多余=%s" % (sorted(miss)[:5], sorted(extra)[:5])
    for e in evs:
        missing = REQUIRED_EVAL_FIELDS - set(e)
        if missing:
            return "id=%s 缺字段 %s" % (e.get("id"), missing)
        if not isinstance(e["is_ai_likely_known"], bool):
            return "id=%s is_ai_likely_known 非布尔" % e["id"]
        if not isinstance(e["worth_skill"], bool):
            return "id=%s worth_skill 非布尔" % e["id"]
        if e["scene_frequency"] not in FREQ:
            return "id=%s 非法 scene_frequency %r" % (e["id"], e.get("scene_frequency"))
        if e["source_quality"] not in SRC_Q:
            return "id=%s 非法 source_quality %r" % (e["id"], e.get("source_quality"))
        if not str(e.get("migration_potential", "")).strip():
            return "id=%s migration_potential 为空" % e["id"]
        if e["worth_skill"] and not isinstance(e["skill_framework"], dict):
            return "id=%s worth_skill=true 但 skill_framework 非对象" % e["id"]
        if not e["worth_skill"] and e["skill_framework"] is not None:
            return "id=%s worth_skill=false 但 skill_framework 非 null" % e["id"]
    return None


def build_batches(src, out_dir, min_score, size, rebuild):
    """从一轮汇总筛 value_score>=min_score，切成 batches2/batch_*.json。已存在则跳过（除非 --rebuild）。"""
    import pandas as pd
    existing = sorted(glob.glob(os.path.join(out_dir, "batch_*.json")))
    if existing and not rebuild:
        return len(existing)
    df = pd.read_parquet(src)
    hi = df[df["value_score"] >= min_score].sort_values(
        "value_score", ascending=False).reset_index(drop=True)
    cols = [c for c in CASE_FIELDS if c in hi.columns]
    hi = hi[cols].where(lambda d: d.notnull(), None)
    os.makedirs(out_dir, exist_ok=True)
    for f in existing:
        os.remove(f)
    n = len(hi)
    nb = (n + size - 1) // size
    for i in range(nb):
        chunk = hi.iloc[i * size:(i + 1) * size]
        bid = "batch_%04d" % i
        recs = chunk.to_dict(orient="records")
        for r in recs:
            r["id"] = int(r["id"])
        payload = {"batch_id": bid, "cases": recs}
        with open(os.path.join(out_dir, bid + ".json"), "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
    log("[build] value_score>=%d 共 %d 条 -> %d 批 × %d，写入 %s/" % (min_score, n, nb, size, out_dir))
    return nb


def aggregate(scored_dir, meta_src, out_prefix, md_path):
    import pandas as pd
    rows = []
    for path in sorted(glob.glob(os.path.join(scored_dir, "batch_*.json"))):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        for e in d.get("detailed_evaluations", []):
            rows.append({
                "id": int(e["id"]),
                "knowledge_point": e.get("knowledge_point"),
                "is_ai_likely_known": e.get("is_ai_likely_known"),
                "scene_frequency": e.get("scene_frequency"),
                "migration_potential": e.get("migration_potential"),
                "source_quality": e.get("source_quality"),
                "worth_skill": e.get("worth_skill"),
                "reason": e.get("reason"),
                "suggested_handling": e.get("suggested_handling"),
                "skill_framework": e.get("skill_framework"),
            })
    r2 = pd.DataFrame(rows).drop_duplicates("id")
    print("第二轮已判断条数:", len(r2))

    meta = pd.read_parquet(meta_src)
    keep = ["id", "value_score", "verdict", "category", "title", "report_url",
            "weakness_name", "max_severity", "attack_chain", "bypass_technique",
            "defensive_insight"]
    keep = [c for c in keep if c in meta.columns]
    merged = r2.merge(meta[keep], on="id", how="left")
    merged = merged.sort_values(
        ["worth_skill", "value_score"], ascending=[False, False]).reset_index(drop=True)

    merged.to_parquet(out_prefix + ".parquet", index=False)
    with open(out_prefix + ".jsonl", "w", encoding="utf-8") as f:
        for _, r in merged.iterrows():
            rec = r.to_dict()
            for k, v in list(rec.items()):
                if isinstance(v, float) and pd.isna(v):
                    rec[k] = None
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    worth = merged[merged["worth_skill"] == True].copy()  # noqa: E712
    print("\n=== worth_skill 分布 ===")
    print(merged["worth_skill"].value_counts(dropna=False).to_string())
    print("\n=== scene_frequency 分布 ===")
    print(merged["scene_frequency"].value_counts(dropna=False).to_string())
    print("\n=== source_quality 分布 ===")
    print(merged["source_quality"].value_counts(dropna=False).to_string())
    print("\nworth_skill=true:", len(worth), "/", len(merged))

    # 人读版：仅 worth_skill=true，按一轮 category 分组
    lines = ["# 第二轮筛选 — 值得固化为 Skill 的候选\n"]
    lines.append("来源：一轮 value_score≥阈值案例，经第二轮'是否值得写成 Skill'判断后 worth_skill=true 的条目。\n")
    lines.append("候选总数: %d\n" % len(worth))
    worth["cat0"] = worth["category"].fillna("其他").str.split(" / ").str[0].str.strip()
    for cat, sub in worth.groupby("cat0"):
        sub = sub.sort_values("value_score", ascending=False)
        lines.append("\n## %s （%d 例）\n" % (cat, len(sub)))
        for _, r in sub.iterrows():
            lines.append("### [%s] %s" % (r["id"], str(r.get("knowledge_point") or r.get("title")).strip()))
            if r.get("report_url"):
                lines.append("- 报告: %s" % r["report_url"])
            lines.append("- 频率/迁移/来源: %s / %s / %s"
                         % (r.get("scene_frequency"), r.get("migration_potential"), r.get("source_quality")))
            lines.append("- 处理建议: %s" % r.get("suggested_handling"))
            fw = r.get("skill_framework")
            if isinstance(fw, dict) and fw.get("name"):
                lines.append("- 建议 Skill 名: %s" % fw.get("name"))
            lines.append("")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n输出:", out_prefix + ".parquet /", out_prefix + ".jsonl /", md_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", ""))
    ap.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    ap.add_argument("--model", default=os.environ.get("SCORING_MODEL", "gpt-4o-mini"))
    ap.add_argument("--prompt", default="round2_prompt.md")
    ap.add_argument("--src", default="scored_all.parquet", help="一轮汇总（第二轮输入源）")
    ap.add_argument("--min-score", type=int, default=7, help="一轮 value_score 下限（默认7=高优先级）")
    ap.add_argument("--size", type=int, default=15, help="每批案例数")
    ap.add_argument("--batches", default="batches2")
    ap.add_argument("--out", default="scored2")
    ap.add_argument("--failed", default="failed2")
    ap.add_argument("--rebuild", action="store_true", help="强制重建批次（改了 --min-score/--size 时用）")
    ap.add_argument("--aggregate", action="store_true", help="仅汇总已评分批次，不调用模型")
    ap.add_argument("--agg-out", default="round2_all")
    ap.add_argument("--agg-md", default="skill_candidates.md")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--limit", type=int, default=0, help="仅跑前 N 批(0=全部)")
    ap.add_argument("--sleep", type=float, default=0.0)
    ap.add_argument("--shards", type=int, default=1)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--concurrency", type=int, default=1)
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--enable-thinking", action="store_true")
    args = ap.parse_args()

    if args.aggregate:
        aggregate(args.out, args.src, args.agg_out, args.agg_md)
        return

    if not args.api_key:
        sys.exit("缺少 API key：--api-key 或环境变量 OPENAI_API_KEY")
    if not (0 <= args.shard < args.shards):
        sys.exit("--shard 必须在 0..--shards-1 之间")

    # 分批只需一个进程做；多分片时 shard 0 负责建，其它等其建好
    if args.shard == 0:
        build_batches(args.src, args.batches, args.min_score, args.size, args.rebuild)
    else:
        for _ in range(60):
            if glob.glob(os.path.join(args.batches, "batch_*.json")):
                break
            time.sleep(1)

    system = load_prompt(args.prompt)
    os.makedirs(args.out, exist_ok=True)
    os.makedirs(args.failed, exist_ok=True)

    batch_files = sorted(f for f in os.listdir(args.batches)
                         if f.startswith("batch_") and f.endswith(".json"))
    if args.limit:
        batch_files = batch_files[:args.limit]
    batch_files = [bf for i, bf in enumerate(batch_files) if i % args.shards == args.shard]

    total = len(batch_files)
    counters = {"done": 0, "skipped": 0, "failed": 0, "processed": 0}
    clock = threading.Lock()
    t0 = time.time()
    log("[start] 第二轮 分片 %d/%d 认领 %d 批 | 并发 %d | 模型 %s"
        % (args.shard, args.shards, total, args.concurrency, args.model))

    def progress(tag, bid, extra=""):
        p = counters["processed"]
        elapsed = time.time() - t0
        rate = p / elapsed if elapsed > 0 else 0
        eta = (total - p) / rate if rate > 0 else 0
        log("[%s] %s %s | %d/%d %.1f%% (ok=%d skip=%d fail=%d) | 用时 %s 预计剩 %s"
            % (tag, bid, extra, p, total, 100.0 * p / total if total else 100,
               counters["done"], counters["skipped"], counters["failed"],
               fmt_dur(elapsed), fmt_dur(eta)))

    def process_one(bf):
        bid = bf[:-5]
        out_path = os.path.join(args.out, bf)
        if os.path.exists(out_path):
            with clock:
                counters["skipped"] += 1
                counters["processed"] += 1
                progress("SKIP", bid, "(已存在)")
            return
        log("[run ] %s 开始…" % bid)
        t_batch = time.time()
        with open(os.path.join(args.batches, bf), encoding="utf-8") as f:
            batch = json.load(f)
        input_ids = [int(r["id"]) for r in batch["cases"]]
        user = json.dumps(batch, ensure_ascii=False)

        last_raw = ""
        for attempt in range(1, args.retries + 1):
            try:
                content = call_model(args.base_url, args.api_key, args.model,
                                     system, user, args.temperature, args.max_tokens,
                                     disable_thinking=not args.enable_thinking)
                last_raw = content
                parsed = json.loads(strip_fences(content))
                for e in parsed.get("detailed_evaluations", []):
                    normalize_eval(e)
                err = validate(parsed, input_ids)
                if err:
                    raise ValueError(err)
                if os.path.exists(out_path):
                    with clock:
                        counters["skipped"] += 1
                    return
                atomic_write_json(out_path, parsed)
                with clock:
                    counters["done"] += 1
                    counters["processed"] += 1
                    progress("OK  ", bid, "%d条 用时%s" % (len(input_ids), fmt_dur(time.time() - t_batch)))
                if args.sleep:
                    time.sleep(args.sleep)
                return
            except (urllib.error.URLError, urllib.error.HTTPError) as e:
                log("[NET] %s attempt %d/%d: %s" % (bid, attempt, args.retries, e))
                time.sleep(min(2 ** attempt, 30))
            except Exception as e:
                log("[ERR] %s attempt %d/%d: %s" % (bid, attempt, args.retries, e))
                time.sleep(1)
        with clock:
            counters["failed"] += 1
            counters["processed"] += 1
            progress("FAIL", bid, "-> failed2/")
        with open(os.path.join(args.failed, bid + ".raw.txt"), "w", encoding="utf-8") as f:
            f.write(last_raw or "")

    if args.concurrency <= 1:
        for bf in batch_files:
            process_one(bf)
    else:
        with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
            futs = [ex.submit(process_one, bf) for bf in batch_files]
            for _ in as_completed(futs):
                pass

    log("\nDONE[shard %d/%d]. scored=%d skipped=%d failed=%d assigned=%d"
        % (args.shard, args.shards, counters["done"], counters["skipped"],
           counters["failed"], len(batch_files)))


if __name__ == "__main__":
    main()
