# v0.1.1 发布准备

用户在验收后明确授权更新 `.gitignore`、README、`release_note.md` 并提交、推送、发布。远端最新 Release 为 v0.1.0，本次是现有 Skill 的兼容性完善，使用 v0.1.1，不重打旧标签。

## 范围

- README 恢复并完整保留已有内容与结构，只增补工作流说明和 npx 安装用法；`git diff --numstat README.md` 为 27 新增、0 删除。
- `.gitignore` 仅追加根目录分发包及 Trellis scripts/agents 规则，既有 H1 生成数据及本地配置忽略保持不变。
- `release_note.md` 仍为唯一发布说明，记录本次改进及静态验证的能力边界。
- 不修改 GitHub Actions 发布机制，不发布 npm 包，不安装或覆盖本机已有 Skill。
- 原有 3 个未推送提交仅包含既有任务归档与日志，保留并随 master 推送；不改写历史。

## 安装方式证据

已通过 GitHub API 读取以下官方 README：

- https://github.com/mattpocock/skills ：使用 `npx skills@latest add mattpocock/skills`。
- https://github.com/vercel-labs/skills ：支持 owner/repo、`skills/<name>/SKILL.md` 自动发现、`--skill`、`--list`、`-g`、`-a pi`。

因此本仓库可以使用 `npx skills@latest add galact-byte/galact-Skills`。这是文档与现有目录结构的核对，未声称实际执行安装测试。

## 本地验证

- `bash tests/run_tests.sh`：16 skills PASS，97 checks pass，0 fail。
- `git diff --check`：退出 0；仅有 Git autocrlf 行尾提示，无空白错误。
- `git check-ignore`：Trellis scripts/agents、分发包、AI 本地配置和 H1 生成数据样例均命中。
- README 原有章节与手动安装命令保留；发布说明没有将静态测试冒充真实模型行为实验。

发布通过现有 v* 标签工作流构建 galact-skills.zip；完成后由主会话回读 CI、标签、Release 正文和实际 ZIP 文件，不能仅以 push 成功作为发布完成。
