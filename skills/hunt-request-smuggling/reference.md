# hunt-request-smuggling · 参考

按 recon 出的前端类型定向查阅。真实报告源自本仓库第二轮 SSRF/协议类高价值案例（value_score≥8）。

> 记号：`\r`=CR(0x0D)，`\n`=LF(0x0A)。走私探测**必须发原始字节**（Burp/raw socket），curl/浏览器会替你规范化头，发不出畸形请求。

## desync 家族（Bypasses）

### A. CL.TE（前端信 Content-Length，后端信 Transfer-Encoding）
```
POST / HTTP/1.1\r\nHost: t\r\nContent-Length: 6\r\nTransfer-Encoding: chunked\r\n\r\n0\r\n\r\nG
```
前端按 CL 读 6 字节，后端按 chunked 在 `0\r\n\r\n` 处结束，剩下的 `G` 成为下一个请求前缀 → 毒 socket。
真实：#771666、#1063493、#648434（TE/CL 冲突批量偷令牌）。

### B. TE.CL（前端信 TE，后端信 CL）
```
POST / HTTP/1.1\r\nHost: t\r\nContent-Length: 4\r\nTransfer-Encoding: chunked\r\n\r\n5c\r\nGPOST /...\r\n0\r\n\r\n
```
前端按 chunked 读完，后端按 CL=4 只读到 `5c\r\n`，剩余成走私请求。

### C. 头畸形绕过前端 TE 检测（让前端"看不见"TE，后端却认）
前端用简单匹配找 `Transfer-Encoding: chunked`，用畸形写法骗过：
- 冒号前空格：`Transfer-Encoding : chunked`（#737140）
- Tab 分隔：`Transfer-Encoding:\tchunked`（#1063627、#1063493）
- 前导空格 / 行折叠：`\tTransfer-Encoding: chunked`
- 双 TE 头：`Transfer-Encoding: chunked\r\nTransfer-Encoding: x`
- CL 头冒号前空格：`Content-Length : 6`（#1238709）

### D. CR-only / LF-only 行分隔差异
一端把单个 `\r` 或 `\n` 当行结束，另一端不当：
- 头值里塞裸 `\r` 注入 TE（#2032842：Empty headers separated by CR）
- CR→连字符转换：`Content\rLength` 被某端转成 `Content-Length`（#922597）

### E. 无冒号 trailer 吞头（chunked trailer 解析分歧）
chunked 结束后的 trailer 段放一条**无冒号**的行，宽容解析器跳过它、把后续请求头吞进 trailer：
- Tomcat CVE-2023-45648（#2299692）；通用 desync 探测里必试。

### F. CRLF 注入进 header 名/值 → 走私 / 打内部服务
库不过滤 header 名里的 CRLF，可拼出完整二次请求打内网（Redis/SMTP）：
- Ruby `Net::HTTP` header 名 CRLF（#1718757）
- LDAP 密码字段 `%0D%0A` 注 Redis 命令（#1054282）
- `git://` 协议 CRLF 注 Redis → RCE（#441090）
- 响应头溢出触发响应拆分（#53843）

### G. Pause-based / 连接层 desync
利用客户端暂停、HTTP/2 降级、连接复用差异制造 desync：
- Apache pause-based（#1667974）。

## Detection Patterns（怎么判，而非猜）

- **时序差分（主）**：发一个"后端会挂起等更多字节"的 CL.TE 探测，若响应明显变慢（接近超时）而正常请求快 → 后端在等被走私走的字节 → 强 desync 信号。反之 TE.CL 探测让前端挂起。
- **socket 状态污染**：连续两个请求，第二个收到"非自己该收到的响应"或错乱状态码 → 毒化成功（仅授权时验证）。
- **前端指纹**：`Via` / `X-Cache` / `CF-RAY` / `Server: cloudflare|Akamai|Varnish` = 有前端层，走私面存在。
- **区分抖动**：每个变体重复≥3 次取中位延迟，和基线比，避免把网络抖动当 desync。

## Real Reports（复现索引）

| desync 家族 | 报告 | 要点 |
|---|---|---|
| 冒号前空格 | 737140 / 1238709 | `TE :`/`CL :` 骗前端 |
| Tab 分隔 | 1063627 / 1063493 | `TE:\tchunked` |
| CR-only | 2032842 / 922597 | 裸 CR / CR→连字符 |
| 无冒号 trailer | 2299692 | Tomcat 吞头 |
| CL.TE 偷令牌 | 771666 / 648434 | 毒 socket 批量偷 X-Access-Token |
| CRLF→内网 | 1718757 / 1054282 / 441090 | Redis/LDAP/git 协议 |
| 响应拆分 | 53843 / 79552 | 头溢出 / Set-Cookie 注入 |
| pause-desync | 1667974 | Apache |

hunt 阶段建议顺序：先 C（畸形 TE 最常见且低破坏）→ A/B 时序差分 → E 无冒号 trailer → 确认 desync 后再评估是否授权做 socket 毒化。
