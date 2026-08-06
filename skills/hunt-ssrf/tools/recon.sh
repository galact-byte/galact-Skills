#!/usr/bin/env bash
# hunt-ssrf recon：枚举"吃 URL/主机/地址"的候选入口。
# 用法:
#   bash tools/recon.sh <target> [--scope-only]
# 输出:
#   evidence/scope.txt      （scope 记录，--scope-only 只做这步）
#   recon/endpoints.json    （候选 SSRF 入口清单）
set -euo pipefail
PYBIN="$(command -v python3 || command -v python || true)"; [[ -z "$PYBIN" ]] && { echo "需要 python3/python" >&2; exit 3; }

TARGET="${1:-}"
MODE="${2:-full}"
if [[ -z "$TARGET" ]]; then
  echo "用法: bash tools/recon.sh <target> [--scope-only]" >&2
  exit 2
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/evidence" "$ROOT/recon"

# 1) scope 记录（人工确认授权，脚本只留痕）
SCOPE="$ROOT/evidence/scope.txt"
if [[ ! -f "$SCOPE" ]]; then
  cat > "$SCOPE" <<EOF
# hunt-ssrf 授权 scope（开工前人工填写并确认）
target: $TARGET
in_scope:            # 允许触达的域名/IP 段
out_of_scope:        # 明确排除
allow_metadata: no   # 是否允许探测云元数据 169.254.169.254
allow_internal: no   # 是否允许探测内网段
oast_domain:         # 你的带外回连域名（Collaborator/interactsh）
authorized_by:       # 授权人/工单号
EOF
  echo "[recon] 已生成 scope 模板: $SCOPE —— 请人工填写并确认授权后再继续" >&2
fi

if [[ "$MODE" == "--scope-only" ]]; then
  echo "[recon] scope-only 完成，仅记录 scope，未发任何请求" >&2
  exit 0
fi

# 2) 抓取目标页面，提取可能吃 URL 的参数/字段（启发式，不发探测请求，只 GET 目标本身）
PAGE="$ROOT/recon/page.html"
curl -sS --max-time 15 -L "$TARGET" -o "$PAGE" || echo "[recon] 目标抓取失败（可能需登录/非 GET），继续用空页面" >&2
touch "$PAGE"

# 常见 SSRF 参数名（合并页面里出现的 name=/query key 命中）
KEYWORDS='url|uri|link|src|source|target|dest|redirect|redirect_uri|callback|webhook|image|img|imageUrl|fetch|feed|proxy|remote|remote_url|remote_attachment_url|host|domain|site|page|path|next|data|reference|open|continue'

"$PYBIN" - "$TARGET" "$PAGE" "$KEYWORDS" "$ROOT/recon/endpoints.json" <<'PY'
import re, sys, json
target, page_path, kw, out = sys.argv[1:5]
try:
    html = open(page_path, encoding="utf-8", errors="ignore").read()
except OSError:
    html = ""
pat = re.compile(r'(?:name|id)\s*=\s*["\']([^"\']+)["\']', re.I)
names = set(pat.findall(html))
# href/action 里带 query 的参数名
for m in re.finditer(r'[?&]([a-zA-Z_][\w\-]*)=', html):
    names.add(m.group(1))
kwre = re.compile(kw, re.I)
hits = sorted(n for n in names if kwre.search(n))
endpoints = [{"url": target, "param": n, "method": "GET", "controllable": True,
              "note": "启发式命中，需人工确认该参数是否触发服务端出站请求"}
             for n in hits]
if not endpoints:
    endpoints = [{"url": target, "param": None, "method": "GET", "controllable": False,
                  "note": "页面未自动命中吃 URL 的参数；需人工排查 JSON API/Webhook/导入功能"}]
json.dump({"target": target, "endpoints": endpoints}, open(out, "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("[recon] 候选入口 %d 个 -> %s" % (len([e for e in endpoints if e['controllable']]), out), file=sys.stderr)
PY

echo "[recon] 完成。下一步: python tools/hunt_ssrf.py --input recon/endpoints.json --output candidates.json --oast <你的回连域名>" >&2
