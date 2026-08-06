# skill 测试

参考 anthropic skill-creator 的校验思路，分两层。都不依赖外部网络。

## 1. 静态完整测试（结构 / 语法 / 完整性）

```bash
bash tests/run_tests.sh
```

对 `skills/` 下每个 skill 跑 6 项：
1. `structure` — 官方 `quick_validate.py`（frontmatter 合法、命名 kebab-case、长度与字段白名单）。
2. `shell-syntax` — 每个 `tools/*.sh` 过 `bash -n`。
3. `py-compile` — 每个 `tools/*.py` 过 `py_compile`。
4. `lf-endings` — `tools/*.sh` 无 CRLF（保证 Linux/mac 可执行）。
5. `xref` — `SKILL.md` 引用的 `tools/*` 与 `reference.md` 真实存在。
6. `py-import` — 每个 `hunt_*.py --help` 退出 0（证明能 import `common` 且 argparse 正常，不触网）。

`tests/quick_validate.py` 是从 anthropics/claude-plugins-official（skill-creator，Apache-2.0）
vendored 的，唯一改动是按 UTF-8 读 `SKILL.md`（否则 Windows 默认 GBK 解码中文会报错）。

## 2. 端到端检测测试（真实靶标）

```bash
python tests/e2e/run_e2e.py
```

在 `127.0.0.1` 起一个故意脆弱的 HTTP 靶标（`tests/e2e/vuln_server.py`）和一个脆弱 Node 应用
（`tests/e2e/pp_app.js`，用于原型链污染），对每个 hunt-* skill 跑 `hunt_*.py` → `validate.sh`
的完整流水线，断言**植入的漏洞被检出**（或按设计正确判负 / 跑完运行时矩阵）：

- 真实漏洞检出：ssrf、open-redirect、path-traversal、sqli、xss、cache-poisoning、csrf、
  command-injection、xxe、prototype-pollution。
- 启发式识别：auth-bypass（识别 OAuth 机制）、deserialization（序列化格式指纹）。
- 正确判负：request-smuggling（单体服务不该被 desync，验证无假阳性）。
- 运行时矩阵：nodejs-permission-bypass（在打了补丁的 Node 上应无内容逃逸）。

安全约束：靶标只绑 loopback；SSRF 出站 2s 超时、仅 http/https；命令注入是**受控延时模拟**，
绝不执行攻击者输入；路径穿越读取限定在启动时构造的 sandbox 内。运行产物写到
`tests/e2e/.run/`（已 gitignore），可反复重跑。需要 `python3`、`curl`，Node 用例需要 `node`。

`recognize-attack-surface` 是路由/研判 skill，不是漏洞流水线，只走静态测试。
