---
name: hunt-ssti
description: 在授权渗透测试中挖掘服务端模板注入与表达式语言注入（SSTI / EL Injection）。当目标把用户输入嵌入模板引擎渲染（Jinja2/Twig/Freemarker/Velocity/Thymeleaf/Pebble/Smarty/ERB/Pug/EL/SpEL/OGNL/MVEL）时使用——典型场景：自定义邮件模板、动态页面渲染、错误页面反射、PDF 生成含用户输入、Spring EL/OGNL 注入。适用目标类型 Web / REST API（Python/Java/PHP/Ruby/Node.js/.NET）。触发场景包括用户说"测下模板注入/SSTI""这个参数会不会被模板渲染""EL/SpEL/OGNL 注入测一下""页面有没有模板引擎"。输出：模板执行 + RCE/文件读取证据的 finding（区分确认、阻塞、未定与误报；影响逐层取证）。
allowed-tools: Read, Grep, Glob, Bash
---

# hunt-ssti · 模板/表达式注入猎杀

只解决**用户输入被模板引擎或表达式解析器执行一类**（SSTI、EL Injection、SpEL、OGNL）。先通过无副作用对照确认服务端求值和预期边界；引擎识别、文件读取、出网与命令执行分别取证，不从算术结果推断 RCE。

服务端表达式执行与 RCE 分层取证。默认使用无副作用算术，例如 `{{7*7}}` 与不同算式、普通文本对照；直接输入 `49` 再回显 `49` 只能证明反射。读取环境/文件、出网或执行命令需明确动作许可，不作为算术判活的默认下一步。方法见 [参考](reference.md)。

## Scope（授权范围）

**先确认授权。**

落实：授权目标、是否允许尝试命令执行、目标技术栈（Java/Python/PHP/Ruby/Node → 决定模板引擎类型）。

## Goal

识别模板/表达式注入点，确定引擎类型，证明可执行任意表达式，评估提权到 RCE 的可行性。

## Workflow

`scope-check → recon → hunt → validate → report`。

### 1. scope-check
- **动作**：确认授权、目标技术栈。
- **终止条件**：scope 明确。

### 2. recon — 识别模板渲染面
- **动作**：枚举用户输入可能进入模板渲染的位置：
  - 自定义邮件/通知模板（用户可编辑模板内容）
  - 动态页面内容（CMS、文章编辑器、模板预览）
  - 错误页面（404/500 页面反射用户输入）
  - PDF/报告生成（用户输入进入渲染）
  - 个人资料字段（用户名/签名/简介被渲染）
  - URL 路径/参数直接反射到页面
- **技术栈指纹**：
  - Java → Freemarker / Velocity / Thymeleaf / Pebble / SpEL / OGNL / MVEL
  - Python → Jinja2 / Mako / Tornado
  - PHP → Twig / Smarty / Blade
  - Ruby → ERB / Slim / Liquid
  - Node.js → Pug / Nunjucks / EJS / Handlebars
  - .NET → Razor

### 3. hunt — 判活与识别引擎

#### 3a. 通用判活（先用这组）
以下仅为按语法选取的候选，不是通用引擎指纹；行为取决于引擎、版本、上下文和配置。一次只测匹配当前线索的一项，核对原始 HTTP 响应，排除客户端计算与缓存。

```text
{{7*7}}       → 在部分 Jinja2/Twig 等环境中可能得到 49
${7*7}        → 在部分 FreeMarker/EL/Mako 等环境中可能得到 49
<%= 7*7 %>    → 在 ERB/EJS 对应上下文中可能得到 49
```

Velocity、Thymeleaf、Smarty 等使用各自语法，不能用此表一项失败就排除。再测另一算式及普通文本对照，避免只碰巧看到页面已有的 49。

#### 3b. 引擎识别（判活成功后）
结合错误类型、已知组件与受控算术/字符串差异缩小范围；单项输出不能唯一确定引擎。Java Runtime 类访问属于更高影响的尝试，不用于默认指纹识别。

例如 `{{7*'7'}}` 在部分 Jinja2 中可能得到重复字符串、部分 Twig 版本中可能得到数值；配置或版本不同也会报错，保留未知而不强行归类。

#### 3c. 影响评估

确认服务端解释受控表达式后先保存证据并评估预期安全边界。自定义模板功能若本就获准解释表达式，需另证越过沙箱或授权边界，不能仅凭算术判为漏洞。

文件读取、出网、沙箱逃逸和命令执行须在明确动作许可、版本/配置前提和隔离测试对象下单独验证；不运行来自旧版本教程的通用 RCE 链。不能从算术成功直接写成任意代码执行。

### 4. validate → report
- **动作**：逐项核对证据；缺许可记 blocked，执行环境不明记 inconclusive，对照证伪才记 false_positive。

## 7-Question Gate（证据不足不确认）

1. 目标在**授权 scope** 内？
2. 用户输入确实**被模板引擎解析执行**（非普通字符串拼接/XSS 反射）？
3. 有**数学运算结果回显**或等价客观证据（非猜测"可能是模板"）？
4. 已**识别引擎类型**或至少确认了执行环境？
5. **可复现**（稳定执行，非缓存/CDN 结果）？
6. 已留存**注入 payload + 执行结果**的完整证据？
7. 动作获准且未超出数据与执行边界，模板副本与测试对象已清理？

## 与其他 hunt skill 的链

- SSTI + `hunt-command-injection`：SSTI → RCE 本质上达到了命令注入的效果
- SSTI + `hunt-ssrf`：模板引擎访问内网资源
- SSTI + `hunt-xss`：模板注入在某些引擎下先表现为 XSS，升级后可达 SSTI

## Finding 输出格式

```
### <Title>
- Severity: Critical | High | Medium | Low
- Asset: <注入点 + 模板引擎类型>
- Reproduction: <判活 payload + 提权 payload + 请求>
- Impact: <RCE / 文件读取 / 信息泄露>
- Evidence: <evidence/ 计算回显 + 命令执行截图>
- Status: confirmed | inconclusive | blocked | false_positive | out_of_scope
```

## 参考

引擎识别、服务端/客户端对照、版本与沙箱边界见 [参考](reference.md)。
