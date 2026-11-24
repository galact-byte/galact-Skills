# 源码与元数据暴露参考

## 文件格式与误报

| 候选 | 可支持的事实 | 常见混淆 |
|---|---|---|
| `.git/HEAD` | `ref: refs/heads/...` 或 detached HEAD 对象名 | SPA 回退、文档代码块、honeypot；Git 也支持 SHA-256，不只 40 位 SHA-1 |
| `.git/packed-refs` | 结构化引用与对象映射 | 只有一个看似哈希的字符串不足以确定 Git |
| `.svn/entries` | 老工作副本格式与路径/版本字段 | 普通 XML/文本不一定是 SVN |
| `.svn/wc.db` | SQLite 文件头，离线检查工作副本表结构 | 文件可能含敏感路径且很大；无上限工具不能下载 |
| `.hg/requires` | 多项 Mercurial 特性声明 | `revlogv1` 等单词也可能出现在普通文档中 |
| `.env` / `.bak` | 非公开部署内容或配置 | 公共示例、构建模板和无敏感内容不自动构成高危 |
| ZIP / SQL / RAR | 归档或数据库格式线索 | 压缩包文件头不证明包含源码或数据库内容 |
| `.DS_Store` | 可离线解析的目录元数据 | 不是源码泄露；需说明实际暴露路径的影响 |

HEAD 文件暴露可以成立为元数据问题，但“整仓可恢复”“包含有效生产密钥”“可访问生产数据库”都需要额外证据与许可。404、403、200、响应长度单独不能证明文件是否真实存在或被保护。

## 读取边界

1. 先定一个明确且小的响应上限，保留响应状态、Content-Type、Content-Length、Content-Range 和实际读取字节数。
2. HEAD 可以用于观察元数据，但不代替 GET 内容判别；服务器对 HEAD 和 GET 的处理可能不同。
3. Range 被忽略、压缩响应解压后变大、分块响应无长度时，客户端上限仍须生效。只看 Content-Length 不足以防止全量读取。
4. 需要恢复源码或检查大文件时，单独取得读取范围与存储许可，在隔离目录使用现有工具。不要把自动 dump 设为默认下一步。
5. 不运行来源仓库内代码、构建、安装脚本或钩子；解析不受信任文件也应使用隔离、受限工具。

## 修复建议

构建产物与源码仓库分离；部署时排除 VCS 目录、编辑器残留、备份和私有配置。服务端规则应覆盖文件子路径而非仅目录列表。凭据已暴露时，仅关闭 Web 路径不够，还需由负责人撤销轮换并审查访问记录。修改生产规则属于独立操作，测试记录本身不授权修改。

## 官方依据

- [Git 仓库布局](https://git-scm.com/docs/gitrepository-layout)：HEAD、refs、packed-refs、objects 的含义，以及 detached HEAD。
- [Git SHA-256 支持](https://git-scm.com/docs/git-init)：对象格式可选 SHA-1 或 SHA-256；不要将 40 位哈希当作所有 Git 仓库的唯一格式。
- [OWASP WSTG：旧文件、备份与未引用文件](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/04-Configuration_and_Deployment_Management_Testing/04-Review_Old_Backup_and_Unreferenced_Files_for_Sensitive_Information)。
