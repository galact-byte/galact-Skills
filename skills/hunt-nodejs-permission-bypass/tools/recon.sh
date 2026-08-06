#!/usr/bin/env bash
# hunt-nodejs-permission-bypass recon：探测 Node 版本与权限模型支持情况。
# 用法: bash tools/recon.sh [--node <path>] [--scope-only]
# 输出: evidence/scope.txt ; recon/node_env.json
set -euo pipefail
PYBIN="$(command -v python3 || command -v python || true)"; [[ -z "$PYBIN" ]] && { echo "需要 python3/python" >&2; exit 3; }

NODE="node"; MODE="full"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --node) NODE="$2"; shift 2;;
    --scope-only) MODE="--scope-only"; shift;;
    *) shift;;
  esac
done
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/evidence" "$ROOT/recon"

SCOPE="$ROOT/evidence/scope.txt"
if [[ ! -f "$SCOPE" ]]; then
  cat > "$SCOPE" <<EOF
# hunt-nodejs-permission-bypass 授权 scope（开工前人工填写）
node_target: $NODE           # 目标 Node 二进制/版本（优先用同版本副本，勿在生产）
restricted_file:             # 受限标记文件绝对路径（PoC 尝试越权读它，内容须无敏感信息）
permission_flags:            # 目标启动方式，如 --experimental-permission --allow-fs-read=/app
authorized_by:
EOF
  echo "[recon] 已生成 scope 模板: $SCOPE —— 填写 restricted_file 并确认授权后再继续" >&2
fi
[[ "$MODE" == "--scope-only" ]] && { echo "[recon] scope-only 完成，未运行 PoC" >&2; exit 0; }

if ! command -v "$NODE" >/dev/null 2>&1; then
  echo "[recon] 找不到 node ($NODE)；请用 --node 指定目标二进制" >&2; exit 2
fi

VER="$("$NODE" -v 2>/dev/null || echo unknown)"
# 探测权限模型标志支持（新版 --permission，旧版 --experimental-permission）
PERM_NEW="no"; PERM_EXP="no"
"$NODE" --permission -e "process.exit(0)" >/dev/null 2>&1 && PERM_NEW="yes"
"$NODE" --experimental-permission -e "process.exit(0)" >/dev/null 2>&1 && PERM_EXP="yes"

"$PYBIN" - "$VER" "$PERM_NEW" "$PERM_EXP" "$ROOT/recon/node_env.json" <<'PY'
import sys, json
ver, pnew, pexp, out = sys.argv[1:5]
try:
    major = int(ver.lstrip("v").split(".")[0])
except ValueError:
    major = 0
primitives = ["inspector", "process.binding", "fs.statfs", "fs.openAsBlob",
              "mainModule.require", "mainModule.__proto__.require", "Module._load",
              "path.resolve-override", "Uint8Array-path", "symlink-rename"]
supported = (pnew == "yes" or pexp == "yes")
json.dump({"node_version": ver, "major": major,
           "permission_new_flag": pnew, "permission_experimental_flag": pexp,
           "permission_model_supported": supported,
           "applicable_primitives": primitives if supported else []},
          open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("[recon] Node %s | 权限模型支持=%s (--permission=%s --experimental-permission=%s)"
      % (ver, supported, pnew, pexp), file=sys.stderr)
if not supported:
    print("[recon] 该版本不支持权限模型，逃逸核验无意义", file=sys.stderr)
PY
echo "[recon] 下一步: python tools/hunt_nodeperm.py --restricted <标记文件> --output candidates.json --node $NODE" >&2
