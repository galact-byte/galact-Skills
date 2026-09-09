# 最终复核记录

## 范围与执行

保留原 agent-workflow，仅修改正文、增加场景附件和文档静态测试，接入原离线 harness。原批准清单保留，并明确只读生产访问和领域检查点。没有新建 Skill、安装依赖、修改 README 或 H1 数据忽略规则，也没有执行提交、推送、发布。

首次实施使用了一次 high 推理子代理；用户随后明确重申非必要不用子代理、推理强度按难度选择。主会话承认该次选择偏重，之后没有再次派遣，直接复核、修正并运行检查。没有把初次子代理自报结果作为最终证据。

## 复核发现与修正

- 正文缺少场景附件引用：补充相对链接，xref 与专用测试均检查。
- harness 原接入位于汇总后，新增结果不计入展示总数：移至 agent-workflow 分支，使用既有 pass/fail 与 Skill 计数；解释器路径保持引号，直接运行测试文件避免缺失时 discovery 以零测试通过。
- 场景仅统计数量：改为逐名覆盖 17 个必需场景，并检查每个场景的四个字段存在、唯一且非空。
- 原负向测试只是 assertIn 的自证：改为在内存中移除六项保障并运行对应的真实契约测试；另检验缺失场景、空字段确实被拒绝。
- 内部修复轮次被笼统视为硬边界：区分诊断检查点与用户硬性预算/轮次及工具实际限制。
- 补齐状态未变可复用证据、状态不明需复测、隔离验证事后测试有效性、生产只读访问和模板不能授权外发等边界。
- 将用户最新的子代理必要性与推理强度要求融入核心原则及正反例。

## RED 与最终 GREEN

初次子代理的 RED/GREEN 记录见 implementation-results.md，属于中间版本记录。

主会话加强测试后实际运行 unittest：10 tests，7 个失败（含子测试），覆盖新增规则与链接缺失；不是导入或语法错误。第一次 Windows 控制台中文诊断显示乱码，后续用 `python -X utf8` 重跑，文件始终按 UTF-8 读取。

最终命令：

- `python -X utf8 -m unittest discover -s tests -p 'test_agent_workflow.py' -v`：10 tests，OK。六项保障删除与两项场景变异均由测试真实运行，并被正确拒绝。
- `bash tests/run_tests.sh`：16 skills PASS / 0 FAIL，97 checks pass / 0 fail。文档契约测试在 harness 中计为 1 项，其中包含上述 10 个 unittest，不能相加成 107 项独立覆盖。
- `git diff --check`：退出 0，无输出。
- `bash -n tests/run_tests.sh`、`python -X utf8 -m py_compile tests/test_agent_workflow.py`：均退出 0。

## 状态绑定

验证环境：Windows、Git Bash、仓库可启动的 Python；harness 自行探测 python3/python，设置 PYTHONUTF8=1，无联网或新增依赖。

四个交付文件的 SHA-256：

```text
95d75975b6f93ecc93f43d04b6f31eda31e4f3b84520f7863ccd075766d881a7  skills/agent-workflow/SKILL.md
af42b5156473b8dd81181316d67b2e20fcd988f57acd146812cc16dcc60fa4f6  skills/agent-workflow/references/scenarios.md
28d28902f46259c429712a29e96d075fb45af6d420fc40e9508ce1c7c7e0c328  tests/test_agent_workflow.py
293c50a3a3c45124dc16823e4fadbace67776d4efd328f13e6320324ad1b83b6  tests/run_tests.sh
```

## 语义复核与保障

主会话逐项对照 PRD 及 17 个场景检查：明确实施/仅计划/先审方案、部分阻塞、普通与连续失败、已有授权、未授权外部操作、真实未完成、状态变化与证据复用、默认与严格 TDD、Trellis/领域检查点、硬预算与内部轮次、模板证据和子代理选择。各条正反例与正文相容，未发现剩余阻断项。

保留删除/覆盖、外部副作用、生产访问、认证/权限/隐私、架构/兼容性、费用、安装下载和用户检查点批准；用户沉默不授权，独立工作不因局部未决而冻结。

## 验证限制

这不是独立模型或真实工具行为实验。场景文件记录的是期望动作，静态检查仅检验结构、字段和特定措辞；主会话语义复核不保证其他模型实际遵循。未新建模型评估器，也没有做付费 API 实验。漏洞检测工具的 E2E 没有运行，因为本次未修改那些工具。

## 规范与收尾

已按 Trellis 3.3 评估规范更新：无需改 backend/frontend 模板，规则主体已落到目标 Skill，验证经验在本记录中保留，避免复制一套工作流规范。当前环境未找到 trellis-update-spec 入口，按 workflow.md 的该步骤直接完成判断。

按用户要求不进行提交或需要提交的自动归档流程；任务保持 in_progress，交付与回归已完成，未提交仅是工作区状态，不代表要求用户继续排错。

## 后续授权：全局规范

主任务完成后重新完整读取 `C:/Users/g1582/.pi/agent/AGENTS.md`，原文只有“缺少可选子代理不应阻塞工作”，未明确写出必要性与推理强度原则。按用户新增明确授权，在 9.6 仅新增“子代理使用”“子代理推理强度”两条，其他全局文件未改。

修改前 SHA-256 为 `a439194184667162b7b822b87a766d4a27bbd0e4ff46d53461a925578c85803b`。修改后通过 Node assert 在内存中移除两条新增行，再计算 SHA-256，与原值一致；同时断言恰有两条新增规则且包含必要性和最低合适强度要求。验证退出 0，证明原有 UTF-8 字节完整保留。
