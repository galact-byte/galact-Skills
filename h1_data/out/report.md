# HackerOne 漏洞报告数据集 — 清洗与筛选报告

## 1. 数据来源

- 数据集: `Hacker0x01/hackerone_disclosed_reports` (HuggingFace)
- 原始文件: train/test/validation 三个 parquet，合并共 **12618** 条，`id` 无重复。

## 2. 清洗操作（全量，不删行 → `h1_clean_full.parquet`）

1. **合并三个 split**，保留来源于 `orig_split` 列。
2. **扁平化嵌套结构**：`reporter`/`team`/`weakness`/`structured_scope` 展开为独立列（reporter_username、team_handle、team_name、weakness_name、asset_type、max_severity 等），丢弃头像 URL 等噪声字段。
3. **日期解析**：`created_at`/`disclosed_at` 转为 UTC datetime。
4. **文本规范化**：统一换行符、剔除控制字符、折叠多余空行；连续 `█` 打码块归一为 `[REDACTED]`。
5. **派生字段**：`vi_length`、`has_content`、`has_redaction`、`content_hash`、`is_duplicate`、`report_url`。
6. **渗透筛选信号**（供下游按列快速过滤，无需再解析正文）：`has_repro_steps`、`has_poc`、`has_impact`、`has_http_request`、`code_block_count`、`url_count`、`cve_ids`、`actionability`(0-4 可操作性评分)。

## 3. 关键分布

**substate**:
  - resolved: 11012
  - informative: 995
  - not-applicable: 313
  - duplicate: 271
  - spam: 27

**visibility**:
  - full: 9482
  - no-content: 3136

**max_severity**:
  - None: 6054
  - critical: 5313
  - none: 879
  - medium: 285
  - high: 66
  - low: 21

**渗透信号（高质量子集内）**:
  - 含复现步骤 has_repro_steps: 4000
  - 含 PoC/payload has_poc: 4255
  - 含 HTTP 请求 has_http_request: 1910
  - 含代码块 code_block_count>0: 3083
  - 含 CVE cve_ids: 446
  - actionability 分布: 0:1907, 1:2901, 2:2340, 3:1373, 4:387

## 4. 筛选步骤（→ `h1_clean_filtered.parquet` / `.jsonl`）

| 步骤 | 剩余行数 |
|---|---|
| 初始 | 12618 |
| 去除无正文(no-content/空) | 9482 |
| 去除 spam | 9455 |
| 去除重复报告 | 9258 |
| 去除过短正文(<50) | 9131 |
| 去除正文完全重复(-223) | 8908 |

最终高质量子集 **8908** 条（约占全量 70.6%）。

## 5. 输出文件

- `out/h1_clean_full.parquet` — 全量清洗（12618 行 × 36 列）
- `out/h1_clean_filtered.parquet` — 高质量子集（8908 行）
- `out/h1_clean_filtered.jsonl` — 高质量子集（关键字段，面向 LLM/检索）
- `out/report.md` — 本报告

## 6. 筛选规则说明

高质量子集保留满足以下全部条件的报告：有正文内容、非 spam、非重复报告、正文≥50 字符、正文非完全重复。
如需其它口径（如仅 `resolved`、仅含 CWE、按严重度），可在 `clean.py::filter_hq` 调整。