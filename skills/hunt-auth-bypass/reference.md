# hunt-auth-bypass · 参考

真实报告源自本仓库第二轮高价值案例（value_score≥8）。始终用**测试账户间**验证越权。

## 绕过模式（Bypasses）

### SAML
- **签名剥离/未校验**：删掉 `<Signature>` 或改 `Assertion` 后重放（#223461）。
- **entityId / NameID 尾随空格/大小写**匹配差异，冒充其他身份（#976603）。
- XML 注释/XSW（签名包裹）：`<NameID>admin<!---->@x</NameID>`。
- 结合 XXE（SAMLResponse 是 XML，见 hunt-xxe）。

### OAuth / OIDC
- **response_type/response_mode 篡改**：改成 `code id_token` + `response_mode=fragment`，配合目标页 XSS 从 fragment 偷 token（#1567186）。
- **redirect_uri 宽松匹配**：`//attacker`、`redirect_uri=https://t.com.attacker.com`、路径追加、`@`。
- **state 缺失**→ Login CSRF / 强制关联攻击者账户（#229528、#384962）。
- code 复用 / 无 PKCE / implicit token 回显。

### 2FA
- 可预测/弱随机（MD5 碰撞预测、时间种子）（#893395、#1067530）。
- 流程可跳过：直接请求 2FA 之后的端点；response 里 `2fa_passed` 可改。
- 无速率限制爆破；备份码逻辑缺陷。

### 邮箱验证 / 注册
- **邮箱规范化差异**：`a@x.com` vs `a@x.com ` vs `a+t@x.com`，或 SCIM/API 直接标记已验证（#565883、#791775）。
- 通过 API/SCIM 建用户绕过验证流程 → 访问依赖邮箱域的内部服务（#565883）。

### 会话 / cookie
- **会话类型混淆**：切换登录方式时状态类型不一致 → 手动构造 cookie 冒充会话（#493324）。
- cookie 解析差异伪造 token（见 hunt-csrf #14883）。

### 密码重置
- token 可预测/不失效、host 头投毒改重置链接、响应泄露 token。

## Detection Patterns（怎么判，而非猜）

- **越权访问（最硬）**：用 A 账户完成绕过后，响应里出现 **B 账户的数据/会话/身份** = 命中。
- **身份切换**：篡改 SAML/OAuth 后，登录成了另一个 subject。
- **2FA 跳过**：绕过后直接进入需 2FA 的资源。
- **redirect_uri 命中**：授权后 token/code 被发到你控制的域。
- 只用测试账户之间验证，绝不读真实用户数据。

## Real Reports（复现索引）

| 机制 | 报告 |
|---|---|
| SAML 签名/entityId | 223461 / 976603 |
| OAuth response_type/mode | 1567186 |
| Login CSRF / 强制关联 | 229528 / 384962 / 155774 |
| 2FA 可预测 | 893395 / 1067530 |
| 邮箱/SCIM 预验证 | 565883 / 791775 |
| 会话类型混淆 | 493324 |

hunt 顺序：先按 recon 指纹定机制 → 跑该机制的已知模式清单 → 用两个测试账户验证越权，任何"拿到他人身份/资源"即 confirmed。
