# hunt-deserialization · 参考

真实报告源自本仓库第二轮高价值案例（value_score≥8）。`<OAST>` 换成你的带外域名。

## 格式指纹（先定位落点语言/格式）

| 语言/格式 | 指纹（值的开头/特征） |
|---|---|
| PHP `serialize()` | `O:<n>:"Class"`、`a:<n>:{`、`s:<n>:"` |
| PHP `phar` | 文件含 `__HALT_COMPILER();`、`phar://` 触发 |
| Java | base64 `rO0AB...`（0xAC 0xED 0x00 0x05）、`ObjectInputStream` |
| Python pickle | base64 常见 `gASV`/`gAJ`、opcode `c__main__` |
| .NET | base64 `AAEAAAD/////`（BinaryFormatter）、`__VIEWSTATE`、`ViewState` |
| Ruby Marshal | base64 `BAh`（`\x04\x08`）；cookie 常见 |
| YAML | `!ruby/object:`、`!!python/object`、`--- ` |
| JSON w/ type | `{"@type":...}`（fastjson/Jackson polymorphic） |

## Bypasses / gadget 入口

### PHP
- `unserialize()` 处理 cookie/token → POP chain 触发 `__wakeup`/`__destruct`/`__toString`（#134321 Ruby 类比、#2248328 Monolog 链、#358570 类型混淆）。
- **phar://**：文件操作函数（`file_exists`/`getimagesize`）遇 `phar://` 触发反序列化，绕上传/长度限制（#410212）。
- 对象注入 → `__toString` 触发 XXE/SSRF/pickle 链（#415501、#416004、#415222）。
- `unserialize()` 未初始化内存/整数溢出 → 内存破坏（#195950、#73244）。

### Ruby
- 已知 `secret_key_base` 签名恶意 cookie → Marshal 还原 → RCE（#134321）。
- `ActiveSupport::MessageVerifier`/`MessageEncryptor` Marshal（#473888）。
- `to_s.bytesize` 差 + Redis 协议注入拼 gadget（#1679624）。

### Python
- `pickle.loads` 内部 API/导入触发命令（#415137、#416004 pickle 链）。

### Java / .NET / YAML
- Java `ObjectInputStream` + ysoserial gadget（CommonsCollections 等）。
- .NET `BinaryFormatter`/`__VIEWSTATE`（无 MAC 或已知 MachineKey）。
- YAML `!ruby/object:` / `!!python/object`（#1663299）。

## Detection Patterns（怎么判，而非猜）

- **格式指纹命中**：值 base64 解码后出现上表特征 = 疑似序列化落点。
- **带外命中**：phar/URI gadget 触发对目标外呼 OAST = 反序列化可达（最硬）。
- **类名报错**：篡改后报错泄露 `unserialize()`/`Class not found`/`ObjectInputStream` = 命中反序列化路径。
- **时延**：某些 gadget（正则/递归）造成可测时延。
- **长度/魔改敏感**：改一个字节即报解析错，说明确在被反序列化。

## Real Reports（复现索引）

| 语言/向量 | 报告 |
|---|---|
| PHP phar | 410212 |
| PHP 对象注入链 | 415501 / 416004 / 415222 / 358570 |
| PHP unserialize 内存 | 195950 / 73244 / 195586 |
| Ruby cookie/Marshal | 134321 / 473888 / 1679624 |
| .NET/WordPress 链 | 2248328 |
| YAML | 1663299 |

hunt 顺序：先格式指纹定位语言 → 该语言的最小带外 gadget 探可达（phar/URI）→ 授权后再上完整 RCE gadget。
