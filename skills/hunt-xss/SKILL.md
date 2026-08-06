---
name: hunt-xss
description: 在授权渗透测试中挖掘跨站脚本（XSS：反射型、存储型、DOM 型，含 WAF/CSP 绕过与 sink 分析）。当目标把用户输入回显到 HTML/JS/属性/URL 上下文、或前端把可控数据喂给危险 sink（innerHTML/eval/srcdoc）时使用——典型场景：搜索/评论/标题回显、SVG/上传、postMessage、javascript: URL、模板属性注入、绕 CSP。适用目标类型 Web 前端 / REST API。触发场景包括用户说"测下 XSS""这个参数会不会弹窗""能绕 CSP/WAF 吗""DOM XSS/存储型看一下"。输出：XSS 触发点 + 上下文 + PoC 的 finding（含 killed 记录）。
allowed-tools: Read, Grep, Glob, Bash
---

# hunt-xss · 跨站脚本猎杀

只解决 **XSS 一类**：反射/存储/DOM。核心是"输入回显在什么上下文（HTML body / 属性 / JS / URL / SVG）"决定 payload 形态，先用**唯一标记**探反射与编码强度，再按上下文构造可执行 PoC，必要时绕 WAF/CSP。判定靠**标记未编码进入可执行上下文**。

XSS PoC 只用**无害标记/`alert(document.domain)`** 证明执行，不投放窃密/蠕虫脚本，不打真实用户。上下文 payload、绕过技巧、真实报告见 `reference.md`。

## Scope（授权范围）

**先确认授权。** 存储型会持久化到页面，影响其他用户。

落实：授权目标、允许存储型（会留痕，需能清理）、允许触碰的页面、PoC 仅用无害标记。任一不清楚就停下问。

## Goal

判定用户输入能否在浏览器上下文执行脚本，给出上下文、可复现 PoC（`alert(document.domain)` 级）与影响（会话窃取/钓鱼/蠕虫的可达性），留存反射/执行证据。

## Workflow

`scope-check → recon → hunt → validate → report`。

### 1. scope-check
- **动作**：写 `evidence/scope.txt`（allow_stored）。
- **命令**：`bash tools/recon.sh <target> --scope-only`。
- **终止条件**：scope 明确，否则 KILL。

### 2. recon
- **动作**：枚举回显参数、搜索/评论/标题字段、上传（SVG/HTML）、URL 片段消费的前端 sink（`location.hash`→`innerHTML`）、postMessage 监听。
- **输出**：`recon/endpoints.json`。
- **命令**：`bash tools/recon.sh <target>`。
- **终止条件**：至少 1 个回显/ sink 入口。

### 3. hunt
- **动作**：对每个入口注入**唯一标记**（如 `hxss9f3a2b`）+ 一组上下文探针（裸文本、`"`、`'`、`<`、`</script>`、`{{7*7}}`），抓响应看标记落在哪个上下文、哪些字符被编码。据此判定可执行上下文。
- **输出**：`candidates.json`（每入口：上下文、未编码字符、疑似可执行）。
- **命令**：`python tools/hunt_xss.py --input recon/endpoints.json --output candidates.json`。
- **终止条件**：`candidates.json` 生成。

### 4. validate → report
- **动作**：过 **7-Question Gate**，对疑似点构造 `alert(document.domain)` PoC 在浏览器/无头确认执行取证。任一 NO → killed。
- **命令**：`bash tools/validate.sh candidates.json`。
- **终止条件**：每条 confirmed/killed，confirmed 有执行/反射证据。

## 7-Question Gate（任一 NO 则 KILL）

1. 目标在**授权 scope** 内？
2. 输入确实**回显/流入前端 sink**？
3. 有**客观信号**（标记未编码进入可执行上下文 / 无头验证到执行），非猜测？
4. 能**真正执行脚本**（非纯文本反射）？
5. **可复现**（存储型验证他处也触发）？
6. 已留存**反射/执行证据**？
7. 影响可陈述，且 PoC **只用无害标记**、存储型可清理？

## Finding 输出格式

```
### <Title>
- Severity: Critical | High | Medium | Low | Info
- Asset: <入口 + 参数 + 上下文(HTML/attr/JS/DOM)>
- Reproduction: <精确 payload + 请求 / DOM 路径>
- Impact: <会话窃取 / 钓鱼 / 存储型蠕虫 可达性>
- Evidence: <evidence/ 反射响应 / 无头执行截图或日志>
- Status: confirmed | killed(<第几问 NO>)
```

## 参考

各上下文 payload、WAF/CSP 绕过、DOM sink 清单、真实报告见 `reference.md`——按 hunt 判出的上下文定向取用。
