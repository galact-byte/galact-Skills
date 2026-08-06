---
name: hunt-csrf
description: 在授权渗透测试中挖掘跨站请求伪造（CSRF）及其防护绕过。当目标存在状态变更操作（改邮箱/密码/角色/设置、转账、增删）而 CSRF 防护缺失或可绕过时使用——典型场景：无 token/token 不校验、SameSite=Lax 被 GET 或子域绕过、Content-Type text/plain 避开 preflight、cookie 注入伪造 token、Flash/307 重定向绕 CORS、Login CSRF。适用目标类型 Web / REST API。触发场景包括用户说"测下 CSRF""这个改密码有没有 CSRF 防护""SameSite 能绕吗""token 校验严不严"。输出：CSRF 可行性 + PoC 的 finding（含 killed 记录）。
allowed-tools: Read, Grep, Glob, Bash
---

# hunt-csrf · 跨站请求伪造猎杀

只解决 **CSRF 一类**：判定状态变更操作能否被跨站伪造。核心是对每个敏感操作检查**防护三要素**（CSRF token 是否存在且被校验、SameSite cookie 属性、是否依赖不可跨站获取的头），再针对缺口构造跨站 PoC。判定靠**去掉/伪造 token 后请求仍成功**、或**跨站发起能改变状态**。

CSRF PoC 会真实触发状态变更。默认只在**测试账户**上验证（改测试账户自己的无害字段），不动真实用户、不做破坏性变更。绕过手法与真实报告见 `reference.md`。

## Scope（授权范围）

**先确认授权。**

落实：授权目标、测试账户、允许触发的状态变更（选无害/可回滚的，如改昵称）、禁止对真实用户或不可逆操作下手。任一不清楚就停下问。

## Goal

判定敏感操作是否可被跨站伪造（含防护绕过），给出可复现 PoC 与影响（账户接管/设置篡改/Login CSRF），只在测试账户上验证。

## Workflow

`scope-check → recon → hunt → validate → report`。

### 1. scope-check
- **动作**：写 `evidence/scope.txt`（测试账户/允许操作）。
- **命令**：`bash tools/recon.sh <target> --scope-only`。
- **终止条件**：scope 明确，否则 KILL。

### 2. recon
- **动作**：枚举状态变更端点——表单 POST、改邮箱/密码/角色/设置、转账、增删；记录其 token 字段、cookie 的 SameSite 属性。
- **输出**：`recon/endpoints.json`。
- **命令**：`bash tools/recon.sh <target>`。
- **终止条件**：至少 1 个状态变更操作。

### 3. hunt
- **动作**：对每个操作检查 `reference.md` 的防护三要素：①删/改 token 重放看是否仍成功 ②cookie 是否 SameSite=None/Lax（Lax 下试 GET/顶层导航/子域）③是否 text/plain 避 preflight。据此判 CSRF 可行性。
- **输出**：`candidates.json`。
- **命令**：`python tools/hunt_csrf.py --input recon/endpoints.json --output candidates.json --cookie "<测试账户cookie>"`。
- **终止条件**：`candidates.json` 生成。

### 4. validate → report
- **动作**：过 **7-Question Gate**，对可行项生成跨站 PoC（HTML 表单/fetch）在测试账户验证状态变更取证。任一 NO → killed。
- **命令**：`bash tools/validate.sh candidates.json`。
- **终止条件**：每条 confirmed/killed，confirmed 有跨站触发的状态变更证据。

## 7-Question Gate（任一 NO 则 KILL）

1. 目标在**授权 scope** 内、只用**测试账户**？
2. 操作确实**改变服务端状态**（非只读）？
3. 有**客观信号**（去/伪 token 仍成功 / 跨站发起状态改变），非猜测？
4. 确实**可跨站伪造**（防护缺失或被绕过，非同源才可行）？
5. **可复现**？
6. 已留存**PoC + 状态变更**证据？
7. 影响可陈述，且只改**测试账户的无害/可回滚**状态？

## Finding 输出格式

```
### <Title>
- Severity: Critical | High | Medium | Low | Info
- Asset: <操作端点>
- Reproduction: <跨站 PoC（HTML/fetch）+ 触发步骤>
- Impact: <账户接管 / 设置篡改 / Login CSRF>
- Evidence: <evidence/ PoC + 状态变更前后对照（测试账户）>
- Status: confirmed | killed(<第几问 NO>)
```

## 参考

防护三要素检查、SameSite/preflight/cookie 注入/Flash 等绕过、真实报告见 `reference.md`。
