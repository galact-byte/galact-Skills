#!/usr/bin/env bash
# hunt-* 通用 validate：对候选过 7-Question Gate、留证、产出 finding 报告。
# schema 无关：适配各 hunt_*.py 产出的不同候选字段。
# 用法: bash tools/validate.sh candidates.json
# 输出: evidence/<n>.req/.resp（有可重放 URL 时）; report/candidates.md
set -euo pipefail
PYBIN="$(command -v python3 || command -v python || true)"; [[ -z "$PYBIN" ]] && { echo "需要 python3/python" >&2; exit 3; }

CAND="${1:-candidates.json}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CAND_PATH="$ROOT/$CAND"; [[ -f "$CAND_PATH" ]] || CAND_PATH="$CAND"
if [[ ! -f "$CAND_PATH" ]]; then
  echo "找不到候选文件: $CAND ；先跑 hunt_*.py" >&2; exit 2
fi
mkdir -p "$ROOT/evidence" "$ROOT/report"

"$PYBIN" - "$CAND_PATH" "$ROOT" <<'PY'
import json, sys, os, subprocess
cand_path, root = sys.argv[1], sys.argv[2]
data = json.load(open(cand_path, encoding="utf-8"))
cands = data.get("candidates", [])
ev = os.path.join(root, "evidence")
rep = os.path.join(root, "report", "candidates.md")

GATE = ["scope 内?", "服务端行为?", "客观信号?", "越权/破坏边界?",
        "可复现?", "留存证据?", "影响可陈述?"]

def has_signal(c):
    # 各 hunt 工具用 signal / suspected_* / slow 等标记；有任一"正向"信号即视为待判
    if c.get("suspected_desync") or c.get("suspected"):
        return True
    sig = c.get("signal")
    return bool(sig) and sig not in (["无明显信号"], ["无明显时序差"])

def scalars(c):
    return {k: v for k, v in c.items() if isinstance(v, (str, int, float, bool))}

lines = ["# hunt finding 报告", "",
         "目标: %s" % data.get("target"),
         "候选总数: %d" % len(cands), "",
         "> 每条须过 7-Question Gate，任一 NO 记 killed。confirmed 项须有 evidence/ 证据。", ""]
pending = killed = 0
for i, c in enumerate(cands):
    sig = has_signal(c)
    stem = "%s_%d" % (str(c.get("variant") or c.get("family") or "cand"), i)
    # 有可重放 URL 的（如注入类）重放取证；时序类把候选原样存证
    ev_note = "无（无信号）"
    if sig:
        purl = c.get("probe_url")
        open(os.path.join(ev, stem + ".cand.json"), "w", encoding="utf-8").write(
            json.dumps(c, ensure_ascii=False, indent=1))
        ev_note = "evidence/%s.cand.json" % stem
        if purl:
            try:
                p = subprocess.run(["curl", "-sS", "-i", "--max-time", "8", purl],
                                   capture_output=True, text=True, timeout=12)
                open(os.path.join(ev, stem + ".resp"), "w", encoding="utf-8").write(
                    (p.stdout or "") + "\n---STDERR---\n" + (p.stderr or ""))
                ev_note += " + %s.resp" % stem
            except Exception as e:
                open(os.path.join(ev, stem + ".resp"), "w", encoding="utf-8").write("replay error: %s" % e)
    lines.append("### [%s] %s" % (stem, c.get("label") or c.get("variant") or c.get("family") or ""))
    lines.append("- Severity: <人工定级>")
    lines.append("- Asset: %s" % (c.get("endpoint") or c.get("host") or data.get("target")))
    lines.append("- Detail: %s" % json.dumps(scalars(c), ensure_ascii=False))
    lines.append("- Signal: %s" % ", ".join(c.get("signal", []) or ["-"]))
    lines.append("- Impact: <人工补>")
    lines.append("- Evidence: %s" % ev_note)
    lines.append("- 7-Gate: %s → 逐问 YES/NO" % " | ".join("Q%d:%s" % (n+1, q) for n, q in enumerate(GATE)))
    if sig:
        lines.append("- Status: confirmed?（人工过 Gate 第 1/4/7 问后定）"); pending += 1
    else:
        lines.append("- Status: killed(Q3 无客观信号)"); killed += 1
    lines.append("")
lines.insert(5, "统计: 待人工判定 %d / 自动 killed %d" % (pending, killed))
os.makedirs(os.path.dirname(rep), exist_ok=True)
open(rep, "w", encoding="utf-8").write("\n".join(lines))
print("[validate] 报告 -> %s（%d 待判, %d killed）" % (rep, pending, killed), file=sys.stderr)
PY
echo "[validate] 完成。人工按 7-Question Gate 复核 report/candidates.md" >&2
