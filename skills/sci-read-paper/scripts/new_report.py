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
        lines.append(line)
    text = "".join(lines)
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
    for name in remaining:
        print(f"  {name}")
    print("\nFill one section per edit, then run:")
    print(f"  python3 {Path(__file__).resolve().parent / 'validate_report.py'} {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
