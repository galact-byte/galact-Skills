# Galact Skills

可复用的 Agent Skill 集合。仓库的主要交付物是 [`skills/`](skills/) 下的 Skill；其中每个 Skill 都可以独立复制到兼容 Agent 的 Skill 目录中使用。

当前内容以**授权安全测试与研究**为主，同时包含通用工作流类 Skill。渗透测试 Skill 只能用于你明确获准测试的目标、CTF、教学和研究，禁止用于未授权目标。

## 快速使用

将需要的 Skill 目录整体复制到 Agent 的 Skill 扫描目录，然后重启或刷新会话：

```bash
# Claude Code
cp -r skills/hunt-ssrf ~/.claude/skills/

# Codex
cp -r skills/hunt-ssrf ~/.codex/skills/

# Pi / .agents
cp -r skills/hunt-ssrf ~/.agents/skills/
```

也可以复制整个 `skills/` 目录，以一次安装全部 Skill。支持 Agent Skills 标准的 Agent 会根据 `SKILL.md` frontmatter 中的 `description` 自动发现 Skill；必要时也可以在任务中明确指定 Skill 名称。

## Skill 清单

- `agent-workflow`：判断任务何时可以自主执行、何时需要澄清或明确批准，并匹配验证强度。
- `recognize-attack-surface`：对目标进行攻击面分诊，路由到适用的漏洞猎杀 Skill，并覆盖攻击链、业务逻辑、配置错误和信息泄露等横切类别。
- `hunt-*`：按漏洞类别进行授权安全测试，包括 SSRF、XSS、SQL 注入、命令注入、路径穿越、XXE、CSRF、开放重定向、缓存投毒、请求走私、反序列化、原型污染、认证绕过和 Node.js 权限绕过。

每个 Skill 通常包含：

```text
<skill>/
├── SKILL.md       触发条件、流程和安全边界
├── tools/         可重复运行的辅助脚本（如有）
└── reference.md   参考资料和测试方法（如有）
```

## 本地验证

仓库提供离线验证 harness，用于检查所有 Skill 的 frontmatter、Shell 语法、Python 编译、行尾、交叉引用和 Python `--help` 冒烟导入：

```bash
bash tests/run_tests.sh
```

验证不访问外部目标。GitHub Actions 会在 push 和 pull request 时自动运行同一检查。

## 仓库结构

```text
skills/       对外复用的主要交付物
 tests/       Skill 静态与离线验证
 h1_data/     用于生成和蒸馏 Skill 的维护者工具与配方
.trellis/     项目工作流与任务记录；不属于 Skill 使用者的运行时依赖
```

`h1_data/` 和 `.trellis/` 主要服务于仓库维护，不需要复制到 Agent 的 Skill 目录。运行时数据、缓存、个人 AI 配置和本地任务状态由 `.gitignore` 排除；可复用的 Skill 源文件、测试和许可证保留在仓库中。

## 贡献

新增或修改 Skill 后，请运行：

```bash
bash tests/run_tests.sh
```

保持每个 Skill 自包含、描述准确，并明确记录授权范围和必要的安全边界。不要提交真实目标的扫描结果、凭据、个人配置或生成的大型数据文件。

## 许可

代码和文档采用 [MIT License](LICENSE)。渗透测试相关 Skill 仍受顶部授权用途声明约束。
