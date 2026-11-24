# JWT、OAuth 与 SAML 验证参考

## JWT：解码不等于验证

JWT 的编码使用 Base64url，可能省略 padding；不要将普通 `base64 -d` 的成功/失败当作格式或签名结论。不把测试令牌上传到公共解码站点。可在本地受控环境中查看 alg、kid、iss、aud、sub、exp、nbf 及角色字段，然后以资源服务器的实际验证结果为准。

| 候选 | 核对条件 | 最小证据 |
|---|---|---|
| alg=none | 服务端是否接受未签名令牌、是否固定允许算法 | 正常/变异测试令牌与实际身份/授权结果 |
| RS→HS 混淆 | 验证器是否混用密钥类型与算法 | 受控变异后服务器真实接受；公钥公开本身不是漏洞 |
| 弱 HMAC 密钥 | 获准测试令牌、算法与离线预算 | 离线恢复后在许可范围内核对有效签名；不在线撞账号 |
| kid/jku/x5u | 密钥选择路径、可信来源绑定 | 受控密钥源是否被接受；SSRF/文件/SQL 检查另取动作许可 |
| claim/生命周期 | 签名、issuer/audience、过期和事务绑定 | 比较服务端身份与权限；payload 可编辑并非绕过 |

现有工具可辅助，但必须先查看当前版本帮助并限定单项测试；本库不提供或默认启动全自动令牌攻击脚本。

## OAuth/OIDC：实际去向与事务绑定

按授权服务器元数据发现端点，核对注册 redirect_uri、client、response_type、授权码单次消费、PKCE 的 challenge/verifier 绑定与 token endpoint 校验。

以 `https://app.example/callback` 为例：

- `https://app.example/../other.example` 的主机仍是 `app.example`。
- `https://app.example/callback@other.example` 中 `@` 在路径内，不会改变主机。
- `https://app.example/callback#@other.example` 中后段是 fragment，不会改变主机，也不会随普通 HTTP 请求发送给服务端。
- `https://app.example.other.example/callback` 的主机确实不同，但授权服务器可能正确拒绝。

字符串变体不等于绕过。记录原始请求、每次 Location、最终 origin、code/token 的接收方、client/PKCE 绑定及是否可兑换；只使用获准的账号和回调设施，不外带真实用户令牌。

缺少 state 字段不能单独证明 CSRF：核对是否有有效的 PKCE/事务绑定等保护。反之，存在 state 也不代表它被正确验证。确认登录 CSRF 或账号绑定影响需要受控的完整流程对照。

## SAML：签名覆盖与应用消费

XSW 的核心是签名验证的元素与应用实际使用的 NameID/Role/Attribute 不一致。核对签名覆盖对象、ID 唯一性、信任证书、Issuer、Audience、Recipient、时间窗口及 InResponseTo/重放处理。

只有受控断言被接受并产生不应有的身份/权限时才确认影响；解析错误、签名字段存在、Response 返回 200 都不够。测试 IdP、SP 或修改断言许可缺失时记 `blocked`，不使用真实用户会话。

## 依据与关联

- [RFC 8725：JWT Best Current Practices](https://www.rfc-editor.org/rfc/rfc8725.html)
- [RFC 9700：OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700.html)
- [开放重定向](../hunt-open-redirect/SKILL.md)
- [对象授权](../hunt-idor/SKILL.md)
