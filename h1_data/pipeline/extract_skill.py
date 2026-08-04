# -*- coding: utf-8 -*-
"""
从评分结果抽取 skill 素材：按类别组织高价值案例的
attack_chain / bypass_technique / defensive_insight。

输入: pipeline/scored_all.parquet
输出:
  pipeline/skill_material.jsonl   每条高价值案例的结构化素材（喂 skill 生成）
  pipeline/skill_source.md        按类别分组的人读版技术模式库

用法: python extract_skill.py [--min-score 7]
"""
import argparse
import json
import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="scored_all.parquet")
    ap.add_argument("--min-score", type=int, default=7)
    ap.add_argument("--jsonl", default="skill_material.jsonl")
    ap.add_argument("--md", default="skill_source.md")
    args = ap.parse_args()

    df = pd.read_parquet(args.src)
    hi = df[df["value_score"] >= args.min_score].copy()
    hi = hi.sort_values("value_score", ascending=False).reset_index(drop=True)
    print("高价值案例(≥%d): %d / %d" % (args.min_score, len(hi), len(df)))

    # 结构化素材 jsonl
    cols = ["id", "report_url", "title", "value_score", "verdict", "category",
            "weakness_name", "max_severity", "asset_type",
            "attack_chain", "bypass_technique", "defensive_insight", "reasoning"]
    cols = [c for c in cols if c in hi.columns]
    with open(args.jsonl, "w", encoding="utf-8") as f:
        for _, r in hi[cols].iterrows():
            rec = {k: (None if pd.isna(v) else v) for k, v in r.to_dict().items()}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # 人读版：按（拆分后的）主类别分组
    hi["cats"] = hi["category"].fillna("其他").str.split(" / ")
    exploded = hi.explode("cats")
    exploded["cats"] = exploded["cats"].str.strip()

    lines = ["# HackerOne 高价值案例 — 渗透 skill 技术模式库\n"]
    lines.append("按类别组织，来源为 value_score ≥ %d 的披露报告。每条含攻击链、绕过技术与防御要点。\n" % args.min_score)
    lines.append("案例总数: %d，覆盖类别: %d\n" % (len(hi), exploded["cats"].nunique()))

    order = (exploded.groupby("cats")["value_score"]
             .agg(["count", "mean"]).sort_values("count", ascending=False))
    for cat, row in order.iterrows():
        sub = exploded[exploded["cats"] == cat].drop_duplicates("id").sort_values(
            "value_score", ascending=False)
        lines.append("\n## %s （%d 例，均分 %.1f）\n" % (cat, int(row["count"]), row["mean"]))
        for _, r in sub.iterrows():
            lines.append("### [%s] %s  (score %d)" % (r["id"], str(r["title"]).strip(), r["value_score"]))
            if pd.notnull(r.get("report_url")):
                lines.append("- 报告: %s" % r["report_url"])
            lines.append("- 攻击链: %s" % r.get("attack_chain"))
            lines.append("- 绕过技术: %s" % r.get("bypass_technique"))
            lines.append("- 防御要点: %s" % r.get("defensive_insight"))
            lines.append("")

    with open(args.md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("输出:", args.jsonl, "/", args.md)

if __name__ == "__main__":
    main()
