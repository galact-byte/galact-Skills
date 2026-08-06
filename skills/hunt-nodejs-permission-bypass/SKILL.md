---
name: hunt-nodejs-permission-bypass
description: 在授权测试中核验 Node.js 权限模型（--permission / --experimental-permission，及旧 policy.json）能否被内部 API 绕过。当目标依赖 Node.js Permission Model 做沙箱隔离、需要判断给定 Node 版本下是否存在已知逃逸（inspector 断点、process.binding、fs.statfs/openAsBlob、process.mainModule.require、Module._load、path.resolve 覆盖、Uint8Array 路径、符号链接重命名）时使用。适用目标类型 Node.js 运行时 / 依赖权限模型的服务或 CLI。触发场景包括用户说"这个 Node 权限模型靠谱吗""--permission 能被绕过吗""测下 policy.json 沙箱逃逸""inspector/process.binding 能突破权限吗"。输出：给定 Node 版本下各绕过原语的命中矩阵 + 建议升级版本（含 killed 记录）。
allowed-tools: Read, Grep, Glob, Bash
---

# hunt-nodejs-permission-bypass · Node.js 权限模型逃逸核验

只解决一件事：**判定某 Node.js 版本 + 权限配置下，已知内部 API 绕过原语还有没有效**。这是本地能力核验（不是远程扫描）——在受权限模型限制的进程里跑一批 PoC，看哪些能读到本应被禁的文件。

权限模型的隔离承诺很脆：很多逃逸是"用内部 API 绕开被拦的公开 API"。本 skill 把已知原语做成可重复的命中矩阵，帮你快速判断目标 Node 版本是否安全。PoC 只读**授权内的标记文件**验证逃逸，不做破坏。绕过原语与对应修复版本见 `reference.md`。

## Scope（授权范围）

**先确认授权，再运行 PoC。** 这些 PoC 会尝试突破沙箱读文件。

开工前落实：
- 授权在**目标环境/副本**上运行 Node PoC（生产慎用，优先用同版本副本）。
- 一个**受限标记文件**路径（PoC 尝试越权读它来证明逃逸），内容无敏感信息。
- 目标 Node 版本与启动方式（`--permission` / `--experimental-permission` / `--allow-fs-read` 白名单 / policy.json）。

任一不清楚就停下问。只在授权环境跑，只读标记文件。

## Goal

产出"该 Node 版本 + 配置下，各已知绕过原语是否仍可逃逸"的命中矩阵，给出可复现 PoC 与修复建议（升级到已修复版本 / 禁用 inspector / 避免动态 path.resolve）。

## Workflow

`scope-check → recon → hunt → validate → report`。

### 1. scope-check
- **输入**：授权 + 受限标记文件路径。
- **动作**：写 `evidence/scope.txt`（含 restricted_file / node_target）。
- **命令**：`bash tools/recon.sh --scope-only`。
- **终止条件**：`evidence/scope.txt` 存在且授权明确，否则 KILL。

### 2. recon
- **输入**：目标 Node（本机 `node` 或指定二进制）。
- **动作**：探测 Node 版本、是否支持/启用权限模型、可用绕过面。
- **输出**：`recon/node_env.json`（版本、权限模型状态、适用原语列表）。
- **命令**：`bash tools/recon.sh [--node <path>]`。
- **终止条件**：拿到版本与权限模型状态；不支持权限模型则记录结束。

### 3. hunt
- **输入**：`recon/node_env.json` + 受限标记文件。
- **动作**：为每个绕过原语生成 PoC .js，在 `--experimental-permission --allow-fs-read=<白名单>` 下运行，检查是否读到**白名单外**的标记文件。
- **输出**：`candidates.json`（每原语：是否逃逸成功 + 原始 stdout/错误）。
- **命令**：`python tools/hunt_nodeperm.py --restricted <标记文件> --output candidates.json [--node <path>]`。
- **终止条件**：`candidates.json` 生成，覆盖全部原语。

### 4. validate → report
- **输入**：`candidates.json`。
- **动作**：对逃逸成功项过 **7-Question Gate**，复现留证；对照 `reference.md` 标注对应 CVE 与修复版本。
- **输出**：`evidence/`（PoC + 输出）+ `report/candidates.md`（命中矩阵）。
- **命令**：`bash tools/validate.sh candidates.json`。
- **终止条件**：每原语有 confirmed/killed，confirmed 有 PoC 与越权读证据。

## 7-Question Gate（任一 NO 则 KILL）

1. 在**授权环境**运行（非未授权生产）？
2. 目标确实**启用了权限模型**（否则"绕过"无意义）？
3. PoC 确实读到了**白名单外**的标记文件（客观逃逸信号）？
4. 逃逸走的是**内部/非预期 API**（而非配置本就放行）？
5. **可复现**（重跑稳定）？
6. 已留存 **PoC 源码 + 运行输出**证据？
7. 能给出**影响与修复版本**，且只读了授权标记文件？

## Finding 输出格式

```
### <原语名>（Node <版本>）
- Severity: Critical | High | Medium | Low | Info
- Asset: Node <版本> + <权限配置>
- Reproduction: <PoC 片段 + 启动命令>
- Impact: <逃逸后可读/可执行范围> + 对应 CVE
- Evidence: <evidence/ PoC.js + 输出>
- Fix: <已修复版本 / 缓解措施>
- Status: confirmed | killed(<第几问 NO + 原因>)
```

## 参考

绕过原语（inspector / process.binding / fs.statfs / fs.openAsBlob / mainModule.require / Module._load / path.resolve 覆盖 / Uint8Array 路径 / 符号链接重命名）、对应 CVE 与修复版本见 `reference.md`——按 recon 出的 Node 版本圈定仍可能有效的原语再跑。
