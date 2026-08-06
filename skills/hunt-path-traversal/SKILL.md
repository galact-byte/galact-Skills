---
name: hunt-path-traversal
description: 在授权渗透测试中系统性挖掘路径遍历/目录穿越（path traversal、directory traversal、zip-slip、archive/symlink 写入）。当目标用用户可控的文件名/路径读取、写入、删除、下载、解压文件时使用——典型场景：`../` 读任意文件（源码/密钥/web.xml）、解压覆盖文件拿 RCE、编码绕过前缀校验、规范化差异逃出目录。适用目标类型 Web / REST API / 桌面/移动客户端 / CI。触发场景包括用户说"测下路径遍历/任意文件读取""这个下载参数能不能 ../""解压有没有 zip slip""能读到 /etc/passwd 吗"。输出：带原始请求与读到的越权文件内容为证据的 finding 报告（含 killed 记录）。
allowed-tools: Read, Grep, Glob, Bash
---

# hunt-path-traversal · 路径遍历猎杀

只解决 **路径遍历一类**：任意文件**读**（`../` 出目录）、**写/删**（解压/上传/日志重定向覆盖文件）、以及**规范化/编码差异**绕过前缀校验。核心是找到"用户输入拼进文件路径且规范化不彻底"的点，用**读到越权文件**或**写入标记文件**做客观判定。

任意文件写/删可直达 RCE 或破坏，风险高。默认**读优先**（无害），写/删 PoC 只在 scope 授权时做且只写无害标记文件。关键动作走 `tools/` 脚本。编码族与真实报告见 `reference.md`。

## Scope（授权范围）

**先确认授权，再探测。**

开工前落实：
- 授权目标与**允许的操作**（仅读 / 允许写标记文件 / 允许删）。
- 敏感文件读取边界（能否尝试 `/etc/passwd`、源码、密钥）。
- 明确禁止：删除/覆盖真实业务文件、越出授权主机。

任一不清楚就停下问。写/删探测**只针对授权内的无害标记路径**。

## Goal

判定用户可控路径能否逃出预期目录，达成越权**读/写/删**，给出可复现 PoC 与影响（读源码/密钥、覆盖文件 RCE、跨租户访问），并留存读到的越权内容或写入痕迹为证据。

## Workflow

`scope-check → recon → hunt → validate → report`。

### 1. scope-check
- **输入**：授权范围 + 允许操作。
- **动作**：写 `evidence/scope.txt`（含 allow_write / sensitive_read 标记）。
- **命令**：`bash tools/recon.sh <target> --scope-only`。
- **终止条件**：`evidence/scope.txt` 存在且授权明确，否则 KILL。

### 2. recon
- **输入**：in-scope 目标。
- **动作**：枚举吃文件名/路径的入口——`file=`/`path=`/`name=`/`download=`/`template=`/`page=`、下载/预览/导出、**上传后解压**（zip/tar/nupkg/包管理）、客户端 `file://`/deep link/intent、CI cache key。
- **输出**：`recon/endpoints.json`（入口 + 落点：read / write-extract / client-uri）。
- **命令**：`bash tools/recon.sh <target>`。
- **终止条件**：至少 1 个候选入口，否则记录结束。

### 3. hunt
- **输入**：`recon/endpoints.json`。
- **动作**：按 `reference.md` 的编码族对每个入口试探：朴素 `../`、URL 编码 `%2e%2e%2f`、双重编码、Windows `..\\`、`....//`、`?`/`#` 截断、绝对路径、规范化差异（`/data/user/0/`、`..;/`）。用**目标文件回显差异**判活（读到 `root:x:0:0` 等）。
- **输出**：`candidates.json`。
- **命令**：`python tools/hunt_pathtrav.py --input recon/endpoints.json --output candidates.json [--marker <标记>]`。
- **终止条件**：`candidates.json` 生成，无信号则全 killed。

### 4. validate → report
- **输入**：`candidates.json`。
- **动作**：过 **7-Question Gate**，通过的复现取证（保存读到的越权文件片段 / 写入标记）。任一 NO → killed。
- **输出**：`evidence/` + `report/candidates.md`。
- **命令**：`bash tools/validate.sh candidates.json`。
- **终止条件**：每条 confirmed/killed，confirmed 有越权文件内容或写入痕迹。

## 7-Question Gate（任一 NO 则 KILL）

1. 目标在**授权 scope** 内？
2. 输入确实**拼进文件路径**（读/写/删/解压）？
3. 有**客观信号**（读到预期外文件内容 / 写入标记出现 / 报错泄露路径），非猜测？
4. 确实**逃出了预期目录**（越权访问，而非目录内正常文件）？
5. **可复现**（重放稳定）？
6. 已留存**越权内容或写入痕迹**证据？
7. 影响可陈述，且写/删 PoC **只碰授权内无害标记**？

## Finding 输出格式

```
### <Title>
- Severity: Critical | High | Medium | Low | Info
- Asset: <目标 + 参数/入口>
- Reproduction: <精确 payload（含编码变体）+ 请求>
- Impact: <读源码/密钥 / 覆盖文件 RCE / 跨租户>
- Evidence: <evidence/ 读到的越权片段 / 写入标记 / 路径报错>
- Status: confirmed | killed(<第几问 NO + 原因>)
```

## 参考

编码族（`../` / 各种编码 / 截断 / 规范化差异 / zip-slip-tar-symlink）、检测特征、真实报告见 `reference.md`——读类入口优先编码族，上传解压入口优先 zip-slip/symlink。
