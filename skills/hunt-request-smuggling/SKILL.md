---
name: hunt-request-smuggling
description: 在授权渗透测试中系统性挖掘 HTTP 请求走私（HTTP Request Smuggling / desync）。当目标前面有反向代理/CDN/负载均衡（前端）转发给后端应用，且怀疑前后端对 Content-Length 与 Transfer-Encoding、畸形头、chunked trailer 的解析不一致时使用——典型场景：想毒化后端 socket 劫持他人请求、批量窃取会话 Cookie/令牌、缓存投毒、绕过前端访问控制。适用目标类型 Web / REST API（有分层代理）。触发场景包括用户说"测下有没有 HTTP 走私/desync""这个 CDN 后端解析一致吗""能不能毒 socket 偷别人 cookie""CL.TE / TE.CL 打一下"。输出：带 desync 时序证据与原始报文的 finding 报告（含 killed 记录）。
allowed-tools: Read, Grep, Glob, Bash
---

# hunt-request-smuggling · HTTP 请求走私猎杀

只解决 **HTTP 请求走私（前后端解析分歧导致的 desync）** 一类。核心是找到"前端按一种方式切分请求边界、后端按另一种方式切分"的差异点，用**时序探测**先判活，再谨慎做 socket 毒化验证。

走私会影响**其他用户的请求**，破坏性和法律风险都高。默认只做**自打自（self-smuggling）时序探测**确认 desync，不在生产上毒化真实用户 socket，除非 scope 明确授权。关键探测走 `tools/` 脚本（raw socket，curl 发不了畸形头）。绕过变体与真实报告见 `reference.md`。

## Scope（授权范围）

**先确认授权，再发探测。** 走私探测本身会向后端注入"半个请求"，可能污染连接。

开工前落实：
- 授权目标与**是否允许 socket 毒化验证**（区别于只做时序判活）。
- 测试窗口（低峰期），避免影响真实用户。
- 允许的验证深度：仅 desync 时序确认 / 允许自请求走私 / 允许受控毒化。

任一不清楚就停下问。**绝不**在未授权目标或高峰期做毒化。

## Goal

判定前端与后端是否对请求边界解析不一致（CL.TE / TE.CL / TE.TE / 畸形头 / trailer），给出可复现的 desync PoC 与影响（socket 毒化劫持请求、偷 Cookie/令牌、缓存投毒、绕前端 ACL），并留存原始报文与时序证据。

## Workflow

`scope-check → recon → hunt → validate → report`。

### 1. scope-check
- **输入**：授权范围 + 是否允许毒化。
- **动作**：写入 `evidence/scope.txt`（含 allow_poison 标记与测试窗口）。
- **命令**：`bash tools/recon.sh <target> --scope-only`。
- **终止条件**：`evidence/scope.txt` 存在且授权明确，否则 KILL。

### 2. recon
- **输入**：in-scope 目标。
- **动作**：识别分层结构——是否有 CDN/反代（看 `Via`、`X-Cache`、`Server`、`CF-*` 头）、支持的 HTTP 版本、是否 keep-alive 复用连接。
- **输出**：`recon/frontend.json`（前端指纹、是否值得试走私）。
- **命令**：`bash tools/recon.sh <target>`。
- **终止条件**：确认存在前后端分层且 keep-alive；否则走私面弱，记录后结束。

### 3. hunt
- **输入**：目标 + `recon/frontend.json`。
- **动作**：按 `reference.md` 的 desync 家族逐个发**时序差分探测**：正常基线 vs CL.TE vs TE.CL vs 畸形分隔（空格/Tab/CR-only/无冒号 trailer）。以**后端挂起超时 vs 快速返回**的时序差判 desync。
- **输出**：`candidates.json`（每个变体：延迟、状态、疑似 desync 类型）。
- **命令**：`python tools/hunt_smuggling.py --target <url> --output candidates.json`。
- **终止条件**：`candidates.json` 生成。无时序差异则记 killed 结束。

### 4. validate → report
- **输入**：`candidates.json`。
- **动作**：对疑似 desync 变体过 **7-Question Gate**，通过的做**受控复现**（自请求走私取证；毒化仅在 allow_poison 时）。任一 NO → killed。
- **输出**：`evidence/`（原始 desync 报文 + 时序）+ `report/candidates.md`。
- **命令**：`bash tools/validate.sh candidates.json`。
- **终止条件**：每个变体有 confirmed/killed 结论，confirmed 项有原始报文与可复现时序。

## 7-Question Gate（任一 NO 则 KILL）

1. 目标在**授权 scope** 内、且在**允许的测试窗口**？
2. 目标确有**前后端分层**（代理/CDN + 后端）且**keep-alive 复用**？
3. 观测到**稳定的时序差分**（后端挂起 vs 正常），而非网络抖动？
4. 差异确由**解析分歧**引起（能指出是 CL.TE/TE.CL/哪种畸形）？
5. desync **可复现**（多次稳定，非偶发）？
6. 已留存**原始畸形报文 + 时序**证据？
7. 能陈述**影响**（毒 socket 劫持/偷令牌/缓存投毒/绕 ACL），且验证方式未伤害真实用户？

## Finding 输出格式

```
### <Title>
- Severity: Critical | High | Medium | Low | Info
- Asset: <目标 + 前端指纹>
- Reproduction: <desync 变体 + 原始畸形报文 + 时序数据>
- Impact: <socket 毒化 / 令牌窃取 / 缓存投毒 / ACL 绕过>
- Evidence: <evidence/ 下原始报文 + 时序日志>
- Status: confirmed | killed(<第几问 NO + 原因>)
```

## 参考

desync 家族（CL.TE / TE.CL / 空格-Tab-CR 畸形 / 无冒号 trailer / CRLF 注入）、检测特征、真实报告见 `reference.md`——按 recon 出的前端类型定向查阅。**深度验证建议配合 Burp Repeater(关自动更新CL) 或 smuggler.py**，本 skill 脚本负责时序判活与证据留存。
