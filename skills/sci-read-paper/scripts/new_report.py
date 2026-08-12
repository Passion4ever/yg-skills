#!/usr/bin/env python3
"""Scaffold one sci-read-paper report from the template.

Usage:
    python3 <skill>/scripts/new_report.py --slug <paper-slug> [--outdir .]
                                          [--mode standard|audit]
                                          [--figure off|brief|generate]

Writes <outdir>/<slug>.html (or <slug>-audit.html) and prints the absolute path
followed by every placeholder still waiting to be filled.

Everything this script does is mechanical: which file name the mode implies,
which conditional lines the figure/mode combination deletes, and what the build
metadata says. Deciding those by hand is how a report ends up shipping a
`{{FIGURE_OUTPUT}}` line or being validated against a mode it was not built in.

Standard library only, so it runs anywhere the skill runs.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "report-template.html"
PLACEHOLDER = re.compile(r"\{\{[A-Z0-9_]+\}\}")

# What goes in each slot. Printing the bare names makes the writer cross-reference
# the contract to tell BODY_7_NO_EFFECT from BODY_7_VERDICTS; one line each removes
# a lookup from every run.
SLOTS = {
    "DISPLAY_TITLE": "短中文标题，如 Transformer 深度精读",
    "PAPER_SUBTITLE": "论文原标题，完整不缩写",
    "SIDEBAR_SUBTITLE": "一行认出这篇论文：作者、编号、任务",
    "STATUS": "complete 或 partial",
    "META_EXTRA": "期刊或预印本编号、DOI、代码地址、访问日期，各一个 <span>",
    "QV_MAINLINE": "速览·作者主线：作者想贡献什么，不下判断",
    "QV_EVIDENCE": "速览·证据状态：会改变结论的缺口，及最小解决材料",
    "QV_REVIEW": "速览·审查入口：第 7 章要处理的问题，不展开答案",
    "CUE_n": "第 n 章的一句中性导读：本章要建立什么",
    "BODY_n": "第 n 章正文（n=1..7）",
    "BODY_7_NO_EFFECT": "第 7 章收尾：逐条列出无实质影响的边界；一条都没有也要说明",
    "BODY_7_VERDICTS": "四档判定卡，只放适用的几档，见 assets/fragments.html 第 6 节",
    "BODY_8_1": "第 8 章：论文真正贡献了什么",
    "BODY_8_2": "第 8 章：最终可以相信到哪里",
    "BODY_8_3": "第 8 章：下一步最该做什么",
    "AUDIT_PANELS": "四块折叠面板，id 固定为 data-training / model-dataflow / "
                    "experiment-matrix / critical-review；只登记穷尽清单，不下判断",
    "REPORT_DETAILS": "页脚来源块：论文版本、代码 commit、未解决问题、完成状态",
    "EVIDENCE_LEDGER": "完整证据台账表，七列，见 assets/fragments.html 第 7 节",
}


def describe(name: str) -> str:
    key = name.strip("{}")
    if key in SLOTS:
        return SLOTS[key]
    generic = re.sub(r"_\d+$", "_n", key)
    return SLOTS.get(generic, "")


def scaffold(template_text: str, mode: str, figure: str) -> str:
    """Resolve every placeholder whose value the two flags already determine."""
    lines = []
    for line in template_text.splitlines(keepends=True):
        # The two conditional blocks are whole lines so that "not applicable"
        # is expressed by the line being absent, never by an empty placeholder.
        if "{{FIGURE_OUTPUT}}" in line and figure == "off":
            continue
        if "{{AUDIT_PANELS}}" in line and mode == "standard":
            continue
        # the sidebar group for those panels lives or dies with them, and its
        # links would be dead — a validation failure — in a standard report
        if "{{AUDIT_NAV}}" in line and mode == "standard":
            continue
        lines.append(line)
    text = "".join(lines)
    text = text.replace("{{AUDIT_NAV}}", "")
    return text.replace("{{MODE}}", mode).replace("{{FIGURE}}", figure)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True, help="stable paper slug, e.g. frameflow-motif-scaffolding")
    parser.add_argument("--outdir", type=Path, default=Path("."))
    parser.add_argument("--mode", choices=("standard", "audit"), default="standard")
    parser.add_argument("--figure", choices=("off", "brief", "generate"), default="off")
    parser.add_argument("--template", type=Path, default=TEMPLATE)
    parser.add_argument("--force", action="store_true", help="overwrite an existing report")
    args = parser.parse_args(argv)

    if not args.template.is_file():
        print(f"FAIL template not found at {args.template}", file=sys.stderr)
        return 1

    suffix = "-audit" if args.mode == "audit" else ""
    target = (args.outdir / f"{args.slug}{suffix}.html").resolve()
    if target.exists() and not args.force:
        print(f"FAIL {target} already exists; pass --force to overwrite", file=sys.stderr)
        return 1

    target.parent.mkdir(parents=True, exist_ok=True)
    text = scaffold(args.template.read_text(encoding="utf-8"), args.mode, args.figure)
    target.write_text(text, encoding="utf-8")

    remaining = list(dict.fromkeys(PLACEHOLDER.findall(text)))
    print(target)
    print(f"mode={args.mode} figure={args.figure}; {len(remaining)} placeholders to fill:")
    width = max(len(name) for name in remaining)
    for name in remaining:
        print(f"  {name:<{width}}  {describe(name)}")
    print("\nFill one section per edit, then run:")
    print(f"  python3 {Path(__file__).resolve().parent / 'validate_report.py'} {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
