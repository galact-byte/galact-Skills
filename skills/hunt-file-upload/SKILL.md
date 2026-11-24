---
name: hunt-file-upload
description: 在授权渗透测试中挖掘文件上传漏洞。当目标接受用户上传的文件（头像、附件、导入、图片、文档、简历）且可能导致 RCE/XSS/覆盖/路径穿越时使用——典型场景：上传 webshell（.php/.jsp/.aspx）、Content-Type 绕过、双扩展名、图片马、SVG XSS、ZIP 解压路径穿越、上传覆盖配置文件。适用目标类型 Web / REST API / 文件管理系统。触发场景包括用户说"测下文件上传""能不能传 shell""上传有没有限制""文件类型校验严不严"。输出：绕过上传限制 + 执行/触发证据的 finding（区分确认、阻塞、未定与误报）。
allowed-tools: Read, Grep, Glob, Bash
---

# hunt-file-upload · 文件上传猎杀

只解决**文件上传功能的安全缺陷一类**（类型绕过→RCE、内容解析→XSS/SSRF、路径操控→覆盖/穿越）。核心是在每个上传点测试文件类型校验的完整性和上传后的处理安全。判定靠**成功上传非预期类型文件并被解析执行/渲染的客观证据**。

默认以随机文本或固定算术标记做**最小证明**，避免 `phpinfo()` 泄露配置。先确认上传、文件类型、存储、访问与清理许可；脚本解析验证需相应明确批准，不植入 WebShell 或后门。方法见 [参考](reference.md)。

## Scope（授权范围）

**先确认授权。**

落实：授权目标、允许的内容与存储位置、访问方式、清理责任及禁用动作。客户约定禁止 WebShell 或存储型 XSS 时必须遵守。上传动作本身及脚本、HTML/SVG 主动内容验证均需相应许可，不能从普通测试许可推导。

## Goal

系统性测试文件上传限制的完整性：类型校验（前端/后端/白名单/黑名单/Content-Type/文件头）、存储安全（路径是否可控/是否在 Web 目录/是否改名）、处理安全（是否渲染 SVG/解压 ZIP/执行脚本），给出绕过证据。

## Workflow

`scope-check → recon → hunt → validate → report`。

### 1. scope-check
- **动作**：确认授权和上传限制。
- **终止条件**：scope 明确。

### 2. recon — 上传点画像
- **动作**：
  - 枚举所有上传入口（头像、附件、导入、编辑器图片插入、API 文件参数）
  - 正常上传一个合法文件，记录：上传接口、允许类型、文件大小限制、返回的文件 URL/路径、是否改名、存储域
  - 判断校验位置：纯前端（改 JS/直接调 API 绕过）vs 后端

### 3. hunt — 按面攻击

#### 3a. 扩展名绕过
- 双扩展名：`shell.php.jpg`、`shell.jpg.php`
- 大小写：`shell.PhP`、`shell.JSP`
- 特殊扩展名：`.phtml`、`.php5`、`.shtml`、`.cer`
- 空字节/截断：`shell.php%00.jpg`（旧版本）
- 点/空格末尾：`shell.php.`、`shell.php `（Windows）
- `.htaccess`/`web.config` 上传（改解析规则）

#### 3b. Content-Type 绕过
- 修改 Content-Type 为 `image/png` 保持内容为脚本
- 修改 Content-Type 和扩展名组合

#### 3c. 文件头/Magic Bytes 绕过
- 仅在脚本解析测试明确获准时，用固定算术标记比较原样返回与处理器执行结果；不转储配置或环境。
- polyglot 文件（同时是有效图片和有效脚本）

#### 3d. 内容型攻击
- SVG 上传含 XSS：`<svg onload=alert(1)>`
- SVG 含 SSRF：`<svg><image xlink:href="http://internal/...">`
- HTML 上传（如果允许 .html/.htm）

#### 3e. 路径/存储攻击
- 仅在获准的受控目录验证文件名规范化或覆盖，不能尝试系统任务目录和现存配置文件。
- ZIP 解压穿越另按路径穿越 Skill 与明确的文件写入许可验证；使用可清理测试对象。

### 4. validate → report
- **动作**：逐项核对证据，登记上传对象、实际路径、内容哈希、清理责任及复核结果。
- **关键**：上传成功或文件公开访问都不单独证明漏洞；需证明违反预期的执行、内容渲染、访问控制或存储边界。
- 缺许可记 blocked，证据不足记 inconclusive，有对照证伪才记 false_positive；不再把所有未确认候选写 killed。

## 7-Question Gate（证据不足不确认）

1. 目标在**授权 scope** 内？
2. 确实**突破预期安全边界**（类型限制、脚本执行、访问控制或写入位置之一），不是正常文件分享？
3. 有**具体影响证据**，而非仅收到上传成功或可下载响应？
4. **可复现**（稳定绕过，非偶发）？
5. 确认是**后端缺陷**（不是仅绕过前端 JS 校验而后端正常拦截）？
6. 已留存**上传请求 + 文件访问/执行**的完整证据？
7. 内容、动作与清理均已获准，未泄露配置、植入后门或覆盖原有资产？

## 与其他 hunt skill 的链

- 上传 + `hunt-path-traversal`：文件名穿越覆盖关键文件
- 上传 + `hunt-xss`：SVG/HTML 上传 → 存储型 XSS
- 上传 + `hunt-ssrf`：SVG/XSLT/文档处理触发 SSRF
- 上传 + `hunt-xxe`：DOCX/XLSX/SVG 中的 XXE
- 上传 + `hunt-command-injection`：文件名注入操作系统命令（ImageMagick/ffmpeg 处理）

## Finding 输出格式

```
### <Title>
- Severity: Critical | High | Medium | Low
- Asset: <上传入口 + 绕过方法>
- Reproduction: <上传请求 + 文件内容 + 访问/执行 URL>
- Impact: <RCE / XSS / 文件覆盖 / 信息泄露>
- Evidence: <evidence/ 上传请求 + 文件执行截图>
- Status: confirmed | inconclusive | blocked | false_positive | out_of_scope
```

## 参考

类型校验、内容处理与存储边界检查见 [参考](reference.md)。
