---
name: hunt-open-redirect
description: 在授权渗透测试中挖掘开放重定向（open redirect）及其危害升级。当目标按用户可控参数做跳转（登录后 next、SSO returnUrl、注销、短链、回调）时使用——典型场景：绕过 URL 白名单跳到外站钓鱼、泄露 token/Referer、开放重定向作为 SSRF/OAuth token 窃取的跳板。适用目标类型 Web / REST API / SSO。触发场景包括用户说"测下开放重定向""这个 next/redirect 参数能跳外站吗""绕过重定向白名单""open redirect 偷 token"。输出：可跳外站的参数 + PoC + 危害升级的 finding（含 killed 记录）。
allowed-tools: Read, Grep, Glob, Bash
---

# hunt-open-redirect · 开放重定向猎杀

只解决**开放重定向一类**：找到"按用户输入跳转且校验不严"的参数，绕过白名单跳到外部域，并评估危害升级（钓鱼、Referer/token 泄露、作为 SSRF/OAuth 窃取跳板）。判定靠**响应把浏览器导向攻击者控制的外部域**（`Location` 头或前端跳转）。

开放重定向本身多为中低危，价值在**升级**（配合 OAuth `redirect_uri`、SSRF、token 泄露）。默认只跳到**自控的无害标记域**证明可控，不做钓鱼/不诱导真实用户。绕过写法与真实报告见 `reference.md`。

## Scope（授权范围）

**先确认授权。**

落实：授权目标、可用的自控标记域（证明可跳外站）、是否评估升级链（OAuth/SSRF）。任一不清楚就停下问。

## Goal

判定跳转参数能否被导向任意外部域（含白名单绕过），给出可复现 PoC 与危害升级路径（钓鱼/token 泄露/SSRF/OAuth），只跳自控域证明。

## Workflow

`scope-check → recon → hunt → validate → report`。

### 1. scope-check
- **动作**：写 `evidence/scope.txt`（marker_domain）。
- **命令**：`bash tools/recon.sh <target> --scope-only`。
- **终止条件**：scope 明确，否则 KILL。

### 2. recon
- **动作**：枚举跳转参数——`redirect`/`redirect_uri`/`next`/`return`/`returnUrl`/`goto`/`dest`/`continue`/`url`/`callback`，登录/注销/SSO/短链流程。
- **输出**：`recon/endpoints.json`。
- **命令**：`bash tools/recon.sh <target>`。
- **终止条件**：至少 1 个跳转参数。

### 3. hunt
- **动作**：对每个参数发绕过变体（`//marker`、`/\marker`、`https://marker`、`https://target@marker`、`https://target.marker`、`https://marker%23.target`、反斜杠/空白/编码），检查 `Location` 头或 meta/JS 跳转是否指向 marker 域。
- **输出**：`candidates.json`。
- **命令**：`python tools/hunt_openredirect.py --input recon/endpoints.json --output candidates.json --marker <你的域>`。
- **终止条件**：`candidates.json` 生成。

### 4. validate → report
- **动作**：过 **7-Question Gate**，对可行项确认跳外站并评估升级（token 是否随跳转泄露、能否喂给 OAuth redirect_uri/SSRF）取证。任一 NO → killed。
- **命令**：`bash tools/validate.sh candidates.json`。
- **终止条件**：每条 confirmed/killed，confirmed 有跳向 marker 域的证据。

## 7-Question Gate（任一 NO 则 KILL）

1. 目标在**授权 scope** 内？
2. 参数确实**驱动跳转**（Location/前端导航）？
3. 有**客观信号**（响应把浏览器导向 marker 外部域），非猜测？
4. 确实**跳到任意外部域**（绕过了白名单，非仅站内跳转）？
5. **可复现**？
6. 已留存**跳转证据**（Location/JS）？
7. 影响可陈述（含升级路径），且只跳**自控标记域**、未诱导真实用户？

## Finding 输出格式

```
### <Title>
- Severity: Critical | High | Medium | Low | Info
- Asset: <入口 + 跳转参数>
- Reproduction: <绕过 payload + 请求；Location/JS 跳转证据>
- Impact: <钓鱼 / Referer-token 泄露 / SSRF / OAuth token 窃取（升级）>
- Evidence: <evidence/ 响应含指向 marker 的跳转>
- Status: confirmed | killed(<第几问 NO>)
```

## 参考

白名单绕过写法、危害升级链、检测特征、真实报告见 `reference.md`。
