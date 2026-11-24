# 子域接管参考

## 逐层证据

| 层级 | 可观察事实 | 不能据此推出 |
|---|---|---|
| DNS | 授权子域仍 CNAME 到失效资源 | 第三方有权或能够认领 |
| HTTP | 原主机出现服务商默认错误 | 所有该服务商域名都可接管 |
| 云资源 | 资源名可创建或被预留 | 自定义域名验证可通过 |
| 绑定 | 测试资源成功关联授权域名 | 原域名当前流量确实进入该资源 |
| 内容 | 原域名返回本次随机标记且归属已验证 | Cookie、邮件或 OAuth 必然可窃取 |

## 厂商条件快查

| 线索 | 需要继续核对 |
|---|---|
| S3 `NoSuchBucket` | endpoint 类型、地区、桶名与原 Host 的关系、名称归属及当前限制；不存在桶不等于能创建或承接原主机流量 |
| GitHub Pages 默认 404 | 账号/组织域名验证保护、子域层级、已有绑定；仅 CNAME 与错误页不能确证 |
| Azure App Service NXDOMAIN/默认错误 | `asuid` TXT、名称保留、租户限制及安全唯一默认主机名；不同 Azure 产品不能套用同一规则 |
| 其他 SaaS 的 unknown domain | 当前官方绑定与所有权验证机制；历史指纹库可能过期 |
| NS/MX 目标异常 | 委派链、冗余服务器、权威结果；不注册 NS 域名、不收取邮件来验证 |

通配 DNS 需用少量随机标签对照；CDN 缓存与 DNS 缓存分别记录。验证只涉及一个精确子域时，不宣称已覆盖整个 zone。TLS 错误不是资源归属证明；不得为“补 HTTPS”擅自申请客户域名证书。

## 修复建议

先核实业务归属，再删除或更新过期记录。按服务商机制使用自定义域名验证、名称保护及安全唯一主机名；资源下线流程同时核对 DNS 与资源绑定。删除测试资源之前按已批准清理顺序处理域名绑定，避免再次留下悬挂。

## 官方依据

- [GitHub Pages 自定义域名验证](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages)：账号或组织验证保护该域及直接子域，通配与更深层级仍需分别核对。
- [Azure App Service 接管预防](https://learn.microsoft.com/en-us/azure/app-service/reference-dangling-subdomain-prevention)：域名令牌、名称保留与安全唯一主机名分别提供保护。
- [Microsoft 悬挂 DNS 风险与治理](https://learn.microsoft.com/en-us/azure/security/fundamentals/subdomain-takeover)。

厂商规则会变化；以上是核对入口，不是永久可接管名单。
