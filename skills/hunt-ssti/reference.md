# 模板与表达式验证参考

## 默认算术对照

1. 普通随机文本确认输入位置与原始响应。
2. 按技术线索选择一种表达式，例如 `{{7*7}}`、`${7*7}` 或 `<%= 7*7 %>`；不把某种语法当作所有引擎通用语法。
3. 改成另一算式，例如 `8*8`，核对结果确实随表达式变化。
4. 在原始 HTTP 正文或服务器生成文件中检查，区分浏览器 JS、客户端模板、预览器和真正的服务端计算。
5. 对照缓存、异步生成、错误页与普通反射，保留正常/变体请求响应。

直接提交 `49` 再看到 `49` 仅说明反射。页面本就包含 49、WAF 错误页含算式或浏览器执行模板都不足以确认 SSTI。

## 引擎与版本

| 线索 | 可以缩小的范围 | 局限 |
|---|---|---|
| `{{...}}` 算术 | Jinja2、Twig、Nunjucks、Pebble 等可能 | 单一输出不能唯一识别引擎 |
| `${...}` 算术 | FreeMarker、部分 EL、Mako 等可能 | Velocity/Thymeleaf 等不保证接受同一表达式 |
| `<%=...%>` | ERB/EJS 相应上下文 | 不同引擎和转义模式不同 |
| 字符串乘法差异 | 部分版本 Jinja2/Twig 的辅助线索 | 类型转换、配置或版本变化可使推断失效 |
| 错误类/堆栈 | 组件与调用路径线索 | 可被包装、伪造或缓存，不单独证明输入已执行 |

结合实际组件、版本和上下文保留“可能”范围。不要通过 Java Runtime、配置转储或枚举对象类树做默认指纹识别，它们可能读取秘密或触发更高影响动作。

## 执行层级与预期边界

确认服务端表达式求值后，仍需判断功能是否本就允许用户编写模板。预期内的受限模板算术不是自动成立的漏洞；需要证明用户输入被当作不应解释的模板代码，或越过实际授权/沙箱边界。

表达式执行、环境读取、任意文件读取、出网与 RCE 分层取证。旧教程中硬编码 `__subclasses__()` 索引依赖 Python 版本和进程类加载状态；某些 Twig 或 FreeMarker 执行链也取决于特定历史版本、对象暴露与配置，不能作为通用载荷。

需要进一步验证时先确认相应动作许可及隔离对象，再按实际组件官方文档选最小测试；不把算术成功直接升级为 RCE，不转储 config、环境或用户数据。

## 修复方向

避免将不受信任输入拼接进模板源码，将其作为数据参数传递。合法自定义模板功能还需能力约束、最小对象暴露和经过验证的隔离；单个字符过滤或 WAF 不能替代边界设计。

## 依据与关联

- [PortSwigger：Server-side template injection](https://portswigger.net/web-security/server-side-template-injection)
- [Jinja Sandbox](https://jinja.palletsprojects.com/en/stable/sandbox/)
- [FreeMarker：模板语言安全](https://freemarker.apache.org/docs/app_faq.html#faq_template_uploading_security)
- [命令注入](../hunt-command-injection/SKILL.md)
- [SSRF](../hunt-ssrf/SKILL.md)
