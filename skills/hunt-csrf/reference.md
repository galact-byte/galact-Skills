# hunt-csrf · 参考

真实报告源自本仓库第二轮高价值案例（value_score≥8）。只在测试账户上验证。

## 防护三要素（先判缺口）

1. **CSRF token**：请求里有没有？服务端**真的校验**吗？（删了/改了还成功 = 未校验）
2. **SameSite cookie**：会话 cookie 的 SameSite=None / Lax / Strict？（None 最易打，Lax 有缺口，Strict 需子域/其他向量）
3. **头依赖**：是否要求不可跨站设置的头（自定义头触发 preflight）？用 `text/plain`/simple request 可避开。

## 绕过手法（Bypasses）

### token 相关
- token 缺失或**不校验**（#155774 强制关联手机号）。
- token 可预测/全局固定/跨用户通用。
- **cookie 注入 + 解析差异**伪造 token（#14883、#26647：分号/逗号/空格解析差把攻击者值当 token）。
- 静态文件/第三方页**泄露 token**（#127703、CloudFlare 场景 #260697）。

### SameSite=Lax 绕过
- **顶层导航 GET**：Lax 允许顶层 GET 带 cookie → 把状态变更做成 GET 即可（#1458236 Lax 下跨站 GET→SSRF）。
- **子域旁路**：从同站子域发起（SameSite 按站点判），配合子域 XSS/接管（#2326194 子域隔离盲区 + text/plain）。
- 新建会话的 120s 宽限窗口（部分浏览器旧行为）。

### preflight 绕过
- `Content-Type: text/plain`（或 `application/x-www-form-urlencoded`/`multipart`）= simple request，不触发 preflight，即使 JSON API 也可能接受（#2326194）。

### 其他向量
- **Flash + 307 重定向**保留 method/body 绕 CORS（#44146、#236349）。
- **Login CSRF**：强制受害者登录攻击者账户，再收集其行为（#229528、#384962）。

## Detection Patterns（怎么判，而非猜）

- **无 token 仍成功**：删除/清空 token 字段重放，操作仍生效 = 未校验（最硬）。
- **伪 token 成功**：改 token 值仍成功。
- **SameSite 观测**：`Set-Cookie` 里会话 cookie 的 SameSite 属性值决定可行向量。
- **跨站触发**：用 PoC 页面（不同 origin）发起后，测试账户状态改变 = confirmed。
- **simple request 被接受**：`text/plain` 的请求服务端仍处理 = 可避 preflight。

## Real Reports（复现索引）

| 缺口/绕过 | 报告 |
|---|---|
| token 未校验 | 155774 |
| cookie 注入伪造 token | 14883 / 26647 |
| token 泄露 | 127703 / 260697 |
| SameSite=Lax GET/子域 | 1458236 / 2326194 |
| text/plain 避 preflight | 2326194 |
| Flash 307 绕 CORS | 44146 / 236349 |
| Login CSRF | 229528 / 384962 |

hunt 顺序：先删 token 重放（最快证伪防护）→ 看 SameSite 决定向量 → JSON API 试 text/plain → Strict 时找子域/Flash 等旁路。

## 更多真实案例（第三轮单例补充）

（来自第二轮单例、第三轮语义路由归入本类；仅列此前未收录的报告，作案例索引）

- **CSRF**
  - #931197 跨站 WebSocket 劫持（Origin 检查绕过）
- **CSRF token缺陷**
  - #732415 CSRF token可逆性导致伪造（Rails per_form_csrf_tokens）
- **CSRF token泄露**
  - #221432 CSRF token泄露通过双斜杠绝对URL
- **深链接与CSRF**
  - #1741430 深链接参数未编码导致 CSRF 和路径穿越
- **OAuth CSRF**
  - #423022 OAuth回调CSRF导致账户接管
- **CSRF绕过**
  - #102376 利用重定向参数绕过 CSRF 防护
- **框架行为利用**
  - #189878 Rails data-remote表单CSRF令牌泄露
- **解析差异**
  - #49935 rails-ujs和jQuery的URL解析差异导致CSRF令牌泄露
- **认证绕过**
  - #161408 CSRF token置空或固定值绕过双重防护
