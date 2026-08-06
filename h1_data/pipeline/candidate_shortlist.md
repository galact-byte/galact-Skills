# 第二轮 知识点候选清单（去重后）

来源：round2 判定 worth_skill=true（强稀缺核心），在一轮主类别内按知识点相似度合并。

原始通过 770 条 → 去重后 **660 个候选**。簇大小=该技术在数据集中反复出现的次数=优先级信号。


## 分类概览

| 类别 | 候选数 |
|---|---|
| 协议行为利用 | 163 |
| 框架行为利用 | 68 |
| 跨组件攻击链 | 68 |
| 认证绕过 | 52 |
| 授权绕过 | 49 |
| XSS | 45 |
| 业务逻辑 | 39 |
| 路径遍历 | 25 |
| SSRF | 24 |
| 命令注入 | 23 |
| 类型混淆 | 20 |
| 反序列化 | 16 |
| 竞争条件 | 13 |
| 原型污染 | 8 |
| 信息泄露 | 6 |
| 代码注入 | 5 |
| 配置错误 | 5 |
| 缓存投毒 | 4 |
| CSRF | 3 |
| SQL注入 | 3 |
| 子域名接管 | 3 |
| IDOR | 2 |
| 内存破坏 | 2 |
| 其他 | 2 |
| XXE | 2 |
| CRLF注入 | 1 |
| CSP绕过 | 1 |
| 开放重定向 | 1 |
| 沙箱逃逸 | 1 |
| CSS注入 | 1 |
| DLL 劫持 | 1 |
| HTML注入 | 1 |
| LLM | 1 |
| WAF绕过 | 1 |
| 资源消耗 | 1 |

## 协议行为利用 （163 个候选）

### [2299692] HTTP请求走私：无冒号trailer行解析差异  (★7次, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到任何HTTP解析器差异） / 高
- 同簇报告(7): 2299692, 1238709, 922597, 1524555, 1665156, 526880, 2001873
- 代表报告: https://hackerone.com/reports/2299692

### [1547048] curl 重定向敏感头泄露  (★5次, max_score 10)
- 频率/迁移/来源: 高频 / 高（适用于所有 HTTP 客户端重定向场景） / 高
- 同簇报告(5): 1547048, 1568175, 1551586, 1551591, 1543773
- 代表报告: https://hackerone.com/reports/1547048

### [771666] HTTP 请求走私（CL.TE）窃取会话令牌  (★5次, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到任何前后端分离的 HTTP 服务） / 高
- 同簇报告(5): 771666, 1063493, 1063627, 648434, 777651
- 代表报告: https://hackerone.com/reports/771666

### [1632921] DNS rebinding 绕过 Node.js 调试器 Host 校验  (★4次, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到调试器、内部服务访问控制） / 高
- 同簇报告(4): 1632921, 1574078, 663729, 1069487
- 代表报告: https://hackerone.com/reports/1632921

### [1718757] Ruby Net::HTTP 头 CRLF 注入导致请求走私  (★4次, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到其他 HTTP 库） / 高
- 同簇报告(4): 1718757, 1391549, 1820955, 146416
- 代表报告: https://hackerone.com/reports/1718757

### [719875] MySQL LOAD DATA LOCAL 特性导致客户端文件读取  (★3次, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他数据库协议、客户端文件读取场景） / 高
- 同簇报告(3): 719875, 171593, 156511
- 代表报告: https://hackerone.com/reports/719875

### [824753] URL 解码差异导致缓存投毒  (★3次, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到 CDN 和缓存系统） / 高
- 同簇报告(3): 824753, 108113, 255991
- 代表报告: https://hackerone.com/reports/824753

### [2493548] curl IPv4-mapped IPv6 地址解析差异导致 SSRF 黑名单绕过  (★2次, max_score 10)
- 频率/迁移/来源: 高频 / 高（SSRF 黑名单、WAF IP 过滤、内网访问控制均可迁移） / 高
- 同簇报告(2): 2493548, 704621
- 代表报告: https://hackerone.com/reports/2493548

### [26647] Django CSRF 保护绕过：通过 Google Analytics cookie 注入  (★2次, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他框架的 CSRF 防护） / 高
- 同簇报告(2): 26647, 14883
- 代表报告: https://hackerone.com/reports/26647

### [2032842] HTTP Request Smuggling via CR as header separator  (★2次, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到所有依赖 HTTP 解析器的场景，如代理、WAF、负载均衡） / 高
- 同簇报告(2): 2032842, 1501679
- 代表报告: https://hackerone.com/reports/2032842

### [1040166] curl FTP PASV 响应信任导致 SSRF 端口扫描  (★2次, max_score 10)
- 频率/迁移/来源: 高频 / 高（SSRF 防护、FTP 客户端安全配置、内网探测） / 高
- 同簇报告(2): 1040166, 1145454
- 代表报告: https://hackerone.com/reports/1040166

### [115857] ffmpeg 协议滥用导致 SSRF 和任意文件读取  (★2次, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用 ffmpeg 处理用户输入的应用） / 高
- 同簇报告(2): 115857, 487008
- 代表报告: https://hackerone.com/reports/115857

### [2212193] 域名大小写规范化绕过PSL检查  (★2次, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何域名校验场景，如CORS、Cookie域、URL解析） / 高
- 同簇报告(2): 2212193, 2274981
- 代表报告: https://hackerone.com/reports/2212193

### [1178562] IMAP STARTTLS 剥离攻击（库未检查响应）  (★2次, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他协议如 SMTP、POP3） / 高
- 同簇报告(2): 1178562, 144782
- 代表报告: https://hackerone.com/reports/1178562

### [1334111] curl协议降级绕过TLS要求  (★2次, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他协议客户端） / 高
- 同簇报告(2): 1334111, 1950627
- 代表报告: https://hackerone.com/reports/1334111

### [1730660] IDN字符绕过HSTS  (★2次, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他域名验证场景） / 高
- 同簇报告(2): 1730660, 1755083
- 代表报告: https://hackerone.com/reports/1730660

### [1892351] libcurl SFTP 路径 ~ 解析差异导致路径遍历  (★2次, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 URL 解析库和路径处理场景） / 高
- 同簇报告(2): 1892351, 1524692
- 代表报告: https://hackerone.com/reports/1892351

### [131052] OAuth redirect_uri 协议校验绕过导致 XSS  (★2次, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何重定向端点） / 高
- 同簇报告(2): 131052, 292783
- 代表报告: https://hackerone.com/reports/131052

### [2390009] undici跨域重定向未清除Proxy-Authorization头  (★2次, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到所有HTTP客户端） / 高
- 同簇报告(2): 2390009, 1086259
- 代表报告: https://hackerone.com/reports/2390009

### [824802] URN 请求绕过 ACL 检查  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（任何协议转换都可能绕过安全检查，可迁移到其他代理、网关） / 高
- 代表报告: https://hackerone.com/reports/824802

### [1054382] 客户端 SSRF：Burp Suite 自动解析 HTML 导致隐藏请求泄露 NetNTLM 哈希  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他客户端工具、HTML 解析场景） / 高
- 代表报告: https://hackerone.com/reports/1054382

### [441090] CRLF 注入与 SSRF：git:// 协议绕过防护并注入 Redis 实现 RCE  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他协议、SSRF 绕过场景） / 高
- 代表报告: https://hackerone.com/reports/441090

### [275269] Gem 签名伪造：tar 重复条目处理不一致  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何处理 tar 或类似格式的包管理器） / 高
- 代表报告: https://hackerone.com/reports/275269

### [1531958] ReDoS via regex without anchor in net/http  (单例, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到任何使用正则的输入处理） / 高
- 代表报告: https://hackerone.com/reports/1531958

### [78158] Flash Content-Type injection bypass  (单例, max_score 10)
- 频率/迁移/来源: 低频 / 高（可迁移到任何MIME类型解析） / 高
- 代表报告: https://hackerone.com/reports/78158

### [1613943] curl未过滤控制字符导致DoS  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何客户端输入校验） / 高
- 代表报告: https://hackerone.com/reports/1613943

### [843256] TURN 协议 peer 访问控制缺失导致 SSRF  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他中继协议如 STUN、ICE） / 高
- 代表报告: https://hackerone.com/reports/843256

### [806577] Set-Cookie 注入 via 分号未编码  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何涉及 Cookie 设置的场景，如会话固定、Cookie 轰炸） / 高
- 代表报告: https://hackerone.com/reports/806577

### [737140] CLTE 请求走私 + 绝对 URI 反射 cookie 实现批量 ATO  (单例, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到任何 HTTP 走私场景，且绝对 URI 处理是通用行为） / 高
- 代表报告: https://hackerone.com/reports/737140

### [1027873] 利用X-Accel-Redirect头进行内部重定向  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用NGINX反向代理的场景） / 高
- 代表报告: https://hackerone.com/reports/1027873

### [329645] LibreSSL和BoringSSL静默忽略证书主机名验证  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用这些库的应用） / 高
- 代表报告: https://hackerone.com/reports/329645

### [1180252] SILK 解码器循环中边界检查缺失导致栈溢出  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何音频/视频解码器或类似循环处理） / 高
- 代表报告: https://hackerone.com/reports/1180252

### [1583680] Undici ProxyAgent 未使用 CONNECT 隧道导致证书验证失效  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何 HTTP 客户端代理实现） / 高
- 代表报告: https://hackerone.com/reports/1583680

### [402671] TLS 实现中 padding 错误与 MAC 错误响应差异导致 oracle 解密  (单例, max_score 10)
- 频率/迁移/来源: 低频 / 高（可迁移到任何 TLS 实现） / 高
- 代表报告: https://hackerone.com/reports/402671

### [458842] 文件扩展名检查绕过（路径中间插入）  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到文件上传、下载场景） / 高
- 代表报告: https://hackerone.com/reports/458842

### [1630336] 利用obs-fold头部绕过Transfer-Encoding校验实现请求走私  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他协议解析差异） / 高
- 代表报告: https://hackerone.com/reports/1630336

### [1892780] libcurl FTP连接重用未考虑账户参数导致认证绕过  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他协议连接重用场景） / 高
- 代表报告: https://hackerone.com/reports/1892780

### [1566462] curl globbing 功能绕过 URL 过滤  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用 curl 的代理或工具） / 高
- 代表报告: https://hackerone.com/reports/1566462

### [1429694] Node.js 证书验证绕过：解析 OpenSSL 打印函数输出导致 SAN 注入  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他依赖 OpenSSL 打印输出的语言/框架，如 Python、Ruby 等） / 高
- 代表报告: https://hackerone.com/reports/1429694

### [824203] Squid 双重 URL 解码导致 ACL 绕过  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他代理服务器或 URL 处理组件） / 高
- 代表报告: https://hackerone.com/reports/824203

### [501] TLS 虚拟主机混淆导致跨域冒充  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（TLS 配置、虚拟主机、DNS 控制） / 高
- 代表报告: https://hackerone.com/reports/501

### [1170024] OCM 协议未认证端点导致权限提升  (单例, max_score 10)
- 频率/迁移/来源: 低频 / 高（联邦共享协议、未认证端点、权限提升） / 高
- 代表报告: https://hackerone.com/reports/1170024

### [304378] ACME TLS-SNI挑战在共享主机环境中的缺陷  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（证书验证、共享主机安全、ACME协议均可迁移） / 高
- 代表报告: https://hackerone.com/reports/304378

### [470520] Steam协议缓冲区溢出：unicode转换和ROP链绕过ASLR  (单例, max_score 10)
- 频率/迁移/来源: 低频 / 高（协议解析、缓冲区溢出、ROP链均可迁移） / 高
- 代表报告: https://hackerone.com/reports/470520

### [1565624] curl 连接复用忽略安全选项  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他连接复用机制） / 高
- 代表报告: https://hackerone.com/reports/1565624

### [407319] ActiveStorage签名URL参数未签名导致URL劫持  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他云存储服务的签名URL验证） / 高
- 代表报告: https://hackerone.com/reports/407319

### [1238470] Wi-Fi协议设计缺陷导致流量注入和劫持  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他无线协议，如蓝牙、Zigbee） / 高
- 代表报告: https://hackerone.com/reports/1238470

### [1542881] curl配置文件读取失败导致安全选项失效  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他使用curl或类似工具的场景） / 高
- 代表报告: https://hackerone.com/reports/1542881

### [1916285] 终端转义序列注入导致任意命令执行  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何输出到终端的CLI工具，如kubectl、git等） / 高
- 代表报告: https://hackerone.com/reports/1916285

### [895727] 编码cookie名称绕过安全前缀  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到所有cookie解析场景） / 高
- 代表报告: https://hackerone.com/reports/895727

### [79348] 协议处理器JavaScript注入  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到所有自定义协议处理器） / 高
- 代表报告: https://hackerone.com/reports/79348

### [731878] DKIM签名绕过通过From头解析差异  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到所有邮件服务） / 高
- 代表报告: https://hackerone.com/reports/731878

### [425314] API 签名重放与 payload 修改  (单例, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到任何使用签名认证的 API） / 高
- 代表报告: https://hackerone.com/reports/425314

### [622170] OpenSSL 默认配置路径劫持  (单例, max_score 10)
- 频率/迁移/来源: 低频 / 高（可迁移到任何使用默认配置路径的库） / 高
- 代表报告: https://hackerone.com/reports/622170

### [409943] Node.js HTTP 解析器对特殊字符处理不当导致请求拆分  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他语言/框架的 HTTP 解析器差异，如 Python、Ruby） / 高
- 代表报告: https://hackerone.com/reports/409943

### [53843] 响应头溢出导致 CRLF 注入  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他服务器行为差异） / 高
- 代表报告: https://hackerone.com/reports/53843

### [28500] iOS URL Scheme 在 iframe 中自动启动导致未授权操作  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 URL Scheme 或跨应用通信） / 高
- 代表报告: https://hackerone.com/reports/28500

### [1590102] 安全机制失败时静默降级导致认证绕过  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何安全机制降级场景，如TLS降级、OAuth降级） / 高
- 代表报告: https://hackerone.com/reports/1590102

### [302997] 空字符截断路径导致连接非预期socket  (单例, max_score 9)
- 频率/迁移/来源: 低频 / 高（可迁移到任何路径处理场景，如文件读写、socket连接） / 高
- 代表报告: https://hackerone.com/reports/302997

### [99435] 浏览器与服务器URL解析差异绕过OAuth重定向校验  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何URL校验场景，如SSRF、开放重定向） / 高
- 代表报告: https://hackerone.com/reports/99435

### [931197] 跨站 WebSocket 劫持（Origin 检查绕过）  (单例, max_score 9)
- 频率/迁移/来源: 高频 / 高（可迁移到任何依赖 Origin 校验的 WebSocket 或 CORS 场景） / 高
- 代表报告: https://hackerone.com/reports/931197

### [85624] 点击劫持绕过（嵌套 iframe 与 CSP2 兼容性）  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何依赖 frame-ancestors 或 X-Frame-Options 的点击劫持防护） / 高
- 代表报告: https://hackerone.com/reports/85624

### [126203] CBC cut-and-paste 攻击构造任意明文  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用 CBC 模式且未认证的加密场景） / 高
- 代表报告: https://hackerone.com/reports/126203

### [1178337] DNS 响应特殊字符注入  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何依赖 DNS 解析的应用） / 高
- 代表报告: https://hackerone.com/reports/1178337

### [816637] 有符号整数溢出绕过边界检查导致堆越界写  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他解码库） / 高
- 代表报告: https://hackerone.com/reports/816637

### [2148242] curl duphandle 隐式加载 'none' 文件导致 cookie 注入  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他库的隐式文件加载、默认文件名利用） / 高
- 代表报告: https://hackerone.com/reports/2148242

### [1226891] DNS托管区域删除后NS记录残留导致域名接管  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到DNS配置、云服务资源接管） / 高
- 代表报告: https://hackerone.com/reports/1226891

### [1204977] CGI::Cookie属性未过滤导致HTTP响应拆分  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他语言Cookie处理） / 高
- 代表报告: https://hackerone.com/reports/1204977

### [2187833] SOCKS5状态机缺陷导致堆溢出  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何SOCKS5代理实现） / 高
- 代表报告: https://hackerone.com/reports/2187833

### [824163] FTP列表解析中strtok与strstr分隔符假设差异导致信息泄露  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用类似解析逻辑的代理或服务） / 高
- 代表报告: https://hackerone.com/reports/824163

### [121863] HTTP URL解析缓冲区溢出覆盖函数指针  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他解析器） / 高
- 代表报告: https://hackerone.com/reports/121863

### [674540] mod_remoteip PROXY协议解析缺陷  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他PROXY协议实现） / 高
- 代表报告: https://hackerone.com/reports/674540

### [126522] 参数解析差异（分号分隔）绕过认证  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（参数解析不一致场景） / 高
- 代表报告: https://hackerone.com/reports/126522

### [156615] URI解析器空主机名宽容导致开放重定向  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（URI解析、开放重定向） / 高
- 代表报告: https://hackerone.com/reports/156615

### [1054282] LDAP 密码字段 CRLF 注入实现协议走私与内部服务交互  (单例, max_score 9)
- 频率/迁移/来源: 低频 / 高（可迁移到其他协议字段注入，如 SMTP、HTTP） / 高
- 代表报告: https://hackerone.com/reports/1054282

### [1675191] HTTP 请求走私（llhttp 解析器对不完整 CLRF 的宽松处理）  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他解析器差异） / 高
- 代表报告: https://hackerone.com/reports/1675191

### [258578] 浏览器拖放操作泄露内部对象  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到浏览器 UI 交互安全、拖放 API 审计） / 高
- 代表报告: https://hackerone.com/reports/258578

### [287835] Resolv::getaddresses 对特殊 IP 格式解析差异绕过 SSRF  (单例, max_score 9)
- 频率/迁移/来源: 高频 / 高（可迁移到 SSRF 防护、DNS 解析器差异） / 高
- 代表报告: https://hackerone.com/reports/287835

### [1526328] curl 连接复用时不检查 SASL 参数导致 OAUTH2 绕过  (单例, max_score 9)
- 频率/迁移/来源: 高频 / 高（可迁移到连接池安全、认证绕过） / 高
- 代表报告: https://hackerone.com/reports/1526328

### [490960] 路径分隔符注入绕过路径校验实现 PATH 劫持  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何路径校验场景，如配置文件、环境变量） / 高
- 代表报告: https://hackerone.com/reports/490960

### [1560324] curl cookie 覆盖规则缺陷导致会话固定  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 HTTP 客户端 cookie 处理） / 高
- 代表报告: https://hackerone.com/reports/1560324

### [854726] 共识规则依赖本地时钟导致时间侧信道  (单例, max_score 9)
- 频率/迁移/来源: 低频 / 高（可迁移到其他区块链或分布式系统） / 高
- 代表报告: https://hackerone.com/reports/854726

### [16910] CSP report-uri作为跨源信息泄露信道  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他浏览器安全机制） / 高
- 代表报告: https://hackerone.com/reports/16910

### [295740] 协议长度字段未校验导致堆内存泄露（heartbleed 式）  (单例, max_score 9)
- 频率/迁移/来源: 低频 / 高（可迁移到其他协议解析器审计） / 高
- 代表报告: https://hackerone.com/reports/295740

### [882923] jsonpath递归下降导致DoS  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用递归下降解析器的场景，如JSONPath、XPath、正则表达式） / 高
- 代表报告: https://hackerone.com/reports/882923

### [489102] 协议字段直接控制内存拷贝长度导致栈溢出（SEH覆盖）  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他协议解析器、网络服务的内存拷贝边界检查） / 高
- 代表报告: https://hackerone.com/reports/489102

### [493176] HTTP/2并发流响应顺序差异实现时序攻击  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他协议的多路复用特性） / 高
- 代表报告: https://hackerone.com/reports/493176

### [1667974] Pause-based desync in Apache HTTPD  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何HTTP服务器与浏览器解析差异） / 高
- 代表报告: https://hackerone.com/reports/1667974

### [726117] curl URL解析器fragment混淆导致路径绕过  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何URL解析器，如浏览器、代理） / 高
- 代表报告: https://hackerone.com/reports/726117

### [500] AES-GCM 模式下 MAC 上下文未初始化导致内存破坏  (单例, max_score 9)
- 频率/迁移/来源: 低频 / 高（可迁移到其他协议实现） / 高
- 代表报告: https://hackerone.com/reports/500

### [2384833] curl --proto -all 参数解析缺陷导致协议未禁用  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何黑名单模式下的默认允许问题） / 高
- 代表报告: https://hackerone.com/reports/2384833

### [2280391] 超长trailer header触发IOException导致请求走私  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（适用于所有基于Tomcat的代理架构，可迁移到其他服务器异常处理） / 高
- 代表报告: https://hackerone.com/reports/2280391

### [855276] git config URL注入实现SSRF  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（适用于任何将用户输入拼接到命令行参数的场景） / 高
- 代表报告: https://hackerone.com/reports/855276

### [1464396] Cookie前缀欺骗通过URL编码  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（适用于任何解析cookie的框架，可迁移到其他协议解析） / 高
- 代表报告: https://hackerone.com/reports/1464396

### [453513] keep-alive连接绕过headersTimeout  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（适用于任何基于超时机制的服务器） / 高
- 代表报告: https://hackerone.com/reports/453513

### [2298922] TLS 会话重用绕过 OCSP 验证  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（适用于所有 TLS 实现） / 高
- 代表报告: https://hackerone.com/reports/2298922

### [423467] WebSocket消息类型混淆覆盖公钥  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用WebSocket或类似消息协议的加密通信场景） / 高
- 代表报告: https://hackerone.com/reports/423467

### [227344] chunked 编码整数符号错误  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（协议解析、内存破坏） / 高
- 代表报告: https://hackerone.com/reports/227344

### [1710652] 无效八进制 IP 解析差异导致 DNS rebinding 绕过  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到所有依赖 IP 解析的防护机制） / 高
- 代表报告: https://hackerone.com/reports/1710652

### [218088] DNS SRV 记录验证缺陷导致请求劫持  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到所有依赖 DNS 发现服务的客户端） / 高
- 代表报告: https://hackerone.com/reports/218088

### [790634] Git分支名与哈希解析优先级差异导致供应链投毒  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何引用哈希的依赖管理场景） / 高
- 代表报告: https://hackerone.com/reports/790634

### [295339] 邮件客户端RFC2047编码解析差异绕过DMARC  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何邮件客户端和MTA） / 高
- 代表报告: https://hackerone.com/reports/295339

### [742588] 加密模式降级与密钥流重用破坏完整性  (单例, max_score 9)
- 频率/迁移/来源: 低频 / 高（可迁移到任何使用CFB/CTR模式的加密系统） / 高
- 代表报告: https://hackerone.com/reports/742588

### [1334763] STARTTLS协议注入绕过加密  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用STARTTLS的协议） / 高
- 代表报告: https://hackerone.com/reports/1334763

### [1553301] curl cookie 尾点绕过 TLD 限制  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 HTTP 客户端、浏览器、WAF 的域名校验） / 高
- 代表报告: https://hackerone.com/reports/1553301

### [1267677] 双 Content-Type 头绕过内容类型检查  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何依赖 Content-Type 校验的代理、WAF、上传功能） / 高
- 代表报告: https://hackerone.com/reports/1267677

### [1223565] libcurl 连接复用检查缺陷导致 TLS 中间人攻击  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用 libcurl 的客户端，如各种编程语言的 HTTP 库） / 高
- 代表报告: https://hackerone.com/reports/1223565

### [919175] HTTP 请求走私配合 X-Forwarded-Host 实现缓存投毒  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用缓存和代理的场景） / 高
- 代表报告: https://hackerone.com/reports/919175

### [893922] IP-in-IP协议默认路由任意流量  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他隧道协议，如GRE） / 高
- 代表报告: https://hackerone.com/reports/893922

### [722327] 编码换行符绕过Nginx配置触发php-fpm下溢  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他编码绕过场景） / 高
- 代表报告: https://hackerone.com/reports/722327

### [1651429] Blockchain transaction parsing bypass leading to silent token transfer  (单例, max_score 9)
- 频率/迁移/来源: 低频 / 高（可迁移到其他区块链钱包和智能合约交互） / 高
- 代表报告: https://hackerone.com/reports/1651429

### [391611] 利用随机数三角分布特性构造无限循环DoS  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他使用随机数选择且存在边界条件的场景，如抽奖、随机分配等） / 高
- 代表报告: https://hackerone.com/reports/391611

### [97292] HTTP头注入绕过域限制设置cookie  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他协议头注入场景，如邮件头、HTTP响应头） / 高
- 代表报告: https://hackerone.com/reports/97292

### [396954] RLP 解析器未检查数据末尾导致数据注入  (单例, max_score 9)
- 频率/迁移/来源: 低频 / 高（可迁移到任何解析器未检查数据末尾的场景） / 高
- 代表报告: https://hackerone.com/reports/396954

### [531032] 硬编码密钥在WebRTC/DTLS中的滥用导致SRTP流劫持  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他使用DTLS的通信协议，如VoIP、IoT设备） / 高
- 代表报告: https://hackerone.com/reports/531032

### [1154003] IPv6子网绕过速率限制  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何基于IP的速率限制、WAF规则） / 高
- 代表报告: https://hackerone.com/reports/1154003

### [317931] URL 解析器对 @ 分隔符处理差异绕过同形字攻击防护  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何 URL 解析和域名校验场景，如 SSRF、开放重定向） / 高
- 代表报告: https://hackerone.com/reports/317931

### [1019891] Windows命名管道中间人攻击  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他IPC机制如Unix域套接字） / 高
- 代表报告: https://hackerone.com/reports/1019891

### [723175] 跨站事件泄漏（xsleaks）实现去匿名化  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到信息泄露、用户状态检测） / 高
- 代表报告: https://hackerone.com/reports/723175

### [1213181] curl Metalink下载凭据泄露  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他下载工具或协议） / 高
- 代表报告: https://hackerone.com/reports/1213181

### [363680] 非恒定时间比较导致时序侧信道  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何密码学实现） / 高
- 代表报告: https://hackerone.com/reports/363680

### [678487] Node.js url.parse() Unicode主机名欺骗  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到SSRF和开放重定向） / 高
- 代表报告: https://hackerone.com/reports/678487

### [589739] HTTP/2 协议特性导致的多种 DoS 攻击（窗口、优先级、帧序列）  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到 HTTP/3 及类似协议） / 高
- 代表报告: https://hackerone.com/reports/589739

### [2402853] HTTP/2 PUSH_PROMISE 畸形帧触发错误路径导致内存泄漏  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他协议帧处理错误路径） / 高
- 代表报告: https://hackerone.com/reports/2402853

### [1176461] TELNET 子选项解析中 sscanf 返回值检查不严导致未初始化内存泄露  (单例, max_score 8)
- 频率/迁移/来源: 低频 / 高（可迁移到其他使用 sscanf 的协议解析） / 高
- 代表报告: https://hackerone.com/reports/1176461

### [281336] 利用 String#oct 解析 tar 头字段时接受负数导致无限循环  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他使用类似宽松解析函数的语言或库，如 Python 的 int() 也接受负数） / 高
- 代表报告: https://hackerone.com/reports/281336

### [276105] 利用 IE 内容嗅探绕过 nosniff 头实现 XSS  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他浏览器内容嗅探绕过场景） / 高
- 代表报告: https://hackerone.com/reports/276105

### [416040] 浏览器协议权限模型缺陷：url: 前缀嵌套绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（浏览器权限模型、协议处理、外部应用启动） / 高
- 代表报告: https://hackerone.com/reports/416040

### [507525] 代理服务器滥用导致 DoS（慢速响应、分块传输、CDN 缓存绕过）  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何代理服务器、CDN、负载均衡器） / 高
- 代表报告: https://hackerone.com/reports/507525

### [5928] 利用应用层压缩（zlib）构造解压炸弹导致DoS  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何支持压缩的协议，如HTTP、WebSocket、SSH） / 高
- 代表报告: https://hackerone.com/reports/5928

### [108082] 利用CFB模式可延展性篡改密文，结合已知明文注入恶意代码  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用非认证加密模式存储数据的场景） / 高
- 代表报告: https://hackerone.com/reports/108082

### [358005] data: URI iframe 继承父 origin 绕过 SOP  (单例, max_score 8)
- 频率/迁移/来源: 低频 / 高（适用于浏览器安全） / 高
- 代表报告: https://hackerone.com/reports/358005

### [268984] 同形异义词攻击绕过 URL 验证  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何 URL 验证场景） / 高
- 代表报告: https://hackerone.com/reports/268984

### [26962] OAuth规范错误处理不明确导致开放重定向  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（影响所有OAuth提供商） / 高
- 代表报告: https://hackerone.com/reports/26962

### [563268] Unicode 双向算法绕过域名显示  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到 URL 显示、邮件客户端、聊天软件等） / 高
- 代表报告: https://hackerone.com/reports/563268

### [2352957] HTTP 重定向时敏感头未清除  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何 HTTP 客户端） / 高
- 代表报告: https://hackerone.com/reports/2352957

### [369218] 浏览器自定义协议处理绕过安全限制  (单例, max_score 8)
- 频率/迁移/来源: 低频 / 高（可迁移到其他自定义协议） / 高
- 代表报告: https://hackerone.com/reports/369218

### [145392] 利用RFC1945头折叠和IE浏览器差异实现响应头注入  (单例, max_score 8)
- 频率/迁移/来源: 低频 / 高（可迁移到其他协议和浏览器） / 高
- 代表报告: https://hackerone.com/reports/145392

### [1455411] OpenSSL X509_verify_cert()内部错误处理不当  (单例, max_score 8)
- 频率/迁移/来源: 低频 / 高（可迁移到TLS/SSL实现安全） / 高
- 代表报告: https://hackerone.com/reports/1455411

### [1096907] Kubernetes Validating Webhook 资源耗尽导致 DoS  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 webhook 场景，如准入控制、API 网关） / 高
- 代表报告: https://hackerone.com/reports/1096907

### [890747] EMV 协议 DDA 模式下 CVM 列表篡改绕过 PIN 验证  (单例, max_score 8)
- 频率/迁移/来源: 低频 / 高（可迁移到其他支付协议或安全协议设计） / 高
- 代表报告: https://hackerone.com/reports/890747

### [1874716] 并行传输导致 HSTS 缓存覆盖绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何依赖持久化状态的安全机制） / 高
- 代表报告: https://hackerone.com/reports/1874716

### [1086108] DNS 尾随点绕过域名所有权验证  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到所有域名验证、SSRF 防护、URL 解析等场景） / 高
- 代表报告: https://hackerone.com/reports/1086108

### [52042] UTF-8 编码绕过 CRLF 过滤  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到所有输入过滤绕过，尤其是编码处理） / 高
- 代表报告: https://hackerone.com/reports/52042

### [462442] 端口抢占冒充 RPC 服务器  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何基于 TCP 的 RPC 或服务） / 高
- 代表报告: https://hackerone.com/reports/462442

### [278095] URL 空白字符绕过主机名检测  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到 URL 解析、SSRF、重定向等场景） / 高
- 代表报告: https://hackerone.com/reports/278095

### [688048] curl IPv6字面量解析缺陷导致连接意外主机  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他URL解析库，如Python的urllib、Java的URI） / 高
- 代表报告: https://hackerone.com/reports/688048

### [187305] strncmp零长度比较导致无限循环  (单例, max_score 8)
- 频率/迁移/来源: 低频 / 高（可迁移到所有使用strncmp的解析器） / 高
- 代表报告: https://hackerone.com/reports/187305

### [541502] 代理 CONNECT 响应非 200 时未 TLS 升级导致明文传输  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到所有代理客户端） / 高
- 代表报告: https://hackerone.com/reports/541502

### [430463] macOS quarantine 属性缺失导致 Gatekeeper 绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到所有 macOS 下载场景） / 高
- 代表报告: https://hackerone.com/reports/430463

### [460928] 换行符绕过路径规范化导致 S3 桶信息泄露  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到所有 URL 解析和云存储） / 高
- 代表报告: https://hackerone.com/reports/460928

### [378805] ftp 协议绕过 chrome-extension 导航限制  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到所有浏览器扩展导航限制） / 高
- 代表报告: https://hackerone.com/reports/378805

### [1002188] 重复 TE 头导致 HTTP 请求走私  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到所有 HTTP 解析不一致场景） / 高
- 代表报告: https://hackerone.com/reports/1002188

### [639473] PGP 密钥服务器短 ID 碰撞与投毒  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他信任模型） / 高
- 代表报告: https://hackerone.com/reports/639473

### [322935] Off-by-one漏洞利用链：从内存破坏到预认证RCE  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他邮件服务器或网络服务的内存破坏利用） / 高
- 代表报告: https://hackerone.com/reports/322935

### [302651] 重定向跟随导致凭据泄露  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何自动跟随重定向的客户端） / 高
- 代表报告: https://hackerone.com/reports/302651

### [2429894] libuv域名解析漏洞导致SSRF  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到其他使用libuv或类似库的运行时） / 高
- 代表报告: https://hackerone.com/reports/2429894

### [2243710] 跨域重定向时 Cookie 未清除（undici-fetch）  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 HTTP 客户端库） / 高
- 代表报告: https://hackerone.com/reports/2243710

### [39658] 反射文件下载（Reflected File Download）  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何反射型漏洞场景，将反射内容伪装成可执行文件） / 高
- 代表报告: https://hackerone.com/reports/39658

### [213437] JWE Invalid Curve 攻击  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用 ECC 的加密协议） / 高
- 代表报告: https://hackerone.com/reports/213437

### [1721098] curl .netrc 解析器对空格字符假设导致的越界读写  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他解析器对输入格式假设的缺陷，如配置文件解析、协议头解析） / 高
- 代表报告: https://hackerone.com/reports/1721098

### [384569] Unicode RTL 覆盖字符绕过可信链接警告  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何依赖 URL 显示的防御机制，如邮件过滤、聊天链接预览） / 高
- 代表报告: https://hackerone.com/reports/384569

### [1102764] URL 规范化缺失绕过 Slack Blocked Previews  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何依赖 URL 匹配的防御机制，如 SSRF 黑名单、WAF 规则） / 高
- 代表报告: https://hackerone.com/reports/1102764


## 框架行为利用 （68 个候选）

### [1962701] Node.js inspector 模块绕过权限模型  (★4次, max_score 10)
- 频率/迁移/来源: 低频 / 高（可迁移到其他调试器或运行时） / 高
- 同簇报告(4): 1962701, 1877919, 2188126, 1961655
- 代表报告: https://hackerone.com/reports/1962701

### [2225660] Node.js权限模型可被覆盖path.resolve绕过  (★3次, max_score 9)
- 频率/迁移/来源: 中频 / 高（Node.js安全、权限模型） / 高
- 同簇报告(3): 2225660, 1966492, 2051224
- 代表报告: https://hackerone.com/reports/2225660

### [1747642] Node.js权限策略绕过 via process.mainModule  (★3次, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何模块加载限制绕过） / 高
- 同簇报告(3): 1747642, 2051257, 2120719
- 代表报告: https://hackerone.com/reports/1747642

### [499030] postMessage origin 检查使用前缀匹配导致 XSS  (★2次, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到任何 postMessage 通信） / 高
- 同簇报告(2): 499030, 691977
- 代表报告: https://hackerone.com/reports/499030

### [470547] 通过原型污染拦截原生方法劫持浏览器扩展脚本  (★2次, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何依赖原生方法的浏览器扩展或Web应用） / 高
- 同簇报告(2): 470547, 187542
- 代表报告: https://hackerone.com/reports/470547

### [178152] JSON.parse 错误消息泄露文件内容  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（错误消息泄露可迁移到其他解析器或日志） / 高
- 代表报告: https://hackerone.com/reports/178152

### [730239] yarn install 任意文件写入：符号链接和 tar transform  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他包管理器或解压工具） / 高
- 代表报告: https://hackerone.com/reports/730239

### [861744] 原型污染结合 sourceURL 导致 RCE（Kibana）  (单例, max_score 10)
- 频率/迁移/来源: 低频 / 高（可迁移到其他 Node.js 应用） / 高
- 代表报告: https://hackerone.com/reports/861744

### [236552] openssl_verify 返回值弱类型比较绕过  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他弱类型语言） / 高
- 代表报告: https://hackerone.com/reports/236552

### [800231] GraphQL 到 REST 参数注入（ActiveResource 未编码）  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 ORM 或 API 网关） / 高
- 代表报告: https://hackerone.com/reports/800231

### [850447] Rack 解析差异绕过 workhorse 签名  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他框架的解析差异） / 高
- 代表报告: https://hackerone.com/reports/850447

### [2208860] Node.js policy 完整性检查绕过（篡改内部绑定）  (单例, max_score 10)
- 频率/迁移/来源: 低频 / 高（Node.js 安全机制绕过、原型链污染、完整性校验） / 高
- 代表报告: https://hackerone.com/reports/2208860

### [1073202] LD_LIBRARY_PATH空条目导致任意库加载  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他使用LD_LIBRARY_PATH的场景） / 高
- 代表报告: https://hackerone.com/reports/1073202

### [1955370] Rails redirect_to控制字符导致XSS  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他框架的类似行为） / 高
- 代表报告: https://hackerone.com/reports/1955370

### [1728174] ingress-nginx configuration-snippet 注入 Lua 代码绕过黑名单  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他支持 Lua 的 Web 服务器配置注入） / 高
- 代表报告: https://hackerone.com/reports/1728174

### [1154542] ExifTool 基于内容识别文件类型绕过扩展名白名单导致 RCE  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何基于内容识别文件类型的解析器） / 高
- 代表报告: https://hackerone.com/reports/1154542

### [1327196] CSP 仅对 HTML 生效，对 image/svg+xml 不生效导致 XSS  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他框架的 CSP 实现，如 Django、Express） / 高
- 代表报告: https://hackerone.com/reports/1327196

### [2138080] Electron contextBridge序列化异常绕过上下文隔离  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用contextBridge的Electron应用） / 高
- 代表报告: https://hackerone.com/reports/2138080

### [302338] Ruby Dir类NULL字符截断路径绕过  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他语言或框架的路径处理） / 高
- 代表报告: https://hackerone.com/reports/302338

### [44513] IP解析差异绕过（IPv6变体）  (单例, max_score 9)
- 频率/迁移/来源: 高频 / 高（可迁移到任何IP白名单校验） / 高
- 代表报告: https://hackerone.com/reports/44513

### [209949] strdup/memccpy NULL字节截断导致堆内存泄露  (单例, max_score 9)
- 频率/迁移/来源: 低频 / 高（C/C++字符串处理） / 高
- 代表报告: https://hackerone.com/reports/209949

### [2140] Flash local-with-fileaccess 沙箱绕过  (单例, max_score 9)
- 频率/迁移/来源: 低频 / 高（可迁移到沙箱绕过、浏览器插件安全） / 高
- 代表报告: https://hackerone.com/reports/2140

### [946728] Rails 保留参数过滤不完整导致开放重定向和 XSS  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他框架的保留参数过滤、URL 生成安全） / 高
- 代表报告: https://hackerone.com/reports/946728

### [170548] 加密库 API 设计缺陷导致 IV 重用  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他加密库的 API 使用检查） / 高
- 代表报告: https://hackerone.com/reports/170548

### [409395] 环境变量展开绕过 YAML 校验实现路径遍历  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到 CI/CD 配置校验、变量展开场景） / 高
- 代表报告: https://hackerone.com/reports/409395

### [1966499] Node.js 权限系统未覆盖文件监视  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他运行时权限系统审计） / 高
- 代表报告: https://hackerone.com/reports/1966499

### [784186] N-API bufsize=0整数下溢导致内存破坏  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何API中类似边界条件处理） / 高
- 代表报告: https://hackerone.com/reports/784186

### [183425] Ruby alias_method 导致 C 扩展类型混淆  (单例, max_score 9)
- 频率/迁移/来源: 低频 / 高（可迁移到其他语言元编程与原生代码交互场景） / 高
- 代表报告: https://hackerone.com/reports/183425

### [1575014] 路径规范化差异：Node.js SDK将`.`规范化为列表接口  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用路径规范化的框架和API设计） / 高
- 代表报告: https://hackerone.com/reports/1575014

### [1025575] Fastify 版本路由默认行为导致缓存投毒  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（适用于所有版本路由框架） / 高
- 代表报告: https://hackerone.com/reports/1025575

### [217745] window.open javascript: URL 导致 XSS  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到所有浏览器窗口交互） / 高
- 代表报告: https://hackerone.com/reports/217745

### [106548] PHP错误处理中格式字符串漏洞  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他语言或框架的错误处理） / 高
- 代表报告: https://hackerone.com/reports/106548

### [1620702] Ingress-nginx 配置注入 + 文件写入 + include 实现 RCE  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他配置注入场景，如 Apache、Envoy） / 高
- 代表报告: https://hackerone.com/reports/1620702

### [843171] Electron 框架原型污染绕过链接验证实现 RCE  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 Electron 应用） / 高
- 代表报告: https://hackerone.com/reports/843171

### [1865991] Rails open redirect bypass via URL parsing differences  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他框架的URL验证绕过，如白名单校验） / 高
- 代表报告: https://hackerone.com/reports/1865991

### [1082847] Partial schema 宽松性导致配置注入  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用schema验证的框架，如TypeScript、JSON Schema） / 高
- 代表报告: https://hackerone.com/reports/1082847

### [1647287] Electron框架安全边界绕过（context isolation禁用）  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他基于Chromium的框架） / 高
- 代表报告: https://hackerone.com/reports/1647287

### [292797] Rails ActionController::Parameters的each方法返回不安全哈希  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他框架的参数处理） / 高
- 代表报告: https://hackerone.com/reports/292797

### [2271054] BigDecimal#sqrt循环次数计算错误导致DoS  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他数值计算库的类似循环逻辑） / 高
- 代表报告: https://hackerone.com/reports/2271054

### [1805899] HTML Sanitizer 嵌套标签绕过（svg+style）  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他HTML解析器、XSS过滤绕过） / 高
- 代表报告: https://hackerone.com/reports/1805899

### [189878] Rails data-remote表单CSRF令牌泄露  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到CSRF防护、框架行为） / 高
- 代表报告: https://hackerone.com/reports/189878

### [1805893] 不完整修复导致XSS绕过（CVE-2022-23520）  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何安全补丁审计） / 高
- 代表报告: https://hackerone.com/reports/1805893

### [1095612] Kubernetes 验证准入 webhook 的 oldObject 字段未正确传递导致绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 webhook 或 API 对象传递场景） / 高
- 代表报告: https://hackerone.com/reports/1095612

### [2408074] undici 跨域重定向未清除 Proxy-Authorization 头  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何 HTTP 客户端，检查重定向时敏感头清理） / 高
- 代表报告: https://hackerone.com/reports/2408074

### [1047447] 正则未锚定导致Host头注入  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何基于正则的输入校验） / 高
- 代表报告: https://hackerone.com/reports/1047447

### [1141623] V8引擎对非法八进制字面量的宽容处理导致SSRF/LFI  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（影响所有依赖V8的Node.js应用） / 高
- 代表报告: https://hackerone.com/reports/1141623

### [1715536] JavaScript 原型链污染导致框架崩溃  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用 in 操作符检查属性的框架） / 高
- 代表报告: https://hackerone.com/reports/1715536

### [470637] macOS quarantine 属性缺失导致 Gatekeeper 绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他下载场景，如浏览器、邮件客户端） / 高
- 代表报告: https://hackerone.com/reports/470637

### [629879] Node.js 模块搜索路径滥用导致代码执行  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他语言或框架的模块解析机制） / 高
- 代表报告: https://hackerone.com/reports/629879

### [180977] mruby 异常处理中 to_s 重写导致 SIGABRT  (单例, max_score 8)
- 频率/迁移/来源: 低频 / 高（可迁移到其他语言运行时或沙箱逃逸） / 高
- 代表报告: https://hackerone.com/reports/180977

### [949513] Active Storage Proxying 允许 inline 导致 XSS  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他文件服务框架） / 高
- 代表报告: https://hackerone.com/reports/949513

### [1884159] Node.js 解析畸形 X509 证书导致崩溃  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他解析器或框架） / 高
- 代表报告: https://hackerone.com/reports/1884159

### [536954] 解析器与消费者对字符串视图不一致（c_str vs getStringView）导致绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用C++字符串视图的解析器，如Nginx、Apache） / 高
- 代表报告: https://hackerone.com/reports/536954

### [789579] AWS SDK预签名URL未签名content-length导致上传大小限制绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他云服务SDK，如Azure、GCP） / 高
- 代表报告: https://hackerone.com/reports/789579

### [532667] 通过控制schema属性名注入JavaScript代码实现RCE  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他代码生成库，如Handlebars、EJS） / 高
- 代表报告: https://hackerone.com/reports/532667

### [1115139] HTML过滤器绕过（<svg><style><h1/>前缀）导致SSRF  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到所有HTML过滤场景） / 高
- 代表报告: https://hackerone.com/reports/1115139

### [1695596] Node.js 在 MacOS 上读取硬编码路径的 openssl.cnf  (单例, max_score 8)
- 频率/迁移/来源: 低频 / 高（可迁移到其他框架的硬编码路径问题） / 高
- 代表报告: https://hackerone.com/reports/1695596

### [633266] macOS DYLD_INSERT_LIBRARIES 注入绕过应用完整性  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他操作系统动态链接器） / 高
- 代表报告: https://hackerone.com/reports/633266

### [49935] rails-ujs和jQuery的URL解析差异导致CSRF令牌泄露  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何依赖前端框架的CSRF防护，如Angular、React等） / 高
- 代表报告: https://hackerone.com/reports/49935

### [1668815] 利用window.caches绕过隐私保护  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何基于存储的追踪机制，如IndexedDB、Cache API等） / 高
- 代表报告: https://hackerone.com/reports/1668815

### [1819668] RSS源链接打开chrome: URL绕过SOP  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他浏览器或RSS阅读器） / 高
- 代表报告: https://hackerone.com/reports/1819668

### [1559262] Rails数组参数解析导致批量token验证绕过速率限制  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他框架的数组参数处理，如PHP、Node.js） / 高
- 代表报告: https://hackerone.com/reports/1559262

### [474262] 模板字符串未转义导致 XSS  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他模板引擎或框架的类似转义缺陷） / 高
- 代表报告: https://hackerone.com/reports/474262

### [1278254] Node.js TLS 模块将 undefined 视为 false 禁用证书验证  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他语言/框架的布尔值处理） / 高
- 代表报告: https://hackerone.com/reports/1278254

### [2038484] OpenSSL 惰性生成导致 DiffieHellman 密钥重用  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到所有使用 OpenSSL 的密码学操作） / 高
- 代表报告: https://hackerone.com/reports/2038484

### [903521] Fastify 默认 allErrors:true 导致 DoS  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到所有使用 AJV 校验的框架） / 高
- 代表报告: https://hackerone.com/reports/903521

### [222020] 命令行工具参数注入（--debugger）导致任意代码执行  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他命令行工具，如git、svn，参数注入导致代码执行） / 高
- 代表报告: https://hackerone.com/reports/222020

### [771596] Node.js遗留API url.parse()与WHATWG URL解析差异导致CRLF注入绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他语言或框架中遗留API与标准API的差异） / 高
- 代表报告: https://hackerone.com/reports/771596


## 跨组件攻击链 （68 个候选）

### [415222] LFI到PHP对象注入再到XXE和pickle反序列化  (★3次, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何多组件攻击链） / 高
- 同簇报告(3): 415222, 416004, 415501
- 代表报告: https://hackerone.com/reports/415222

### [1142918] Android Intent 返回任意 URI 导致私有文件泄露  (★3次, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 Android 组件间通信场景） / 高
- 同簇报告(3): 1142918, 482998, 1454002
- 代表报告: https://hackerone.com/reports/1142918

### [1455987] 导出Activity导致WebView通用XSS  (★3次, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到所有Android应用） / 高
- 同簇报告(3): 1455987, 328486, 532836
- 代表报告: https://hackerone.com/reports/1455987

### [781253] 多环节组合攻击链：邮箱字符剥离、CSP绕过、IDOR、SSRF、Chrome调试端口  (★2次, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到类似多环节渗透） / 高
- 同簇报告(2): 781253, 780285
- 代表报告: https://hackerone.com/reports/781253

### [276031] Electron preload脚本作用域缺陷导致RCE  (★2次, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何基于Electron的桌面应用，以及类似preload脚本场景） / 高
- 同簇报告(2): 276031, 943725
- 代表报告: https://hackerone.com/reports/276031

### [1069171] DNS rebinding 绕过 SSRF 防护  (★2次, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到所有 SSRF 防护） / 高
- 同簇报告(2): 1069171, 1069189
- 代表报告: https://hackerone.com/reports/1069171

### [534450] 账户接管：cookie 操作端点与 XSS 结合绕过 HttpOnly 和 CORS  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他认证绕过、会话管理场景） / 高
- 代表报告: https://hackerone.com/reports/534450

### [966494] LPE via XPC service version validation bypass  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何客户端-服务端验证） / 高
- 代表报告: https://hackerone.com/reports/966494

### [694181] 容器内符号链接替换导致宿主机任意文件读取  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何容器文件复制、备份、日志处理场景） / 高
- 代表报告: https://hackerone.com/reports/694181

### [1842829] kOps 配置错误导致集群接管  (单例, max_score 10)
- 频率/迁移/来源: 低频 / 高（可迁移到其他云平台和集群管理工具） / 高
- 代表报告: https://hackerone.com/reports/1842829

### [403602] AppCache FALLBACK 与 Cookie 轰炸结合劫持附件  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用 AppCache 或 Service Worker 的缓存机制） / 高
- 代表报告: https://hackerone.com/reports/403602

### [1458236] SameSite=Lax cookie 在跨站请求中仍可发送，结合 SSRF 实现 CSRF  (单例, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到任何使用 SameSite=Lax 的 Web 应用） / 高
- 代表报告: https://hackerone.com/reports/1458236

### [1160407] x-http-method-override 头与缓存键不一致导致缓存投毒 DoS  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何 CDN 或缓存层） / 高
- 代表报告: https://hackerone.com/reports/1160407

### [399166] 未认领云存储桶劫持导致供应链攻击  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到 Azure Blob、GCP Storage 等） / 高
- 代表报告: https://hackerone.com/reports/399166

### [676581] 未认证 gRPC 端点导致跨组件授权绕过  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 API 集成场景） / 高
- 代表报告: https://hackerone.com/reports/676581

### [1066914] 多种绕过技术组合（intval 科学计数法、str_replace 递归、DNS rebinding、二次注入）  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到各种输入验证场景） / 高
- 代表报告: https://hackerone.com/reports/1066914

### [265943] SSO token 窃取链（CSRF+重定向+SVG XSS）  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到 OAuth、SSO 等 token 传递场景） / 高
- 代表报告: https://hackerone.com/reports/265943

### [1066206] PHP 类型混淆（is_numeric 与 intval 差异）和 DNS rebinding 组合利用  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 PHP 应用和 DNS rebinding 场景） / 高
- 代表报告: https://hackerone.com/reports/1066206

### [1442118] 容器逃逸：利用 cgroup release_agent  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他容器运行时） / 高
- 代表报告: https://hackerone.com/reports/1442118

### [1547877] JDBC 上传文件 + SSRF 到 Jolokia 实现 RCE  (单例, max_score 10)
- 频率/迁移/来源: 低频 / 高（JDBC 驱动滥用、SSRF 到内部服务、JMX 利用） / 高
- 代表报告: https://hackerone.com/reports/1547877

### [329957] 利用图片加载和cookie认证实现跨站追踪  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（隐私追踪、CSRF、资源认证均可迁移） / 高
- 代表报告: https://hackerone.com/reports/329957

### [1353103] CSRF 与路径遍历结合实现任意文件删除  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何依赖浏览器路径解析的 Web 应用） / 高
- 代表报告: https://hackerone.com/reports/1353103

### [299473] Webhook 注入 Redis 命令实现 RCE  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 SSRF 到 RCE 场景） / 高
- 代表报告: https://hackerone.com/reports/299473

### [894949] 多漏洞链组合利用（CTF 式）  (单例, max_score 10)
- 频率/迁移/来源: 低频 / 高（可迁移到复杂攻击链设计） / 高
- 代表报告: https://hackerone.com/reports/894949

### [1065885] PHP 弱类型与 DNS 重绑定绕过  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他弱类型语言和网络绕过） / 高
- 代表报告: https://hackerone.com/reports/1065885

### [416123] PHP反序列化触发XXE读取文件并泄露API令牌  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他语言的反序列化漏洞利用，如Java、Python） / 高
- 代表报告: https://hackerone.com/reports/416123

### [783877] Electron应用中HTML注入结合CSP绕过实现RCE  (单例, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到其他桌面应用框架，如Tauri、NW.js） / 高
- 代表报告: https://hackerone.com/reports/783877

### [1436558] WebView JS桥接和字符串拼接导致UXSS  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他WebView应用，如Android、iOS） / 高
- 代表报告: https://hackerone.com/reports/1436558

### [781281] 多漏洞组合攻击链：从账户接管到内网渗透  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到类似业务逻辑漏洞组合场景） / 高
- 代表报告: https://hackerone.com/reports/781281

### [1249583] ingress-nginx配置片段注入导致集群提权  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他Kubernetes组件或类似配置注入场景） / 高
- 代表报告: https://hackerone.com/reports/1249583

### [777241] 多漏洞链组合实现敏感信息泄露  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何多组件系统） / 高
- 代表报告: https://hackerone.com/reports/777241

### [534794] 导入功能路径遍历覆盖其他用户文件  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何具有导入/导出功能的应用） / 高
- 代表报告: https://hackerone.com/reports/534794

### [1073780] ESI 注入与 XSS 链式利用窃取 HttpOnly Cookie  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用 ESI 的应用） / 高
- 代表报告: https://hackerone.com/reports/1073780

### [1089914] HTML video/audio 标签 fallback 行为实现 XS-Leak  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 HTML 标签的 fallback 行为） / 高
- 代表报告: https://hackerone.com/reports/1089914

### [430854] 浏览器扩展 UI 注入导致信息泄露  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他浏览器扩展或插件） / 高
- 代表报告: https://hackerone.com/reports/430854

### [6017] OAuth redirect_uri 宽松校验结合开放重定向窃取token  (单例, max_score 9)
- 频率/迁移/来源: 高频 / 高（可迁移到OAuth、SAML等认证协议） / 高
- 代表报告: https://hackerone.com/reports/6017

### [263718] 同源iframe脚本导致权限提升（XSS到RCE）  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何同源iframe场景，如CMS、管理后台） / 高
- 代表报告: https://hackerone.com/reports/263718

### [1378175] Ingress-nginx注解注入获取service account token  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他注解驱动的配置系统） / 高
- 代表报告: https://hackerone.com/reports/1378175

### [221432] CSRF token泄露通过双斜杠绝对URL  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何URL处理） / 高
- 代表报告: https://hackerone.com/reports/221432

### [761726] SOP绕过利用浏览器缓存  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何浏览器缓存场景） / 高
- 代表报告: https://hackerone.com/reports/761726

### [858598] 硬链接滥用导致特权文件写入  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（适用于Windows和Linux特权服务，可迁移到其他文件操作场景） / 高
- 代表报告: https://hackerone.com/reports/858598

### [446585] 导入数据字段级权限校验缺失导致模板投毒  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到所有导入功能，检查字段权限） / 高
- 代表报告: https://hackerone.com/reports/446585

### [2371019] postMessage监听器未编码avatar_url导致DOM XSS  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到所有postMessage数据处理） / 高
- 代表报告: https://hackerone.com/reports/2371019

### [1245165] CSS加载跟随重定向导致数据窃取  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他资源加载） / 高
- 代表报告: https://hackerone.com/reports/1245165

### [378148] 正则表达式对换行符匹配缺陷导致任意文件写入  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用正则过滤文件名的场景，以及符号链接处理） / 高
- 代表报告: https://hackerone.com/reports/378148

### [867699] 容器内写/etc/hosts导致宿主机磁盘耗尽  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何容器挂载可写文件场景） / 高
- 代表报告: https://hackerone.com/reports/867699

### [1533976] HTML注入结合DOMPurify gadget和浏览器缓存实现任意POST请求  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到XSS过滤绕过、CSRF攻击） / 高
- 代表报告: https://hackerone.com/reports/1533976

### [224198] 内部组件信任：通过消息队列注入恶意任务实现RCE  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何消息队列和Worker模型） / 高
- 代表报告: https://hackerone.com/reports/224198

### [415202] 多阶段攻击链：路径遍历→对象注入→XXE→SSRF→反序列化RCE  (单例, max_score 9)
- 频率/迁移/来源: 低频 / 高（可抽象为多阶段攻击链模式，适用于复杂系统） / 高
- 代表报告: https://hackerone.com/reports/415202

### [899103] 容器默认能力 CAP_NET_RAW 与 hostNetwork 组合导致中间人攻击  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（适用于容器安全配置审计） / 高
- 代表报告: https://hackerone.com/reports/899103

### [2107680] librsvg 未初始化内存泄露导致敏感信息泄露  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（适用于图像处理库安全） / 高
- 代表报告: https://hackerone.com/reports/2107680

### [389108] 浏览器扩展 postMessage 处理不当导致任意请求带 cookie  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到所有浏览器扩展、Electron 应用的消息通信） / 高
- 代表报告: https://hackerone.com/reports/389108

### [1741430] 深链接参数未编码导致 CSRF 和路径穿越  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到所有深链接处理） / 高
- 代表报告: https://hackerone.com/reports/1741430

### [1439552] Service Worker 拦截 OAuth 响应窃取令牌  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何基于 OAuth 的 Web 应用） / 高
- 代表报告: https://hackerone.com/reports/1439552

### [892337] JWT 路径遍历 + CSS 数据外泄绕过 2FA  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 JWT 验证和 2FA 场景） / 高
- 代表报告: https://hackerone.com/reports/892337

### [863979] kubectl 301重定向重放Authorization头  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他客户端重定向场景） / 高
- 代表报告: https://hackerone.com/reports/863979

### [943737] Electron WebView 权限配置不当导致任意文件读取  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何Electron应用或类似WebView环境） / 高
- 代表报告: https://hackerone.com/reports/943737

### [1274695] Chrome 远程调试端口滥用导致RCE  (单例, max_score 9)
- 频率/迁移/来源: 低频 / 高（可迁移到任何使用Chrome远程调试的应用） / 高
- 代表报告: https://hackerone.com/reports/1274695

### [899964] Electron 中 XSS 升级为 RCE（覆盖 RegExp.prototype.test）  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何 Electron 应用和原型污染场景） / 高
- 代表报告: https://hackerone.com/reports/899964

### [1668258] 智能合约重入攻击（以太坊）  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何智能合约） / 高
- 代表报告: https://hackerone.com/reports/1668258

### [1261413] HEIC 预览调用 Imagick 导致任意文件读取  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（文件处理库、图像处理、SSRF） / 高
- 代表报告: https://hackerone.com/reports/1261413

### [17390] Flash 内容类型嗅探绕过上传限制并跨域读取  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任意文件上传场景，如 SVG、HTML、XML 等） / 高
- 代表报告: https://hackerone.com/reports/17390

### [1893186] 跨组件CSP绕过实现XSS  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用CSP的Web应用） / 高
- 代表报告: https://hackerone.com/reports/1893186

### [99708] 路径遍历绕过 CSRF 保护  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到 URL 解析差异导致的防护绕过） / 高
- 代表报告: https://hackerone.com/reports/99708

### [1036886] kubelet /logs 端点符号链接跟随导致权限提升  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他容器运行时或日志服务） / 高
- 代表报告: https://hackerone.com/reports/1036886

### [697055] 符号链接绕过容器隔离读取宿主机文件  (单例, max_score 8)
- 频率/迁移/来源: 低频 / 高（可迁移到任何构建系统处理符号链接的场景） / 高
- 代表报告: https://hackerone.com/reports/697055

### [395729] WebSocket 无 CORS 限制导致扩展任意连接  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何 WebSocket 客户端场景） / 高
- 代表报告: https://hackerone.com/reports/395729

### [1544133] Kubernetes 聚合 API 重定向导致凭据泄露  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他信任组件间的重定向攻击） / 高
- 代表报告: https://hackerone.com/reports/1544133


## 认证绕过 （52 个候选）

### [861940] IDN同形字绕过OAuth redirect_uri  (★3次, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到域名验证、URL解析） / 高
- 同簇报告(3): 861940, 131202, 405100
- 代表报告: https://hackerone.com/reports/861940

### [136169] SAML签名验证绕过  (★3次, max_score 9)
- 频率/迁移/来源: 中频 / 高（适用于所有SAML实现，可迁移到OAuth等签名验证场景） / 高
- 同簇报告(3): 136169, 812064, 356284
- 代表报告: https://hackerone.com/reports/136169

### [4795] 数据库字段长度截断导致认证绕过  (★2次, max_score 9)
- 频率/迁移/来源: 高频 / 高（可迁移到邮箱、用户名、密码等字段长度限制场景） / 高
- 同簇报告(2): 4795, 2224
- 代表报告: https://hackerone.com/reports/4795

### [1372667] Deep link 重定向参数绕过 URL 白名单窃取 JWT  (★2次, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何重定向参数验证场景） / 高
- 同簇报告(2): 1372667, 637194
- 代表报告: https://hackerone.com/reports/1372667

### [1567186] OAuth 响应类型切换与 XSS 结合实现账户劫持  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 OAuth 实现） / 高
- 代表报告: https://hackerone.com/reports/1567186

### [976603] SAML entityId 尾随空格绕过导致 SSO DOS 和账户接管  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（输入规范化不一致可迁移到其他认证协议） / 高
- 代表报告: https://hackerone.com/reports/976603

### [1040786] Path traversal in Workhorse JWT exposure and Geo header spoofing  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何前后端URL解析不一致和信任头） / 高
- 代表报告: https://hackerone.com/reports/1040786

### [1342088] 通过直接调用后端API绕过UI限制进行账户接管  (单例, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到任何使用第三方身份提供商API的应用） / 高
- 代表报告: https://hackerone.com/reports/1342088

### [565883] 利用SCIM API信任关系绕过邮箱验证  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用SCIM或类似身份同步机制的应用） / 高
- 代表报告: https://hackerone.com/reports/565883

### [1380121] 弱密钥伪造会话结合密码重置接管管理员  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用会话签名的应用） / 高
- 代表报告: https://hackerone.com/reports/1380121

### [241244] 线程局部变量残留导致认证绕过  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到 Java Web 框架、线程池场景） / 高
- 代表报告: https://hackerone.com/reports/241244

### [1580493] AWS IAM Authenticator 参数大小写绕过  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（参数规范化、认证绕过、云安全） / 高
- 代表报告: https://hackerone.com/reports/1580493

### [1357948] 路径编码绕过 ingress 外部认证  (单例, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到任何基于路径的认证系统） / 高
- 代表报告: https://hackerone.com/reports/1357948

### [617896] 第三方 IdP 集成导致邮箱验证绕过  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用第三方 IdP 的认证系统） / 高
- 代表报告: https://hackerone.com/reports/617896

### [770504] 客户端篡改服务器响应绕过密码验证  (单例, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到任何客户端-服务器交互） / 高
- 代表报告: https://hackerone.com/reports/770504

### [921780] IDOR导致OTP token泄露  (单例, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到任何涉及用户标识的端点） / 高
- 代表报告: https://hackerone.com/reports/921780

### [855618] 移动端deeplink拦截导致账户接管  (单例, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到所有使用deeplink的移动应用） / 高
- 代表报告: https://hackerone.com/reports/855618

### [1923672] SAML RelayState开放重定向结合OAuth隐式授权窃取令牌  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他SSO协议） / 高
- 代表报告: https://hackerone.com/reports/1923672

### [975983] Safari URL特殊字符解析绕过Referer校验  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（CSRF防护、Referer校验） / 高
- 代表报告: https://hackerone.com/reports/975983

### [922456] OAuth授权流程中邮箱验证缺失导致账户接管  (单例, max_score 9)
- 频率/迁移/来源: 高频 / 高（可迁移到所有OAuth实现，检查邮箱验证） / 高
- 代表报告: https://hackerone.com/reports/922456

### [736522] JWT验证逻辑不完整导致身份伪造  (单例, max_score 9)
- 频率/迁移/来源: 高频 / 高（可迁移到任何使用JWT或类似token的系统） / 高
- 代表报告: https://hackerone.com/reports/736522

### [732415] CSRF token可逆性导致伪造（Rails per_form_csrf_tokens）  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他框架的CSRF token设计） / 高
- 代表报告: https://hackerone.com/reports/732415

### [128085] 参数优先级导致 2FA 绕过  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他认证流程） / 高
- 代表报告: https://hackerone.com/reports/128085

### [110293] OAuth回调验证绕过（路径遍历+开放重定向）  (单例, max_score 9)
- 频率/迁移/来源: 高频 / 高（适用于所有OAuth/OIDC实现，可迁移到回调URL验证场景） / 高
- 代表报告: https://hackerone.com/reports/110293

### [1018489] 未验证邮箱账户添加外部登录  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（认证流程、业务逻辑） / 高
- 代表报告: https://hackerone.com/reports/1018489

### [129873] String.search() 隐式正则导致 origin 校验绕过  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到所有使用 String.search() 的校验） / 高
- 代表报告: https://hackerone.com/reports/129873

### [124845] 跨账户 token 重用绕过密码验证  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用 token 的认证场景） / 高
- 代表报告: https://hackerone.com/reports/124845

### [148151] SMB map to guest认证绕过  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他认证绕过场景） / 高
- 代表报告: https://hackerone.com/reports/148151

### [1040471] 利用换行符绕过速率限制  (单例, max_score 9)
- 频率/迁移/来源: 高频 / 高（可迁移到其他输入验证场景） / 高
- 代表报告: https://hackerone.com/reports/1040471

### [490946] 暴露的intent绕过锁保护  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他组件间通信场景，如IPC） / 高
- 代表报告: https://hackerone.com/reports/490946

### [1020371] 账户关闭后预签名 URL 未失效导致文件上传  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（预签名 URL、令牌撤销、云存储） / 高
- 代表报告: https://hackerone.com/reports/1020371

### [2104566] Node.js 权限策略绕过：module.constructor.createRequire()  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（Node.js 安全、权限模型、模块加载） / 高
- 代表报告: https://hackerone.com/reports/2104566

### [2233] 利用MySQL字符集截断绕过邮箱域名验证  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何依赖数据库字符集截断的验证逻辑） / 高
- 代表报告: https://hackerone.com/reports/2233

### [461308] ActivityPub 协议中 keyId 未校验来源导致身份冒充  (单例, max_score 8)
- 频率/迁移/来源: 低频 / 高（适用于任何联邦协议） / 高
- 代表报告: https://hackerone.com/reports/461308

### [587910] 禁用 2FA 时未验证密码  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何多因素认证流程） / 高
- 代表报告: https://hackerone.com/reports/587910

### [218230] 利用邮件别名功能接收第三方验证信实现身份绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何提供邮件别名功能的服务） / 高
- 代表报告: https://hackerone.com/reports/218230

### [1817214] token可预测性导致账户接管  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用token的认证系统） / 高
- 代表报告: https://hackerone.com/reports/1817214

### [722748] 2FA绕过：登录时设置新提供者  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到多因素认证流程） / 高
- 代表报告: https://hackerone.com/reports/722748

### [141239] Nginx auth_basic密码截断绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他解析差异） / 高
- 代表报告: https://hackerone.com/reports/141239

### [204802] 环境变量覆盖 socket 路径绕过文件权限  (单例, max_score 8)
- 频率/迁移/来源: 低频 / 高（可迁移到其他使用环境变量指定资源路径的场景） / 高
- 代表报告: https://hackerone.com/reports/204802

### [103787] CSRF token 未绑定操作 + _method 覆盖 + 浏览器不发送 Origin 头的组合绕过  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到所有基于 token 的 CSRF 防护场景，以及依赖 Origin 头校验的 WAF） / 高
- 代表报告: https://hackerone.com/reports/103787

### [1552110] 连接复用未验证认证凭据导致认证绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到 HTTP、FTP、SMTP 等所有支持连接复用的协议） / 高
- 代表报告: https://hackerone.com/reports/1552110

### [747726] Android Activity 启动模式绕过锁屏  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到所有 Android 应用锁屏绕过） / 高
- 代表报告: https://hackerone.com/reports/747726

### [532225] Android deeplink 中 navigation_bar_type 参数绕过 host 校验  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他移动端 deeplink 校验绕过场景） / 高
- 代表报告: https://hackerone.com/reports/532225

### [1172205] 注销请求参数缺失导致 token 未撤销  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到所有注销/失效场景） / 高
- 代表报告: https://hackerone.com/reports/1172205

### [168116] 空Referer绕过验证  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到CSRF防护和来源验证） / 高
- 代表报告: https://hackerone.com/reports/168116

### [1108874] Host头注入污染密码重置链接导致账户接管  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何依赖Host头生成链接的功能，如密码重置、邮件验证、回调URL等） / 高
- 代表报告: https://hackerone.com/reports/1108874

### [205908] LDAP认证时未强制应用用户过滤器导致任意有效账户登录  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他认证系统如OAuth、SAML中的过滤逻辑复用） / 高
- 代表报告: https://hackerone.com/reports/205908

### [161408] CSRF token置空或固定值绕过双重防护  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何CSRF防护实现） / 高
- 代表报告: https://hackerone.com/reports/161408

### [1363672] 输入规范化不完整绕过限流  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何输入规范化场景） / 高
- 代表报告: https://hackerone.com/reports/1363672

### [2410774] QUIC 证书验证绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到所有使用 QUIC 的客户端） / 高
- 代表报告: https://hackerone.com/reports/2410774

### [796956] 多步流程依赖URL路径且无服务端状态机校验导致认证绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（任何多步流程应用都可能存在） / 高
- 代表报告: https://hackerone.com/reports/796956


## 授权绕过 （49 个候选）

### [1861487] GraphQL变量篡改绕过审批  (★2次, max_score 9)
- 频率/迁移/来源: 高频 / 高（可迁移到状态机、审批流程等业务逻辑） / 高
- 同簇报告(2): 1861487, 781175
- 代表报告: https://hackerone.com/reports/1861487

### [1485500] S3 签名 URL 路径解析绕过：使用 `/.` 和 `?` 注释掉后续路径  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他云存储、签名 URL 场景） / 高
- 代表报告: https://hackerone.com/reports/1485500

### [703058] ASP.NET path parsing bypass of redirect rules  (单例, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到任何框架的路径解析差异） / 高
- 代表报告: https://hackerone.com/reports/703058

### [674195] 账户关联未验证所有权导致数据泄露  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何账户关联功能） / 高
- 代表报告: https://hackerone.com/reports/674195

### [1327742] 开放重定向结合历史域名注册窃取access_token  (单例, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到OAuth流程、SSO） / 高
- 代表报告: https://hackerone.com/reports/1327742

### [1023669] WebSocket事件订阅未授权导致信息泄露  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到所有WebSocket应用） / 高
- 代表报告: https://hackerone.com/reports/1023669

### [518669] ContentProvider投影映射限制绕过导致SQL注入  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他URI过滤绕过场景） / 高
- 代表报告: https://hackerone.com/reports/518669

### [358339] WebDAV搜索和预览API绕过文件访问控制  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他API端点） / 高
- 代表报告: https://hackerone.com/reports/358339

### [1026146] SOAP Header认证绕过  (单例, max_score 9)
- 频率/迁移/来源: 低频 / 高（SOAP服务、API安全） / 高
- 代表报告: https://hackerone.com/reports/1026146

### [1501611] GraphQL IDOR：可预测对象ID与缺失对象级授权  (单例, max_score 9)
- 频率/迁移/来源: 高频 / 高（适用于所有GraphQL API，可迁移到REST API的IDOR检测） / 高
- 代表报告: https://hackerone.com/reports/1501611

### [827816] 客户端信任权限标志导致权限提升  (单例, max_score 9)
- 频率/迁移/来源: 高频 / 高（可迁移到任何依赖客户端权限标志的系统） / 高
- 代表报告: https://hackerone.com/reports/827816

### [835005] GraphQL泄露内部ID结合IDOR实现组织接管  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（适用于所有使用GraphQL的API，可迁移到其他IDOR场景） / 高
- 代表报告: https://hackerone.com/reports/835005

### [1751258] 通过篡改 noteable_type 参数绕过项目权限检查，访问私有 personal_snippet  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用多态关联且参数可控的场景，如评论、附件、标签等） / 高
- 代表报告: https://hackerone.com/reports/1751258

### [497047] CI/CD token绕过用户封禁  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他token管理场景） / 高
- 代表报告: https://hackerone.com/reports/497047

### [312647] Onebox preview bypassing access control via user-controlled parameter  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他引用/预览功能，如Slack、Teams） / 高
- 代表报告: https://hackerone.com/reports/312647

### [1034346] 对象关联劫持：孤儿附件与多态关联绕过授权  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用ORM多态关联的应用，如Rails、Django） / 高
- 代表报告: https://hackerone.com/reports/1034346

### [901775] 利用apps权限提取analytics token绕过权限限制  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他权限模型，如OAuth scope设计） / 高
- 代表报告: https://hackerone.com/reports/901775

### [1424291] 内容协商绕过授权检查（Accept: application/json）  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何基于内容协商的 API 设计） / 高
- 代表报告: https://hackerone.com/reports/1424291

### [423496] 邀请token未绑定商店ID导致跨商店注册绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何多租户应用中的邀请/授权机制） / 高
- 代表报告: https://hackerone.com/reports/423496

### [2746] S3 URL可预测性结合信息泄露实现数据抓取  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到云存储安全、信息泄露） / 高
- 代表报告: https://hackerone.com/reports/2746

### [429000] IDOR结合CAC认证绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到IDOR、认证绕过） / 高
- 代表报告: https://hackerone.com/reports/429000

### [1193062] 外部用户通过项目令牌提升权限  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他权限继承场景） / 高
- 代表报告: https://hackerone.com/reports/1193062

### [1519099] Electron 默认配置下 renderer 进程可访问蓝牙设备（Web Bluetooth API）  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 Electron 敏感 API 如 WebUSB、WebMIDI） / 高
- 代表报告: https://hackerone.com/reports/1519099

### [1521336] 未文档化内部端点绕过权限  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何内部端点） / 高
- 代表报告: https://hackerone.com/reports/1521336

### [608656] 禁用账户后 GraphQL 端点未同步状态检查导致授权绕过  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（所有 API 端点、微服务架构、状态管理场景） / 高
- 代表报告: https://hackerone.com/reports/608656

### [1193321] 受限 token 可修改自身权限导致权限提升  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何基于 token 的授权系统，如 OAuth、API 密钥等） / 高
- 代表报告: https://hackerone.com/reports/1193321

### [403039] 黑名单角色提升绕过（通过中间角色）  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何基于角色的权限系统） / 高
- 代表报告: https://hackerone.com/reports/403039

### [667408] 新功能未继承现有权限模型导致信息泄露  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（适用于任何新功能上线时的权限继承检查） / 高
- 代表报告: https://hackerone.com/reports/667408

### [1767771] API 端点未验证域名所有权导致子域名接管  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（适用于任何域名绑定 API） / 高
- 代表报告: https://hackerone.com/reports/1767771

### [1990443] 联邦分享权限提升通过伪造通知  (单例, max_score 8)
- 频率/迁移/来源: 低频 / 高（可迁移到任何跨信任边界的控制面接口） / 高
- 代表报告: https://hackerone.com/reports/1990443

### [343626] 信任Referer头进行权限校验导致提权  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何基于Referer的权限校验场景） / 高
- 代表报告: https://hackerone.com/reports/343626

### [1088159] 权限传播状态不一致导致提权  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何权限管理场景） / 高
- 代表报告: https://hackerone.com/reports/1088159

### [809816] 跨组织token未校验资源归属导致提权  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何多租户系统） / 高
- 代表报告: https://hackerone.com/reports/809816

### [397478] XPC服务未授权导致提权  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到macOS应用安全、提权漏洞） / 高
- 代表报告: https://hackerone.com/reports/397478

### [55670] 删除用户后权限残留导致越权  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（用户管理、角色变更、组织权限等场景均可迁移） / 高
- 代表报告: https://hackerone.com/reports/55670

### [134299] 多态关联 IDOR（noteable_id 跨项目引用）  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他多态关联场景） / 高
- 代表报告: https://hackerone.com/reports/134299

### [1596663] 角色变更后权限残留  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到权限管理场景） / 高
- 代表报告: https://hackerone.com/reports/1596663

### [243943] 低权限用户通过IDOR获取商店敏感信息  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何多租户应用，通过枚举ID访问其他租户数据） / 高
- 代表报告: https://hackerone.com/reports/243943

### [1043480] 授权检查时间窗口绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何临时链接、一次性凭证等场景） / 高
- 代表报告: https://hackerone.com/reports/1043480

### [1806387] 修改HTTP响应状态码绕过基于重定向的访问控制  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何基于重定向的访问控制） / 高
- 代表报告: https://hackerone.com/reports/1806387

### [416983] 静态HMAC不绑定用户身份导致权限撤销后仍可重用  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何基于静态令牌的授权） / 高
- 代表报告: https://hackerone.com/reports/416983

### [1285226] 密码过期状态与token认证不一致导致授权绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何多认证机制的系统） / 高
- 代表报告: https://hackerone.com/reports/1285226

### [1892200] IDOR：未验证关联对象权限导致跨组关联  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何对象关联场景） / 高
- 代表报告: https://hackerone.com/reports/1892200

### [700831] 第三方应用泄露Access Token导致权限撤销失效  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移至任何第三方应用集成场景） / 高
- 代表报告: https://hackerone.com/reports/700831

### [213942] 文件生成机制与策略继承脱节导致 IDOR  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何文件生成和分享场景） / 高
- 代表报告: https://hackerone.com/reports/213942

### [698708] 签名URL刷新绕过权限撤销  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何签名机制） / 高
- 代表报告: https://hackerone.com/reports/698708

### [781150] GraphQL node接口绕过基于角色的授权检查  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（任何使用GraphQL node接口的应用都可能存在） / 高
- 代表报告: https://hackerone.com/reports/781150

### [871749] GraphQL嵌套查询泄露空引用关联数据  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（任何GraphQL API都可能存在类似问题） / 高
- 代表报告: https://hackerone.com/reports/871749

### [1257428] 第三方应用代理绕过内部API权限检查  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何平台型应用，如SaaS、PaaS，第三方应用与核心API的权限边界） / 高
- 代表报告: https://hackerone.com/reports/1257428


## XSS （45 个候选）

### [207042] postMessage无origin校验+JSONP导致XSS  (★4次, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到所有postMessage使用） / 高
- 同簇报告(4): 207042, 423218, 894518, 381192
- 代表报告: https://hackerone.com/reports/207042

### [1238528] Safari 对 javascript: URL 的解析差异导致 XSS  (★2次, max_score 10)
- 频率/迁移/来源: 中频 / 高（浏览器差异导致的 XSS 可迁移到其他浏览器或 WebView） / 高
- 同簇报告(2): 1238528, 684268
- 代表报告: https://hackerone.com/reports/1238528

### [1212822] Mermaid 配置覆盖绕过消毒导致 XSS  (★2次, max_score 10)
- 频率/迁移/来源: 中频 / 高（配置覆盖、类型混淆、CSP 绕过） / 高
- 同簇报告(2): 1212822, 312548
- 代表报告: https://hackerone.com/reports/1212822

### [1579645] DOMPurify 过滤不完整结合 Rails-ujs 属性导致 XSS  (★2次, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他前端框架的属性过滤不完整） / 高
- 同簇报告(2): 1579645, 1024734
- 代表报告: https://hackerone.com/reports/1579645

### [1481207] base标签重写相对URL绕过CSP  (★2次, max_score 9)
- 频率/迁移/来源: 高频 / 高（适用于所有允许HTML注入且使用相对URL的场景） / 高
- 同簇报告(2): 1481207, 500436
- 代表报告: https://hackerone.com/reports/1481207

### [497724] 利用URL编码绕过消毒函数实现存储XSS  (★2次, max_score 9)
- 频率/迁移/来源: 高频 / 高（可迁移到其他框架的消毒顺序问题） / 高
- 同簇报告(2): 497724, 249131
- 代表报告: https://hackerone.com/reports/497724

### [1665658] 通过标签颜色注入XSS并绕过CSP  (★2次, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他字段注入和CSP绕过场景） / 高
- 同簇报告(2): 1665658, 1693150
- 代表报告: https://hackerone.com/reports/1665658

### [977697] iframe srcdoc 绕过 CSP 实现存储型 XSS  (★2次, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何 CSP 防护的 XSS 场景） / 高
- 同簇报告(2): 977697, 836649
- 代表报告: https://hackerone.com/reports/977697

### [1398305] XSS 过滤器绕过：服务端 SyntaxHighlightFilter 与前端 gl-emoji 自定义元素属性注入  (单例, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到其他富文本编辑器、自定义元素、属性过滤场景） / 高
- 代表报告: https://hackerone.com/reports/1398305

### [227486] WAF 绕过：使用 %u0022 编码注入 onclick 属性并利用现有事件绑定  (单例, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到其他 WAF 绕过、XSS 注入场景） / 高
- 代表报告: https://hackerone.com/reports/227486

### [232174] SVG 白名单绕过：使用 XML 实体注入 onload 事件  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 XML 解析、白名单绕过场景） / 高
- 代表报告: https://hackerone.com/reports/232174

### [921635] DOM XSS：利用 Cloud Save 存储 payload 结合 eval 和 URL 片段绕过长度限制  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他存储型 XSS、DOM XSS 场景） / 高
- 代表报告: https://hackerone.com/reports/921635

### [2010530] Cookie 解析差异（空格分隔）导致 Cookie 走私，结合 XSS 实现账户接管  (单例, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到任何依赖 cookie 解析的 Web 应用，如会话管理、CSRF 防护） / 高
- 代表报告: https://hackerone.com/reports/2010530

### [662083] pushState 路径遍历绕过 admin 前缀实现 DOM XSS  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用 pushState 或类似 API 的 Web 应用） / 高
- 代表报告: https://hackerone.com/reports/662083

### [1760213] WAF 与服务器解析差异绕过（双引号插入）  (单例, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到所有 WAF 绕过场景） / 高
- 代表报告: https://hackerone.com/reports/1760213

### [134546] Flash XSS 利用 URL 解析差异、ES6 模板字符串和浏览器行为绕过多层过滤  (单例, max_score 10)
- 频率/迁移/来源: 低频 / 高（可迁移到其他浏览器解析差异、模板注入场景） / 高
- 代表报告: https://hackerone.com/reports/134546

### [1444682] Swagger-UI configUrl 加载 data: 协议导致 XSS  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（Swagger-UI 配置加载、data: 协议绕过、XSS 利用） / 高
- 代表报告: https://hackerone.com/reports/1444682

### [390344] 移动应用内浏览器渲染附件时共享会话导致 XSS  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他移动应用或 WebView 场景） / 高
- 代表报告: https://hackerone.com/reports/390344

### [982291] CSS url(cid://) 绕过 HTML 过滤器  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用 HTML 过滤器的邮件或 Web 应用） / 高
- 代表报告: https://hackerone.com/reports/982291

### [724153] 事件处理器绕过script标签过滤实现存储XSS并读取本地文件  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他XSS过滤绕过和桌面客户端安全） / 高
- 代表报告: https://hackerone.com/reports/724153

### [259100] JSONP/频道消息通道投递未转义反射导致XSS  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到消息通道、WebSocket等） / 高
- 代表报告: https://hackerone.com/reports/259100

### [1212067] 上传文件名引号逃逸+JSONP绕过CSP导致存储XSS  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到文件上传、渲染管线） / 高
- 代表报告: https://hackerone.com/reports/1212067

### [1087061] git配置email注入HTML属性导致存储XSS  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他用户可控字段） / 高
- 代表报告: https://hackerone.com/reports/1087061

### [1758132] autolink 正则缺陷导致 DOM XSS  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他自动链接生成场景） / 高
- 代表报告: https://hackerone.com/reports/1758132

### [429298] 表情解析中 URL 未校验结合 jQuery 自动执行导致存储型 XSS  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（适用于所有 URL 校验和 jQuery 使用场景） / 高
- 代表报告: https://hackerone.com/reports/429298

### [1404804] XSS filter bypass via js-xss parsing difference combined with HMAC and clickjacking  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他XSS过滤器绕过） / 高
- 代表报告: https://hackerone.com/reports/1404804

### [463915] Universal XSS via postMessage in browser extension  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他浏览器扩展和postMessage处理） / 高
- 代表报告: https://hackerone.com/reports/463915

### [85488] Unicode 转义序列解析差异绕过 XSS 过滤  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 XSS 过滤绕过） / 高
- 代表报告: https://hackerone.com/reports/85488

### [84601] 未知文件类型上传结合浏览器嗅探和AppCache缓存投毒  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他上传场景和缓存机制） / 高
- 代表报告: https://hackerone.com/reports/84601

### [473950] 模板字符串拼接导致 WebView XSS  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用模板字符串拼接用户输入的场景） / 高
- 代表报告: https://hackerone.com/reports/473950

### [171670] HTML5 实体绕过 xss_clean() 正则过滤  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（XSS 过滤、WAF 绕过、实体编码） / 高
- 代表报告: https://hackerone.com/reports/171670

### [394016] X-Forwarded-Host 头注入导致缓存 XSS  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用 X-Forwarded-Host 的缓存场景） / 高
- 代表报告: https://hackerone.com/reports/394016

### [132104] 编辑模式与预览模式安全检查不一致导致 XSS  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何富文本编辑器） / 高
- 代表报告: https://hackerone.com/reports/132104

### [1731349] 选择器与取值对象不一致导致XSS注入  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何HTML构建场景） / 高
- 代表报告: https://hackerone.com/reports/1731349

### [293689] HTTP 参数重复解析差异绕过签名  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何签名校验场景） / 高
- 代表报告: https://hackerone.com/reports/293689

### [526325] Wiki 层级链接语法转换绕过 XSS 过滤  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他支持层级链接的 Markdown 渲染器） / 高
- 代表报告: https://hackerone.com/reports/526325

### [229735] 模板占位符二次注入绕过过滤  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（模板引擎、XSS、URL构造等场景均可迁移） / 高
- 代表报告: https://hackerone.com/reports/229735

### [1518343] 利用javascript:伪协议和注释符绕过URL白名单  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到所有URL白名单校验场景） / 高
- 代表报告: https://hackerone.com/reports/1518343

### [991713] 阅读器模式模板注入导致数据窃取  (单例, max_score 8)
- 频率/迁移/来源: 低频 / 高（可迁移到其他模板渲染场景） / 高
- 代表报告: https://hackerone.com/reports/991713

### [425007] Open Graph 标签注入导致持久性 XSS  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何支持 oEmbed/Open Graph 的内容平台） / 高
- 代表报告: https://hackerone.com/reports/425007

### [633231] WordPress shortcode 函数副作用导致 XSS  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他框架的类似函数副作用） / 高
- 代表报告: https://hackerone.com/reports/633231

### [1167034] 八进制编码绕过大小写转换过滤实现 XSS  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何基于字符转换的过滤绕过场景） / 高
- 代表报告: https://hackerone.com/reports/1167034

### [246794] 安全处理的状态标记由输入数据控制导致转义禁用  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何安全处理依赖输入数据属性的场景） / 高
- 代表报告: https://hackerone.com/reports/246794

### [1736317] 客户端模板注入（CSTI）导致XSS，结合编码绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何模板引擎的CSTI检测与利用） / 高
- 代表报告: https://hackerone.com/reports/1736317

### [632017] 存储XSS与登录/登出CSRF组合链实现ATO  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何有登录/登出CSRF和存储XSS的Web应用） / 高
- 代表报告: https://hackerone.com/reports/632017


## 业务逻辑 （39 个候选）

### [743953] 导入功能未过滤关联属性导致IDOR  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何导入/导出功能） / 高
- 代表报告: https://hackerone.com/reports/743953

### [1330529] OTP 验证流程参数篡改导致未授权认领  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 OTP 验证场景） / 高
- 代表报告: https://hackerone.com/reports/1330529

### [1295844] 签名拼接漏洞导致支付金额篡改  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何签名验证场景，如支付、API 认证） / 高
- 代表报告: https://hackerone.com/reports/1295844

### [258084] WebDAV 复制操作中文件名冲突导致目录遍历和信息泄露  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何文件共享或 WebDAV 实现） / 高
- 代表报告: https://hackerone.com/reports/258084

### [684092] 智能合约跨合约攻击：flip.kick 缺乏验证导致清算窃取  (单例, max_score 10)
- 频率/迁移/来源: 低频 / 高（可迁移到其他 DeFi 协议） / 高
- 代表报告: https://hackerone.com/reports/684092

### [307670] 跨组件参数解析差异导致业务逻辑错误  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（参数解析歧义、跨组件数据流、业务逻辑漏洞） / 高
- 代表报告: https://hackerone.com/reports/307670

### [364904] Monero 交易 tx pubkey 重复导致金额虚报  (单例, max_score 10)
- 频率/迁移/来源: 低频 / 高（可迁移到任何解析协议字段的应用） / 高
- 代表报告: https://hackerone.com/reports/364904

### [665798] DeFi 利率同步漏洞导致无风险套利  (单例, max_score 10)
- 频率/迁移/来源: 低频 / 高（可迁移到任何 DeFi 协议） / 高
- 代表报告: https://hackerone.com/reports/665798

### [785243] Unicode 不可见字符绕过应用名称唯一性校验  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何依赖字符串唯一性校验的系统） / 高
- 代表报告: https://hackerone.com/reports/785243

### [205000] OTP重发接口无速率限制绕过尝试次数限制  (单例, max_score 9)
- 频率/迁移/来源: 高频 / 高（OTP机制、暴力破解） / 高
- 代表报告: https://hackerone.com/reports/205000

### [882258] 用户名复用导致数据隔离失效  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用用户名作为关联键的系统，如论坛、云存储、协作平台） / 高
- 代表报告: https://hackerone.com/reports/882258

### [218872] git submodule URL注入XSS  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何用户可控的配置文件注入） / 高
- 代表报告: https://hackerone.com/reports/218872

### [1357013] 邀请链接 token 与邮箱解耦导致账户接管  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他邀请机制） / 高
- 代表报告: https://hackerone.com/reports/1357013

### [1350444] 利用执行超时和可预测临时目录名绕过清理实现RCE  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他具有临时文件下载功能且使用可预测随机数的系统） / 高
- 代表报告: https://hackerone.com/reports/1350444

### [703138] Yarn cache poisoning via lock file hash/integrity check bypass  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他包管理器如npm、pip的缓存机制） / 高
- 代表报告: https://hackerone.com/reports/703138

### [321511] 交易原子性导致订单簿状态不一致（crossing offers）  (单例, max_score 9)
- 频率/迁移/来源: 低频 / 高（可迁移到任何依赖多步操作原子性的系统，如金融、分布式账本） / 高
- 代表报告: https://hackerone.com/reports/321511

### [905816] 通过 cookie 中的 MD5 密码绕过速率限制暴力破解  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何基于 cookie 的认证和速率限制场景） / 高
- 代表报告: https://hackerone.com/reports/905816

### [1040047] 敏感令牌泄露给非预期角色导致邮箱验证绕过  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何邀请/注册/密码重置流程） / 高
- 代表报告: https://hackerone.com/reports/1040047

### [785833] 邮箱重复注册结合密码重置导致账户接管  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何使用邮箱注册和密码重置的应用） / 高
- 代表报告: https://hackerone.com/reports/785833

### [423136] 会话固定结合XSS实现跨应用身份冒充  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到会话管理、子域cookie安全） / 高
- 代表报告: https://hackerone.com/reports/423136

### [195058] 命名空间重命名后旧链接未失效导致旧导出文件泄露  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他资源 URL 变化场景） / 高
- 代表报告: https://hackerone.com/reports/195058

### [1018336] 客户端可控布尔标志破坏数据最小化策略  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用布尔标志控制权限的 API） / 高
- 代表报告: https://hackerone.com/reports/1018336

### [422279] URL 解析差异导致钓鱼（反斜杠和 @ 符号）  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何 URL 校验场景） / 高
- 代表报告: https://hackerone.com/reports/422279

### [410015] 利用报告计数差异侧信道探测私有程序存在性  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他平台的功能差异探测，如用户存在性、资源存在性） / 高
- 代表报告: https://hackerone.com/reports/410015

### [330105] 利用交易舍入误差和最小交易单位进行套利  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他交易系统、金融协议） / 高
- 代表报告: https://hackerone.com/reports/330105

### [307675] 平台间信任链验证缺陷：fork 的 gist 被误认为所有权证明  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何依赖第三方平台所有权验证的场景，如 OAuth 回调、社交账号绑定） / 高
- 代表报告: https://hackerone.com/reports/307675

### [1446090] 服务端对同一数值使用不同取整函数（ceil/floor）导致业务逻辑漏洞  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何涉及数值计算和计费的场景） / 高
- 代表报告: https://hackerone.com/reports/1446090

### [481518] GraphQL 负值参数绕过速率限制  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他成本计算或配额系统） / 高
- 代表报告: https://hackerone.com/reports/481518

### [1615790] 过期令牌仍被服务端接受（状态混淆）  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（密码重置、会话管理、授权令牌等场景均可迁移） / 高
- 代表报告: https://hackerone.com/reports/1615790

### [968165] 邮箱验证仅检查域名部分导致信息泄露  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（邮箱验证、订单查询、用户枚举等场景均可迁移） / 高
- 代表报告: https://hackerone.com/reports/968165

### [1350401] 密码重置流程状态混淆绕过邮箱验证  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他验证流程） / 高
- 代表报告: https://hackerone.com/reports/1350401

### [244612] 密码重置链接未随邮箱变更失效  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到所有敏感操作后的凭证失效） / 高
- 代表报告: https://hackerone.com/reports/244612

### [170310] 空字节截断绕过速率限制  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到所有输入校验和速率限制） / 高
- 代表报告: https://hackerone.com/reports/170310

### [219215] 支付接收方参数可篡改导致支付不一致  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（支付流程、业务逻辑） / 高
- 代表报告: https://hackerone.com/reports/219215

### [2106708] HEAD/GET 请求差异绕过 MIME 校验（TOCTOU）  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何基于 HEAD 校验的场景） / 高
- 代表报告: https://hackerone.com/reports/2106708

### [1849626] 业务逻辑幂等性缺失导致无限折扣  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何涉及金额或权益的操作，如优惠券、积分、折扣等） / 高
- 代表报告: https://hackerone.com/reports/1849626

### [808975] 浮点数舍入误差绕过佣金  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何涉及金额计算的应用，如佣金、折扣、税收等） / 高
- 代表报告: https://hackerone.com/reports/808975

### [1089978] 支付金额字段篡改导致超收或退款  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何涉及金额计算的业务） / 高
- 代表报告: https://hackerone.com/reports/1089978

### [889795] 路径归一化差异导致授权绕过（path="." 共享根目录）  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何涉及路径解析的授权检查，如文件分享、API 访问控制） / 高
- 代表报告: https://hackerone.com/reports/889795


## 路径遍历 （25 个候选）

### [436928] 路径遍历结合chmod修改权限实现RCE  (★4次, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何文件上传和权限管理场景） / 高
- 同簇报告(4): 436928, 298873, 733072, 519220
- 代表报告: https://hackerone.com/reports/436928

### [850775] Windows 反斜杠路径绕过  (★3次, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他平台路径处理） / 高
- 同簇报告(3): 850775, 315760, 797159
- 代表报告: https://hackerone.com/reports/850775

### [1408692] Android 路径遍历：使用 /data/user/0/ 替代 /data/data/ 绕过路径前缀检查  (★2次, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他路径校验、符号链接场景） / 高
- 同簇报告(2): 1408692, 377107
- 代表报告: https://hackerone.com/reports/1408692

### [1439593] tar 解压 symlink 导致任意文件读取  (★2次, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何文件解压场景） / 高
- 同簇报告(2): 1439593, 827052
- 代表报告: https://hackerone.com/reports/1439593

### [1912777] SFTP 路径 ~ 解析差异导致路径遍历  (★2次, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他协议或工具中的路径解析差异） / 高
- 同簇报告(2): 1912777, 1131465
- 代表报告: https://hackerone.com/reports/1912777

### [270068] 路径遍历绕过start_with?检查  (★2次, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他语言和框架的路径检查逻辑） / 高
- 同簇报告(2): 270068, 486933
- 代表报告: https://hackerone.com/reports/270068

### [288955] Android 导出组件 URI 解码差异与符号链接实现任意文件读写  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何文件处理场景，如导出组件、文件上传） / 高
- 代表报告: https://hackerone.com/reports/288955

### [822262] Nuget 包上传路径遍历结合竞态条件实现任意文件读取  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何包管理器或文件上传功能） / 高
- 代表报告: https://hackerone.com/reports/822262

### [301432] CI 缓存 key 路径遍历导致跨项目缓存投毒  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 CI/CD 系统如 Jenkins、CircleCI 的缓存机制） / 高
- 代表报告: https://hackerone.com/reports/301432

### [413193] HTTP 参数污染截断后缀实现路径遍历  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他参数污染场景） / 高
- 代表报告: https://hackerone.com/reports/413193

### [682774] Windows 路径规范化与符号链接导致任意文件创建  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到 Windows 应用、日志处理） / 高
- 代表报告: https://hackerone.com/reports/682774

### [317321] 利用符号链接在解压时删除任意目录  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他解压场景，如 ZIP、TAR） / 高
- 代表报告: https://hackerone.com/reports/317321

### [1404731] URL编码二次解码绕过路径遍历补丁  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何URL解码场景，如WAF绕过、路径校验） / 高
- 代表报告: https://hackerone.com/reports/1404731

### [344595] tar 硬链接任意文件覆盖  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何 tar 解压场景） / 高
- 代表报告: https://hackerone.com/reports/344595

### [637840] 客户端信任服务器路径导致dlopen任意文件  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到客户端安全、文件加载） / 高
- 代表报告: https://hackerone.com/reports/637840

### [270072] symlink 绕过 realpath 检查实现任意文件写入  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到文件上传、解压、安装等场景） / 高
- 代表报告: https://hackerone.com/reports/270072

### [1115864] Android ContentProvider 路径遍历导致持久化代码执行  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何 Android 应用，涉及 ContentProvider、导出组件、文件写入） / 高
- 代表报告: https://hackerone.com/reports/1115864

### [1952978] Node.js 权限策略未处理路径遍历  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何权限检查系统，强调路径规范化） / 高
- 代表报告: https://hackerone.com/reports/1952978

### [1004007] 路径解析差异（..;）绕过代理  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（路径遍历、WAF绕过、代理配置等场景均可迁移） / 高
- 代表报告: https://hackerone.com/reports/1004007

### [1415820] URL 编码的路径遍历绕过静态文件服务过滤  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到所有静态文件服务） / 高
- 代表报告: https://hackerone.com/reports/1415820

### [1132378] open-uri误用导致任意文件读取和SSRF  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用open-uri或类似库的语言，如Python的urllib） / 高
- 代表报告: https://hackerone.com/reports/1132378

### [2302558] 路径遍历（..）创建无法管理的资源导致持久后门  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何资源创建和管理场景，如用户、文件、配置） / 高
- 代表报告: https://hackerone.com/reports/2302558

### [2168002] 导入流程中 /proc/self/fd 竞速导致 XSS 和 DoS  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何导入文件路径与上传临时文件交互的场景） / 高
- 代表报告: https://hackerone.com/reports/2168002

### [1765631] 反斜杠与正斜杠转换差异绕过路径验证  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（跨平台路径分隔符差异普遍存在） / 高
- 代表报告: https://hackerone.com/reports/1765631

### [310690] indexOf返回-1导致路径遍历过滤失效  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何使用indexOf进行过滤的路径遍历、SSRF、命令注入等场景） / 高
- 代表报告: https://hackerone.com/reports/310690


## SSRF （24 个候选）

### [61312] IPv6环回地址绕过SSRF防护  (★5次, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到所有SSRF防护场景） / 高
- 同簇报告(5): 61312, 1379656, 736867, 1702864, 288950
- 代表报告: https://hackerone.com/reports/61312

### [1364797] URL 路径解析差异绕过 SSRF 防护  (★5次, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何 URL 校验场景） / 高
- 同簇报告(5): 1364797, 423437, 1747596, 643622, 180434
- 代表报告: https://hackerone.com/reports/1364797

### [878779] SSRF绕过：URL解码和开放重定向链  (★2次, max_score 10)
- 频率/迁移/来源: 高频 / 高（SSRF防护、URL解析、重定向链均可迁移） / 高
- 同簇报告(2): 878779, 287496
- 代表报告: https://hackerone.com/reports/878779

### [776017] Kubernetes StorageClass SSRF 升级为完全控制  (★2次, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他云原生组件） / 高
- 同簇报告(2): 776017, 941178
- 代表报告: https://hackerone.com/reports/776017

### [53004] DNS rebinding 绕过回调 URL 黑名单  (★2次, max_score 9)
- 频率/迁移/来源: 高频 / 高（可迁移到 SSRF 防护、DNS 安全） / 高
- 同簇报告(2): 53004, 1369312
- 代表报告: https://hackerone.com/reports/53004

### [885975] 利用PDF生成器读取本地文件实现SSRF  (★2次, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他PDF生成器或HTML渲染引擎） / 高
- 同簇报告(2): 885975, 1628209
- 代表报告: https://hackerone.com/reports/885975

### [374737] Sentry source code scraping 配置缺陷导致盲SSRF  (★2次, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他第三方组件配置缺陷导致的SSRF，如监控、日志系统） / 高
- 同簇报告(2): 374737, 756149
- 代表报告: https://hackerone.com/reports/374737

### [713900] SSRF绕过白名单结合模板注入实现RCE  (单例, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到任何SSRF和模板注入场景） / 高
- 代表报告: https://hackerone.com/reports/713900

### [341876] SSRF 到 Kubernetes RCE 的完整攻击链  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到云环境 SSRF 利用） / 高
- 代表报告: https://hackerone.com/reports/341876

### [237381] FFmpeg HLS 处理 SSRF  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到媒体处理、文件上传场景） / 高
- 代表报告: https://hackerone.com/reports/237381

### [1354335] SSRF 结合 Gopher 攻击 FastCGI  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他内部协议） / 高
- 代表报告: https://hackerone.com/reports/1354335

### [826361] CarrierWave remote_attachment_url 属性导致 SSRF  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到框架属性清理、SSRF 防护） / 高
- 代表报告: https://hackerone.com/reports/826361

### [115748] SSRF 协议混淆绕过过滤  (单例, max_score 9)
- 频率/迁移/来源: 高频 / 高（可迁移到其他 SSRF 防护绕过） / 高
- 代表报告: https://hackerone.com/reports/115748

### [287245] Ruby Resolv解析畸形IP返回空导致SSRF绕过  (单例, max_score 9)
- 频率/迁移/来源: 高频 / 高（可迁移到其他语言或库的IP解析差异） / 高
- 代表报告: https://hackerone.com/reports/287245

### [392859] gopher 协议 + 302 重定向绕过 SSRF 黑名单  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何支持 gopher 的 HTTP 客户端） / 高
- 代表报告: https://hackerone.com/reports/392859

### [429617] 反向代理 Host 头信任导致敏感头泄露  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用反向代理的场景） / 高
- 代表报告: https://hackerone.com/reports/429617

### [632101] DNS 重绑定绕过 SSRF 防护（DNS 解析失败时跳过 IP 检查）  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何基于 DNS 解析的 IP 过滤场景） / 高
- 代表报告: https://hackerone.com/reports/632101

### [326040] 插件功能滥用导致 SSRF 访问云元数据  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何插件系统、OAuth 实现、URL 参数处理） / 高
- 代表报告: https://hackerone.com/reports/326040

### [925527] SSRF 绕过：DNS rebinding 和未检查 IP 范围（0.0.0.0, 169.254.0.0/16）  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何 SSRF 防护场景，包括 WAF、内网访问控制） / 高
- 代表报告: https://hackerone.com/reports/925527

### [369451] CI 运行状态差异导致 SSRF 防护绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何依赖状态的安全机制，如缓存、初始化逻辑） / 高
- 代表报告: https://hackerone.com/reports/369451

### [187520] 利用重定向绕过SSRF的IP/端口过滤并支持basic-auth  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何SSRF防护，如WAF、代理） / 高
- 代表报告: https://hackerone.com/reports/187520

### [1608039] 云元数据服务地址遗漏  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移至所有云环境） / 高
- 代表报告: https://hackerone.com/reports/1608039

### [809248] 信任边界内组件不可信导致 SSRF  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何信任边界内的组件交互） / 高
- 代表报告: https://hackerone.com/reports/809248

### [333419] TURN 服务器允许代理到内网导致 SSRF  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他代理协议，如 SOCKS、HTTP CONNECT） / 高
- 代表报告: https://hackerone.com/reports/333419


## 命令注入 （23 个候选）

### [587854] git archive 参数注入导致 RCE  (★4次, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他命令注入场景） / 高
- 同簇报告(4): 587854, 653125, 315773, 925324
- 代表报告: https://hackerone.com/reports/587854

### [497312] ShellExecute 非 http 前缀命令注入  (★3次, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用 ShellExecute 的桌面应用） / 高
- 同簇报告(3): 497312, 122113, 495382
- 代表报告: https://hackerone.com/reports/497312

### [390871] 跨平台模块行为差异导致命令注入  (★2次, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他跨平台模块） / 高
- 同簇报告(2): 390871, 1609965
- 代表报告: https://hackerone.com/reports/390871

### [2471956] GitHub Actions 命令注入：通过 PR 标题利用未加引号变量窃取 token  (单例, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到其他 CI/CD 系统，如 Jenkins、CircleCI） / 高
- 代表报告: https://hackerone.com/reports/2471956

### [104465] git 子模块 ext 协议命令执行  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 git 协议利用） / 高
- 代表报告: https://hackerone.com/reports/104465

### [212696] escapeshellcmd 不转义空格导致命令参数注入（GraphicsMagick）  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他命令注入场景） / 高
- 代表报告: https://hackerone.com/reports/212696

### [214022] 通过备份恢复功能绕过输入限制实现命令注入  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他备份/恢复功能、数据导入导出场景） / 高
- 代表报告: https://hackerone.com/reports/214022

### [1838674] ImageMagick MSL 功能滥用导致 RCE  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他图像处理库） / 高
- 代表报告: https://hackerone.com/reports/1838674

### [955016] Windows路径规范化绕过命令注入防护  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何拼接前缀后执行外部程序的场景，如命令执行、程序加载） / 高
- 代表报告: https://hackerone.com/reports/955016

### [973386] 黑名单过滤不完整导致参数注入  (单例, max_score 9)
- 频率/迁移/来源: 高频 / 高（命令注入、参数注入、SSRF 等） / 高
- 代表报告: https://hackerone.com/reports/973386

### [1785378] bash PS1 二次求值命令注入  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（shell 环境、命令注入） / 高
- 代表报告: https://hackerone.com/reports/1785378

### [390881] 原型污染触发 morgan 代码注入  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到所有使用 Function() 的库） / 高
- 代表报告: https://hackerone.com/reports/390881

### [851807] bash 子命令替换绕过参数过滤实现 RCE  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何 shell 命令拼接场景） / 高
- 代表报告: https://hackerone.com/reports/851807

### [1401444] Lua沙箱逃逸通过loadstring  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他沙箱逃逸场景） / 高
- 代表报告: https://hackerone.com/reports/1401444

### [260005] ssh:// URI 解析差异导致RCE  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何处理URI的组件，如下载器、版本控制工具） / 高
- 代表报告: https://hackerone.com/reports/260005

### [164224] Smarty 模板引擎 {php} 标签导致 SSTI  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他模板引擎如 Twig、Jinja2） / 高
- 代表报告: https://hackerone.com/reports/164224

### [730111] Node.js子进程命令拼接导致命令注入  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何使用子进程执行命令的场景） / 高
- 代表报告: https://hackerone.com/reports/730111

### [682442] Git 命令选项注入导致任意文件读取  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何命令行工具的参数注入） / 高
- 代表报告: https://hackerone.com/reports/682442

### [1161691] open()函数处理用户可控文件名导致命令注入  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用open()的场景） / 高
- 代表报告: https://hackerone.com/reports/1161691

### [288704] 用户输入注入命令行参数（分支名注入--config）  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（命令注入、参数注入、钩子执行等场景均可迁移） / 高
- 代表报告: https://hackerone.com/reports/288704

### [319467] npm 库命令注入（macaddress）  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到所有库输入校验） / 高
- 代表报告: https://hackerone.com/reports/319467

### [692603] 恶意 .deb 包利用 postinst 脚本提权  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他包管理器如 RPM） / 高
- 代表报告: https://hackerone.com/reports/692603

### [449482] Pathname管道符命令注入  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移至其他语言类似API） / 高
- 代表报告: https://hackerone.com/reports/449482


## 类型混淆 （20 个候选）

### [960244] GraphQL object_from_id 类型混淆导致授权绕过  (★2次, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到任何使用 GraphQL 的 API） / 高
- 同簇报告(2): 960244, 858671
- 代表报告: https://hackerone.com/reports/960244

### [966347] 负 consume() 导致未初始化内存泄露  (★2次, max_score 9)
- 频率/迁移/来源: 低频 / 高（可迁移到任何对长度参数缺乏非负校验的库） / 高
- 同簇报告(2): 966347, 330351
- 代表报告: https://hackerone.com/reports/966347

### [1595299] C语言隐式类型转换导致越界读取  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何C/C++代码审计） / 高
- 代表报告: https://hackerone.com/reports/1595299

### [2256167] Node.js权限模型绕过：Uint8Array类型路径  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（类型混淆、权限绕过、路径遍历防护均可迁移） / 高
- 代表报告: https://hackerone.com/reports/2256167

### [1455248] 整数溢出导致缓冲区分配不足进而堆溢出  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他C扩展、语言实现） / 高
- 代表报告: https://hackerone.com/reports/1455248

### [321692] JavaScript弱类型导致未初始化Buffer  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他JS库的类型混淆） / 高
- 代表报告: https://hackerone.com/reports/321692

### [298246] Ruby pack/unpack 负长度导致缓冲区下读  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他语言库的符号错误检查） / 高
- 代表报告: https://hackerone.com/reports/298246

### [182169] 异常状态注入导致类型混淆  (单例, max_score 9)
- 频率/迁移/来源: 低频 / 高（可迁移到其他语言运行时异常处理） / 高
- 代表报告: https://hackerone.com/reports/182169

### [175315] 整数溢出导致内存破坏（Locale方法）  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他语言/框架的整数溢出处理） / 高
- 代表报告: https://hackerone.com/reports/175315

### [419896] 数组null字节绕过present?触发IS NULL查询  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（适用于任何使用present?或类似检查的Rails应用） / 高
- 代表报告: https://hackerone.com/reports/419896

### [49652] React children 类型混淆导致 XSS  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他前端框架的类似类型混淆问题） / 高
- 代表报告: https://hackerone.com/reports/49652

### [386807] MongoDB 盲注提取密码重置令牌  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到所有 NoSQL 数据库） / 高
- 代表报告: https://hackerone.com/reports/386807

### [449356] 类型混淆导致 SQL 查询变为 IN 子句，提高暴力破解效率  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用参数化查询但未严格校验类型的场景） / 高
- 代表报告: https://hackerone.com/reports/449356

### [358570] PHP数组参数类型混淆导致SQL注入  (单例, max_score 9)
- 频率/迁移/来源: 高频 / 高（可迁移到其他语言或框架的数组参数处理） / 高
- 代表报告: https://hackerone.com/reports/358570

### [1183335] 对象注入导致SQL语义改变实现认证绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他ORM或SQL构建库，如Knex、Sequelize等） / 高
- 代表报告: https://hackerone.com/reports/1183335

### [116286] Python partial对象类型混淆导致内存破坏  (单例, max_score 8)
- 频率/迁移/来源: 低频 / 高（可迁移到其他语言运行时类型混淆攻击） / 高
- 代表报告: https://hackerone.com/reports/116286

### [1444539] libcurl 在 64 位 Windows 上的整数截断导致内存泄露  (单例, max_score 8)
- 频率/迁移/来源: 低频 / 高（可迁移到其他跨平台库或系统） / 高
- 代表报告: https://hackerone.com/reports/1444539

### [181321] mruby Array#to_h 回调导致 UAF  (单例, max_score 8)
- 频率/迁移/来源: 低频 / 高（可迁移到其他语言运行时或回调机制） / 高
- 代表报告: https://hackerone.com/reports/181321

### [319532] Node.js Buffer构造函数对非字符串类型的隐式转换导致DoS  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他语言或框架的类似API） / 高
- 代表报告: https://hackerone.com/reports/319532

### [340053] 原型链 getter 导致类型混淆和 UAF  (单例, max_score 8)
- 频率/迁移/来源: 低频 / 高（可迁移到其他类型检查不严格的场景） / 高
- 代表报告: https://hackerone.com/reports/340053


## 反序列化 （16 个候选）

### [410212] 利用phar://触发二次反序列化绕过长度限制  (★3次, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用unserialize的PHP应用） / 高
- 同簇报告(3): 410212, 410237, 403083
- 代表报告: https://hackerone.com/reports/410212

### [473888] Rails Marshal 反序列化 RCE  (★2次, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他使用 Marshal 的框架） / 高
- 同簇报告(2): 473888, 413388
- 代表报告: https://hackerone.com/reports/473888

### [1189419] XMLRPC 未限制反序列化类导致 RCE  (★2次, max_score 9)
- 频率/迁移/来源: 中频 / 高（适用于所有 XMLRPC 实现） / 高
- 同簇报告(2): 1189419, 198734
- 代表报告: https://hackerone.com/reports/1189419

### [55029] PHP unserialize 中 DateTimeZone 对象的 use-after-free 漏洞  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他反序列化漏洞、内存破坏场景） / 高
- 代表报告: https://hackerone.com/reports/55029

### [1679624] Ruby对象方法覆盖结合Redis协议注入实现RCE  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（反序列化、Redis协议注入、方法覆盖均可迁移） / 高
- 代表报告: https://hackerone.com/reports/1679624

### [407552] 反序列化 gadget 链构造实现 RCE  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他反序列化场景） / 高
- 代表报告: https://hackerone.com/reports/407552

### [410882] phar 反序列化通过 getimagesize 触发实现未认证 RCE  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用 phar 协议的应用） / 高
- 代表报告: https://hackerone.com/reports/410882

### [159946] PHP 会话数据注入  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（会话处理、反序列化漏洞） / 高
- 代表报告: https://hackerone.com/reports/159946

### [921288] PHAR 反序列化触发任意文件删除  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到所有 PHP 文件系统函数） / 高
- 代表报告: https://hackerone.com/reports/921288

### [73257] YAML解析器中的!php/object标签触发反序列化  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他YAML解析器，如Python的PyYAML） / 高
- 代表报告: https://hackerone.com/reports/73257

### [2334460] 绕过反序列化保护配置（enable_xcom_pickling=False）实现RCE  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他反序列化保护被绕过的场景） / 高
- 代表报告: https://hackerone.com/reports/2334460

### [146233] PHP GC算法UAF导致反序列化RCE  (单例, max_score 8)
- 频率/迁移/来源: 低频 / 高（可迁移到PHP反序列化漏洞利用） / 高
- 代表报告: https://hackerone.com/reports/146233

### [350401] Node.js 反序列化中利用 IIFE 和全局对象访问执行任意代码  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 Node.js 反序列化场景，如 JSON.parse 的 reviver 函数） / 高
- 代表报告: https://hackerone.com/reports/350401

### [1702859] Ruby JSON.load 反序列化导致 ReDoS 或意外对象  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他使用 JSON.load 的 Ruby 应用） / 高
- 代表报告: https://hackerone.com/reports/1702859

### [274990] 绕过Psych.safe_load通过YAML到Marshal转换实现RCE  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他使用YAML反序列化的语言和框架，如Python的PyYAML、Java的SnakeYAML） / 高
- 代表报告: https://hackerone.com/reports/274990

### [1529790] 通过Kafka Connect的JAAS配置触发JNDI注入实现RCE  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他使用JNDI的中间件，如Tomcat、Spring） / 高
- 代表报告: https://hackerone.com/reports/1529790


## 竞争条件 （13 个候选）

### [1929597] siglongjmp 竞争条件导致崩溃  (★2次, max_score 8)
- 频率/迁移/来源: 低频 / 高（可迁移到其他信号处理竞争） / 高
- 同簇报告(2): 1929597, 1990421
- 代表报告: https://hackerone.com/reports/1929597

### [300305] TOCTOU race condition in email verification  (单例, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到任何验证流程） / 高
- 代表报告: https://hackerone.com/reports/300305

### [768110] 利用TOCTOU竞争条件和NTFS机会锁进行文件替换实现本地权限提升  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何涉及文件验证后使用的场景） / 高
- 代表报告: https://hackerone.com/reports/768110

### [1251464] SUID 二进制竞态条件提权  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到文件系统安全、提权场景） / 高
- 代表报告: https://hackerone.com/reports/1251464

### [1520931] Rust标准库remove_dir_all的TOCTOU漏洞  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他文件操作API） / 高
- 代表报告: https://hackerone.com/reports/1520931

### [2078571] curl fopen TOCTOU竞态导致符号链接跟随  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到文件操作安全） / 高
- 代表报告: https://hackerone.com/reports/2078571

### [859962] DNS解析TOCTOU绕过apiserver代理过滤  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到SSRF防护、代理过滤） / 高
- 代表报告: https://hackerone.com/reports/859962

### [2039870] renameat2原子交换制造TOCTOU竞态  (单例, max_score 9)
- 频率/迁移/来源: 低频 / 高（适用于任何存在TOCTOU的代码，可迁移到文件操作） / 高
- 代表报告: https://hackerone.com/reports/2039870

### [1897203] 多线程竞争导致HSTS double-free  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（适用于任何多线程共享资源场景） / 高
- 代表报告: https://hackerone.com/reports/1897203

### [858603] 硬链接与日志文件竞争条件 DoS  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（文件系统攻击、竞争条件） / 高
- 代表报告: https://hackerone.com/reports/858603

### [55140] OAuth2 实现中的竞争条件导致 token 撤销绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 token 管理场景） / 高
- 代表报告: https://hackerone.com/reports/55140

### [578119] logrotate 竞争条件导致权限提升  (单例, max_score 8)
- 频率/迁移/来源: 低频 / 高（可迁移到其他日志轮转工具，如 logrotate 的替代品） / 高
- 代表报告: https://hackerone.com/reports/578119

### [381356] 客户端竞争条件+postMessage无源检查+data:URL钓鱼  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他客户端竞态和消息验证场景） / 高
- 代表报告: https://hackerone.com/reports/381356


## 原型污染 （8 个候选）

### [454365] jQuery $.extend 原型污染  (★3次, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何深拷贝函数） / 高
- 同簇报告(3): 454365, 980649, 801522
- 代表报告: https://hackerone.com/reports/454365

### [869574] 原型污染导致 SQL 注入或 DoS（TypeORM mergeDeep）  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他深拷贝库如 lodash.merge、jQuery.extend 等） / 高
- 代表报告: https://hackerone.com/reports/869574

### [968355] 使用constructor.prototype绕过__proto__黑名单实现原型污染  (单例, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到任何JavaScript应用） / 高
- 代表报告: https://hackerone.com/reports/968355

### [1431042] console.table 原型污染  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用 console.table 的 Node.js 应用） / 高
- 代表报告: https://hackerone.com/reports/1431042

### [712065] lodash 原型污染：zipObjectDeep 函数  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到其他原型污染场景） / 高
- 代表报告: https://hackerone.com/reports/712065

### [998398] 原型污染 + eval gadget 实现 XSS  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何使用不安全解析函数的场景） / 高
- 代表报告: https://hackerone.com/reports/998398

### [878181] 原型污染注入NODE_OPTIONS导致RCE  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他环境变量注入） / 高
- 代表报告: https://hackerone.com/reports/878181

### [1280002] Mermaid 原型污染导致存储 XSS  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用不安全合并的 JavaScript 库） / 高
- 代表报告: https://hackerone.com/reports/1280002


## 信息泄露 （6 个候选）

### [491473] URL重定向差异作为侧信道提取数据  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何有状态差异的场景） / 高
- 代表报告: https://hackerone.com/reports/491473

### [2244229] 跨域导入动态JS文件窃取用户信息  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何依赖cookie生成动态JS的场景，如用户个性化脚本） / 高
- 代表报告: https://hackerone.com/reports/2244229

### [2209665] 利用URL编码差异绕过敏感信息掩码  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何基于参数解析的掩码/过滤机制） / 高
- 代表报告: https://hackerone.com/reports/2209665

### [1173436] 默认配置导致隐私数据泄露（联邦云 ID 发送到查找服务器）  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他默认配置导致数据泄露的场景） / 高
- 代表报告: https://hackerone.com/reports/1173436

### [1262434] 会话参数经Referer泄露导致店铺密码绕过  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何含权限参数的URL） / 高
- 代表报告: https://hackerone.com/reports/1262434

### [2382120] API与GraphQL权限不一致导致信息泄露  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（任何同时提供API和GraphQL的应用都可能存在） / 高
- 代表报告: https://hackerone.com/reports/2382120


## 代码注入 （5 个候选）

### [390929] 原型污染控制模板引擎配置导致 RCE  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他模板引擎如 EJS、Pug） / 高
- 代表报告: https://hackerone.com/reports/390929

### [1636382] 代码生成中的注释逃逸注入  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何代码生成、模板渲染场景） / 高
- 代表报告: https://hackerone.com/reports/1636382

### [2039464] nginx-ingress 注解注入绕过 snippet 禁用导致代码执行  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他注解注入场景，如 Apache、Nginx 配置注入） / 高
- 代表报告: https://hackerone.com/reports/2039464

### [346516] 依赖包中测试代码后门导致RCE  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到供应链审计、依赖安全扫描） / 高
- 代表报告: https://hackerone.com/reports/346516

### [894308] JSON Schema验证器代码生成注入导致RCE  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（任何使用代码生成的验证库都可能存在） / 高
- 代表报告: https://hackerone.com/reports/894308


## 配置错误 （5 个候选）

### [2262939] CDN配置指向未认领S3桶导致供应链攻击  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他云服务配置审计） / 高
- 代表报告: https://hackerone.com/reports/2262939

### [1238482] AWS Load Balancer Controller 标签伪造安全组归属  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他云服务或组件） / 高
- 代表报告: https://hackerone.com/reports/1238482

### [347296] 构建沙箱反向SSH隧道访问内部Docker Registry  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何CI/CD环境或沙箱环境） / 高
- 代表报告: https://hackerone.com/reports/347296

### [714215] OpenSSL环境变量覆盖默认配置路径导致代码执行  (单例, max_score 8)
- 频率/迁移/来源: 低频 / 高（可迁移到其他环境变量覆盖场景） / 高
- 代表报告: https://hackerone.com/reports/714215

### [783360] Spring Boot Actuator heapdump 泄露  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他框架的类似端点） / 高
- 代表报告: https://hackerone.com/reports/783360


## 缓存投毒 （4 个候选）

### [303730] X-Forwarded-Host缓存投毒导致存储型XSS  (★2次, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他缓存投毒场景） / 高
- 同簇报告(2): 303730, 148300
- 代表报告: https://hackerone.com/reports/303730

### [728664] 利用平台调试头污染CDN缓存实现DoS  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他平台/CDN缓存投毒） / 高
- 代表报告: https://hackerone.com/reports/728664

### [334709] NULL 字节和超长 URL 导致缓存投毒  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到所有缓存系统） / 高
- 代表报告: https://hackerone.com/reports/334709

### [591302] 缓存投毒针对 CORS 头导致 DoS  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（适用于任何缓存服务器配置） / 高
- 代表报告: https://hackerone.com/reports/591302


## CSRF （3 个候选）

### [2326194] SameSite=Lax 子域隔离盲区 + 服务端不校验 Content-Type 导致 CSRF 集群接管  (★2次, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到任何同父域子域场景） / 高
- 同簇报告(2): 2326194, 303390
- 代表报告: https://hackerone.com/reports/2326194

### [423022] OAuth回调CSRF导致账户接管  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（OAuth、OpenID、社交登录等场景均可迁移） / 高
- 代表报告: https://hackerone.com/reports/423022

### [102376] 利用重定向参数绕过 CSRF 防护  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何依赖 token 的 CSRF 防护，且存在重定向参数） / 高
- 代表报告: https://hackerone.com/reports/102376


## SQL注入 （3 个候选）

### [31756] Drupal 数组键 SQL 注入导致 RCE  (单例, max_score 10)
- 频率/迁移/来源: 低频 / 高（可迁移到其他框架的类似函数） / 高
- 代表报告: https://hackerone.com/reports/31756

### [1663299] SQL注入逃逸事务结合反序列化实现RCE  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用事务和反序列化的系统） / 高
- 代表报告: https://hackerone.com/reports/1663299

### [1039821] 二阶SOQL注入通过异步查询执行  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他ORM或查询语言） / 高
- 代表报告: https://hackerone.com/reports/1039821


## 子域名接管 （3 个候选）

### [1439355] 利用GitHub用户名重命名后旧名称可注册接管Action仓库  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到其他供应链场景） / 高
- 代表报告: https://hackerone.com/reports/1439355

### [716677] CDN 域名分配机制滥用导致子域名接管  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（子域名接管、CSP 绕过、CDN 配置） / 高
- 代表报告: https://hackerone.com/reports/716677

### [1297689] S3 bucket 删除后 DNS 记录未清理导致子域名接管  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到其他云服务，如 Azure、GCP） / 高
- 代表报告: https://hackerone.com/reports/1297689


## IDOR （2 个候选）

### [842625] IDOR 获取敏感信息结合密码重置实现账户接管  (单例, max_score 10)
- 频率/迁移/来源: 高频 / 高（可迁移到任何有 IDOR 和密码重置功能的系统） / 高
- 代表报告: https://hackerone.com/reports/842625

### [447930] GraphQL node 接口暴露内部主键导致 IDOR  (单例, max_score 10)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用 GraphQL 且内部主键自增的系统） / 高
- 代表报告: https://hackerone.com/reports/447930


## 内存破坏 （2 个候选）

### [520903] Apache HTTP 本地提权：共享内存越界访问控制函数指针  (单例, max_score 10)
- 频率/迁移/来源: 低频 / 高（可迁移到其他使用共享内存的服务器软件） / 高
- 代表报告: https://hackerone.com/reports/520903

### [1269242] libcurl MQTT实现中UAF和double-free  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他网络库的内存管理） / 高
- 代表报告: https://hackerone.com/reports/1269242


## 其他 （2 个候选）

### [181319] mruby String#lines 迭代器修改导致悬垂指针  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到迭代器安全、内存安全） / 高
- 代表报告: https://hackerone.com/reports/181319

### [2255968] 哈希不绑定数据边界导致共识分叉  (单例, max_score 9)
- 频率/迁移/来源: 低频 / 高（可迁移到任何拼接哈希的数据结构） / 高
- 代表报告: https://hackerone.com/reports/2255968


## XXE （2 个候选）

### [1095645] LIBXML_NOENT 标志导致 XXE（框架行为变化）  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 XML 解析库的配置） / 高
- 代表报告: https://hackerone.com/reports/1095645

### [845832] SVG 上传触发 XXE 进而 SSRF/LFI  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移到任何 XML 上传解析场景，如 DOCX、XLSX、SVG 等） / 高
- 代表报告: https://hackerone.com/reports/845832


## CRLF注入 （1 个候选）

### [1200647] 配置注入导致 RCE（CRLF 注入配置项）  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他配置驱动的应用） / 高
- 代表报告: https://hackerone.com/reports/1200647


## CSP绕过 （1 个候选）

### [2279346] CSP绕过利用Angular库和nonce窃取  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到其他使用Angular或类似框架的CSP绕过） / 高
- 代表报告: https://hackerone.com/reports/2279346


## 开放重定向 （1 个候选）

### [236599] stristr子串匹配绕过开放重定向保护  (单例, max_score 9)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用子串匹配的校验场景） / 高
- 代表报告: https://hackerone.com/reports/236599


## 沙箱逃逸 （1 个候选）

### [809012] 沙箱逃逸通过原型链和 bind 方法  (单例, max_score 9)
- 频率/迁移/来源: 高频 / 高（适用于所有 JS 沙箱） / 高
- 代表报告: https://hackerone.com/reports/809012


## CSS注入 （1 个候选）

### [386334] CSS 注入枚举 CSRF token 并组合 XSS  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何使用 CSS 注入且 token 在页面中的场景，如邮件客户端、Web 应用） / 高
- 代表报告: https://hackerone.com/reports/386334


## DLL 劫持 （1 个候选）

### [630903] OpenSSL 配置文件搜索路径导致 DLL 劫持  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（DLL 劫持、路径搜索顺序、配置加载） / 高
- 代表报告: https://hackerone.com/reports/630903


## HTML注入 （1 个候选）

### [110578] HTML 注入利用 meta refresh 和单引号未转义绕过 CSP 窃取数据  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他 CSP 绕过场景） / 高
- 代表报告: https://hackerone.com/reports/110578


## LLM （1 个候选）

### [2372363] Unicode 标签字符隐藏提示注入  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到任何 LLM 输入处理） / 高
- 代表报告: https://hackerone.com/reports/2372363


## WAF绕过 （1 个候选）

### [716761] WAF字符范围过滤不完整绕过  (单例, max_score 8)
- 频率/迁移/来源: 高频 / 高（可迁移至所有WAF绕过） / 高
- 代表报告: https://hackerone.com/reports/716761


## 资源消耗 （1 个候选）

### [774896] 未认证请求导致指标基数爆炸引发资源耗尽  (单例, max_score 8)
- 频率/迁移/来源: 中频 / 高（可迁移到其他监控系统或指标系统） / 高
- 代表报告: https://hackerone.com/reports/774896
