---
name: hunt-cache-poisoning
description: 在授权渗透测试中挖掘 Web 缓存投毒与缓存欺骗（web cache poisoning / cache deception）。当目标前有缓存层（CDN/反代/Varnish）且缓存键未覆盖某些影响响应的输入（unkeyed header/参数/解析差异）时使用——典型场景：X-Forwarded-Host 反射进响应被缓存、unkeyed 参数、缓存键规范化差异、静态扩展名欺骗缓存私有页。适用目标类型 Web / CDN。触发场景包括用户说"测下缓存投毒""X-Forwarded-Host 能不能毒缓存""缓存欺骗看一下""unkeyed 输入有没有"。输出：投毒/欺骗可行性 + 被缓存证据的 finding（含 killed 记录）。
allowed-tools: Read, Grep, Glob, Bash
---

# hunt-cache-poisoning · Web 缓存投毒猎杀

只解决**缓存投毒/缓存欺骗一类**：找到"影响响应但不进缓存键"的输入（unkeyed header/参数/解析差异），把恶意内容写进共享缓存，或诱导缓存把私有页当静态资源存下。判定靠**投毒后无害请求也拿到被污染响应**、或**私有内容被缓存**。

投毒污染的是**共享缓存**，会影响其他用户。默认只投**无害标记**（如 `hcp9f3a2b`）证明可被缓存，并尽量用**唯一 cache-buster** 把影响限制在自己的缓存条目，不投恶意内容、不毒公共路径。手法与真实报告见 `reference.md`。

## Scope（授权范围）

**先确认授权。** 投毒共享缓存可能波及真实用户。

落实：授权目标、是否允许触碰共享缓存键（优先用唯一 cache-buster 限制影响）、测试窗口、只投无害标记。任一不清楚就停下问。

## Goal

判定缓存键是否漏掉影响响应的输入，达成**缓存投毒或缓存欺骗**，给出可复现 PoC（含被缓存证明）与影响，尽量把影响限制在自控缓存条目。

## Workflow

`scope-check → recon → hunt → validate → report`。

### 1. scope-check
- **动作**：写 `evidence/scope.txt`（allow_shared_cache）。
- **命令**：`bash tools/recon.sh <target> --scope-only`。
- **终止条件**：scope 明确，否则 KILL。

### 2. recon
- **动作**：确认缓存层与缓存状态头（`X-Cache`/`CF-Cache-Status`/`Age`/`Cache-Control`），找可缓存页面与反射点。
- **输出**：`recon/endpoints.json`（缓存指纹 + 候选页）。
- **命令**：`bash tools/recon.sh <target>`。
- **终止条件**：确认存在缓存层。

### 3. hunt
- **动作**：对候选页发 unkeyed 输入探针（`X-Forwarded-Host`/`X-Host`/`X-Forwarded-Scheme` 等带标记），看①标记是否**反射进响应** ②是否**被缓存**（换用带唯一 cache-buster 的干净请求仍见标记）。再试缓存欺骗（`/account/foo.css` 让私有页被当静态缓存）。
- **输出**：`candidates.json`。
- **命令**：`python tools/hunt_cache.py --target <url> --output candidates.json`。
- **终止条件**：`candidates.json` 生成。

### 4. validate → report
- **动作**：过 **7-Question Gate**，对可行项证明"投毒后干净请求拿到污染响应"取证。任一 NO → killed。
- **命令**：`bash tools/validate.sh candidates.json`。
- **终止条件**：每条 confirmed/killed，confirmed 有被缓存证据（X-Cache: HIT + 标记）。

## 7-Question Gate（任一 NO 则 KILL）

1. 目标在**授权 scope** 内？
2. 目标确有**缓存层**且响应可缓存（X-Cache/Age 佐证）？
3. 有**客观信号**（标记反射 + 后续请求命中缓存仍见标记），非猜测？
4. 输入确实 **unkeyed**（不进缓存键却影响响应）？
5. **可复现**（缓存 TTL 内稳定复现）？
6. 已留存**投毒→命中**证据？
7. 影响可陈述，且用**无害标记 + cache-buster** 限制了对真实用户的影响？

## Finding 输出格式

```
### <Title>
- Severity: Critical | High | Medium | Low | Info
- Asset: <可缓存页 + unkeyed 输入>
- Reproduction: <投毒请求 + 干净请求命中缓存的对照（X-Cache: HIT）>
- Impact: <存储型 XSS / 重定向 / 私有信息缓存欺骗>
- Evidence: <evidence/ 投毒响应 + HIT 响应>
- Status: confirmed | killed(<第几问 NO>)
```

## 参考

unkeyed 输入清单、缓存欺骗手法、缓存状态判读、真实报告见 `reference.md`。
