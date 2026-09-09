# 执行清单 — H1 数据集清洗与评分管线

进度快照（2026-08-04）。勾选项为已完成，方框为待办。

## 阶段 1：清洗与筛选 ✅
- [x] 下载三个 parquet（train/test/validation）到 `h1_data/raw/`
- [x] `clean.py`：扁平化 + 日期/文本规范化 + 派生信号字段
- [x] 产出 `out/h1_clean_full.parquet`(12618) 与 `out/h1_clean_filtered.parquet`(8908)
- [x] `out/report.md` 清洗报告 + 全量校验通过

## 阶段 2：分批 ✅
- [x] `build_batches.py --size 20` → `pipeline/batches/` 446 批
- [x] `pipeline/batches/_manifest.json` 覆盖清单

## 阶段 3：一轮 LLM 评分 ✅
- [x] 定稿 `pipeline/score_prompt.md`（四维 rubric + 3 个校准锚点）
- [x] `run_scoring.py`：OpenAI 兼容、分片/并发、逐批校验、可续跑、原子写入
- [x] 修复 v4-flash thinking 烧预算问题（默认 `thinking:{type:disabled}`）
- [x] 修复 value_score 心算误差（`normalize_scores` 以四维和为准）
- [x] 加进度条 + ETA
- [x] **446/446 批评分完成**，8908 条 0 缺失 0 校验错误
- [x] `aggregate.py` 汇总 → `scored_all.parquet` / `.jsonl`

## 阶段 4：二轮筛选 ⬜（用户 galact 主导）
- [ ] 明确二轮筛选口径（参考 `Prompt2.md`）
- [ ] 在 `scored_all.parquet` 上执行二轮精筛
- [ ] 产出二轮高价值案例集

## 阶段 5：skill 素材 ⬜（二轮后，用户确认再做）
- [ ] `extract_skill.py --min-score <阈值>` 抽取 attack_chain/bypass/defensive
- [ ] 组织成技术模式库（`skill_material.jsonl` / `skill_source.md`）
- [ ] 交付渗透测试 skill

## 验证命令
```powershell
# 覆盖率 + 硬校验（应 8908 条 0 问题）
D:\Tools\Python\Anaconda3\python.exe aggregate.py
```
