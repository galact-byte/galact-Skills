---
name: hunt-oauth-jwt
description: 在授权渗透测试中挖掘 OAuth/OIDC/JWT/SAML 认证体系的设计缺陷。当目标使用 JWT 令牌、OAuth 2.0 授权流、OpenID Connect、SAML SSO 进行认证授权时使用——典型场景：JWT alg=none/密钥混淆/弱密钥/claim 篡改、OAuth redirect_uri 绕过/state 缺失/授权码泄露、SAML 签名绕过/断言篡改、刷新令牌窃取。适用目标类型 Web / REST API / SSO / 移动端。触发场景包括用户说"测下 JWT""OAuth 有没有漏洞""这个 SSO/SAML 安全吗""token 能伪造吗""刷新令牌能偷吗"。输出：认证绕过/令牌伪造 + 越权证据的 finding（区分确认、阻塞、未定与误报）。
allowed-tools: Read, Grep, Glob, Bash
---

# hunt-oauth-jwt · OAuth/JWT/SAML 认证猎杀

只解决**认证体系（JWT/OAuth/OIDC/SAML）的设计与实现缺陷一类**。核心是检验令牌签发、验证、传输各环节的安全性。判定靠**成功伪造令牌/窃取授权/冒充他人身份的客观证据**。

只在受控测试账号上做最小证明。先确认令牌变异、离线密钥检查、回调域和授权流动作的许可，禁止获取或使用真实用户会话。严重度按实际影响评定；方法与判定边界见 [参考](reference.md)。

## Scope（授权范围）

**先确认授权。**

落实：授权目标、认证体系类型（JWT/OAuth/SAML/自定义）、是否有测试 IdP（SAML 场景）、是否允许尝试令牌伪造。

## Goal

系统性检测认证体系：令牌完整性（签名验证是否可绕）、授权流安全（redirect_uri/state/PKCE）、密钥管理（弱密钥/泄露/混淆）、令牌生命周期（刷新/撤销），给出可复现的认证绕过证据。

## Workflow

`scope-check → recon → hunt → validate → report`。

### 1. scope-check
- **动作**：确认授权、识别认证体系类型、准备测试账号。
- **终止条件**：scope 明确。

### 2. recon — 认证体系画像
- **动作**：
  - 抓取认证流量，识别 JWT/OAuth/SAML 使用
  - JWT：解码 Header（alg、kid）、Payload（iss、sub、exp、自定义 claim）
  - OAuth：识别 grant_type、authorization/token endpoint、redirect_uri 格式
  - 检查 `/.well-known/openid-configuration`、`/jwks.json`、`/.well-known/oauth-authorization-server`
  - SAML：获取 SP/IdP metadata、签名算法
- **输出**：认证体系档案 + 攻击面清单。

### 3. hunt — 按体系攻击

#### 3a. JWT 攻击
- **alg 篡改**：改 `alg: none` → 去掉签名；改 `RS256 → HS256` → 用公钥当 HMAC 密钥
- **密钥检查**：仅对获准的测试令牌做有预算的离线弱密钥检查，不对登录端点进行在线口令爆破。
- **kid 输入**：核对是否参与路径/数据库查询；需要文件读取或 SQL 验证时，另按相应 Skill 与动作许可执行。
- **claim 篡改**：只使用受控账号与角色，比较服务端实际身份和授权结果，解码成功不等于接受。
- **jku/x5u**：只使用获准的测试 JWKS 地址，不能自动探测内网。
- **exp 篡改**：移除或设极大值

#### 3b. OAuth 2.0 攻击
- **redirect_uri 校验**：用受控回调比较注册 URI 与单字段变体；记录实际 Location、浏览器最终 origin、code/token 去向和可兑换条件。
  - 路径规范化、子域匹配、query/fragment 与重复参数需分别测试，不能只看字符串包含另一个域名。
  - `https://legit.example/../attacker.example` 仍属于 `legit.example`；片段中的 `@` 也不会改变主机。只有实际泄露/越权链路证据才确认影响。
- **state / PKCE**：检查事务绑定、单次消费和端点强制校验；缺少 state 字段本身不直接证明 CSRF，需考虑 PKCE 与其他有效绑定措施。
- **授权码泄露**：Referer 泄露、日志泄露、code 重放
- **implicit flow token 泄露**：fragment 中的 token 通过开放重定向窃取
- **PKCE 绕过**：code_verifier 不校验或可预测

#### 3c. SAML 攻击
- **签名绕过**：XML 签名包裹（XSW）、仅校验存在性不校验完整性
- **断言篡改**：修改 NameID/Role/Attribute
- **重放攻击**：旧 SAML Response 重放

### 4. validate → report
- **动作**：逐项核对证据，私有保存测试令牌及请求，公开材料脱敏；核对服务端实际身份/权限而非仅 HTTP 200。
- 缺许可记 blocked，链路不明记 inconclusive，对照证伪记 false_positive；不能把未确认候选一律 killed。

## 7-Question Gate（证据不足不确认）

1. 目标在**授权 scope** 内？
2. 确实存在**签名验证/授权流/密钥管理缺陷**（非正常令牌的合法使用）？
3. 能够**以非授权身份获取访问**（不是仅修改了令牌但被拒绝）？
4. **可复现**（稳定可冒充，非令牌过期/单次时序）？
5. 对比了**正常身份 vs 伪造身份**的访问结果？
6. 已留存**伪造令牌 + 成功访问**的完整请求响应证据？
7. **未窃取/使用真实用户的活跃会话**？

## 与其他 hunt skill 的链

- OAuth + `hunt-open-redirect`：开放重定向窃取 OAuth token（implicit flow 经典链）
- JWT + `hunt-idor`：JWT claim 篡改 → IDOR（改 user_id claim 越权访问）
- SAML + `hunt-xxe`：SAML XML 解析 → XXE（SAML Response 中注入实体）
- OAuth + `hunt-csrf`：缺少有效事务绑定时，在受控流程中检查登录 CSRF，不能只凭缺少 state 确认。

## Finding 输出格式

```
### <Title>
- Severity: Critical | High | Medium | Low
- Asset: <认证端点 + 令牌类型>
- Reproduction: <伪造方法 + 篡改字段 + 请求>
- Impact: <身份冒充范围 / 权限提升程度>
- Evidence: <evidence/ 伪造令牌 + 成功访问截图>
- Status: confirmed | inconclusive | blocked | false_positive | out_of_scope
```

## 参考

JWT 验证、OAuth 回调与事务绑定、SAML 签名覆盖检查见 [参考](reference.md)。
