# -*- coding: utf-8 -*-
"""把第三轮路由结果回填进各 skill 的 reference.md（幂等）。

fold→hunt-* : 追加/替换 "## 更多真实案例（第三轮单例补充）" 附录（报告号+主题+知识点，
              去重已在文中出现的报告号）。
fold→recognize-attack-surface : 追加到 references/patterns.md。
drop / new-skill : 不回填（决策单里已列出）。

用法: python fold_singletons.py
"""
import json
import os
import re
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.normpath(os.path.join(BASE, "..", "..", "skills"))
MARKER = "## 更多真实案例（第三轮单例补充）"


def target_file(target):
    if target == "recognize-attack-surface":
        return os.path.join(SKILLS, target, "references", "patterns.md")
    return os.path.join(SKILLS, target, "reference.md")


def existing_ids(text):
    return set(re.findall(r'\b(\d{5,7})\b', text))


def build_appendix(items, existing):
    """items: [{id, theme, knowledge_point, report_url}]。去重已存在报告号。"""
    by_theme = defaultdict(list)
    for it in items:
        by_theme[it.get("theme") or "其他"].append(it)
    lines = ["", MARKER, "",
             "（来自第二轮单例、第三轮语义路由归入本类；仅列此前未收录的报告，作案例索引）", ""]
    added = 0
    for theme, its in sorted(by_theme.items(), key=lambda x: -len(x[1])):
        new = [i for i in its if str(i["id"]) not in existing]
        if not new:
            continue
        lines.append("- **%s**" % theme)
        for i in new:
            kp = (i.get("knowledge_point") or "").strip()
            lines.append("  - #%s %s" % (i["id"], kp))
            added += 1
    lines.append("")
    return ("\n".join(lines), added) if added else ("", 0)


def upsert(path, appendix):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if MARKER in text:
        text = text[:text.index(MARKER)].rstrip() + "\n"
    else:
        text = text.rstrip() + "\n"
    text = text + appendix.rstrip() + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main():
    rows = json.load(open(os.path.join(BASE, "routing_all.json"), encoding="utf-8"))
    folds = defaultdict(list)
    stats = defaultdict(int)
    for r in rows:
        stats[r["action"]] += 1
        if r["action"] == "fold" and r.get("target"):
            folds[r["target"]].append(r)

    total_added = 0
    for target, items in sorted(folds.items()):
        path = target_file(target)
        if not os.path.exists(path):
            print("跳过（文件不存在）:", path); continue
        existing = existing_ids(open(path, encoding="utf-8").read())
        appendix, added = build_appendix(items, existing)
        if added:
            upsert(path, appendix)
        total_added += added
        print("%-32s 路由 %3d 条，去重后追加 %3d 条 -> %s"
              % (target, len(items), added, os.path.relpath(path, SKILLS)))
    print("\n动作统计:", dict(stats))
    print("共追加案例索引 %d 条（其余为已收录报告，去重跳过）" % total_added)


if __name__ == "__main__":
    main()
