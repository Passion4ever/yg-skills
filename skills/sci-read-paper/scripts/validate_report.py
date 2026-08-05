#!/usr/bin/env python3
"""Validate one generated sci-read-paper HTML report against the output contract.

Usage:
    python3 <skill>/scripts/validate_report.py <report.html> [--figure off|brief|generate]

Exits 0 when the report satisfies every mechanical rule in
references/output-contract.md, 1 otherwise. Warnings never fail the run.

Standard library only, so it runs anywhere the skill runs.
"""

from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

SECTION_TITLES = [
    "为什么要做这项研究：背景、现状与本文切入点",
    "三分钟建立论文全局地图",
    "从问题到方法：作者为什么这样设计",
    "数据从哪里来，又怎样进入训练",
    "模型内部：数据怎样一步步变成输出",
    "实验逻辑：每项实验在回答什么问题",
    "批判性审查：证据究竟支持到哪里",
    "读完这篇论文，真正应该带走什么",
]
REVIEW_CARD_FIELDS = [
    "处理的证据边界",
    "作者主张",
    "支持证据",
    "反证或替代解释",
    "证据缺少什么",
    "对中心结论的影响",
    "最小解决实验",
]
FOOTER_DISCLOSURES = ("report-info", "evidence-ledger")
NO_EFFECT_BLOCK = "no-effect-boundaries"
FIGURE_OUTPUT = "figure-output"
EVIDENCE_ID = re.compile(r"^E\d{2,}$")
BOUNDARY_ID = re.compile(r"^B\d{2,}$")
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}
CJK = re.compile(r"[㐀-䶿一-鿿豈-﫿]")

READING_LENGTH_MIN = 4500
READING_LENGTH_MAX = 11000


class Element:
    __slots__ = ("tag", "id", "classes")

    def __init__(self, tag: str, element_id: str, classes: set[str]) -> None:
        self.tag = tag
        self.id = element_id
        self.classes = classes


class ReportIndex(HTMLParser):
    """One pass over the report, recording everything the contract constrains.

    Section membership is tracked by the open-element stack, not by tag depth:
    a stray close tag must not silently reassign every later element to no
    section at all.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.internal_targets: list[str] = []
        self.boundary_links: list[tuple[str, bool]] = []
        self.styles: list[str] = []
        self.section_ids: list[str] = []
        self.section_headings: dict[int, str] = {}
        self.chapter_labels: list[str] = []
        self.classes_by_id: dict[str, set[str]] = {}
        self.evidence_links: list[tuple[str, str, int]] = []
        self.boundary_ids: list[tuple[str, int | None]] = []
        self.unlabelled_boundaries: list[tuple[int, int | None]] = []
        self.review_card_fields: list[tuple[str, list[str]]] = []
        self.details_open: dict[str, bool] = {}
        self.external_resources: list[str] = []
        self.structural_errors: list[str] = []
        self.main_text: list[str] = []
        self.hero_text: list[str] = []
        self.images: list[str] = []

        self._stack: list[Element] = []
        self._in_style = False
        self._style_buf: list[str] = []
        self._capture: list[str] | None = None
        self._capture_kind: str | None = None
        self._capture_href = ""
        self._card_stack: list[list[str]] = []

    # -- context helpers -------------------------------------------------
    @property
    def section(self) -> int | None:
        for element in reversed(self._stack):
            if element.tag == "section" and re.fullmatch(r"section-[1-8]", element.id):
                return int(element.id.rsplit("-", 1)[1])
        return None

    def _in_main(self) -> bool:
        return any(element.tag == "main" for element in self._stack)

    def _in_hero(self) -> bool:
        return any("paper-hero" in element.classes for element in self._stack)

    def _has_boundary_ancestor(self) -> bool:
        return any(BOUNDARY_ID.match(element.id) for element in self._stack)

    def _in_discharge_context(self) -> bool:
        """A boundary counts as discharged only from a review card or the closing list."""
        return any(
            "review-card" in element.classes or element.id == NO_EFFECT_BLOCK
            for element in self._stack
        )

    def _current_card(self) -> list[str] | None:
        return self._card_stack[-1] if self._card_stack else None

    def _flush_capture(self) -> None:
        if self._capture is None:
            return
        text = "".join(self._capture).strip()
        if self._capture_kind == "evidence":
            self.evidence_links.append((self._capture_href, text, self.getpos()[0]))
        elif self._capture_kind == "chapter":
            self.chapter_labels.append(text)
        elif self._capture_kind == "heading":
            section = self.section
            if section is not None and section not in self.section_headings:
                self.section_headings[section] = text
        elif self._capture_kind == "field":
            card = self._current_card()
            if card is not None:
                card.append(text.rstrip("：: "))
        self._capture = None
        self._capture_kind = None
        self._capture_href = ""

    # -- parser hooks ----------------------------------------------------
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key: (value or "") for key, value in attrs}
        classes = set(attributes.get("class", "").split())
        element_id = attributes.get("id", "")
        line = self.getpos()[0]

        if tag == "style":
            self._in_style = True
            self._style_buf = []

        if element_id:
            self.ids.append(element_id)
            self.classes_by_id.setdefault(element_id, set()).update(classes)
            if tag == "section" and re.fullmatch(r"section-[1-8]", element_id):
                self.section_ids.append(element_id)
            if BOUNDARY_ID.match(element_id):
                self.boundary_ids.append((element_id, self.section))
            if tag == "details":
                self.details_open[element_id] = "open" in attributes

        href = attributes.get("href", "")
        if tag == "a" and href.startswith("#"):
            self.internal_targets.append(href[1:])
            if "boundary-link" in classes:
                self.boundary_links.append((href[1:], self._in_discharge_context()))
        if tag == "link" and "stylesheet" in attributes.get("rel", ""):
            self.external_resources.append(f'line {line}: <link rel="stylesheet">')
        if tag == "script":
            self.external_resources.append(f"line {line}: <script>")
        if tag == "iframe":
            self.external_resources.append(f"line {line}: <iframe>")
        src = attributes.get("src", "")
        if src and not src.startswith("data:"):
            self.external_resources.append(f'line {line}: src="{src[:60]}"')
        if tag == "img":
            self.images.append(f"line {line}")

        self._flush_capture()
        if tag == "a" and "evidence-link" in classes:
            self._capture, self._capture_kind, self._capture_href = [], "evidence", href
        elif tag == "p" and "chapter-label" in classes:
            self._capture, self._capture_kind = [], "chapter"
        elif tag == "h2" and self.section is not None:
            self._capture, self._capture_kind = [], "heading"
        elif tag == "strong" and self._current_card() is not None:
            self._capture, self._capture_kind = [], "field"

        if tag not in VOID_TAGS:
            self._stack.append(Element(tag, element_id, classes))
            if "review-card" in classes:
                card: list[str] = []
                self._card_stack.append(card)
                self.review_card_fields.append((element_id or f"line {line}", card))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS and self._stack:
            self.handle_endtag(tag)

    def handle_data(self, data: str) -> None:
        if self._in_style:
            self._style_buf.append(data)
            return
        if self._capture is not None:
            self._capture.append(data)
        if self._in_main():
            self.main_text.append(data)
        if self._in_hero():
            self.hero_text.append(data)

        section = self.section
        if (
            section is not None
            and 1 <= section <= 6
            and "证据边界" in data
            and "处理的证据边界" not in data
            and not self._has_boundary_ancestor()
        ):
            self.unlabelled_boundaries.append((self.getpos()[0], section))

    def handle_endtag(self, tag: str) -> None:
        if tag == "style":
            self._in_style = False
            self.styles.append("".join(self._style_buf))
        self._flush_capture()

        if not any(element.tag == tag for element in self._stack):
            self.structural_errors.append(
                f"line {self.getpos()[0]}: stray </{tag}> with no open element"
            )
            return
        while self._stack:
            popped = self._stack.pop()
            if "review-card" in popped.classes and self._card_stack:
                self._card_stack.pop()
            if popped.tag == tag:
                break
            if popped.tag == "section" and re.fullmatch(r"section-[1-8]", popped.id):
                self.structural_errors.append(
                    f"line {self.getpos()[0]}: </{tag}> closes across"
                    f" the still-open <section id=\"{popped.id}\">"
                )


def load_template_style(template: Path) -> str | None:
    if not template.is_file():
        return None
    index = ReportIndex()
    index.feed(template.read_text(encoding="utf-8"))
    return index.styles[0] if index.styles else None


def validate(path: Path, template: Path, figure: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8")
    index = ReportIndex()
    index.feed(text)

    # 0. structural integrity — everything below assumes the tree parses sanely
    errors.extend(index.structural_errors)

    # 1. no unreplaced template tokens (the truncation and copy-paste tripwire)
    for token in sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", text))):
        errors.append(f"unreplaced template token {token}")

    # 2. the template stylesheet must survive untouched
    template_style = load_template_style(template)
    if len(index.styles) != 1:
        errors.append(
            f"expected exactly 1 <style> element, found {len(index.styles)}"
            " — a second stylesheet means the report was not built from the template"
        )
    if template_style is None:
        warnings.append(f"template not found at {template}; skipped CSS comparison")
    elif index.styles and index.styles[0].strip() != template_style.strip():
        errors.append(
            "the report stylesheet differs from assets/report-template.html;"
            " copy the template and replace only the {{TOKEN}} placeholders"
        )

    # 3. eight sections, in order, with the contract's exact headings and labels
    expected_sections = [f"section-{n}" for n in range(1, 9)]
    if index.section_ids != expected_sections:
        errors.append(
            f"sections must be exactly {expected_sections} in order, found {index.section_ids}"
        )
    for number, title in enumerate(SECTION_TITLES, start=1):
        heading = index.section_headings.get(number)
        if heading is None:
            errors.append(f"section-{number} has no <h2> heading")
        elif heading != title:
            errors.append(f"section-{number} heading is {heading!r}, expected {title!r}")
    expected_labels = [f"CHAPTER {n:02d}" for n in range(1, 9)]
    if index.chapter_labels != expected_labels:
        errors.append(
            f"chapter labels must be {expected_labels}, found {index.chapter_labels}"
        )

    # 4. anchors must resolve
    duplicates = sorted({i for i in index.ids if index.ids.count(i) > 1})
    if duplicates:
        errors.append(f"duplicate HTML ids: {duplicates}")
    known = set(index.ids)
    dead = sorted({target for target in index.internal_targets if target not in known})
    if dead:
        errors.append(f"internal links with no target: {dead}")

    # 5. every evidence citation is one ID linked to its own ledger row
    if not index.evidence_links:
        errors.append("no evidence citations found in the report")
    for href, label, line in index.evidence_links:
        if not EVIDENCE_ID.match(label):
            errors.append(
                f"line {line}: evidence-link text {label!r} must be exactly one"
                " evidence ID — keep 〔 、 〕 outside the anchor"
            )
            continue
        if href != f"#{label}":
            errors.append(f"line {line}: evidence-link {label} points at {href!r}")
        elif label not in known:
            errors.append(f"line {line}: evidence-link {label} has no ledger row")
        elif "ledger-row" not in index.classes_by_id.get(label, set()):
            errors.append(f"line {line}: {label} exists but is not a ledger-row")

    # 6. every deferred boundary is labelled, and discharged in Section 7
    for line, section in index.unlabelled_boundaries:
        errors.append(
            f"line {line}: section {section} states a 证据边界 with no B-id —"
            " an unlabelled boundary cannot be checked against Section 7"
        )
    discharged = {target for target, in_context in index.boundary_links if in_context}
    linked_anywhere = {target for target, _ in index.boundary_links}
    for boundary, section in index.boundary_ids:
        if boundary in discharged:
            continue
        if boundary in linked_anywhere:
            errors.append(
                f"{boundary} is linked, but not from a review card or"
                f" #{NO_EFFECT_BLOCK} — a passing mention is not a discharge"
            )
        else:
            errors.append(
                f"evidence boundary {boundary} is raised in section {section}"
                " but never discharged in Section 7"
            )
    if not index.boundary_ids:
        warnings.append(
            'no evidence boundaries (id="Bnn") were raised — expected at least one'
            " conclusion-changing fact deferred to Section 7"
        )

    # 7. review cards carry the full contract field set, in order
    if not index.review_card_fields:
        errors.append("Section 7 has no review cards")
    for card_id, fields in index.review_card_fields:
        present = [f for f in fields if f in REVIEW_CARD_FIELDS]
        if present != REVIEW_CARD_FIELDS:
            missing = [f for f in REVIEW_CARD_FIELDS if f not in present]
            problem = f"missing {missing}" if missing else f"out of order: {present}"
            errors.append(f"review card {card_id}: {problem}")

    # 8. offline and self-contained
    for resource in index.external_resources:
        errors.append(f"external resource: {resource}")
    if "@import" in text:
        errors.append("stylesheet uses @import")

    # 9. footer disclosures survive printing
    for disclosure in FOOTER_DISCLOSURES:
        if disclosure not in known:
            errors.append(f"missing footer disclosure #{disclosure}")
        elif not index.details_open.get(disclosure, False):
            errors.append(
                f"#{disclosure} must carry the open attribute so print and PDF"
                " keep the cited evidence visible"
            )

    # 10. declared mode and completion status
    # join with spaces: adjacent badges produce adjacent text nodes, and
    # "standard" + "partial" concatenated would hide the word boundary
    hero = " ".join(index.hero_text)
    if not re.search(r"mode\s*[:：]\s*(standard|audit)", hero):
        errors.append("hero metadata must record mode: standard|audit")
    if not re.search(r"\b(complete|partial)\b", hero):
        errors.append("hero metadata must record complete|partial")

    # 11. figure output must match the selected figure mode, in both directions
    has_figure_block = FIGURE_OUTPUT in known
    if figure == "off":
        if has_figure_block:
            errors.append(f"figure=off but #{FIGURE_OUTPUT} is present")
        if index.images:
            errors.append(f"figure=off but the report embeds images: {index.images}")
    elif not has_figure_block:
        errors.append(
            f"figure={figure} but the report has no #{FIGURE_OUTPUT} section"
        )
    elif figure == "generate" and not index.images:
        errors.append("figure=generate but no image was embedded")

    # -- warnings --------------------------------------------------------
    body_cjk = len(CJK.findall("".join(index.main_text)))
    if not READING_LENGTH_MIN <= body_cjk <= READING_LENGTH_MAX:
        warnings.append(
            f"main report is {body_cjk} CJK characters; the 15–20 minute reading"
            f" path is roughly {READING_LENGTH_MIN}–{READING_LENGTH_MAX}"
        )
    cited = {label for _href, label, _line in index.evidence_links}
    uncited = sorted(i for i in known if EVIDENCE_ID.match(i) and i not in cited)
    if uncited:
        warnings.append(f"ledger rows never cited in the report: {uncited}")

    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="the delivered report HTML")
    parser.add_argument(
        "--template",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "assets" / "report-template.html",
    )
    parser.add_argument("--figure", choices=("off", "brief", "generate"), default="off")
    args = parser.parse_args(argv)

    if not args.report.is_file():
        print(f"FAIL {args.report}: file not found", file=sys.stderr)
        return 1

    errors, warnings = validate(args.report, args.template, args.figure)
    for warning in warnings:
        print(f"warn  {warning}")
    for error in errors:
        print(f"FAIL  {error}", file=sys.stderr)
    if errors:
        print(f"\n{len(errors)} contract violation(s) in {args.report}", file=sys.stderr)
        return 1
    print(f"ok    {args.report} satisfies the output contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
