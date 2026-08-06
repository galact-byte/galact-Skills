# -*- coding: utf-8 -*-
"""
第二轮候选合并去重：把 worth_skill=true 的 1346 条聚成有限个"知识点候选"。

问题：round2 模型几乎给每条起了独立框架名（近乎逐条唯一），没做合并。
本脚本在"一轮主类别"内，按 knowledge_point 文本相似度贪心聚类，
每簇取一轮 value_score 最高者为代表，簇大小=该技术反复出现的次数=优先级。

输入: round2_all.parquet
输出:
  candidate_shortlist.md    去重后的知识点候选清单（按类分组，簇内折叠成员）
  candidate_shortlist.jsonl 结构化版（每簇一行：代表+成员ids+信号）
控制台: 每类候选簇数、总簇数

用法: python consolidate_round2.py [--min-score 7] [--sim 0.55] [--strict]
  --strict: 只保留 is_ai_likely_known=false & source_quality=高 & migration 以"高"开头 的强稀缺核心
"""
import argparse
import json
import re
from difflib import SequenceMatcher
import pandas as pd

_STOP = re.compile(r"[\s，。、（）()\[\]/：:；;\-—_“”\"'’·]+")


def norm(s):
    s = str(s or "").strip().lower()
    return _STOP.sub("", s)


def cluster(names_scores, sim_th):
    """贪心聚类：names_scores=[(idx, name)]。返回 [[idx...], ...]，按代表分数降序稳定。"""
    clusters = []  # each: {rep_name, members:[idx]}
    for idx, name in names_scores:
        key = norm(name)
        placed = False
        for c in clusters:
            if SequenceMatcher(None, key, c["key"]).ratio() >= sim_th:
                c["members"].append(idx)
                placed = True
                break
        if not placed:
            clusters.append({"key": key, "members": [idx]})
    return clusters


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="round2_all.parquet")
    ap.add_argument("--min-score", type=int, default=7)
    ap.add_argument("--sim", type=float, default=0.55, help="同簇相似度阈值(0-1)，越高越不易合并")
    ap.add_argument("--strict", action="store_true", help="仅强稀缺核心")
    ap.add_argument("--md", default="candidate_shortlist.md")
    ap.add_argument("--jsonl", default="candidate_shortlist.jsonl")
    args = ap.parse_args()

    d = pd.read_parquet(args.src)
    w = d[(d["worth_skill"] == True) & (d["value_score"] >= args.min_score)].copy()  # noqa: E712
    if args.strict:
        w = w[(w["is_ai_likely_known"] == False)  # noqa: E712
              & (w["source_quality"] == "高")
              & (w["migration_potential"].fillna("").str.startswith("高"))]
    w["kp"] = w["knowledge_point"].fillna(w["title"]).astype(str)
    w["cat0"] = w["category"].fillna("其他").str.split(" / ").str[0].str.strip()
    print("参与合并:", len(w), "| strict=", args.strict, "| sim=", args.sim)

    all_clusters = []
    for cat, sub in w.groupby("cat0"):
        sub = sub.reset_index(drop=True)
        cl = cluster(list(zip(sub.index, sub["kp"])), args.sim)
        for c in cl:
            mem = sub.loc[c["members"]]
            rep = mem.sort_values("value_score", ascending=False).iloc[0]
            all_clusters.append({
                "category": cat,
                "size": len(mem),
                "rep_id": int(rep["id"]),
                "knowledge_point": rep["kp"],
                "max_score": int(mem["value_score"].max()),
                "scene_frequency": rep.get("scene_frequency"),
                "migration_potential": rep.get("migration_potential"),
                "source_quality": rep.get("source_quality"),
                "member_ids": [int(x) for x in mem["id"].tolist()],
                "report_url": rep.get("report_url"),
                "suggested_handling": rep.get("suggested_handling"),
            })

    # 排序：先按簇大小(复现次数)降序，再按最高分降序
    all_clusters.sort(key=lambda c: (c["size"], c["max_score"]), reverse=True)
    print("去重后候选簇总数:", len(all_clusters))

    with open(args.jsonl, "w", encoding="utf-8") as f:
        for c in all_clusters:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    # 人读版：按类分组，类内按簇大小降序
    by_cat = {}
    for c in all_clusters:
        by_cat.setdefault(c["category"], []).append(c)
    cat_order = sorted(by_cat, key=lambda k: len(by_cat[k]), reverse=True)

    lines = ["# 第二轮 知识点候选清单（去重后）\n"]
    lines.append("来源：round2 判定 worth_skill=true%s，在一轮主类别内按知识点相似度合并。\n"
                 % ("（强稀缺核心）" if args.strict else ""))
    lines.append("原始通过 %d 条 → 去重后 **%d 个候选**。簇大小=该技术在数据集中反复出现的次数=优先级信号。\n"
                 % (len(w), len(all_clusters)))
    lines.append("\n## 分类概览\n")
    lines.append("| 类别 | 候选数 |\n|---|---|")
    for cat in cat_order:
        lines.append("| %s | %d |" % (cat, len(by_cat[cat])))

    for cat in cat_order:
        lines.append("\n## %s （%d 个候选）\n" % (cat, len(by_cat[cat])))
        for c in by_cat[cat]:
            tag = "★%d次" % c["size"] if c["size"] > 1 else "单例"
            lines.append("### [%s] %s  (%s, max_score %d)"
                         % (c["rep_id"], c["knowledge_point"].strip(), tag, c["max_score"]))
            lines.append("- 频率/迁移/来源: %s / %s / %s"
                         % (c["scene_frequency"], c["migration_potential"], c["source_quality"]))
            if c["size"] > 1:
                lines.append("- 同簇报告(%d): %s" % (c["size"], ", ".join(map(str, c["member_ids"][:15]))
                                                 + (" …" if c["size"] > 15 else "")))
            if c.get("report_url"):
                lines.append("- 代表报告: %s" % c["report_url"])
            lines.append("")

    with open(args.md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("输出:", args.md, "/", args.jsonl)
    print("\n=== 各类候选数(去重后) ===")
    for cat in cat_order:
        print("%-12s %d" % (cat, len(by_cat[cat])))


if __name__ == "__main__":
    main()
