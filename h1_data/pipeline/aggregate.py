# -*- coding: utf-8 -*-
"""
汇总所有已评分批次 -> 单一评分数据集，并 join 回元数据。

输入: pipeline/scored/batch_*.json, pipeline/batches/_manifest.json, 高质量子集 parquet
输出:
  pipeline/scored_all.parquet   评分 + 元数据（每条报告一行）
  pipeline/scored_all.jsonl
  控制台: 覆盖率校验 + verdict/分数/类别分布

用法: python aggregate.py [--meta ../out/h1_clean_filtered.parquet]
"""
import argparse
import glob
import json
import os
import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scored", default="scored")
    ap.add_argument("--meta", default="../out/h1_clean_filtered.parquet")
    ap.add_argument("--manifest", default="batches/_manifest.json")
    ap.add_argument("--out", default="scored_all")
    args = ap.parse_args()

    rows = []
    for path in sorted(glob.glob(os.path.join(args.scored, "batch_*.json"))):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        for e in d.get("detailed_evaluations", []):
            b = e.get("score_breakdown", {})
            rows.append({
                "id": int(e["id"]),
                "value_score": e.get("value_score"),
                "unexpectedness": b.get("unexpectedness"),
                "elegance": b.get("elegance"),
                "chain": b.get("chain"),
                "reproducibility": b.get("reproducibility"),
                "verdict": e.get("verdict"),
                "category": e.get("category"),
                "reasoning": e.get("reasoning"),
                "attack_chain": e.get("attack_chain"),
                "bypass_technique": e.get("bypass_technique"),
                "defensive_insight": e.get("defensive_insight"),
            })
    scored = pd.DataFrame(rows).drop_duplicates("id")
    print("已汇总评分条数:", len(scored))

    # 覆盖率校验
    if os.path.exists(args.manifest):
        man = json.load(open(args.manifest, encoding="utf-8"))
        all_ids = {i for b in man["batches"] for i in b["ids"]}
        got = set(scored["id"])
        missing = all_ids - got
        print("应评分:", len(all_ids), "| 已评分:", len(got),
              "| 缺失:", len(missing))
        if missing:
            print("  缺失样例(前10):", sorted(missing)[:10])

    # join 元数据
    meta = pd.read_parquet(args.meta)
    keep_meta = ["id", "title", "report_url", "substate", "weakness_name",
                 "max_severity", "asset_type", "team_handle", "team_name",
                 "has_bounty", "vote_count", "disclosed_at", "vi_length",
                 "actionability"]
    keep_meta = [c for c in keep_meta if c in meta.columns]
    merged = scored.merge(meta[keep_meta], on="id", how="left")

    merged = merged.sort_values("value_score", ascending=False).reset_index(drop=True)
    merged.to_parquet(args.out + ".parquet", index=False)
    with open(args.out + ".jsonl", "w", encoding="utf-8") as f:
        for _, r in merged.iterrows():
            rec = r.to_dict()
            if pd.notnull(rec.get("disclosed_at")):
                rec["disclosed_at"] = rec["disclosed_at"].isoformat()
            for k, v in list(rec.items()):
                if pd.isna(v):
                    rec[k] = None
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # 分布
    print("\n=== verdict 分布 ===")
    print(merged["verdict"].value_counts(dropna=False).to_string())
    print("\n=== value_score 分布 ===")
    print(merged["value_score"].value_counts().sort_index().to_string())
    print("\n=== 高优先级(≥7) 分类 Top15 ===")
    hi = merged[merged["value_score"] >= 7]
    cats = hi["category"].fillna("其他").str.split(" / ").explode().str.strip()
    print(cats.value_counts().head(15).to_string())
    print("\n保留 vs 丢弃:",
          int(merged["verdict"].str.startswith("保留").sum()), "/",
          int(merged["verdict"].str.startswith("丢弃").sum()))
    print("高优先级(≥7):", len(hi))
    print("\n输出:", args.out + ".parquet /", args.out + ".jsonl")

if __name__ == "__main__":
    main()
