# Release Notes

## 2026-08-25

### ✨ 新增功能

- 新增 `agent-workflow` Skill，统一说明 Agent 的自主执行、澄清、明确批准和验证范围决策。
- 新增 GitHub Actions 工作流，在 push 和 pull request 时自动运行全部 Skill 离线校验。
- 提供只包含 `skills/` 内容的分发包，便于使用者直接安装所需 Skill，而无需获取数据管线和 Trellis 开发材料。

### 🛠️ 修复与优化

- 修复 Windows Git Bash 下测试 harness 错误选择 Microsoft Store `python3` 别名的问题；现在会实际探测解释器是否可运行，并自动回退到可用的 `python`。
- 更新 README，明确 Skill 是仓库的主要交付物，并区分使用者内容与维护者工具。
- 补充 `.gitignore` 对 Trellis 本地运行态、备份目录和常见测试缓存的忽略规则。
- 修正测试 harness 顶部检查层数说明，使其与实际的 6 类检查一致。

### 🔄 兼容性说明

- Skill 仍按 Agent Skills `SKILL.md` 目录结构分发，可单独复制到 Claude Code、Codex、Pi / `.agents` 等兼容目录。
- GitHub Actions 在 Ubuntu 上运行与本地相同的离线验证，不访问外部测试目标。
- 渗透测试相关 Skill 仅限明确授权的安全测试、CTF、教学和研究用途。

### 已知边界

- 本次不包含自动发布 GitHub Release；分发包由维护者手动从仓库构建并提供。
- `h1_data/` 与 `.trellis/` 主要用于维护和生成，不属于 Skill 使用者安装所需内容。
