# hunt-cache-poisoning · 参考

真实报告源自本仓库第二轮高价值案例（value_score≥8）。探针标记 `hcp9f3a2b`，尽量带唯一 cache-buster 限制影响。

## unkeyed 输入清单（Bypasses）

### unkeyed header（最常见）
```
X-Forwarded-Host: hcp9f3a2b.evil        （反射进绝对 URL / 重定向 / 资源引用）
X-Host / X-Forwarded-Server: ...
X-Forwarded-Scheme: http   X-Forwarded-Proto: http   （降级/重定向循环）
X-Original-URL / X-Rewrite-URL: ...
```
- X-Forwarded-Host 反射被缓存 → 存储型（#303730、#728664、#919175）。

### unkeyed 参数 / 解析差异
- 缓存键规范化差异：不同 URL 映射到同一缓存键（#824753）。
- UTF-8 大字节字符使缓存与后端解析不一致（#350847）。
- NULL 字节截断 + URL 规范化绕过缓存键（#334709）。
- Accept-Version 等头改变响应但不进键（#1025575）。
- CDN 对参数处理差异（#1160407）。

### 缓存欺骗（cache deception）
- 给私有页加静态扩展名/路径：`/account/profile.css`、`/account/x.js?`、`/account/;.css`，让 CDN 按"静态资源"缓存下私有响应，攻击者再读缓存。
- 未 key 的扩展名使动态内容被当静态缓存（#1698316）。

## Detection Patterns（怎么判，而非猜）

- **缓存指纹**：`X-Cache: HIT/MISS`、`CF-Cache-Status`、`Age: >0`、`Cache-Control: public` = 有缓存、可缓存。
- **反射**：unkeyed header 的标记出现在响应体/头（尤其绝对 URL、`<base>`、重定向 `Location`、资源 `src`）。
- **被缓存（关键两步）**：
  1. 带恶意 header + 唯一 buster `?cb=hcp9f3a2b` 发一次（写缓存）。
  2. **不带** header、同 URL+同 buster 再发，若仍见标记且 `X-Cache: HIT` = 投毒成功。
- **缓存欺骗**：`/private/x.css` 返回私有内容且被缓存（第二次 HIT）。
- 始终用唯一 buster，避免污染真实用户会命中的公共缓存键。

## Real Reports（复现索引）

| 手法 | 报告 |
|---|---|
| X-Forwarded-Host 反射缓存 | 303730 / 728664 / 919175 |
| 缓存键规范化差异 | 824753 / 1160407 |
| UTF-8 大字节 / NULL 截断 | 350847 / 334709 |
| unkeyed 头改响应 | 1025575 |
| 扩展名欺骗静态缓存 | 1698316 |

hunt 顺序：先确认缓存指纹 → 逐个 unkeyed header 探反射 → 命中就走"两步法"证明被缓存 → 私有页试缓存欺骗。全程带唯一 buster。
