# GraphQL、WebSocket Skill 与 v0.2.0 发布

## 授权与范围

用户要求发布新 Release，并再次检查本机可沉淀流程；已明确批准新增 GraphQL、WebSocket 两项，要求只收录有实际复用价值的内容，减少子代理。本任务由主代理完成。

## 行为缺口与改动边界

现有库只有 GraphQL 对象授权和 WebSocket 的零散线索，缺少协议层完整判断流程。新增两个自包含目录（各含 SKILL.md、reference.md）；更新攻击面路由、README 计数、离线分发检查、CHANGES.md 和 release_note.md。既有私有知识文件只作为线索，不原样复制。保留用户的 Trellis 初始化改动。

非渗透筛选覆盖本机文档办公、游戏汉化/巡检、开发启动器、UI 工作流与工具项目。已有成熟第三方方案、已有专门维护源、不能脱离本机路径或仅是一次性操作的内容不直接收录；本次不新增其他领域的 Skill。

## 验收

- GraphQL 区分 introspection、对象/字段授权、alias、HTTP 批处理、业务限流与资源影响；不将 schema 开放或 HTTP 200 判为漏洞，不以压力测试证明复杂度问题。
- WebSocket 区分握手与消息授权；CSWSH 必须核实浏览器实际携带身份并获得受保护能力；CLI 修改 Origin 不作为跨站利用证明；覆盖会话过期、注销和订阅生命周期。
- 官方依据随参考文件提供；不依赖私有路径、额外插件或未附脚本。
- 离线验证通过；按真实发布工作流构建 ZIP 并核对入口与文件哈希。
- AAASRC 同步只新增不存在的两个目录，逐文件 SHA-256 一致；对其定制攻击面路由只补两项入口及引用，原文备份与差异私有留存。
- 相对 v0.1.1 编写中文发布说明，准确说明新增 11 项至共 27 项、分发修复及许可变化。
- 提交、推送、发布 v0.2.0；回读标签、说明、附件和远端校验结果。

## 验证限制

静态检查与场景审阅不等于模型行为评测或真实漏洞验证。本轮不连接测试目标、不运行攻击、不调用子代理模型评测；交付时如实说明。

## 执行记录

- 扩充分发入口检查后先运行 RED：缺少 GraphQL、WebSocket 两个入口，2 个预期失败；原始日志 `E:/DevData/galact-skills-portability/graphql-websocket-red.log`。
- 两项各含入口与自包含参考，参考官方 GraphQL 文档、RFC、OWASP 与浏览器 API 文档；更新攻击面路由及 README。
- `python -m unittest discover -s tests -p test_distribution.py -v`：6 项通过；`bash tests/run_tests.sh`：27 Skill / 164 项、0 失败；完整输出保存在私有交付目录。
- 复用实际 release 工作流构建 ZIP：27 入口、130 文件、源文件逐一一致、失效本地链接 0；可重建打包副本检查后删除。
- AAASRC 新增两项共 4 文件，SHA-256 一致；本地定制路由只作局部入口补充，原文及差异保存在 `E:/DevData/galact-skills-portability/v0.2.0-local-router-original/`。
- v0.2.0 已发布，标签指向内容提交 `cde8bba`；发布流水线与 master、tag 的离线 CI 均通过（27 Skill / 164 项、0 失败）。
- 回读正式 Release 正文与标签内说明一致；下载附件后，130 文件逐字节匹配标签 Git blob、27 入口、无缺失或多余路径。工作树与附件的换行差异经原文核实，不属于发布内容变化。
- 已补充跨平台附件校验约定；可重下载的附件副本删除，验证摘要、同步哈希与必要日志在本地私有交付目录保留。
