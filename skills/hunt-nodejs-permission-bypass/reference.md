# hunt-nodejs-permission-bypass · 参考

真实报告源自本仓库第二轮高价值案例（框架行为利用类，value_score≥8）。这些绕过共性：
**用内部/非预期 API 绕开被拦的公开 fs/child_process API**。命中与否强依赖 Node 版本——按 recon 版本圈定。

## 绕过原语（Bypasses）

### A. inspector 模块改内部状态
`inspector` 未被权限模型限制，用 `Debugger.setBreakpointByUrl` 在 `WorkerImpl` 处下条件断点，把 `isInternal` 改成 true，创建"内部" Worker 执行任意命令。
- 报告 #1962701。修复：权限模型下禁用 inspector。

### B. process.binding / internalBinding 直取内部模块
`process.binding('spawn_sync')` / `process.binding('fs')` 绕过公开 API 的权限检查。
- `process.binding('spawn_sync')` 执行命令绕依赖策略（#2120719）。
- `process.binding('fs').mkdir` 路径含 `../` 未规范化，绕权限模型（#2051257）。

### C. 权限模型未覆盖的 fs API
模型漏挂某些文件 API：
- `fs.statfs`（#2051224）、`fs.openAsBlob()`（#1966492）读/探未授权路径。

### D. 原型链 / mainModule 取 require
绕过"require 白名单"：
- `process.mainModule.require(...)`（#1747642）
- `process.mainModule.__proto__.require(...)`（#1877919）
- `Module._load` / `require.extensions`（#2188126，CVE-2023-32559）

### E. path.resolve 覆盖
应用代码把 `require('path').resolve` 覆盖成恒等函数，权限模型内部动态查找该函数做规范化 → 不再解析 `/../` → 逃逸。
- #2225660。修复：模型内部缓存原始 `path.resolve` 引用。

### F. 类型化路径绕检查
路径存进 `Uint8Array`（非 Buffer/string），基于类型的路径检查漏判。
- #2256167（Node 20）。

### G. 符号链接重命名重定向
重命名已存在的相对符号链接，使其指向白名单外目录，绕过初始路径检查。
- #1961655。

## 命中判定（Detection）

- **逃逸成功**：PoC 在 `--allow-fs-read=<仅白名单>` 下**读到了白名单外的标记文件内容** = 命中。
- **被拦**：抛 `ERR_ACCESS_DENIED` = 该原语在此版本已修复/无效 → killed(Q3)。
- **不适用**：API 不存在（版本太老/太新移除）→ killed(Q2/Q4)。
- 逐原语记 stdout 与错误码，形成"版本 × 原语"命中矩阵。

## 版本与修复（对照）

- Node 的权限模型从 v20 起演进，多数原语在 v20.x → v22.x 的补丁中陆续修复；核验时**以目标精确版本实测为准**，不要只看 CVE 描述。
- 通用修复方向：升级到最新 LTS；权限模型下禁用 `inspector`；避免应用层覆盖内置模块方法；对内部 binding 也施加权限检查。

## Real Reports（复现索引）

| 原语 | 报告 | 备注 |
|---|---|---|
| inspector | 1962701 | 条件断点改 isInternal |
| process.binding | 2120719 / 2051257 | spawn_sync / fs.mkdir |
| 未覆盖 fs API | 2051224 / 1966492 | statfs / openAsBlob |
| mainModule/proto | 1747642 / 1877919 | require 逃逸 |
| Module._load | 2188126 | CVE-2023-32559 |
| path.resolve 覆盖 | 2225660 | 恒等函数 |
| Uint8Array 路径 | 2256167 | 类型绕过 |
| symlink 重命名 | 1961655 | 重定向 |

hunt：recon 出版本后，先跑 A/B/D（最经典且影响大），再跑 C/E/F/G；命中即对照修复版本给升级建议。
