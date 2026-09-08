## ✨ 新增功能

- 新增 `agent-workflow` Skill，统一说明 Agent 的自主执行、澄清、明确批准和验证范围决策。
- 新增 GitHub Actions 自动校验与发布流程，推送版本标签即可生成 Skill 分发包。
- 发布资产提供只包含 `skills/` 的 `galact-skills.zip`，无需获取数据管线和 Trellis 开发材料。

## 🛠️ 修复与优化

- 修复 Windows Git Bash 下测试 harness 错误选择 Microsoft Store `python3` 别名的问题。
- 更新 README，明确 Skill 是仓库的主要交付物，并区分使用者内容与维护者工具。
- 补充本地运行态、备份目录和常见测试缓存的忽略规则。

## 🔄 兼容性说明

- Skill 按 Agent Skills `SKILL.md` 目录结构分发，可单独复制到 Claude Code、Codex、Pi / `.agents` 等兼容目录。
- 发布前会在 Ubuntu 上运行完整离线验证，不访问外部测试目标。
- 渗透测试相关 Skill 仅限明确授权的安全测试、CTF、教学和研究用途。

## 已知边界

- `h1_data/` 与 `.trellis/` 主要用于维护和生成，不属于 Skill 使用者安装所需内容。
