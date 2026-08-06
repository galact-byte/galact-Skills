---
name: hunt-prototype-pollution
description: 在授权渗透测试中挖掘 JavaScript 原型污染（prototype pollution，服务端 Node.js 与客户端）。当目标把用户可控的键名递归合并进对象（merge/extend/set/clone、JSON body、query 解析）时使用——典型场景：用 `__proto__`/`constructor.prototype` 注入属性，污染全局原型，进而 DoS、改逻辑、配合 gadget 提权到 XSS/RCE。适用目标类型 Web / REST API（Node.js） / 前端。触发场景包括用户说"测下原型污染""这个 merge 能不能 __proto__""污染原型打 RCE/XSS""lodash/jquery 有没有污染点"。输出：污染点 + 可用 gadget 判定 + 反射证据的 finding（含 killed 记录）。
allowed-tools: Read, Grep, Glob, Bash
---

# hunt-prototype-pollution · 原型污染猎杀

只解决**原型污染一类**：找到"用户可控键名进入递归合并/属性赋值"的点，用 `__proto__`/`constructor.prototype` 往 `Object.prototype` 注入属性，再看能否被下游 gadget 放大（模板/HTML sink→XSS、spawn/sourceURL→RCE、逻辑标志→提权）。判定靠**注入的属性在响应/行为中被观测到**。

污染是全局副作用，可能影响其他用户请求。默认注入**无害探针属性**（如 `huntpp`），确认污染后再评估 gadget，破坏性/持久化操作需授权。污染向量、常见 gadget、真实报告见 `reference.md`。

## Scope（授权范围）

**先确认授权。** 全局原型污染可能影响并发请求与后续行为。

落实：授权目标、测试窗口（污染可能残留到进程重启）、允许深度（仅探针 / 允许 gadget PoC）。任一不清楚就停下问。

## Goal

判定用户可控键名能否污染 `Object.prototype`，并评估可达 gadget 与影响（DoS / 逻辑绕过 / XSS / RCE），留存注入属性被反射或行为改变的证据。

## Workflow

`scope-check → recon → hunt → validate → report`。

### 1. scope-check
- **动作**：写 `evidence/scope.txt`。
- **命令**：`bash tools/recon.sh <target> --scope-only`。
- **终止条件**：scope 明确，否则 KILL。

### 2. recon
- **动作**：枚举吃 JSON body / 深合并 / query 的入口（配置、设置、批量更新、`merge`/`extend` 风格 API）。
- **输出**：`recon/endpoints.json`。
- **命令**：`bash tools/recon.sh <target>`。
- **终止条件**：至少 1 个候选入口。

### 3. hunt
- **动作**：对每个入口发多种污染向量（`__proto__[huntpp]`、`constructor[prototype][huntpp]`、JSON 嵌套 `__proto__`），再请求一个**回显对象属性**的端点或复用同接口，看 `huntpp` 是否出现在返回/默认值里。
- **输出**：`candidates.json`。
- **命令**：`python tools/hunt_protopollution.py --input recon/endpoints.json --output candidates.json [--probe-url <回显端点>]`。
- **终止条件**：`candidates.json` 生成。

### 4. validate → report
- **动作**：过 **7-Question Gate**，通过的评估 gadget（是否有 sink 放大）取证。任一 NO → killed。
- **命令**：`bash tools/validate.sh candidates.json`。
- **终止条件**：每条 confirmed/killed。

## 7-Question Gate（任一 NO 则 KILL）

1. 目标在**授权 scope** 内？
2. 键名确实进入**递归合并/属性赋值**？
3. 有**客观信号**（注入属性被反射 / 默认值被改 / 已知 gadget 触发），非猜测？
4. 达成了**全局原型污染**（影响其他对象），而非局部覆盖？
5. **可复现**（考虑污染残留，验证新连接仍受影响）？
6. 已留存**证据**？
7. 影响可陈述，且未做破坏性/持久化污染？

## Finding 输出格式

```
### <Title>
- Severity: Critical | High | Medium | Low | Info
- Asset: <入口 + 参数/JSON 路径>
- Reproduction: <污染向量 payload + 观测到 huntpp 的请求>
- Impact: <DoS / 逻辑绕过 / XSS / RCE（gadget）>
- Evidence: <evidence/ 原始 payload + 反射证据>
- Status: confirmed | killed(<第几问 NO>)
```

## 参考

污染向量、服务端/客户端 gadget、检测特征、真实报告见 `reference.md`。
