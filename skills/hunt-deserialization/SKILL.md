---
name: hunt-deserialization
description: 在授权渗透测试中挖掘不安全反序列化（insecure deserialization）。当目标把用户可控数据交给 unserialize/Marshal/pickle/ObjectInputStream/BinaryFormatter/YAML.load 等还原成对象时使用——典型场景：cookie/token/viewstate/隐藏字段里出现序列化数据、导入文件触发对象还原、想借 gadget chain 拿 RCE。适用目标类型 Web / REST API（PHP/Ruby/Python/Java/.NET）。触发场景包括用户说"测下反序列化""这个 cookie 是不是序列化对象""能不能 gadget chain 打 RCE""phar/Marshal/pickle 打一下"。输出：识别出的序列化落点 + gadget 可用性判定 + 带外/回显证据的 finding（含 killed 记录）。
allowed-tools: Read, Grep, Glob, Bash
---

# hunt-deserialization · 不安全反序列化猎杀

只解决**不安全反序列化一类**：识别"用户可控数据被还原成对象"的落点，判断序列化格式与是否有可用 gadget chain。核心是先靠**格式指纹**定位落点，再用**带外/时序**探可达性，gadget 利用谨慎且授权后做。

反序列化 gadget 直达 RCE，破坏性极高。默认只做**格式识别 + 带外探测**（不投放破坏性 gadget），完整 RCE 利用仅在 scope 明确授权时进行。格式指纹、各语言 gadget 与真实报告见 `reference.md`。

## Scope（授权范围）

**先确认授权。** gadget PoC 可能在目标执行代码。

落实：授权目标、允许深度（仅识别/带外探测 / 允许 gadget PoC）、OAST 地址、禁止破坏性/持久化 gadget。任一不清楚就停下问。

## Goal

判定用户可控数据是否进入不安全反序列化，识别语言/格式，给出可复现 PoC 与影响（RCE / 对象注入 / 认证绕过），并留存带外命中或回显证据。

## Workflow

`scope-check → recon → hunt → validate → report`。

### 1. scope-check
- **动作**：写 `evidence/scope.txt`（allow_gadget / oast_domain）。
- **命令**：`bash tools/recon.sh <target> --scope-only`。
- **终止条件**：scope 明确，否则 KILL。

### 2. recon
- **动作**：枚举 cookie/token/viewstate/隐藏字段/导入功能，抓取其值做**格式指纹**（见 `reference.md`）。
- **输出**：`recon/endpoints.json`。
- **命令**：`bash tools/recon.sh <target>`。
- **终止条件**：至少 1 个疑似序列化落点，否则记录结束。

### 3. hunt
- **动作**：对落点用 `tools/hunt_deser.py` 判定格式（PHP `O:`/Java `rO0`/pickle/.NET/YAML），并发**无害带外探针**（能触发外呼的最小 gadget，如 PHP `phar`/Ruby URI gadget 打 OAST）判可达性。
- **输出**：`candidates.json`。
- **命令**：`python tools/hunt_deser.py --input recon/endpoints.json --output candidates.json --oast <域名>`。
- **终止条件**：`candidates.json` 生成。

### 4. validate → report
- **动作**：过 **7-Question Gate**，通过的在授权下做 gadget PoC 取证。任一 NO → killed。
- **命令**：`bash tools/validate.sh candidates.json`。
- **终止条件**：每条 confirmed/killed，confirmed 有带外/回显证据。

## 7-Question Gate（任一 NO 则 KILL）

1. 目标在**授权 scope** 内？
2. 数据确实被**反序列化成对象**（格式指纹 + 行为佐证）？
3. 有**客观信号**（带外命中 / 报错泄露类名 / 时延），非猜测？
4. 存在**可用 gadget** 或对象注入达成越权？
5. **可复现**？
6. 已留存**证据**（带外/回显/原始 payload）？
7. 影响可陈述，且 PoC **未做破坏性/持久化**？

## Finding 输出格式

```
### <Title>
- Severity: Critical | High | Medium | Low | Info
- Asset: <落点：cookie/参数/导入>
- Reproduction: <格式 + payload + 请求；带外域名/时延>
- Impact: <RCE / 对象注入 / 认证绕过>
- Evidence: <evidence/ 原始 payload + OAST 命中 / 类名报错>
- Status: confirmed | killed(<第几问 NO>)
```

## 参考

格式指纹（PHP/Java/Python/.NET/Ruby/YAML）、各语言 gadget 入口、检测特征、真实报告见 `reference.md`——按 recon 出的语言定向查阅。
