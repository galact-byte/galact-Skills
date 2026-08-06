---
name: hunt-sqli
description: 在授权渗透测试中挖掘 SQL/NoSQL 注入（SQLi、NoSQLi，含 WAF 绕过、盲注、堆叠查询、类型混淆注入）。当用户输入拼进 SQL/NoSQL 查询时使用——典型场景：id/搜索/排序/过滤参数、数组键当 SQL 片段、PHP 类型混淆、MongoDB `$where`/`$regex`、堆叠查询到 xp_cmdshell。适用目标类型 Web / REST API。触发场景包括用户说"测下 SQL 注入""这个参数能不能注入""盲注/时间注入试试""NoSQL/MongoDB 注入看一下"。输出：注入点 + 类型 + 证据的 finding（含 killed 记录）。
allowed-tools: Read, Grep, Glob, Bash
---

# hunt-sqli · SQL/NoSQL 注入猎杀

只解决**注入到查询语句一类**（SQL 与 NoSQL）。核心是对每个参数按**错误型 → 布尔盲 → 时间盲**递进判活，识别数据库类型，必要时绕 WAF。判定靠**可控的响应差异/时延/报错**，只做**只读证明**（`sleep`/布尔差异/版本号），不 dump 真实数据、不改写数据。

注入可读写数据库甚至 RCE，敏感且可能破坏。默认只做**判活与最小证明**（拿到 DB 版本/布尔可控/时延），不 `DROP`/`UPDATE`/不批量导出真实数据。payload、绕过、真实报告见 `reference.md`。

## Scope（授权范围）

**先确认授权。**

落实：授权目标、允许深度（仅判活 / 允许读 schema / 禁止写与批量 dump）、是否允许时间盲注（会拖慢目标）。任一不清楚就停下问。

## Goal

判定参数是否可注入查询，识别 DB 类型与注入类型（错误/布尔/时间/堆叠/NoSQL），给出可复现 PoC 与最小证明，不动真实数据。

## Workflow

`scope-check → recon → hunt → validate → report`。

### 1. scope-check
- **动作**：写 `evidence/scope.txt`（allow_time_blind / allow_schema_read）。
- **命令**：`bash tools/recon.sh <target> --scope-only`。
- **终止条件**：scope 明确，否则 KILL。

### 2. recon
- **动作**：枚举进查询的参数——`id`/搜索/排序（`order`/`sort`）/过滤/分页，JSON body（NoSQL），数组参数（`a[]=`）。
- **输出**：`recon/endpoints.json`。
- **命令**：`bash tools/recon.sh <target>`。
- **终止条件**：至少 1 个候选参数。

### 3. hunt
- **动作**：对每个参数按 `reference.md` 递进：①错误型（`'`、`"`、`)` 触发 SQL 报错）②布尔型（`' AND 1=1` vs `' AND 1=2` 响应差异）③时间型（`' AND SLEEP(6)`、`;WAITFOR DELAY`、`pg_sleep`）④NoSQL（`[$ne]`/`[$gt]`/`$where`）。以差异/时延判活。
- **输出**：`candidates.json`。
- **命令**：`python tools/hunt_sqli.py --input recon/endpoints.json --output candidates.json [--delay 6]`。
- **终止条件**：`candidates.json` 生成。

### 4. validate → report
- **动作**：过 **7-Question Gate**，对疑似点做最小证明（DB 版本/稳定布尔差）取证。任一 NO → killed。
- **命令**：`bash tools/validate.sh candidates.json`。
- **终止条件**：每条 confirmed/killed，confirmed 有差异/时延/报错证据。

## 7-Question Gate（任一 NO 则 KILL）

1. 目标在**授权 scope** 内？
2. 参数确实**拼进查询**（错误/差异佐证）？
3. 有**客观信号**（SQL 报错 / 稳定布尔差 / 可控时延），非猜测？
4. 确实**可注入查询逻辑**（非普通参数校验报错）？
5. **可复现**（多次稳定，时延取中位排抖动）？
6. 已留存**报错/差异/时延**证据？
7. 影响可陈述，且**未 dump 真实数据、未写库**？

## Finding 输出格式

```
### <Title>
- Severity: Critical | High | Medium | Low | Info
- Asset: <入口 + 参数>
- Reproduction: <注入类型 + payload + 请求；布尔/时延对照数据>
- Impact: <数据读取 / 认证绕过 / 堆叠→命令 可达性>
- Evidence: <evidence/ 报错 / 布尔差 / 时延日志>
- Status: confirmed | killed(<第几问 NO>)
```

## 参考

各注入类型 payload、DB 指纹、WAF 绕过、NoSQL、真实报告见 `reference.md`。
