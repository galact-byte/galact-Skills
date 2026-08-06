#!/usr/bin/env bash
# hunt-path-traversal recon：枚举吃文件名/路径的入口。
# 用法: bash tools/recon.sh <target> [--scope-only]
# 输出: evidence/scope.txt ; recon/endpoints.json
set -euo pipefail
PYBIN="$(command -v python3 || command -v python || true)"; [[ -z "$PYBIN" ]] && { echo "需要 python3/python" >&2; exit 3; }

TARGET="${1:-}"; MODE="${2:-full}"
[[ -z "$TARGET" ]] && { echo "用法: bash tools/recon.sh <target> [--scope-only]" >&2; exit 2; }
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/evidence" "$ROOT/recon"

SCOPE="$ROOT/evidence/scope.txt"
if [[ ! -f "$SCOPE" ]]; then
  cat > "$SCOPE" <<EOF
# hunt-path-traversal 授权 scope（开工前人工填写）
target: $TARGET
in_scope:
out_of_scope:
allow_write: no        # 是否允许写标记文件 PoC（否则只做读）
sensitive_read: no     # 是否允许尝试读 /etc/passwd、源码、密钥
authorized_by:
EOF
  echo "[recon] 已生成 scope 模板: $SCOPE —— 填写确认后再继续" >&2
fi
[[ "$MODE" == "--scope-only" ]] && { echo "[recon] scope-only 完成，未发请求" >&2; exit 0; }

PAGE="$ROOT/recon/page.html"
curl -sS --max-time 15 -L "$TARGET" -o "$PAGE" || echo "[recon] 目标抓取失败，继续" >&2
touch "$PAGE"

KEYWORDS='file|filename|filepath|path|dir|folder|name|download|dl|load|read|view|preview|page|template|include|doc|document|attachment|image|img|src|url|export|import|backup|log|cache|key|zip|tar|archive|extract|unpack|nupkg'

"$PYBIN" - "$TARGET" "$PAGE" "$KEYWORDS" "$ROOT/recon/endpoints.json" <<'PY'
import re, sys, json
target, page_path, kw, out = sys.argv[1:5]
try: html = open(page_path, encoding="utf-8", errors="ignore").read()
except OSError: html = ""
names = set(re.findall(r'(?:name|id)\s*=\s*["\']([^"\']+)["\']', html, re.I))
for m in re.finditer(r'[?&]([a-zA-Z_][\w\-]*)=', html): names.add(m.group(1))
uploads = bool(re.search(r'type\s*=\s*["\']?file', html, re.I))
kwre = re.compile(kw, re.I)
hits = sorted(n for n in names if kwre.search(n))
eps = [{"url": target, "param": n, "method": "GET", "controllable": True,
        "sink": "read?", "note": "启发式命中，需确认是否拼进文件路径"} for n in hits]
if uploads:
    eps.append({"url": target, "param": "<file upload>", "method": "POST", "controllable": True,
                "sink": "write-extract", "note": "存在上传，疑似解压/写入落点，试 zip-slip/symlink"})
if not eps:
    eps = [{"url": target, "param": None, "controllable": False,
            "note": "未自动命中路径入口；人工排查下载/预览/导出/解压/客户端 file:// 功能"}]
json.dump({"target": target, "endpoints": eps}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("[recon] 候选入口 %d（含上传=%s）-> %s" % (len([e for e in eps if e['controllable']]), uploads, out), file=sys.stderr)
PY
echo "[recon] 下一步: python tools/hunt_pathtrav.py --input recon/endpoints.json --output candidates.json" >&2
