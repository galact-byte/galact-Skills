#!/usr/bin/env bash
# hunt-ssrf validate：对候选过 7-Question Gate，复现取证，产出 finding 报告。
# 用法:
#   bash tools/validate.sh candidates.json
# 输出:
#   evidence/<family>_<n>.req / .resp   （confirmed 项的原始请求/响应）
#   report/candidates.md                （finding 报告，含 killed 记录）
set -euo pipefail

CAND="${1:-candidates.json}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CAND_PATH="$ROOT/$CAND"
[[ -f "$CAND_PATH" ]] || CAND_PATH="$CAND"
if [[ ! -f "$CAND_PATH" ]]; then
  echo "找不到候选文件: $CAND ；先跑 hunt_ssrf.py" >&2
  exit 2
fi
mkdir -p "$ROOT/evidence" "$ROOT/report"

# 对每条候选：有信号的重放取证到 evidence/，并生成报告骨架。
# 7-Question Gate 的判定需人工介入（授权/影响/可复现性无法纯自动断言），
# 脚本负责重放留证 + 把 Gate 清单写进报告，逼每条给出 confirmed/killed 结论。
python3 - "$CAND_PATH" "$ROOT" <<'PY'
import json, sys, os, subprocess, time
cand_path, root = sys.argv[1], sys.argv[2]
data = json.load(open(cand_path, encoding="utf-8"))
cands = data.get("candidates", [])
ev_dir = os.path.join(root, "evidence")
rep = os.path.join(root, "report", "candidates.md")

lines = ["# hunt-ssrf finding 报告", "",
         "目标: %s" % data.get("target"), "OAST: %s" % data.get("oast"),
         "候选总数: %d" % len(cands), "",
         "> 每条须过 7-Question Gate，任一 NO 记 killed。confirmed 项须有 evidence/ 原始报文。", ""]

GATE = ["scope 内?", "服务端出站?", "客观信号?", "越权资源?",
        "可复现?", "留存证据?", "影响可陈述?"]

confirmed = killed = pending = 0
for i, c in enumerate(cands):
    has_signal = c.get("signal") and c["signal"] != ["无明显信号"]
    stem = "%s_%d" % (c.get("family", "x"), i)
    # 有信号的重放两次取证（复现性初判 + 原始报文留存）
    status = "pending"
    if has_signal:
        req = os.path.join(ev_dir, stem + ".req")
        resp = os.path.join(ev_dir, stem + ".resp")
        open(req, "w", encoding="utf-8").write(c.get("curl", ""))
        try:
            p = subprocess.run(["curl", "-sS", "-i", "--max-time", "8", c.get("probe_url", "")],
                               capture_output=True, text=True, timeout=12)
            open(resp, "w", encoding="utf-8").write((p.stdout or "") + "\n---STDERR---\n" + (p.stderr or ""))
            status = "confirmed?" # 仍需人工过 Gate 第 1/4/7 问
        except Exception as e:
            open(resp, "w", encoding="utf-8").write("replay error: %s" % e)
    sev = "High" if c.get("family","").startswith("metadata") else "Medium"
    lines.append("### [%s] %s @ param=%s" % (c.get("family"), c.get("label"), c.get("param")))
    lines.append("- Severity: %s (待人工定级)" % sev)
    lines.append("- Asset: %s" % c.get("endpoint"))
    lines.append("- Reproduction: `%s`  (probe: %s)" % (c.get("curl"), c.get("probe_url")))
    lines.append("- Signal: %s | status=%s size=%s time=%s" %
                 (", ".join(c.get("signal", [])), c.get("status"), c.get("size"), c.get("time")))
    lines.append("- Impact: <人工补：内网/元数据/RCE 链>")
    lines.append("- Evidence: %s" % ("evidence/%s.req + .resp" % stem if has_signal else "无（无信号）"))
    gate = " ".join("Q%d:%s?" % (n+1, q.split('?')[0]) for n, q in enumerate(GATE))
    lines.append("- 7-Gate: %s  → 逐问填 YES/NO" % gate)
    if has_signal:
        lines.append("- Status: confirmed?（人工过 Gate 第 1/4/7 问后定 confirmed/killed）")
        pending += 1
    else:
        lines.append("- Status: killed(Q3 无客观信号)")
        killed += 1
    lines.append("")

lines.insert(5, "统计: 待人工判定 %d / 自动 killed %d" % (pending, killed))
os.makedirs(os.path.dirname(rep), exist_ok=True)
open(rep, "w", encoding="utf-8").write("\n".join(lines))
print("[validate] 报告 -> %s（%d 待人工过 Gate, %d 已 killed）" % (rep, pending, killed), file=sys.stderr)
PY

echo "[validate] 完成。人工按 7-Question Gate 复核 report/candidates.md，confirmed 项证据在 evidence/" >&2
