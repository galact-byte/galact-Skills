---
name: hunt-command-injection
description: 在授权渗透测试中系统性挖掘命令注入与参数/标志注入（OS command injection、argument/flag injection、外部程序 delegate 注入）。当目标把用户输入拼进 shell 命令、或作为参数传给 git/tar/curl/ffmpeg/ImageMagick 等外部程序、或经模板/eval 执行时使用——典型场景：文件名/路径/URL/ref 参数最终进了命令行，想拿 RCE 或任意文件读写。适用目标类型 Web / REST API / CI 系统。触发场景包括用户说"测下命令注入/RCE""这个参数会不会进 shell""git/tar/ffmpeg 参数能注入吗""上传头像触发 ImageMagick 了"。输出：带原始请求/命令回显或带外证据的 finding 报告（含 killed 记录）。
allowed-tools: Read, Grep, Glob, Bash
---

# hunt-command-injection · 命令注入猎杀

只解决 **命令注入一类**：直接 OS 命令注入、**参数/标志注入**（把 `--output` 之类塞进已有命令）、以及**外部程序 delegate 注入**（ImageMagick/ffmpeg 解析时执行命令）。核心是追踪"用户输入 → 命令行 argv"的数据流，用**带外/时序/回显**判活，而非盲打分号。

命令注入直达 RCE，破坏性极高。默认只做**无害探测**（sleep 时序、带外 DNS/HTTP、`id`/`whoami` 只读回显），**不投放持久化/破坏性 payload**，除非 scope 明确授权。关键动作走 `tools/` 脚本，证据统一留存。payload 族与真实报告见 `reference.md`。

## Scope（授权范围）

**先确认授权，再探测。** 命令注入探测可能真的在目标上执行命令。

开工前落实：
- 授权目标与**允许的探测深度**（仅时序/带外判活 / 允许只读命令 `id` / 允许写文件 PoC）。
- 带外回连地址（OAST）与是否允许触达内网。
- 明确禁止：破坏性命令（rm/关机/改配置）、持久化后门。

任一不清楚就停下问。**绝不**投放破坏性或持久化 payload。

## Goal

判定用户输入是否能进入命令行并被执行（或改变命令语义），给出可复现 PoC 与影响（RCE / 任意文件读写 / CI 接管），并留存带外命中或回显证据。

## Workflow

`scope-check → recon → hunt → validate → report`。

### 1. scope-check
- **输入**：授权范围 + 允许深度。
- **动作**：写 `evidence/scope.txt`（含 allow_write / oast_domain）。
- **命令**：`bash tools/recon.sh <target> --scope-only`。
- **终止条件**：`evidence/scope.txt` 存在且授权明确，否则 KILL。

### 2. recon
- **输入**：in-scope 目标。
- **动作**：枚举"输入可能进命令行"的入口——文件名/路径/URL/ref/分支名/格式转换/导出/备份/ping/whois 类功能，尤其**上传后触发的图像/视频处理**（ImageMagick/ffmpeg）与 **CI/git 操作**（clone/archive/import）。
- **输出**：`recon/endpoints.json`（入口 + 疑似落点类型：shell / argv / delegate）。
- **命令**：`bash tools/recon.sh <target>`。
- **终止条件**：至少 1 个候选入口，否则记录结束。

### 3. hunt
- **输入**：`recon/endpoints.json` + OAST。
- **动作**：按 `reference.md` 分族探测：shell 元字符（`;`/`|`/`$()`/反引号）、**时序**（`sleep`/`ping -c`）、**带外**（`nslookup`/`curl` 到 OAST）、**参数注入**（`--output`/`-o`/前导 `-`）、**delegate**（恶意 MVG/SVG/m3u8）。以带外命中/时延判活。
- **输出**：`candidates.json`。
- **命令**：`python tools/hunt_cmdi.py --input recon/endpoints.json --output candidates.json --oast <域名>`。
- **终止条件**：`candidates.json` 生成，无信号则全 killed。

### 4. validate → report
- **输入**：`candidates.json`。
- **动作**：过 **7-Question Gate**，通过的复现取证（只读回显或授权内写文件 PoC）。任一 NO → killed。
- **输出**：`evidence/` + `report/candidates.md`。
- **命令**：`bash tools/validate.sh candidates.json`。
- **终止条件**：每条 confirmed/killed，confirmed 有带外命中或回显证据。

## 7-Question Gate（任一 NO 则 KILL）

1. 目标在**授权 scope** 内？
2. 输入确实进入了**命令行/外部程序 argv**（非纯字符串存储）？
3. 有**客观信号**（带外命中 / sleep 时延 / 命令回显），非猜测？
4. 达成了**越权执行**（RCE / 任意文件读写 / 改命令语义）？
5. **可复现**（重放稳定）？
6. 已留存**原始请求 + 带外/回显**证据？
7. 影响可陈述，且 PoC **未做破坏性/持久化**操作？

## Finding 输出格式

```
### <Title>
- Severity: Critical | High | Medium | Low | Info
- Asset: <目标 + 参数/入口>
- Reproduction: <精确 payload + 请求；带外域名/时延对照>
- Impact: <RCE / 文件读写 / CI 接管>
- Evidence: <evidence/ 原始请求 + OAST 命中日志 / 回显>
- Status: confirmed | killed(<第几问 NO + 原因>)
```

## 参考

payload 族（shell 元字符 / 时序盲注 / 带外 / 参数-标志注入 / delegate 注入）、检测特征、真实报告见 `reference.md`——按 recon 落点类型定向查阅（上传处理优先 delegate，CI/git 优先参数注入）。
