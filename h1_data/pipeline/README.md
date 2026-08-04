# HackerOne 高质量案例库 — 评分量产管线（路线 3）

用 LLM 逐条深度评分（`score_prompt.md`）对全部 8908 条高质量报告打分，
产出可直接喂"渗透 skill"的技术模式库。评分尺度已用校准批 few-shot 锚定。

## 数据流

```
../out/h1_clean_filtered.parquet          (8908 条清洗后子集)
  └─ build_batches.py  →  batches/batch_*.json      (446 批 × 20)
        └─ run_scoring.py (LLM, score_prompt.md)  →  scored/batch_*.json
              └─ aggregate.py  →  scored_all.parquet / .jsonl   (评分+元数据)
                    └─ extract_skill.py  →  skill_material.jsonl / skill_source.md
```

## 步骤

### 1. 分批（已完成，可重跑改批大小）
```
python build_batches.py --size 20
```

### 2. LLM 评分（核心，需配置模型）
模型无关，走 OpenAI 兼容 `/v1/chat/completions`。**建议用强模型**（评分质量直接决定 skill 质量）。
```
# DeepSeek（OpenAI 兼容）
export OPENAI_API_KEY=<你的 DeepSeek key>
export OPENAI_BASE_URL=https://api.deepseek.com/v1
python run_scoring.py --model deepseek-v4-flash --concurrency 3 --max-tokens 16000 --limit 3   # 先试跑
python run_scoring.py --model deepseek-v4-flash --concurrency 16 --max-tokens 16000            # 全量（可续跑）
```
注意：
- 用 **`deepseek-v4-flash`**（V4，1M 上下文 / 384K 输出）。旧名 `deepseek-chat`/`deepseek-reasoner` 于 2026-07-24 退役。
- 提速主力是 `--concurrency`（生成是瓶颈，1M 上下文不提速）；不必为此重新分大批。
- v4-flash 默认开 thinking，会把 max_tokens 全花在思考上导致正文为空/截断；`run_scoring.py` 已**默认关 thinking**（发 `thinking:{type:disabled}`）。如需开思考加 `--enable-thinking`。
- 诊断工具 `probe.py`：对单批发一次原始请求并打印 finish_reason/usage/reasoning 长度，用于排查截断/思考/格式问题。
- 逐批校验：输出 id 集合必须与输入一致、`value_score`=四维之和、字段齐全、verdict 合法；不通过自动重试，用尽则存 `failed/`。
- 可续跑：中断后重跑只补未完成批次。
- 温度默认 0，保证可复现。

### 3. 汇总
```
python aggregate.py
```
输出 `scored_all.parquet`（评分+元数据），并打印覆盖率校验与 verdict/分数/类别分布。

### 4. 抽取 skill 素材
```
python extract_skill.py --min-score 7
```
- `skill_material.jsonl`：每条高价值案例的结构化素材（id/类别/攻击链/绕过/防御）。
- `skill_source.md`：按类别分组的人读版技术模式库。

## 评分口径（score_prompt.md）
- 四维：非预期性(0-3)、绕过优雅度/通用性(0-3)、攻击链跨组件(0-2)、可复现性(0-2)，满分 10。
- verdict：≥7 高优先级 / 5-6 普通 / <5 常见套路 / 信息不足。
- **关键校准**：优雅的逻辑/业务漏洞常缺 PoC/代码/HTTP 等机械特征，不因此低估；成熟套路的单点漏洞不给高分。
- 校准锚点见 `score_prompt.md` 的 `<calibration_examples>`（源自会话内人工校准批 10 条）。

## 质量控制建议
- 先 `--limit 3` 试跑，人工抽查 3~5 条评分是否与校准尺度一致，再全量。
- 全量后看 `aggregate.py` 的分数分布：若高优先级占比异常偏高/偏低，说明模型尺度漂移，调 prompt 锚点或换模型。
- `extract_skill.py --min-score` 可调；出 skill 建议先用 7，素材不足再降到 6。
