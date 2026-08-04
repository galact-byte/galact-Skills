# -*- coding: utf-8 -*-
"""
将高质量子集切分为 LLM 评分输入批次。

每个批次文件: pipeline/batches/batch_XXXX.json
格式: { "batch_id": "batch_0000", "reports": [ {report对象}, ... ] }

report 对象仅含策展所需字段（正文为主、title 为辅、weakness 仅参考、
substate 供复现性规则），避免多余字段引入偏差与 token 浪费。

用法:
  python build_batches.py [--size 20] [--src ../out/h1_clean_filtered.parquet]
"""
import argparse
import json
import os
import pandas as pd

FIELDS = ["id", "title", "substate", "weakness_name", "vulnerability_information"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=20, help="每批报告数")
    ap.add_argument("--src", default="../out/h1_clean_filtered.parquet")
    ap.add_argument("--out", default="batches")
    args = ap.parse_args()

    df = pd.read_parquet(args.src)[FIELDS].reset_index(drop=True)
    # weakness_name 缺失填 None -> null；确保 JSON 干净
    df = df.where(pd.notnull(df), None)

    os.makedirs(args.out, exist_ok=True)
    # 清空旧批次，避免残留
    for f in os.listdir(args.out):
        if f.startswith("batch_") and f.endswith(".json"):
            os.remove(os.path.join(args.out, f))

    n = len(df)
    nbatches = (n + args.size - 1) // args.size
    manifest = []
    for i in range(nbatches):
        chunk = df.iloc[i*args.size:(i+1)*args.size]
        bid = "batch_%04d" % i
        recs = chunk.to_dict(orient="records")
        payload = {"batch_id": bid, "reports": recs}
        path = os.path.join(args.out, bid + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        manifest.append({"batch_id": bid, "count": len(recs),
                         "ids": [int(r["id"]) for r in recs]})

    with open(os.path.join(args.out, "_manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"total_reports": n, "batch_size": args.size,
                   "num_batches": nbatches, "batches": manifest},
                  f, ensure_ascii=False, indent=1)

    print("total=%d size=%d -> %d batches in %s/" % (n, args.size, nbatches, args.out))

if __name__ == "__main__":
    main()
