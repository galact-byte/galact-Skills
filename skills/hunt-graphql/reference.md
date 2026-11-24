# GraphQL 参考与判定边界

## 优先依据

- [GraphQL Security](https://graphql.org/learn/security/)：需求控制、可信文档、深度/宽度、成本与限流。
- [GraphQL Authorization](https://graphql.org/learn/authorization/)：业务层与字段权限，不能以 schema 可见性代替授权。
- [GraphQL Serving over HTTP](https://graphql.org/learn/serving-over-http/)：请求结构、方法与错误响应。
- [OWASP GraphQL Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/GraphQL_Cheat_Sheet.html)：输入、资源保护、访问控制、批量和配置问题。

上述资料用于确认机制；服务端库及部署配置决定现场行为。不能仅根据“使用 GraphQL”推断具体扩展已开启。

## 三种“多个”的区别

| 形式 | 实际语义 | 常见误判 |
|---|---|---|
| 一个 operation 中的 alias | 同一请求选择多个命名响应字段，可带不同参数 | 支持 alias 就算绕过 |
| 文档中定义多个 operation | 使用 operationName 选择一个；不能假定全部执行 | 把定义数当执行数 |
| HTTP body 是 JSON 数组 | 部分服务器/中间件支持的批处理扩展 | 当成协议必然支持 |

服务端 DataLoader 的批量加载/缓存是内部优化，不等于客户端 HTTP 批处理。判断限流应看受保护的业务动作，而不是只看网络请求或返回字段数量。

## 有界查询示例

以下内容是供本地理解与修改的示意，不包含自动发送脚本。字段、对象 ID 与权限必须来自现场资料；只用于已允许的自有测试对象。

最小识别：

```graphql
query Identify {
  __typename
}
```

按需读取根查询字段，而非默认导出所有类型：

```graphql
query RootFields {
  __schema {
    queryType {
      name
      fields { name }
    }
  }
}
```

同一 operation 内的两个 alias；假定现场 schema 存在 `item(id:)` 且这两个 ID 都属于测试账号：

```graphql
query TwoTestItems($first: ID!, $second: ID!) {
  first: item(id: $first) { id }
  second: item(id: $second) { id }
}
```

HTTP 请求体还需携带相应 `variables`。该查询只演示语法，不证明业务限流、授权或缓存问题；`__typename` 也不能证明某个昂贵 resolver 已被执行。

## 分层确认

| 观察 | 能支持的结论 | 还缺什么 |
|---|---|---|
| schema 返回类型/字段名 | 可发现性 | 私密性要求及实际越界影响 |
| 同对象公开字段可读、私密字段被拒 | 字段权限可能正常 | 其他角色/入口仍需分别验证 |
| B 读到 A 的受限测试字段 | 可能的对象/字段授权缺口 | 对象归属、权限规则和稳定对照 |
| 支持 JSON batch 或多个 alias | 执行能力 | 明确的业务计数规则及违反结果 |
| 拒绝深查询或返回成本错误 | 本次命中某条限制 | 不证明全部资源消耗面安全 |
| 一个请求慢或返回 500 | 错误/性能线索 | 可归因的资源证据与有界复现 |
| APQ 接受完整 query | 可能是正常缓存协商 | 是否配置可信文档白名单及预期边界 |

## 特殊执行面

- **GET 与 mutation**：按实际 HTTP 层与业务行为取证。状态变化还需检查浏览器可达性、Cookie 策略与 CSRF 防护；允许 GET 查询本身不构成 CSRF。
- **持久化查询**：APQ 通常用哈希减少查询传输；预先注册的可信文档/allowlist 是另一种控制。哈希命中/未命中需按现场产品文档解释。
- **订阅**：记录实际传输、子协议、初始化认证、订阅 ID 与事件来源；协议能连接不证明可以接收受保护事件。停止订阅后核对资源释放。
- **联合/网关**：网关 schema 与下游服务可能采用不同角色上下文；只用获准的已知测试对象比较权限，不能擅自绕过网关直连内部服务。

## 建议记录

端点与实现（已知/未知）、测试角色/租户、对象归属、字段路径、选中 operation、变量、HTTP/GraphQL 错误、实际业务计数、UTC 时间、成本/大小/时长、请求预算、对照、确认层级和未验证影响。只保留最小必要数据；令牌和完整 schema 不写进公开报告。
