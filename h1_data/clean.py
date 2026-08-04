# -*- coding: utf-8 -*-
"""
HackerOne Disclosed Reports 数据集清洗与筛选管线

输入: raw/*.parquet (train/test/validation)
输出:
  out/h1_clean_full.parquet   —— 全量清洗结果（扁平化+规范化+派生字段，不删行）
  out/h1_clean_filtered.parquet / .jsonl —— 高质量子集（按文档化规则筛选）
  out/report.md               —— 清洗与筛选统计报告

设计要点见 report.md。
"""
import glob
import json
import re
import hashlib
import pandas as pd

RAW_GLOB = "raw/*.parquet"
OUT_DIR = "out"

# ---------- 工具函数 ----------

_ws_multi_nl = re.compile(r"\n{3,}")
_trailing_ws = re.compile(r"[ \t]+\n")
_redaction = re.compile(r"\u2588+")  # 连续的 █ 打码块

# 渗透相关信号（便于下游按列筛选）
_re_repro = re.compile(r"steps?\s+to\s+reproduce|reproduc(e|tion)|复现步骤", re.I)
_re_poc = re.compile(r"proof\s*of\s*concept|\bpoc\b|exploit|payload", re.I)
_re_impact = re.compile(r"##?\s*impact|impact\s*:|影响\s*[:：]", re.I)
_re_http = re.compile(r"\b(?:GET|POST|PUT|DELETE|PATCH)\s+/|HTTP/1\.[01]|\bcurl\s|Authorization:\s|Cookie:\s", re.I)
_re_code = re.compile(r"```")
_re_url = re.compile(r"https?://[^\s)\]\"'>]+", re.I)
_re_cve = re.compile(r"CVE-\d{4}-\d{4,7}", re.I)

def norm_text(s):
    """规范化正文文本：统一换行、去零宽/控制字符、折叠多余空行、打码块归一。"""
    if s is None:
        return ""
    s = str(s)
    # 统一换行
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    # 去除 NULL 与不可见控制字符（保留 \n \t）
    s = "".join(ch for ch in s if ch == "\n" or ch == "\t" or ord(ch) >= 32)
    # 连续打码块 -> 单一标记
    s = _redaction.sub("[REDACTED]", s)
    # 折叠行尾空白与多空行
    s = _trailing_ws.sub("\n", s)
    s = _ws_multi_nl.sub("\n\n", s)
    return s.strip()

def g(d, *keys):
    """安全读取嵌套 dict 字段。"""
    if not isinstance(d, dict):
        return None
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur

def to_dt(s):
    return pd.to_datetime(s, errors="coerce", utc=True)

# ---------- 1. 载入并合并三个 split ----------

def load():
    frames = []
    for f in sorted(glob.glob(RAW_GLOB)):
        split = f.replace("\\", "/").split("/")[-1].split("-")[0]
        d = pd.read_parquet(f)
        d["orig_split"] = split
        frames.append(d)
    return pd.concat(frames, ignore_index=True)

# ---------- 2. 扁平化 + 规范化 + 派生 ----------

def build_clean(df):
    out = pd.DataFrame()
    out["id"] = df["id"].astype("int64")
    out["title"] = df["title"].map(lambda x: norm_text(x))
    out["substate"] = df["substate"]
    out["visibility"] = df["visibility"]
    out["has_bounty"] = df["has_bounty?"].astype(bool)
    out["vote_count"] = df["vote_count"].astype("int64")

    # 日期
    out["created_at"] = to_dt(df["created_at"])
    out["disclosed_at"] = to_dt(df["disclosed_at"])

    # 正文
    out["vulnerability_information"] = df["vulnerability_information"].map(norm_text)

    # reporter
    out["reporter_username"] = df["reporter"].map(lambda x: g(x, "username"))
    out["reporter_url"] = df["reporter"].map(lambda x: g(x, "url"))

    # team / program
    out["team_handle"] = df["team"].map(lambda x: g(x, "handle"))
    out["team_name"] = df["team"].map(lambda x: g(x, "profile", "name"))
    out["team_id"] = df["team"].map(lambda x: g(x, "id"))
    out["offers_bounties"] = df["team"].map(lambda x: g(x, "offers_bounties"))

    # weakness (CWE 类别)
    out["weakness_id"] = df["weakness"].map(lambda x: g(x, "id"))
    out["weakness_name"] = df["weakness"].map(lambda x: g(x, "name"))

    # structured_scope
    out["asset_type"] = df["structured_scope"].map(lambda x: g(x, "asset_type"))
    out["asset_identifier"] = df["structured_scope"].map(lambda x: g(x, "asset_identifier"))
    out["max_severity"] = df["structured_scope"].map(lambda x: g(x, "max_severity"))

    # 重复标记
    out["original_report_id"] = df["original_report_id"]
    out["is_duplicate"] = df["original_report_id"].notnull()

    out["orig_split"] = df["orig_split"]

    # 派生字段
    vi = out["vulnerability_information"]
    out["vi_length"] = vi.str.len().astype("int64")
    out["has_content"] = (out["visibility"] != "no-content") & (vi.str.strip() != "")
    out["has_redaction"] = vi.str.contains("[REDACTED]", regex=False)
    out["content_hash"] = vi.map(
        lambda s: hashlib.sha1(s.encode("utf-8")).hexdigest() if s else None
    )
    # 报告原始链接
    out["report_url"] = "https://hackerone.com/reports/" + out["id"].astype(str)

    # 渗透筛选信号字段（仅基于正文启发式判断，供下游快速过滤）
    out["has_repro_steps"] = vi.str.contains(_re_repro)
    out["has_poc"] = vi.str.contains(_re_poc)
    out["has_impact"] = vi.str.contains(_re_impact)
    out["has_http_request"] = vi.str.contains(_re_http)
    out["code_block_count"] = vi.str.count(_re_code).floordiv(2).astype("int64")
    out["url_count"] = vi.str.count(_re_url).astype("int64")
    out["cve_ids"] = vi.map(lambda s: ",".join(sorted(set(m.upper() for m in _re_cve.findall(s)))) or None)
    # 综合“可操作性”评分：有复现/PoC/HTTP/代码 各计 1 分
    out["actionability"] = (
        out["has_repro_steps"].astype(int)
        + out["has_poc"].astype(int)
        + out["has_http_request"].astype(int)
        + (out["code_block_count"] > 0).astype(int)
    ).astype("int64")

    return out

# ---------- 3. 筛选高质量子集 ----------

def filter_hq(clean):
    steps = []
    df = clean.copy()
    steps.append(("初始", len(df)))

    # a) 必须有正文内容（排除 no-content / 空）
    df = df[df["has_content"]]
    steps.append(("去除无正文(no-content/空)", len(df)))

    # b) 去除 spam
    df = df[df["substate"] != "spam"]
    steps.append(("去除 spam", len(df)))

    # c) 去除重复报告（original_report_id 指向他人）
    df = df[~df["is_duplicate"]]
    steps.append(("去除重复报告", len(df)))

    # d) 去除过短正文（<50 字符，信息量不足）
    df = df[df["vi_length"] >= 50]
    steps.append(("去除过短正文(<50)", len(df)))

    # e) 去除正文完全相同的行（保留首个）
    before = len(df)
    df = df.drop_duplicates(subset=["content_hash"], keep="first")
    steps.append((f"去除正文完全重复(-{before-len(df)})", len(df)))

    return df.reset_index(drop=True), steps

# ---------- 主流程 ----------

def main():
    import os
    os.makedirs(OUT_DIR, exist_ok=True)

    raw = load()
    clean = build_clean(raw)
    hq, steps = filter_hq(clean)

    # 写出
    clean.to_parquet(f"{OUT_DIR}/h1_clean_full.parquet", index=False)
    hq.to_parquet(f"{OUT_DIR}/h1_clean_filtered.parquet", index=False)

    # JSONL（面向 LLM/检索，仅保留关键字段）
    jsonl_cols = [
        "id", "report_url", "title", "substate", "weakness_name", "weakness_id",
        "asset_type", "asset_identifier", "max_severity", "team_handle", "team_name",
        "reporter_username", "has_bounty", "vote_count",
        "created_at", "disclosed_at", "vi_length", "has_redaction",
        "has_repro_steps", "has_poc", "has_impact", "has_http_request",
        "code_block_count", "url_count", "cve_ids", "actionability",
        "vulnerability_information",
    ]
    with open(f"{OUT_DIR}/h1_clean_filtered.jsonl", "w", encoding="utf-8") as f:
        for _, r in hq[jsonl_cols].iterrows():
            rec = r.to_dict()
            for k in ("created_at", "disclosed_at"):
                rec[k] = None if pd.isna(rec[k]) else rec[k].isoformat()
            for k, v in list(rec.items()):
                if pd.isna(v):
                    rec[k] = None
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # 报告
    write_report(clean, hq, steps)
    print("DONE. full=%d filtered=%d" % (len(clean), len(hq)))

def write_report(clean, hq, steps):
    lines = []
    A = lines.append
    A("# HackerOne 漏洞报告数据集 — 清洗与筛选报告\n")
    A("## 1. 数据来源\n")
    A("- 数据集: `Hacker0x01/hackerone_disclosed_reports` (HuggingFace)")
    A("- 原始文件: train/test/validation 三个 parquet，合并共 **%d** 条，`id` 无重复。\n" % len(clean))

    A("## 2. 清洗操作（全量，不删行 → `h1_clean_full.parquet`）\n")
    A("1. **合并三个 split**，保留来源于 `orig_split` 列。")
    A("2. **扁平化嵌套结构**：`reporter`/`team`/`weakness`/`structured_scope` 展开为独立列"
      "（reporter_username、team_handle、team_name、weakness_name、asset_type、max_severity 等），丢弃头像 URL 等噪声字段。")
    A("3. **日期解析**：`created_at`/`disclosed_at` 转为 UTC datetime。")
    A("4. **文本规范化**：统一换行符、剔除控制字符、折叠多余空行；连续 `█` 打码块归一为 `[REDACTED]`。")
    A("5. **派生字段**：`vi_length`、`has_content`、`has_redaction`、`content_hash`、`is_duplicate`、`report_url`。")
    A("6. **渗透筛选信号**（供下游按列快速过滤，无需再解析正文）：`has_repro_steps`、`has_poc`、`has_impact`、`has_http_request`、`code_block_count`、`url_count`、`cve_ids`、`actionability`(0-4 可操作性评分)。\n")

    A("## 3. 关键分布\n")
    def dist(col):
        vc = clean[col].value_counts(dropna=False)
        return "\n".join("  - %s: %d" % (k, v) for k, v in vc.items())
    A("**substate**:\n" + dist("substate") + "\n")
    A("**visibility**:\n" + dist("visibility") + "\n")
    A("**max_severity**:\n" + dist("max_severity") + "\n")
    A("**渗透信号（高质量子集内）**:")
    A("  - 含复现步骤 has_repro_steps: %d" % int(hq["has_repro_steps"].sum()))
    A("  - 含 PoC/payload has_poc: %d" % int(hq["has_poc"].sum()))
    A("  - 含 HTTP 请求 has_http_request: %d" % int(hq["has_http_request"].sum()))
    A("  - 含代码块 code_block_count>0: %d" % int((hq["code_block_count"] > 0).sum()))
    A("  - 含 CVE cve_ids: %d" % int(hq["cve_ids"].notnull().sum()))
    A("  - actionability 分布: " + ", ".join("%s:%d" % (k, v) for k, v in hq["actionability"].value_counts().sort_index().items()) + "\n")

    A("## 4. 筛选步骤（→ `h1_clean_filtered.parquet` / `.jsonl`）\n")
    A("| 步骤 | 剩余行数 |")
    A("|---|---|")
    for name, n in steps:
        A("| %s | %d |" % (name, n))
    A("")
    A("最终高质量子集 **%d** 条（约占全量 %.1f%%）。\n" % (len(hq), 100.0*len(hq)/len(clean)))

    A("## 5. 输出文件\n")
    A("- `out/h1_clean_full.parquet` — 全量清洗（%d 行 × %d 列）" % (len(clean), clean.shape[1]))
    A("- `out/h1_clean_filtered.parquet` — 高质量子集（%d 行）" % len(hq))
    A("- `out/h1_clean_filtered.jsonl` — 高质量子集（关键字段，面向 LLM/检索）")
    A("- `out/report.md` — 本报告\n")

    A("## 6. 筛选规则说明\n")
    A("高质量子集保留满足以下全部条件的报告：有正文内容、非 spam、非重复报告、正文≥50 字符、正文非完全重复。")
    A("如需其它口径（如仅 `resolved`、仅含 CWE、按严重度），可在 `clean.py::filter_hq` 调整。")

    with open(f"{OUT_DIR}/report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    main()
