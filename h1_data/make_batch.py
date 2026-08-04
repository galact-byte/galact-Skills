# -*- coding: utf-8 -*-
"""从高质量子集中取一个分层校准批，导出正文供策展打分。"""
import pandas as pd, json, sys

h = pd.read_parquet("out/h1_clean_filtered.parquet")

# 分层：actionability 4/3/2/1 各取若干，按 vote_count 降序取代表性样本
picks = []
plan = {4: 3, 3: 3, 2: 2, 1: 2}
for act, n in plan.items():
    sub = h[h["actionability"] == act].sort_values("vote_count", ascending=False)
    picks.append(sub.head(n))
batch = pd.concat(picks).drop_duplicates("id")

cols = ["id", "title", "substate", "weakness_name", "max_severity",
        "vote_count", "actionability", "has_repro_steps", "has_poc",
        "has_http_request", "vi_length", "vulnerability_information"]
batch = batch[cols].reset_index(drop=True)

with open("out/batch_calib.json", "w", encoding="utf-8") as f:
    json.dump({"reports": batch.to_dict(orient="records")}, f, ensure_ascii=False, indent=1)

# 同时打印简表
for _, r in batch.iterrows():
    print(f"id={r.id} act={r.actionability} votes={r.vote_count} sub={r.substate} "
          f"wk={r.weakness_name} len={r.vi_length} | {r.title[:60]}")
print("\nrows:", len(batch))
