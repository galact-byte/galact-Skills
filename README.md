# skills · 个人自用 Agent Skill 库

一套自用的 [Agent Skill](https://agentskills.io)（`SKILL.md` 标准，跨 Claude Code / Codex 等）集合。
**现阶段聚焦渗透测试漏洞挖掘**，后续会扩展到其它自用领域（写作、工作流、数据处理等）——
仓库结构与测试/生产方法都按"通用 skill 库"设计，不锁死安全领域。

> ⚠️ **授权与用途声明**：`skills/` 下的渗透 skill 仅用于**你有明确授权**的安全测试、CTF、
> 教学与研究。每个 skill 内建 scope 确认与"7 问研判"纪律，只在授权范围内取证。
> 请勿用于未授权目标。

## 仓库结构

```
skills/            15 个 skill（当前全为渗透类）
  hunt-*/          14 个"单类漏洞猎杀"skill（ssrf/xss/sqli/…）
  recognize-attack-surface/   攻击面识别与研判总线（路由到各 hunt skill）
h1_data/           蒸馏管线的**配方**（代码 + 提示词 + pipeline/README）；
                   中间数据/报告等可再生产物不入库（见 .gitignore）
tests/             skill 测试套件（静态校验 + 本地靶标端到端检测）
```

> 蒸馏提示词的**可复用模板**（领域中立）不在本库，而是在个人 skill `distill-dataset-to-skills`
> 的 `references/` 下；`h1_data/` 里只留填好的渗透实例版作样板。

### 每个 skill 的结构（渐进式披露）

```
<skill>/
├── SKILL.md       frontmatter（触发 description）+ 正文（猎杀流程）
├── tools/         确定性脚本（recon → hunt → validate 流水线，零第三方依赖）
└── reference.md   payload / 绕过手法 / 真实案例（按需加载，Level 3）
```

## 当前 skill 一览

- **单类漏洞猎杀（hunt-\*）**：ssrf、xss、sqli、command-injection、path-traversal、
  xxe、csrf、open-redirect、cache-poisoning、request-smuggling、deserialization、
  prototype-pollution、auth-bypass、nodejs-permission-bypass。
- **研判总线**：recognize-attack-surface —— 拿到目标先分诊、路由到对应 hunt skill，
  并处理跨组件攻击链 / 业务逻辑 / 配置错误 / 信息泄露等横切类别。

## 怎么用

把某个 skill 目录整个拷进你 agent 的 skill 扫描目录，重开/刷新会话即可被识别：

```bash
# Claude Code（个人）
cp -r skills/hunt-ssrf ~/.claude/skills/
# Codex
cp -r skills/hunt-ssrf ~/.codex/skills/
# Pi / .agents
cp -r skills/hunt-ssrf ~/.agents/skills/
```

之后直接描述任务（如"测下这个 URL 抓取有没有 SSRF"），匹配到 description 就会自动触发。

## 这些 skill 怎么来的（蒸馏管线）

不是手写的，而是从公开漏洞报告数据集**蒸馏**出来的：

1. **清洗**：HackerOne 披露报告 → 高质量子集（`h1_data/clean.py`）。
2. **评分**：LLM 按启发性 rubric 逐条打分（四维求和，`h1_data/pipeline/score_prompt.md`）。
3. **筛选/合并/路由**：worth-skill 判断 → 知识点聚类去重 → 单例语义路由。
4. **抽素材 → 做 skill → 测试 → 优化**。

完整流程与命令见 [`h1_data/pipeline/README.md`](h1_data/pipeline/README.md)。

## 测试

两层，都不依赖外部网络：

```bash
# 1) 静态：结构(quick_validate)/shell 语法/py 编译/LF 行尾/交叉引用/脚本 import
bash tests/run_tests.sh                # 当前：15/15 通过

# 2) 端到端：在 127.0.0.1 起脆弱靶标，跑各 skill 的 hunt→validate 流水线，
#    断言植入的漏洞被真正检出（或按设计正确判负）
python tests/e2e/run_e2e.py            # 当前：14/14 通过（recognize-* 为路由 skill，走静态）
```

细节见 [`tests/README.md`](tests/README.md)。`tests/quick_validate.py` vendored 自
anthropic skill-creator（Apache-2.0），仅改为 UTF-8 读取以适配 Windows。

## Roadmap

- [ ] 扩展非渗透自用 skill（写作 / 工作流 / 数据处理等）。
- [ ] 新领域 skill 复用同一套测试套件（静态必过；有客观输出的补端到端夹具）。

## 许可与致谢

- 数据源：HackerOne 公开披露报告（`Hacker0x01/hackerone_disclosed_reports`）。
- `tests/quick_validate.py`：源自 anthropics/claude-plugins-official（Apache-2.0）。
