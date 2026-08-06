#!/usr/bin/env bash
# 全 skill 离线完整测试 harness。
# 5 层检查（都不触网，安全可复现）：
#   1. structure  — 官方 quick_validate.py（frontmatter/命名/长度规范）
#   2. shell-syntax — 每个 tools/*.sh 过 `bash -n`
#   3. py-compile — 每个 tools/*.py 过 py_compile
#   4. lf-endings — tools/*.sh 无 CRLF（保证 Linux/mac 可执行）
#   5. xref       — SKILL.md 里引用的 tools/* 与 reference.md 真实存在
#   6. py-import  — 每个 hunt_*.py `--help` 退出 0（证明可 import common + argparse 正常，不触网）
# 用法: bash tests/run_tests.sh
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$ROOT/skills"
VALIDATOR="$ROOT/tests/quick_validate.py"
PYBIN="$(command -v python3 || command -v python)"
export PYTHONUTF8=1

pass_total=0; fail_total=0; skill_fail=0; skill_pass=0
FAILED_SKILLS=()

check() {  # check "<label>" <exit-code> "<detail>"
  local label="$1" code="$2" detail="${3:-}"
  if [[ "$code" -eq 0 ]]; then
    printf '    ✓ %s\n' "$label"; pass_total=$((pass_total+1)); return 0
  else
    printf '    ✗ %s%s\n' "$label" "${detail:+ — $detail}"; fail_total=$((fail_total+1)); return 1
  fi
}

for skill in "$SKILLS_DIR"/*/; do
  skill="${skill%/}"; name="$(basename "$skill")"
  echo "▶ $name"
  ok=1

  # 1. structure
  out="$("$PYBIN" "$VALIDATOR" "$skill" 2>&1)"; code=$?
  check "structure (quick_validate)" $code "$out" || ok=0

  # 2. shell 语法
  sh_bad=""
  for f in "$skill"/tools/*.sh; do
    [[ -e "$f" ]] || continue
    err="$(bash -n "$f" 2>&1)" || sh_bad+="$(basename "$f"): $err; "
  done
  check "shell-syntax (bash -n)" "$([[ -z "$sh_bad" ]] && echo 0 || echo 1)" "$sh_bad" || ok=0

  # 3. python 编译
  py_bad=""
  for f in "$skill"/tools/*.py; do
    [[ -e "$f" ]] || continue
    err="$("$PYBIN" -m py_compile "$f" 2>&1)" || py_bad+="$(basename "$f"): $err; "
  done
  check "py-compile" "$([[ -z "$py_bad" ]] && echo 0 || echo 1)" "$py_bad" || ok=0

  # 4. LF 行尾
  crlf=""
  for f in "$skill"/tools/*.sh; do
    [[ -e "$f" ]] || continue
    grep -lq $'\r' "$f" 2>/dev/null && crlf+="$(basename "$f") "
  done
  check "lf-endings (no CRLF in .sh)" "$([[ -z "$crlf" ]] && echo 0 || echo 1)" "${crlf:+CRLF in: $crlf}" || ok=0

  # 5. 交叉引用：SKILL.md 提到的 tools/* 与 reference.md 必须存在
  xref_bad=""
  refs="$(grep -oE '(tools/[A-Za-z0-9_./-]+|reference\.md|references/[A-Za-z0-9_./-]+)' "$skill/SKILL.md" 2>/dev/null | sort -u)"
  while IFS= read -r ref; do
    [[ -z "$ref" ]] && continue
    [[ -e "$skill/$ref" ]] || xref_bad+="$ref "
  done <<< "$refs"
  check "xref (referenced files exist)" "$([[ -z "$xref_bad" ]] && echo 0 || echo 1)" "${xref_bad:+missing: $xref_bad}" || ok=0

  # 6. python import 冒烟：hunt_*.py --help 退出 0（不触网）
  imp_bad=""
  for f in "$skill"/tools/hunt_*.py; do
    [[ -e "$f" ]] || continue
    err="$("$PYBIN" "$f" --help 2>&1 >/dev/null)" || imp_bad+="$(basename "$f"): ${err##*Error}; "
  done
  check "py-import (--help exits 0)" "$([[ -z "$imp_bad" ]] && echo 0 || echo 1)" "$imp_bad" || ok=0

  if [[ "$ok" -eq 1 ]]; then skill_pass=$((skill_pass+1)); else skill_fail=$((skill_fail+1)); FAILED_SKILLS+=("$name"); fi
  echo
done

echo "════════════════════════════════════════"
echo "skills: $skill_pass PASS / $skill_fail FAIL   |   checks: $pass_total pass / $fail_total fail"
[[ "$skill_fail" -gt 0 ]] && echo "失败 skill: ${FAILED_SKILLS[*]}"
echo "════════════════════════════════════════"
exit $([[ "$skill_fail" -eq 0 ]] && echo 0 || echo 1)
