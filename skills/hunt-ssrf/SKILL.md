---
name: hunt-ssrf
description: 在授权渗透测试中系统性挖掘服务端请求伪造（SSRF）。当目标存在"服务端按用户可控的 URL/主机/地址发起出站请求"的功能——如 URL 预览、图片/视频抓取、Webhook、集成回调、导入远程资源、PDF/截图渲染、代理转发——需要判定是否可绕过 SSRF 防护访问内网/云元数据/受限服务时使用。适用目标类型 REST API / Web 应用。触发场景包括用户说"测下这个 URL 抓取有没有 SSRF""这个 webhook 能打内网吗""帮我挖 SSRF/内网探测""看看能不能读云元数据"。输出：带原始请求/响应证据的 finding 报告（含 killed 记录）。
allowed-tools: Read, Grep, Glob, Bash
---

# hunt-ssrf · 服务端请求伪造猎杀

一个只解决 **SSRF 一类漏洞** 的挖掘 skill。把"哪里能让服务端替我发请求"变成一条可复现、有证据、可判真伪的猎杀流水线，而不是零散试 payload。

关键动作都走 `tools/` 下的脚本执行，模型负责决策与判读，**不直接乱发请求**——这样证据统一留存、过程可复现。具体 payload、绕过手法、检测特征与真实报告在 `reference.md`，按需读取（渐进式披露）。

## Scope（授权范围）

**先确认授权，再动手。** 未拿到明确 scope 前不发任何出站探测请求。

开工前必须落实：
- 授权目标域名/IP 段（in-scope）与明确排除项（out-of-scope）。
- 是否允许触达云元数据、内网段、第三方回调地址。
- OAST/带外回连是否允许（用自己的 Burp Collaborator / interactsh / 自建监听）。

这些任一不清楚就停下问用户，不要"先打了再说"。SSRF 天然会打到内网与元数据，越权探测风险高。

## Goal

判定目标的"服务端取 URL"功能是否可被诱导访问**攻击者不应触达的资源**（内网服务、`169.254.169.254` 云元数据、`localhost` 管理端口、受限协议），给出可复现的 PoC 与影响链，并留存原始请求/响应证据。

## Workflow

四个阶段顺序执行：`scope-check → recon → hunt → validate → report`。每阶段做完看"终止条件"再进下一步。

### 1. scope-check
- **输入**：用户给的授权范围。
- **动作**：把 in-scope / out-of-scope / 是否允许元数据与 OAST 写进 `evidence/scope.txt`。
- **命令**：`bash tools/recon.sh <target> --scope-only`（仅记录 scope，不发请求）。
- **终止条件**：`evidence/scope.txt` 存在且授权明确。否则 KILL 整个任务。

### 2. recon
- **输入**：in-scope 目标。
- **动作**：枚举一切"吃 URL/主机/地址"的入口——表单字段、JSON 键、query 参数、Webhook 配置、导入功能、`url=`/`src=`/`callback=`/`image=`/`proxy=` 类参数、SSO/OAuth `redirect_uri`。
- **输出**：`recon/endpoints.json`（候选入口清单：URL、参数名、方法、可控点）。
- **命令**：`bash tools/recon.sh <target>`。
- **终止条件**：`recon/endpoints.json` 至少含 1 个候选入口；为空则本目标无 SSRF 面，记录后结束。

### 3. hunt
- **输入**：`recon/endpoints.json` + 你的 OAST 回连地址。
- **动作**：对每个入口按 `reference.md` 的绕过族逐层试探：直连 OAST → 内网/loopback → 云元数据 → 备用 IP 编码 → DNS rebinding → 重定向/协议切换 → Host 头类。以**带外命中/响应差异/时间差异**判定，而非猜测。
- **输出**：`candidates.json`（每条候选：入口、payload、观测信号、疑似类型）。
- **命令**：`python tools/hunt_ssrf.py --input recon/endpoints.json --output candidates.json --oast <你的回连域名>`。
- **终止条件**：`candidates.json` 生成。无任何信号则全部记为 killed 并结束。

### 4. validate → report
- **输入**：`candidates.json`。
- **动作**：对每条候选过 **7-Question Gate**（见下），任一 NO 即 KILL 并记录原因；通过的复现取证。
- **输出**：`evidence/`（原始请求/响应）+ `report/candidates.md`（finding 报告）。
- **命令**：`bash tools/validate.sh candidates.json`。
- **终止条件**：每条候选都有 confirmed 或 killed 结论，且 confirmed 项都有 `evidence/` 原始报文。

## 7-Question Gate（任一 NO 则 KILL）

对每个候选逐条自问，任意一个答 NO 就判定为 killed（并在报告里记原因，不丢弃）：

1. 目标在**授权 scope** 内？
2. 该参数确实触发了**服务端出站请求**（非前端 fetch）？
3. 能观测到**带外命中 / 响应差异 / 时间差异**等客观信号（非纯猜测）？
4. 触达的是**攻击者不应访问**的资源（内网 / 元数据 / loopback / 受限协议）？
5. 该绕过**可复现**（重放≥2 次稳定，非一次性偶发）？
6. 已留存**原始请求与响应**证据？
7. 能清楚陈述**影响**（读内部资源 / 窃取云凭据 / 升级为 RCE 链）？

## Finding 输出格式

每条 confirmed / killed 都用统一结构写入 `report/candidates.md`：

```
### <Title>
- Severity: Critical | High | Medium | Low | Info
- Asset: <目标 URL / 参数>
- Reproduction: <逐步复现，含精确 payload 与请求>
- Impact: <能拿到什么：内网服务 / 元数据凭据 / RCE 链>
- Evidence: <evidence/ 下原始请求响应文件名 + OAST 命中截图/日志>
- Status: confirmed | killed(<第几问 NO + 原因>)
```

## 参考

payload 库、绕过手法族、检测特征、真实报告索引见 `reference.md`——在 hunt 阶段按当前入口类型定向查阅，不要一次性全读。
