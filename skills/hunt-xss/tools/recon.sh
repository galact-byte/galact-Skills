#!/usr/bin/env bash
# hunt-xss recon：枚举相关入口参数。
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
# hunt-xss 授权 scope（开工前人工填写并确认）
target: $TARGET
in_scope:
out_of_scope:
oast_domain:          # 带外回连域名（需要时）
authorized_by:        # 授权人/工单号
EOF
  echo "[recon] 已生成 scope 模板: $SCOPE —— 填写确认授权后再继续" >&2
fi
[[ "$MODE" == "--scope-only" ]] && { echo "[recon] scope-only 完成，未发请求" >&2; exit 0; }

PAGE="$ROOT/recon/page.html"
curl -sS --max-time 15 -L "$TARGET" -o "$PAGE" || echo "[recon] 目标抓取失败，继续" >&2
touch "$PAGE"

KEYWORDS='q|search|query|name|comment|message|title|url|redirect|callback|input|text|body|content|html|desc|ref|lang|template'
"$PYBIN" - "$TARGET" "$PAGE" "$KEYWORDS" "$ROOT/recon/endpoints.json" <<'PY'
import re, sys, json
target, page_path, kw, out = sys.argv[1:5]
try: html = open(page_path, encoding="utf-8", errors="ignore").read()
except OSError: html = ""
names = set(re.findall(r'(?:name|id)\s*=\s*["\']([^"\']+)["\']', html, re.I))
for m in re.finditer(r'[?&]([a-zA-Z_][\w\-]*)=', html): names.add(m.group(1))
forms = len(re.findall(r'<form', html, re.I))
uploads = bool(re.search(r'type\s*=\s*["\']?file', html, re.I))
kwre = re.compile(kw, re.I)
hits = sorted(n for n in names if kwre.search(n))
eps = [{"url": target, "param": n, "method": "GET", "controllable": True,
        "note": "启发式命中，需人工确认落点"} for n in hits]
if not eps:
    eps = [{"url": target, "param": None, "controllable": False,
            "note": "未自动命中相关参数；人工排查 API/表单/上传/头部输入"}]
json.dump({"target": target, "forms": forms, "has_upload": uploads, "endpoints": eps},
          open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("[recon] 候选入口 %d（forms=%d upload=%s）-> %s"
      % (len([e for e in eps if e['controllable']]), forms, uploads, out), file=sys.stderr)
PY
echo "[recon] 下一步: 见 SKILL.md 的 hunt 阶段命令" >&2
