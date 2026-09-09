# skills · 个人自用 Agent Skill 库

一套自用的 [Agent Skill](https://agentskills.io)（`SKILL.md` 标准，跨 Claude Code / Codex 等）集合。

**现阶段聚焦渗透测试漏洞挖掘**；后续会按需要扩展写作、工作流、数据处理等其它自用领域。仓库的主要交付物是 `skills/` 下的可复用 Skill，使用者通常只需要复制所需的 Skill 目录，不需要获取整个维护工程。

> ⚠️ **授权与用途声明**：`skills/` 下的渗透 skill 仅用于**你有明确授权**的安全测试、CTF、
> 教学与研究。每个 skill 内建 scope 确认与“7 问研判”纪律，只在授权范围内取证。
> 请勿用于未授权目标。

## 仓库结构

```
skills/            16 个可复用 skill
  hunt-*/          14 个“单类漏洞猎杀” skill（ssrf/xss/sqli/…）
  recognize-attack-surface/   攻击面识别与研判总线（路由到各 hunt skill）
  agent-workflow/  通用 Agent 工作流决策 skill
h1_data/           渗透 skill 的数据处理与蒸馏配方（维护者使用）
tests/             skill 校验与本地离线测试
.trellis/          项目工作流与任务记录（维护者使用）
```

`h1_data/` 和 `.trellis/` 主要用于维护和生成，不需要复制到 Agent 的 Skill 目录。对外分发时直接使用 `skills/` 目录或 GitHub Release 中的 `galact-skills.zip`。

### 每个 skill 的结构

```
<skill>/
├── SKILL.md       frontmatter（触发 description）+ 正文（流程与边界）
├── tools/         确定性脚本（recon → hunt → validate 流水线，零第三方依赖）
└── reference.md   payload / 绕过手法 / 真实案例（按需加载）
```

## 当前 skill 一览

- **单类漏洞猎杀（hunt-\*）**：ssrf、xss、sqli、command-injection、path-traversal、
  xxe、csrf、open-redirect、cache-poisoning、request-smuggling、deserialization、
  prototype-pollution、auth-bypass、nodejs-permission-bypass。
- **研判总线**：recognize-attack-surface —— 拿到目标先分诊、路由到对应 hunt skill，
  并处理跨组件攻击链 / 业务逻辑 / 配置错误 / 信息泄露等横切类别。
- **通用工作流**：agent-workflow —— 判断任务何时可以自主执行、何时需要澄清或明确批准，
  并按风险匹配验证强度。

本次完善了 `agent-workflow` 的部分阻塞处理、失败诊断、完成证据和默认测试/严格 TDD 边界；保留 Trellis 与显式流程的批准要求，并提供场景正反例。

## 怎么用

### 通过 npx 安装

已安装 Node.js 和 Git 时，可通过 [skills CLI](https://github.com/vercel-labs/skills) 选择 Skill 和目标 Agent：

```bash
npx skills@latest add galact-byte/galact-Skills
```

常用选项：

```bash
# 只查看可用 Skill，不安装
npx skills@latest add galact-byte/galact-Skills --list

# 只安装 agent-workflow
npx skills@latest add galact-byte/galact-Skills --skill agent-workflow

# 安装 agent-workflow 到全局 Pi 目录
npx skills@latest add galact-byte/galact-Skills --skill agent-workflow -g -a pi
```

默认安装到当前项目；`-g` 表示全局安装，`-a` 指定 Agent（如 `claude-code`、`codex`、`pi`）。已有同名且自行修改过的 Skill 时，安装或更新前先保留本地修改。

### 手动复制或下载 Release

把某个 skill 目录整个拷进你 agent 的 skill 扫描目录，重开/刷新会话即可被识别：

```bash
# Claude Code（个人）
cp -r skills/hunt-ssrf ~/.claude/skills/
# Codex
cp -r skills/hunt-ssrf ~/.codex/skills/
# Pi / .agents
cp -r skills/hunt-ssrf ~/.agents/skills/
```

之后直接描述任务（如“测下这个 URL 抓取有没有 SSRF”）；支持该标准的 Agent 会根据 skill 的
`description` 发现并选择合适的 skill。必要时也可明确要求使用对应 skill。

也可以从 GitHub Release 下载 `galact-skills.zip`，解压后将其中的 `skills/` 内容复制到目标 Agent 的 Skill 目录。GitHub Actions 会在推送 `v*` 版本标签时自动校验并生成该分发包。

## 本地验证

维护者可以运行仓库提供的离线验证 harness：

```bash
bash tests/run_tests.sh
```

它会检查所有 Skill 的 frontmatter、Shell 语法、Python 编译、行尾、交叉引用和 Python `--help` 冒烟导入，不访问外部测试目标。GitHub Actions 会在 push、pull request 和版本发布时运行相应验证。

## Roadmap

- [ ] 扩展非渗透自用 skill（写作 / 工作流 / 数据处理等）。
- [ ] 持续补充和迭代现有渗透测试 skill。

## 许可

[MIT](LICENSE)。渗透相关 skill 仍仅限授权测试与研究（见顶部声明）。
