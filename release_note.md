## 新增专项 Skill

相对 v0.1.1，本版新增 11 个 Skill，总数从 16 个增加到 27 个：

- IDOR、文件上传、OAuth/JWT/SAML、业务逻辑、竞态条件、SSTI。
- 子域接管、源码与版本控制元数据暴露、JNDI 注入。
- GraphQL、WebSocket：覆盖字段和消息授权、批量操作与业务限流、浏览器跨站条件及会话生命周期。

确认标准随流程细化：DNS 悬挂不直接判为可接管，JNDI 出网回调不等于代码执行；GraphQL 开放 schema 或支持 alias、WebSocket 连接成功，也不直接判为漏洞。

## 分发与使用

修复新增 Skill 对私有知识库的依赖，参考文件随目录提供；移除未附带的竞态脚本引用，合并攻击面识别 Skill 的重复入口。复制单个 Skill 目录即可取得它的必需参考，外部工具按现场已有能力选择。

继续提供 `galact-skills.zip`，其中包含 `skills/`、`LICENSE`、`NOTICE` 和 `licenses/` 下的许可文本。下载后将所需 Skill 的整个目录复制到 Agent 扫描目录；也可继续使用 README 中的 `npx skills@latest add galact-byte/galact-Skills` 安装方式。已有同名且自行修改过的 Skill 时，更新前先保留修改。

新增离线分发检查，检查私有依赖、失效本地链接与嵌套入口。静态与冒烟检查不代表模型在真实任务中的行为或目标漏洞可利用；本次没有进行真实目标测试或模型行为评测。渗透测试相关 Skill 仍只用于明确授权的测试、CTF、教学与研究。

## 许可变化

本版原创且有权授权的部分采用自定义源码可用许可 `LicenseRef-Galact-Internal-Use-1.0`，不是 MIT 或 OSI 开源许可。允许合法个人及公司内部自用、保留署名与许可的免费分发；对外售卖、集成收费产品或提供直接收费的软件服务，需要另行取得书面商业授权。修改版须标识修改。

此前版本已经授予的 MIT 权利继续有效，不会撤回。`tests/quick_validate.py` 仍适用 Apache-2.0；具体范围与第三方例外见分发包的 `LICENSE`、`NOTICE` 和许可文本。
