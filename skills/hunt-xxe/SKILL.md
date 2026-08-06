---
name: hunt-xxe
description: 在授权渗透测试中挖掘 XML 外部实体注入（XXE）。当目标解析用户可控的 XML——SOAP、SAML、SVG、RSS/Atom、DOCX/XLSX、WSDL/XSL、含 XML 的反序列化——且可能启用了外部实体时使用。典型场景：外部实体读本地文件、SSRF 打内网、OOB 带外/报错型外带数据、XXE→反序列化链。适用目标类型 Web / REST API / SOAP。触发场景包括用户说"测下 XXE""这个 XML/SVG 接口能不能读文件""XXE 打内网/带外""SAML 里能注实体吗"。输出：XXE 触发点 + 读到的文件/带外证据的 finding（含 killed 记录）。
allowed-tools: Read, Grep, Glob, Bash
---

# hunt-xxe · XML 外部实体注入猎杀

只解决 **XXE 一类**：找到解析用户 XML 的入口，判断外部实体是否被解析，用**文件读取回显**或**OOB 带外**证明。对无回显场景用外部 DTD 做 OOB/报错型外带。

XXE 常打到内网与本地文件，风险高。默认只**读授权内的无害文件**（如 `/etc/hostname`）+ 带外探测，不读敏感数据、不打未授权内网。payload、OOB 技巧、真实报告见 `reference.md`。

## Scope（授权范围）

**先确认授权。**

落实：授权目标、可读文件边界、是否允许 OOB（需你的外部 HTTP/DTD 服务器与 OAST）、是否允许内网 SSRF。任一不清楚就停下问。

## Goal

判定 XML 解析是否启用外部实体，达成**本地文件读取 / SSRF / OOB 外带**，给出可复现 PoC 与读到的内容/带外证据。

## Workflow

`scope-check → recon → hunt → validate → report`。

### 1. scope-check
- **动作**：写 `evidence/scope.txt`（oast_domain / dtd_url / allow_internal）。
- **命令**：`bash tools/recon.sh <target> --scope-only`。
- **终止条件**：scope 明确，否则 KILL。

### 2. recon
- **动作**：找吃 XML 的入口——`Content-Type: application/xml|text/xml|application/soap+xml`、SVG/DOCX/XLSX 上传、SAML、RSS 导入、任何 body 是 XML 的 API。
- **输出**：`recon/endpoints.json`。
- **命令**：`bash tools/recon.sh <target>`。
- **终止条件**：至少 1 个 XML 入口。

### 3. hunt
- **动作**：对每个入口发分级 payload：①内部实体回显（判是否解析实体）②`file://` 读授权文件 ③外部实体打 OAST（OOB 判可达）④无回显则挂外部 DTD 做报错/带外外带。
- **输出**：`candidates.json`。
- **命令**：`python tools/hunt_xxe.py --input recon/endpoints.json --output candidates.json --oast <域名> [--read-file /etc/hostname]`。
- **终止条件**：`candidates.json` 生成。

### 4. validate → report
- **动作**：过 **7-Question Gate**，通过的复现取证（保存读到的文件片段 / OAST 命中）。任一 NO → killed。
- **命令**：`bash tools/validate.sh candidates.json`。
- **终止条件**：每条 confirmed/killed，confirmed 有文件内容或带外证据。

## 7-Question Gate（任一 NO 则 KILL）

1. 目标在**授权 scope** 内？
2. 入口确实**解析 XML**（非当字符串存）？
3. 有**客观信号**（实体被展开 / 读到文件 / OAST 命中 / 报错外带），非猜测？
4. 达成**越权读取或 SSRF**（内部资源）？
5. **可复现**？
6. 已留存**文件内容/带外**证据？
7. 影响可陈述，且只读**授权内无害文件**？

## Finding 输出格式

```
### <Title>
- Severity: Critical | High | Medium | Low | Info
- Asset: <XML 入口 + Content-Type>
- Reproduction: <完整 XML payload + 请求；OOB 用的 DTD>
- Impact: <文件读取 / SSRF / OOB 外带 / →反序列化链>
- Evidence: <evidence/ 读到的文件片段 / OAST 命中日志>
- Status: confirmed | killed(<第几问 NO>)
```

## 参考

分级 payload（内部实体 / file:// / OOB 外部 DTD / 报错型）、SVG/SAML/DOCX 载体、真实报告见 `reference.md`。
