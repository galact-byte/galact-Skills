#!/usr/bin/env bash
# hunt-command-injection recon：枚举"输入可能进命令行/外部程序"的入口。
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
# hunt-command-injection 授权 scope（开工前人工填写）
target: $TARGET
in_scope:
out_of_scope:
allow_write: no      # 是否允许写文件 PoC（否则只做时序/带外/只读回显）
oast_domain:         # 带外回连域名
authorized_by:
EOF
  echo "[recon] 已生成 scope 模板: $SCOPE —— 填写确认后再继续" >&2
fi
[[ "$MODE" == "--scope-only" ]] && { echo "[recon] scope-only 完成，未发请求" >&2; exit 0; }

PAGE="$ROOT/recon/page.html"
curl -sS --max-time 15 -L "$TARGET" -o "$PAGE" || echo "[recon] 目标抓取失败，继续" >&2
touch "$PAGE"

# 命令注入相关入口关键词：文件名/路径/命令/转换/CI-git/网络工具
KEYWORDS='cmd|command|exec|run|ping|host|ip|dns|whois|nslookup|traceroute|file|filename|path|name|ref|branch|tag|repo|url|src|source|format|convert|resize|thumbnail|image|img|video|upload|import|export|backup|archive|output|target|dest|template|eval|proxy_binary'

"$PYBIN" - "$TARGET" "$PAGE" "$KEYWORDS" "$ROOT/recon/endpoints.json" <<'PY'
import re, sys, json
target, page_path, kw, out = sys.argv[1:5]
try: html = open(page_path, encoding="utf-8", errors="ignore").read()
except OSError: html = ""
names = set(re.findall(r'(?:name|id)\s*=\s*["\']([^"\']+)["\']', html, re.I))
for m in re.finditer(r'[?&]([a-zA-Z_][\w\-]*)=', html): names.add(m.group(1))
# 表单里带 type=file 的上传点 → 疑似 delegate 落点
uploads = bool(re.search(r'type\s*=\s*["\']?file', html, re.I))
kwre = re.compile(kw, re.I)
hits = sorted(n for n in names if kwre.search(n))
eps = [{"url": target, "param": n, "method": "GET", "controllable": True,
        "sink": "shell/argv?", "note": "启发式命中，需确认是否进命令行"} for n in hits]
if uploads:
    eps.append({"url": target, "param": "<file upload>", "method": "POST", "controllable": True,
                "sink": "delegate", "note": "存在文件上传，疑似 ImageMagick/ffmpeg delegate 落点"})
if not eps:
    eps = [{"url": target, "param": None, "controllable": False,
            "note": "未自动命中命令行入口；人工排查 CI/git/导入/图像处理功能"}]
json.dump({"target": target, "endpoints": eps}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("[recon] 候选入口 %d（含上传=%s）-> %s" % (len([e for e in eps if e['controllable']]), uploads, out), file=sys.stderr)
PY
echo "[recon] 下一步: python tools/hunt_cmdi.py --input recon/endpoints.json --output candidates.json --oast <域名>" >&2
