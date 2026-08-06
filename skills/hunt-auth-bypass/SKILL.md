---
name: hunt-auth-bypass
description: 在授权渗透测试中挖掘认证/授权绕过（authentication & authorization bypass）。当目标的登录、SSO/OAuth/SAML、2FA、会话、密码重置、邮箱验证等鉴权环节可能被逻辑缺陷或解析差异绕过时使用——典型场景：SAML 签名/entityId 绕过、OAuth `response_type`/`redirect_uri` 篡改窃取 token、邮箱规范化/预验证绕过、2FA 可预测/可跳过、会话类型混淆。适用目标类型 Web / REST API / SSO。触发场景包括用户说"测下认证绕过""这个 SAML/OAuth 有没有问题""能不能跳过 2FA""邮箱验证能绕吗"。输出：绕过路径 + 越权访问证据的 finding（含 killed 记录）。
allowed-tools: Read, Grep, Glob, Bash
---

# hunt-auth-bypass · 认证/授权绕过猎杀

只解决**认证与授权绕过一类**：登录、SSO（SAML/OAuth/OIDC）、2FA、会话、密码重置、邮箱验证等环节的逻辑缺陷与解析差异。这类漏洞**高度依赖业务流程**，脚本只做入口枚举与已知模式探测，真正判定靠**能否以他人身份/越权访问**为客观标准，多数验证需人工按流程走。

绕过认证会触及他人账户，风险与合规敏感。默认只在**自己控制的测试账户**间验证（A 账户能否越权访问 B 的资源/身份），不碰真实用户数据。已知模式与真实报告见 `reference.md`。

## Scope（授权范围）

**先确认授权。**

落实：授权目标、可用的测试账户（至少 2 个，用于验证越权）、允许触碰的鉴权环节、明确禁止访问真实用户数据。任一不清楚就停下问。

## Goal

判定鉴权环节能否被绕过达成**以他人身份登录 / 越权访问 / 跳过 2FA / 接管账户**，给出可复现路径与越权证据。

## Workflow

`scope-check → recon → hunt → validate → report`。

### 1. scope-check
- **动作**：写 `evidence/scope.txt`（含测试账户）。
- **命令**：`bash tools/recon.sh <target> --scope-only`。
- **终止条件**：scope 与测试账户明确，否则 KILL。

### 2. recon
- **动作**：识别鉴权面——登录/注册/重置端点、SSO 类型（SAML/OAuth/OIDC，看 `SAMLResponse`/`response_type`/`redirect_uri`/`id_token`）、2FA 机制、会话 cookie 结构。
- **输出**：`recon/endpoints.json`（鉴权入口 + 机制指纹）。
- **命令**：`bash tools/recon.sh <target>`。
- **终止条件**：至少识别出一种鉴权机制。

### 3. hunt
- **动作**：按 `reference.md` 对识别出的机制跑已知模式检查：OAuth `response_type=code id_token`/`response_mode=fragment` 篡改、`redirect_uri` 宽松匹配、SAML 签名剥离/`entityId` 尾随空格、邮箱规范化差异、2FA 可预测/可跳过。多数产出"待人工按流程验证"的结构化清单。
- **输出**：`candidates.json`。
- **命令**：`python tools/hunt_authbypass.py --input recon/endpoints.json --output candidates.json`。
- **终止条件**：`candidates.json` 生成。

### 4. validate → report
- **动作**：过 **7-Question Gate**，用**两个测试账户**验证越权（A 拿到 B 的身份/资源）取证。任一 NO → killed。
- **命令**：`bash tools/validate.sh candidates.json`。
- **终止条件**：每条 confirmed/killed，confirmed 有越权访问证据。

## 7-Question Gate（任一 NO 则 KILL）

1. 目标在**授权 scope** 内、且只用**测试账户**？
2. 命中的是**真实鉴权环节**（非无鉴权的公开资源）？
3. 有**客观信号**（以他人身份登录 / 拿到他人资源 / 跳过了 2FA），非猜测？
4. 确实**越权**（跨越了身份/权限边界）？
5. **可复现**？
6. 已留存**越权访问证据**（响应含他人数据/会话）？
7. 影响可陈述，且**未触碰真实用户数据**？

## Finding 输出格式

```
### <Title>
- Severity: Critical | High | Medium | Low | Info
- Asset: <鉴权入口 + 机制>
- Reproduction: <逐步流程 + 篡改点 + 请求>
- Impact: <账户接管 / 越权访问 / 2FA 绕过>
- Evidence: <evidence/ 越权响应（测试账户间）>
- Status: confirmed | killed(<第几问 NO>)
```

## 参考

各机制绕过模式（SAML / OAuth-OIDC / 2FA / 邮箱验证 / 会话 / 密码重置）、检测特征、真实报告见 `reference.md`。
