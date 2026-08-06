# hunt-prototype-pollution · 参考

真实报告源自本仓库第二轮高价值案例（value_score≥8）。探针属性统一用 `huntpp`。

## 污染向量（Bypasses）

### JSON body（服务端 Node.js）
```json
{"__proto__":{"huntpp":"polluted"}}
{"constructor":{"prototype":{"huntpp":"polluted"}}}
```
`constructor.prototype` 用于绕过只过滤 `__proto__` 的防护（#968355）。

### query / 表单（被 qs/扁平键解析成嵌套）
```
?__proto__[huntpp]=polluted
?__proto__.huntpp=polluted
?constructor[prototype][huntpp]=polluted
```

### 易受影响的合并/赋值函数
- lodash `merge`/`mergeWith`/`defaultsDeep`（#380873）、`_.set`（#852613）。
- jQuery `$.extend(true, ...)`（深拷贝）。
- 手写递归 merge、`Object.assign` 嵌套、YAML/config 加载。

## Gadget（污染后如何放大）

### 服务端 → RCE
- 污染 `sourceURL`/spawn 选项 → 命令执行（#861744 Kibana）。
- 污染模板引擎默认配置项 → 模板/代码注入（#390929）。
- 污染 `shell`/`NODE_OPTIONS`/env 相关默认值 → spawn 时注入。

### 客户端 → XSS / CSP 绕过
- 污染属性流入 `innerHTML`/框架模板（AngularJS/Vue）→ XSS，甚至绕 CSP（#986386）。
- 污染 `String.prototype` 方法（如 `indexOf`）劫持逻辑（#470547）。

### 逻辑绕过
- 污染鉴权/开关默认标志（`isAdmin`/`enabled`）绕过检查（#310707、#311236）。

## Detection Patterns（怎么判，而非猜）

- **属性反射**：污染 `huntpp` 后，请求返回新对象里出现 `huntpp` 默认值 = 命中（最硬）。
- **默认值改变**：某个未提供的字段现在返回 `polluted` = 原型被污染。
- **行为改变/报错**：污染 `toString`/`then` 等常触发全局异常或 500，是强信号（也要小心 DoS 影响）。
- **客户端**：DevTools 里 `Object.prototype.huntpp` 存在 = 前端污染。
- **验证残留 vs 真污染**：换新会话/新对象仍带 `huntpp` 才算全局污染。

## Real Reports（复现索引）

| 向量/gadget | 报告 |
|---|---|
| lodash merge / _.set | 380873 / 852613 |
| constructor.prototype 绕过 | 968355 |
| →innerHTML/CSP 绕过 | 986386 |
| →sourceURL RCE | 861744 |
| →模板代码注入 | 390929 |
| String.prototype 劫持 | 470547 |
| 逻辑绕过 | 310707 / 311236 / 869574 |

hunt 顺序：先 JSON body `__proto__` 探针 → 无效再 `constructor.prototype` 与 query 变体 → 命中后按语言找 gadget（服务端优先 spawn/模板，客户端优先 HTML sink）。
