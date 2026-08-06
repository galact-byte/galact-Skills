# skills · 个人自用 Agent Skill 库

一套自用的 [Agent Skill](https://agentskills.io)（`SKILL.md` 标准，跨 Claude Code / Codex 等）集合。

**现阶段聚焦渗透测试漏洞挖掘**；后续会按需要扩展写作、工作流、数据处理等其它自用领域。

> ⚠️ **授权与用途声明**：`skills/` 下的渗透 skill 仅用于**你有明确授权**的安全测试、CTF、
> 教学与研究。每个 skill 内建 scope 确认与“7 问研判”纪律，只在授权范围内取证。
> 请勿用于未授权目标。

## 仓库结构

```
skills/            15 个 skill（当前全为渗透类）
  hunt-*/          14 个“单类漏洞猎杀” skill（ssrf/xss/sqli/…）
  recognize-attack-surface/   攻击面识别与研判总线（路由到各 hunt skill）
h1_data/           渗透 skill 的数据处理与蒸馏配方
tests/             skill 校验与本地端到端测试
```

### 每个 skill 的结构

```
<skill>/
├── SKILL.md       frontmatter（触发 description）+ 正文（猎杀流程）
├── tools/         确定性脚本（recon → hunt → validate 流水线，零第三方依赖）
└── reference.md   payload / 绕过手法 / 真实案例（按需加载）
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

之后直接描述任务（如“测下这个 URL 抓取有没有 SSRF”）；支持该标准的 Agent 会根据 skill 的
`description` 发现并选择合适的 skill。必要时也可明确要求使用对应 skill。

## Roadmap

- [ ] 扩展非渗透自用 skill（写作 / 工作流 / 数据处理等）。
- [ ] 持续补充和迭代现有渗透测试 skill。

## 许可

[MIT](LICENSE)。渗透相关 skill 仍仅限授权测试与研究（见顶部声明）。
