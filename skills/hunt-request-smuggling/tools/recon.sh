#!/usr/bin/env bash
# hunt-request-smuggling recon：识别前端分层（代理/CDN）与 keep-alive，判断走私面。
# 用法: bash tools/recon.sh <target> [--scope-only]
# 输出: evidence/scope.txt ; recon/frontend.json
set -euo pipefail
PYBIN="$(command -v python3 || command -v python || true)"; [[ -z "$PYBIN" ]] && { echo "需要 python3/python" >&2; exit 3; }

TARGET="${1:-}"
MODE="${2:-full}"
if [[ -z "$TARGET" ]]; then
  echo "用法: bash tools/recon.sh <target> [--scope-only]" >&2; exit 2
fi
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/evidence" "$ROOT/recon"

SCOPE="$ROOT/evidence/scope.txt"
if [[ ! -f "$SCOPE" ]]; then
  cat > "$SCOPE" <<EOF
# hunt-request-smuggling 授权 scope（开工前人工填写）
target: $TARGET
in_scope:
out_of_scope:
allow_poison: no       # 是否允许 socket 毒化验证（否则只做 desync 时序判活）
test_window:           # 低峰测试窗口
authorized_by:
EOF
  echo "[recon] 已生成 scope 模板: $SCOPE —— 填写并确认授权后再继续" >&2
fi
[[ "$MODE" == "--scope-only" ]] && { echo "[recon] scope-only 完成，未发请求" >&2; exit 0; }

# 取响应头做前端指纹（只发一个正常 HEAD/GET，不发畸形请求）
HDR="$ROOT/recon/headers.txt"
curl -sS -D "$HDR" -o /dev/null --max-time 15 "$TARGET" || echo "[recon] 抓取失败，继续" >&2
touch "$HDR"

"$PYBIN" - "$TARGET" "$HDR" "$ROOT/recon/frontend.json" <<'PY'
import sys, json, re
target, hdr_path, out = sys.argv[1:4]
try:
    h = open(hdr_path, encoding="utf-8", errors="ignore").read()
except OSError:
    h = ""
low = h.lower()
signals = {
    "server": (re.search(r'(?im)^server:\s*(.+)$', h) or [None, None])[1],
    "via": "via:" in low,
    "x_cache": "x-cache" in low,
    "cf": "cf-ray" in low or "cloudflare" in low,
    "akamai": "akamai" in low or "x-akamai" in low,
    "varnish": "varnish" in low or "x-varnish" in low,
    "keep_alive": "keep-alive" in low or "connection: close" not in low,
    "http2": False,  # 需 --http2 探测，留待 hunt
}
has_frontend = any([signals["via"], signals["x_cache"], signals["cf"],
                    signals["akamai"], signals["varnish"]])
verdict = "值得试走私（存在前端层）" if has_frontend else "前端层不明显，走私面弱（仍可试畸形 TE）"
json.dump({"target": target, "signals": signals, "has_frontend": has_frontend,
           "verdict": verdict}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("[recon] 前端指纹: has_frontend=%s | %s" % (has_frontend, verdict), file=sys.stderr)
PY

echo "[recon] 下一步: python tools/hunt_smuggling.py --target $TARGET --output candidates.json" >&2
