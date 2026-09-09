# H1 漏洞报告数据集清洗与评分管线

## 背景与目标

从 HackerOne 公开披露报告数据集出发，清洗筛选出高质量报告，再用 LLM 按"启发性"
rubric 逐条深度评分，最终**产出渗透测试 skill 的素材库**（高价值案例的攻击链 /
绕过技术 / 防御要点，按类别组织）。

- 数据源：HuggingFace `Hacker0x01/hackerone_disclosed_reports`（train/test/validation 三 parquet）
- 工作目录：`D:/tmp/skills/h1_data/`
- 评分模型：DeepSeek **deepseek-v4-flash**（1M 上下文 / 384K 输出；OpenAI 兼容 `https://api.deepseek.com/v1`）

## 当前进度（截至 2026-08-04）

### ✅ 已完成
1. **下载 + 清洗**（`h1_data/clean.py`）：12618 条 → 扁平化嵌套结构、日期规范化、
   文本规范化（打码块 `█`→`[REDACTED]`）、派生信号字段。产出：
   - `out/h1_clean_full.parquet`（全量 12618×36）
   - `out/h1_clean_filtered.parquet`（**高质量子集 8908 条**：去无正文/spam/重复/超短/正文重复）
   - `out/report.md`（清洗与筛选报告）
2. **分批**（`pipeline/build_batches.py`）：8908 条 → `pipeline/batches/` **446 批 × 20**。
3. **一轮 LLM 评分**（`pipeline/run_scoring.py` + `pipeline/score_prompt.md`）：
   **446/446 批全部完成**，`pipeline/scored/` 下 8908 条评估，**0 缺失、0 校验问题**。
   - 评分口径：四维（非预期性0-3 / 绕过优雅度0-3 / 攻击链0-2 / 可复现性0-2），满分 10。
   - 结果分布：保留 4793 / 丢弃 4115；**高优先级(≥7) 2605 条**。
   - verdict：高优先级 2393、普通 2400、常见套路 3659、信息不足 456。
4. **汇总**（`pipeline/aggregate.py`）：产出 `pipeline/scored_all.parquet` / `.jsonl`
   （评分 + 元数据 join，按 value_score 降序）。

### ⬜ 待完成
- **二轮筛选**（**由用户 galact 主导**）：在一轮评分结果上按用户口径进一步精筛，
  产出更聚焦的高价值案例集。参考提示词：`Prompt1.md`（一轮）、`Prompt2.md`（二轮）。
- **skill 素材抽取 / 生成**：二轮筛完后再做（`pipeline/extract_skill.py` 可按
  `value_score≥阈值` 抽取，但**当前用户明确要求先不生成 skill**）。

## 关键约束 / 决策
- 评分靠 `run_scoring.py --concurrency` 提速（生成是瓶颈，1M 上下文不提速）；
  多终端用 `--shards N --shard i` 分片互不冲突。
- **必须关 thinking**：v4-flash 默认开思考会烧光 max_tokens 导致正文为空/截断；
  脚本已默认发送 `thinking:{type:disabled}`。
- `value_score` 一律以四维之和为准（脚本 `normalize_scores` 自动修正模型心算误差）。
- 数据文件大：git 只提交代码 + 提示词 + `scored/` + 报告，忽略可再生成的
  raw/out-parquet/batches（见根目录 `.gitignore`）。

## 验收标准
- [x] 高质量子集 `out/h1_clean_filtered.parquet` 生成且通过校验（8908 条）
- [x] 446 批一轮评分全部完成，`scored/` 8908 条 0 缺失 0 校验错误
- [x] `pipeline/scored_all.parquet` 汇总可用（供二轮筛选）
- [ ] 二轮筛选完成（用户主导，口径待定）
- [ ] skill 素材产出（二轮后，用户确认再做）

## 复现 / 续跑命令
```powershell
# 评分续跑（自动跳过已完成批；全 446 批已完成，此命令用于补漏或复现）
python run_scoring.py --model deepseek-v4-flash --concurrency 16 --max-tokens 16000

# 汇总（需 pandas，用 Anaconda python）
D:\Tools\Python\Anaconda3\python.exe aggregate.py

# 二轮筛完后再抽 skill 素材
D:\Tools\Python\Anaconda3\python.exe extract_skill.py --min-score 7
```

详见 `h1_data/pipeline/README.md`。
