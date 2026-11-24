# WebSocket 参考与证据要求

## 官方依据

- [RFC 6455](https://datatracker.ietf.org/doc/html/rfc6455)：WebSocket 握手、Origin、子协议、帧与关闭机制。
- [RFC 8441](https://datatracker.ietf.org/doc/html/rfc8441)：HTTP/2 的 WebSocket 扩展 CONNECT，不能把 HTTP/1.1 的 101 套给所有传输。
- [OWASP WebSocket Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/WebSocket_Security_Cheat_Sheet.html)：来源校验、认证、消息授权、会话注销、资源保护与日志。
- [PortSwigger CSWSH](https://portswigger.net/web-security/websockets/cross-site-websocket-hijacking)：浏览器跨站握手、会话身份和双向能力的验证条件。
- [MDN WebSocket constructor](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/WebSocket)：浏览器构造器可用参数与子协议。
- [MDN Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie)：Cookie 属性与跨站携带条件。

## 条件不要混在一起

| 观察 | 说明 | 不能直接得出的结论 |
|---|---|---|
| 101 或工具显示 connected | 传输连接建立 | 已认证、可操作私有对象 |
| 非浏览器可伪造 Origin | 客户端可控制该请求头 | 普通恶意网页可带受害者身份 |
| 缺少 ACAO/CORS 响应头 | 不能按 fetch 的 CORS 判断 WS | 必然存在 CSWSH |
| 浏览器跨源握手 | 来源不同 | 必定跨站、Cookie 必定携带 |
| 登录后可订阅公共频道 | 正常或待核实功能 | 读取私密频道成功 |
| 注销后连接未关闭 | 连接生命周期现象 | 撤销后的消息仍被授权 |
| Token 放在查询串 | 可能暴露给日志/历史等处理链 | 已泄露给攻击者 |
| Socket.IO 返回握手包 | 上层协议初始化 | 任意 WebSocket JSON 可调用动作 |

## CSWSH 最小证据链

1. 测试账号在目标正常登录，权限与对象归属已知。
2. 测试页面在被允许的不同来源运行；记录 scheme、host、port 及站点关系。
3. 浏览器实际握手发送了可用身份；记录 Cookie 属性及浏览器策略，不公开凭据。
4. 服务器接受并在相同浏览器上下文中授予受保护消息/动作能力。
5. 负对照（不带有效身份或被拒来源）与正常同源对照能够区分该能力；只访问自有测试数据。

若目标必须提供脚本无法获得的首帧 Token/握手 nonce，不能手动填入后再称普通网页可利用。浏览器 WebSocket API 不提供任意设置握手 HTTP Header 的通用参数；不要编造 `headers` 选项。非浏览器客户端测试可以辅助定位服务端控制，但不能补齐浏览器证据链。

本参考不附带自动连接页面，避免脱离业务协议误发消息。应复用已捕获的自有测试流，并在许可范围内改一个消息字段；主动写入、重放和跨站页面托管分别受当前任务许可约束。

## 生命周期对照表

| 阶段 | 需要观察 |
|---|---|
| 连接建立 | Origin、Cookie/Token、子协议、匿名资源限制 |
| 应用认证 | 认证前后消息权限、超时/失败、身份绑定 |
| 加入/订阅 | 对象归属、租户、房间权限、订阅者身份 |
| 处理/投递消息 | 每个动作与事件数据是否仍在权限内 |
| 注销/过期/撤销 | HTTP 身份已失效；新消息/新事件、重连和订阅的实际行为 |
| 离开/取消/断开 | 不再接收受保护事件；资源释放与可观察清理结果 |

需要区分关闭帧、TCP 断开和业务订阅取消。连接断开可能自动重连；验证清理时不能漏掉客户端新建连接。短窗口只观察到静默不能证明已释放全部服务端资源。

## 上层协议

- **Socket.IO**：包含 Engine.IO 及自身事件/namespace 协议，可能先 polling 再升级；按实际版本与客户端文档还原。不能只改 WebSocket URL 就当作同一业务调用。
- **STOMP**：关注 CONNECT/SUBSCRIBE/SEND 的身份和 destination 权限；frame 的 ACK 不保证业务写入成功。
- **GraphQL 订阅**：子协议可能不同，初始化、订阅开始/完成消息不通用；使用已捕获格式，核实订阅对象和发布时的权限。
- **二进制消息**：先确定编码与 schema，不把未知字节当作可自由修改的 JSON。不注入未知序列化对象或触发解压/反序列化利用。

## 资源与日志

心跳、最大帧/消息、连接数、消息速率与压缩是否安全要结合实现、版本和负载配置。仅开启 `permessage-deflate` 不能确认敏感信息压缩侧信道；仅未看到限流响应不能确认无限制。优先使用配置与受控日志，无法安全验证时保留线索。

证据至少关联连接 ID、消息 ID、方向、UTC 时间、身份角色、对象和预期策略。HTTP 访问日志通常不足以证明消息级动作；必要时读取经授权的业务日志。Token、Cookie、完整聊天内容不出现在公共日志或报告中。
