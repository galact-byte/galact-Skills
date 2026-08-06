# hunt-xss · 参考

真实报告源自本仓库第二轮高价值案例（value_score≥8）。探针标记统一 `hxss9f3a2b`，PoC 用 `alert(document.domain)`。

## 按上下文的 payload

### HTML body
```
<script>alert(document.domain)</script>
<img src=x onerror=alert(document.domain)>
<svg onload=alert(document.domain)>
```

### 属性上下文（先闭合）
```
"><svg onload=alert(document.domain)>
' autofocus onfocus=alert(document.domain) x='
```
利用已有事件绑定（无需闭合标签）：注入 `onclick`/`onmouseover`（#227486、#396493）。

### JS 上下文
```
';alert(document.domain)//        </script><script>alert(document.domain)</script>
```

### URL / DOM
- `javascript:alert(document.domain)`（href/iframe src；Safari host 解析差异 #1238528）。
- `location.hash`/`search` → `innerHTML`/`document.write` sink。

## 绕过技巧（Bypasses）

- **SVG + XML 实体**使白名单/清理失效，注入 `onload`（#232174）。
- **iframe srcdoc** 加载外部脚本绕 CSP（#1342009）。
- **WAF 绕过**：`%u0022`→`"`（#227486）、大小写/换行/注释、`<svg/onload=`、事件属性无空格。
- **CSP 绕过**：JSONP 端点、`eval` + URL 片段（#921635）、AngularJS/Vue 模板表达式（原型污染→#986386）、白名单里的可控 JS。
- **属性注入 + 现有事件**：不注脚本，注 `onclick` 复用页面已绑定（#227486、#396493）。
- **富文本/Markdown sink**：`data-sourcepos`/emoji `name` 属性注入（#1398305）、SwaggerUI（#806571）。
- **Electron nodeIntegration**：XSS→RCE（#291539，桌面端）。

## Detection Patterns（怎么判，而非猜）

- **标记未编码**：`hxss9f3a2b<>"'` 原样出现在响应 = 有反射；看 `<`/`"`/`'` 哪些没被实体化，定可用上下文。
- **上下文定位**：标记落在 `<script>` 内 / 属性内 / body 内决定 payload。
- **DOM 型**：源码里 `innerHTML=`/`eval(`/`document.write(` 消费 `location.*` = DOM sink；用无头验证。
- **执行确认**：无头浏览器（Playwright）加载 PoC，`alert`/`console` 触发 = confirmed。纯文本反射不算。
- **存储型**：提交后在**另一个页面/账户视图**触发才算存储型。

## Real Reports（复现索引）

| 类型/绕过 | 报告 |
|---|---|
| SVG XML 实体 onload | 232174 |
| iframe srcdoc CSP 绕过 | 1342009 |
| WAF %u0022 + 属性事件 | 227486 / 396493 |
| javascript: host 解析 | 1238528 |
| CSP 绕过 eval/fragment | 921635 |
| 富文本 sink | 1398305 / 806571 |
| Electron→RCE | 291539 |

hunt 顺序：唯一标记探反射与编码 → 定上下文 → 该上下文最小 PoC → 被拦再上 WAF/CSP 绕过 → 无头确认执行。

## 更多真实案例（第三轮单例补充）

（来自第二轮单例、第三轮语义路由归入本类；仅列此前未收录的报告，作案例索引）

- **XSS**
  - #1955370 Rails redirect_to控制字符导致XSS
  - #390344 移动应用内浏览器渲染附件时共享会话导致 XSS
  - #982291 CSS url(cid://) 绕过 HTML 过滤器
  - #724153 事件处理器绕过script标签过滤实现存储XSS并读取本地文件
  - #259100 JSONP/频道消息通道投递未转义反射导致XSS
  - #1212067 上传文件名引号逃逸+JSONP绕过CSP导致存储XSS
  - #1087061 git配置email注入HTML属性导致存储XSS
  - #1758132 autolink 正则缺陷导致 DOM XSS
  - #429298 表情解析中 URL 未校验结合 jQuery 自动执行导致存储型 XSS
  - #1404804 XSS filter bypass via js-xss parsing difference combined with HMAC and clickjacking
  - #463915 Universal XSS via postMessage in browser extension
  - #217745 window.open javascript: URL 导致 XSS
  - #84601 未知文件类型上传结合浏览器嗅探和AppCache缓存投毒
  - #473950 模板字符串拼接导致 WebView XSS
- **XSS过滤绕过**
  - #132104 编辑模式与预览模式安全检查不一致导致 XSS
  - #1731349 选择器与取值对象不一致导致XSS注入
  - #526325 Wiki 层级链接语法转换绕过 XSS 过滤
  - #229735 模板占位符二次注入绕过过滤
  - #1518343 利用javascript:伪协议和注释符绕过URL白名单
  - #1167034 八进制编码绕过大小写转换过滤实现 XSS
  - #246794 安全处理的状态标记由输入数据控制导致转义禁用
- **协议行为利用**
  - #79348 协议处理器JavaScript注入
  - #723175 跨站事件泄漏（xsleaks）实现去匿名化
  - #276105 利用 IE 内容嗅探绕过 nosniff 头实现 XSS
  - #39658 反射文件下载（Reflected File Download）
- **框架行为利用**
  - #2138080 Electron contextBridge序列化异常绕过上下文隔离
  - #1805899 HTML Sanitizer 嵌套标签绕过（svg+style）
  - #1805893 不完整修复导致XSS绕过（CVE-2022-23520）
  - #949513 Active Storage Proxying 允许 inline 导致 XSS
- **DOM XSS**
  - #662083 pushState 路径遍历绕过 admin 前缀实现 DOM XSS
  - #2371019 postMessage监听器未编码avatar_url导致DOM XSS
- **XSS绕过**
  - #1327196 CSP 仅对 HTML 生效，对 image/svg+xml 不生效导致 XSS
  - #85488 Unicode 转义序列解析差异绕过 XSS 过滤
  - #171670 HTML5 实体绕过 xss_clean() 正则过滤
- **XSS WAF绕过**
  - #1760213 WAF 与服务器解析差异绕过（双引号插入）
- **模板注入**
  - #991713 阅读器模式模板注入导致数据窃取
  - #1736317 客户端模板注入（CSTI）导致XSS，结合编码绕过
- **XSS注入**
  - #425007 Open Graph 标签注入导致持久性 XSS
  - #633231 WordPress shortcode 函数副作用导致 XSS
- **跨组件攻击链**
  - #899964 Electron 中 XSS 升级为 RCE（覆盖 RegExp.prototype.test）
  - #1893186 跨组件CSP绕过实现XSS
- **XSS账户接管**
  - #2010530 Cookie 解析差异（空格分隔）导致 Cookie 走私，结合 XSS 实现账户接管
- **Flash XSS**
  - #134546 Flash XSS 利用 URL 解析差异、ES6 模板字符串和浏览器行为绕过多层过滤
- **XSS配置错误**
  - #1444682 Swagger-UI configUrl 加载 data: 协议导致 XSS
- **内容类型注入**
  - #78158 Flash Content-Type injection bypass
- **WebView UXSS**
  - #1436558 WebView JS桥接和字符串拼接导致UXSS
- **ESI注入+XSS**
  - #1073780 ESI 注入与 XSS 链式利用窃取 HttpOnly Cookie
- **XS-Leak**
  - #1089914 HTML video/audio 标签 fallback 行为实现 XS-Leak
- **CSP绕过**
  - #2279346 CSP绕过利用Angular库和nonce窃取
- **供应链注入**
  - #218872 git submodule URL注入XSS
- **点击劫持**
  - #85624 点击劫持绕过（嵌套 iframe 与 CSP2 兼容性）
- **类型混淆**
  - #49652 React children 类型混淆导致 XSS
- **XSS到RCE**
  - #263718 同源iframe脚本导致权限提升（XSS到RCE）
- **XSS与缓存利用**
  - #1533976 HTML注入结合DOMPurify gadget和浏览器缓存实现任意POST请求
- **浏览器扩展安全**
  - #389108 浏览器扩展 postMessage 处理不当导致任意请求带 cookie
- **CSS注入**
  - #386334 CSS 注入枚举 CSRF token 并组合 XSS
- **HTML注入**
  - #110578 HTML 注入利用 meta refresh 和单引号未转义绕过 CSP 窃取数据
- **参数解析差异**
  - #293689 HTTP 参数重复解析差异绕过签名
- **XSS组合链**
  - #632017 存储XSS与登录/登出CSRF组合链实现ATO
- **SOP绕过**
  - #358005 data: URI iframe 继承父 origin 绕过 SOP
- **隐私绕过**
  - #1668815 利用window.caches绕过隐私保护
- **注入**
  - #474262 模板字符串未转义导致 XSS
- **竞争条件**
  - #381356 客户端竞争条件+postMessage无源检查+data:URL钓鱼
