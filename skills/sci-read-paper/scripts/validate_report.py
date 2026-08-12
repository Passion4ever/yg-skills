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
from collections import Counter
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
EXPERIMENT_CARD_FIELDS = [
    "作者要回答什么",
    "实验类型",
    "实验怎样设计",
    "改变了什么，控制了什么",
    "数据与指标",
    "实际观察到什么",
    "作者据此主张什么",
    "证据边界",
]

# Closed vocabularies. Each of these is a set the report chooses from, never a
# phrase it invents: two reports that name the same kind of experiment
# differently cannot be compared, and comparability is the whole point of a
# fixed contract. The choice stays a judgement; the wording does not.
EXPERIMENT_TYPES = [
    "主实验", "基线对比", "对照", "消融", "稳健性", "泛化", "分析", "案例研究", "外部验证",
]
IMPACT_CALIBRATIONS = ["无实质影响", "降低置信", "收窄范围", "削弱主张", "否定主张"]
VERDICTS = {
    "被现有证据否定": "verdict-rejected",
    "当前不能推出": "verdict-qualified",
    "可以暂时相信": "verdict-qualified",
    "可以相信": "verdict-supported",
}
LEDGER_LABELS = {"[论文]", "[代码]", "[外部核验]", "[推断]", "[缺失]", "[冲突]"}
LEDGER_COLUMNS = 7
BUILD_META = "sci-read-paper"
SECTION_MIN_CJK = 300
# a 证据边界 field that raises nothing writes exactly 无 and needs no B-id
EMPTY_BOUNDARY = re.compile(r"证据边界\s*[：:]\s*无\s*$")
# the label sits in an inline tag; the value it introduces belongs to the block around it
INLINE_TAGS = {
    "a", "b", "code", "em", "i", "mark", "small", "span", "strong", "sub", "sup", "u",
}
FOOTER_DISCLOSURES = ("report-info", "evidence-ledger")
# audit mode adds traceability, not a second narrative. The four panels are a
# fixed set: an audit report that ships three of them, or renames one, is not a
# different reading — it is an incomplete one, and nothing said so until now.
AUDIT_PANELS = ("data-training", "model-dataflow", "experiment-matrix", "critical-review")
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
READING_LENGTH_BASE = 8000
READING_LENGTH_PER_BOUNDARY = 350

# Readability. A Chinese technical sentence reads comfortably at 30–50 characters.
# Both limits sit well above that, so breaching one means a genuine run-on rather
# than a dense-but-fair sentence.
SENTENCE_HARD_CAP = 120
SENTENCE_P90_CAP = 80
SENTENCE_MEDIAN_TARGET = 45
# Distinct English terms per 1000 CJK characters — not the share of Latin
# characters, which conflates two opposite things. Reusing one glossed term a
# hundred times is the healthy pattern; introducing a hundred terms once each is
# what makes a report unreadable, and only the second is a writing problem.
# Calibrated on the shipped readings: 12 and 17 for the two that read cleanly,
# 44 for the one still carrying ability/achieved/available in English.
# Two tiers, because a warning is not a gate. The old Latin-share warning fired on
# a shipped reading for two rounds and the reading shipped anyway; whatever only
# warns is whatever drifts. Warn above 28 — look at it — and fail above 40, which
# no reading that reads cleanly has ever approached (10.8, 16.3, 18.4 observed).
TERM_DENSITY_WARN = 28
TERM_DENSITY_FAIL = 40
# card values live in <dd>; leaving it out would exempt every card from the
# sentence-length limits, which is where the densest writing actually is
PROSE_TAGS = {"p", "li", "dd"}
NON_PROSE_TAGS = {"table", "pre", "code", "style", "script"}
SENTENCE_SPLIT = re.compile(r"[。！？]")
CITATION = re.compile(r"〔[^〕]*〕")
LATIN_TERM = re.compile(r"[A-Za-z][A-Za-z0-9\-']*")
BARE_BOUNDARY_ID = re.compile(r"\bB\d{2,}\b")


class Element:
    __slots__ = ("tag", "id", "classes", "boundary_line", "boundary_section", "buf")

    def __init__(self, tag: str, element_id: str, classes: set[str]) -> None:
        self.tag = tag
        self.id = element_id
        self.classes = classes
        self.boundary_line: int | None = None
        self.boundary_section: int | None = None
        self.buf: list[str] | None = None


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
        self.experiment_card_fields: list[tuple[str, list[str]]] = []
        self.details_open: dict[str, bool] = {}
        self.external_resources: list[str] = []
        self.structural_errors: list[str] = []
        self.main_text: list[str] = []
        self.hero_text: list[str] = []
        self.images: list[str] = []
        self.prose_blocks: list[str] = []
        self.section_text: dict[int, list[str]] = {}
        self.panel_text: dict[str, list[str]] = {}
        self.status_badges: list[str] = []
        self.ledger_rows: list[tuple[str, list[str]]] = []
        self.verdict_cards: list[tuple[set[str], str, int]] = []
        self.used_classes: set[str] = set()
        self.build_meta = ""
        self._prose_buf: list[str] | None = None
        self._non_prose = 0

        self._stack: list[Element] = []
        self._in_style = False
        self._style_buf: list[str] = []
        self._capture: list[str] | None = None
        self._capture_kind: str | None = None
        self._capture_href = ""
        self._card_stack: list[list[list]] = []
        self._value: list[str] | None = None
        self._cells: list[str] | None = None
        self._cell: list[str] | None = None

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

    def _current_card(self) -> list[list] | None:
        return self._card_stack[-1] if self._card_stack else None

    def _verdict_classes(self) -> set[str] | None:
        for element in reversed(self._stack):
            hit = {c for c in element.classes if c.startswith("verdict-")}
            if hit:
                return hit
        return None

    def _close_prose_block(self) -> None:
        if self._prose_buf is not None:
            self.prose_blocks.append("".join(self._prose_buf))
            self._prose_buf = None

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
                card.append([text.rstrip("：: "), [], ""])
        elif self._capture_kind == "badge":
            self.status_badges.append(text)
        elif self._capture_kind == "verdict":
            classes = self._verdict_classes()
            if classes is not None:
                self.verdict_cards.append((classes, text, self.getpos()[0]))
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
        if tag == "meta" and attributes.get("name") == BUILD_META:
            self.build_meta = attributes.get("content", "")
        self.used_classes.update(classes)
        if "ledger-row" in classes:
            self._cells = []
            self.ledger_rows.append((element_id or f"line {line}", self._cells))
        if tag == "td" and self._cells is not None:
            self._cell = []
        if tag == "dd" and self._current_card():
            field = self._current_card()[-1]
            self._value = field[1]
            field[2] = element_id
        if tag in NON_PROSE_TAGS:
            self._non_prose += 1
        elif (
            tag in PROSE_TAGS
            and self._in_main()
            and not self._non_prose
            # CHAPTER 07 is furniture, not a sentence the reader parses
            and "chapter-label" not in classes
        ):
            self._close_prose_block()
            self._prose_buf = []

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
        elif tag == "dt" and self._current_card() is not None:
            self._capture, self._capture_kind = [], "field"
        elif "status-badge" in classes:
            self._capture, self._capture_kind = [], "badge"
        elif tag == "h3" and self._verdict_classes() is not None:
            self._capture, self._capture_kind = [], "verdict"

        if tag not in VOID_TAGS:
            self._stack.append(Element(tag, element_id, classes))
            for marker, sink in (
                ("review-card", self.review_card_fields),
                ("experiment-card", self.experiment_card_fields),
            ):
                if marker in classes:
                    card: list[list] = []
                    self._card_stack.append(card)
                    sink.append((element_id or f"line {line}", card))

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
        if self._value is not None:
            self._value.append(data)
        if self._cell is not None:
            self._cell.append(data)
        if self._prose_buf is not None and not self._non_prose:
            self._prose_buf.append(data)
        if self._in_main():
            self.main_text.append(data)
        if self._in_hero():
            self.hero_text.append(data)
        in_section = self.section
        if in_section is not None:
            self.section_text.setdefault(in_section, []).append(data)
        for element in self._stack:
            if element.id in AUDIT_PANELS:
                self.panel_text.setdefault(element.id, []).append(data)

        # A 证据边界 needs a B-id unless its whole value is 无. The verdict can only
        # be reached once the containing element closes, so start buffering here.
        for element in self._stack:
            if element.buf is not None:
                element.buf.append(data)
        section = self.section
        # A card's own 证据边界 field is checked structurally in validate(): its
        # B-id sits on the sibling <dd>, not on an ancestor, so the ancestor walk
        # below would report every well-formed card as unlabelled.
        if (
            section is not None
            and 1 <= section <= 6
            and "证据边界" in data
            and "处理的证据边界" not in data
            and self._current_card() is None
            and not self._has_boundary_ancestor()
            and self._stack
        ):
            # attach to the enclosing block, not to the <strong> holding the label
            holder = next(
                (e for e in reversed(self._stack) if e.tag not in INLINE_TAGS),
                self._stack[-1],
            )
            if holder.boundary_line is None:
                holder.boundary_line = self.getpos()[0]
                holder.boundary_section = section
                holder.buf = [data]

    def handle_endtag(self, tag: str) -> None:
        if tag == "style":
            self._in_style = False
            self.styles.append("".join(self._style_buf))
        if tag in PROSE_TAGS:
            self._close_prose_block()
        if tag in NON_PROSE_TAGS:
            self._non_prose = max(0, self._non_prose - 1)
        if tag == "td" and self._cell is not None and self._cells is not None:
            self._cells.append("".join(self._cell).strip())
            self._cell = None
        if tag == "dd":
            self._value = None
        self._flush_capture()

        if not any(element.tag == tag for element in self._stack):
            self.structural_errors.append(
                f"line {self.getpos()[0]}: stray </{tag}> with no open element"
            )
            return
        while self._stack:
            popped = self._stack.pop()
            if (
                "review-card" in popped.classes or "experiment-card" in popped.classes
            ) and self._card_stack:
                self._card_stack.pop()
            if "ledger-row" in popped.classes:
                self._cells = None
            if popped.boundary_line is not None:
                text = re.sub(r"\s+", "", "".join(popped.buf or []))
                if not EMPTY_BOUNDARY.search(text):
                    self.unlabelled_boundaries.append(
                        (popped.boundary_line, popped.boundary_section)
                    )
            if popped.tag == tag:
                break
            if popped.tag == "section" and re.fullmatch(r"section-[1-8]", popped.id):
                self.structural_errors.append(
                    f"line {self.getpos()[0]}: </{tag}> closes across"
                    f" the still-open <section id=\"{popped.id}\">"
                )


def prose_sentences(blocks: list[str]) -> list[str]:
    """Sentences a human actually reads: paragraph and list text, no tables or code.

    Evidence citations are stripped first — 〔E01、E02〕 is punctuation to the eye,
    not words, and counting it would penalise well-cited prose.
    """
    sentences = []
    for block in blocks:
        text = CITATION.sub("", re.sub(r"\s+", "", block))
        sentences.extend(s for s in SENTENCE_SPLIT.split(text) if len(s) > 4)
    return sentences


def prose_terms(blocks: list[str]) -> tuple[Counter[str], int]:
    """Distinct English terms in the prose, and the CJK characters around them.

    Whitespace is collapsed to a single space rather than removed. Removing it —
    which is right for measuring a Chinese sentence — welds `ablation study` into
    one token and would make the vocabulary look wider than it is.

    Evidence citations and bare boundary ids are stripped first: E01 and B07 are
    references, not terms the reader has to learn.
    """
    terms: Counter[str] = Counter()
    cjk = 0
    for block in blocks:
        text = BARE_BOUNDARY_ID.sub("", CITATION.sub("", re.sub(r"\s+", " ", block)))
        terms.update(match.lower() for match in LATIN_TERM.findall(text))
        cjk += len(CJK.findall(text))
    return terms, cjk


def load_template_style(template: Path) -> str | None:
    if not template.is_file():
        return None
    index = ReportIndex()
    index.feed(template.read_text(encoding="utf-8"))
    return index.styles[0] if index.styles else None


def validate(
    path: Path, template: Path, figure: str | None = None
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8")
    index = ReportIndex()
    index.feed(text)

    # 0. structural integrity — everything below assumes the tree parses sanely
    errors.extend(index.structural_errors)

    # 1. no unreplaced template tokens (the truncation and copy-paste tripwire)
    for token in sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", text))):
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
    # the class carries the amber panel and the :target highlight, so a boundary
    # without it renders as ordinary text and Section 7's link lands invisibly
    for boundary, _section in index.boundary_ids:
        if "evidence-boundary" not in index.classes_by_id.get(boundary, set()):
            errors.append(
                f'{boundary} does not carry class="evidence-boundary";'
                " Section 7's link would jump to an unhighlighted element"
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

    # 7. cards carry the full contract field set, in order
    # Enforced on both card kinds: whatever the validator does not check drifts.
    if not index.review_card_fields:
        errors.append("Section 7 has no review cards")
    if not index.experiment_card_fields:
        errors.append("Section 6 has no experiment cards")
    for kind, expected, cards in (
        ("review", REVIEW_CARD_FIELDS, index.review_card_fields),
        ("experiment", EXPERIMENT_CARD_FIELDS, index.experiment_card_fields),
    ):
        for card_id, fields in cards:
            present = [label for label, _value, _id in fields if label in expected]
            if present != expected:
                missing = [f for f in expected if f not in present]
                extra = [f for f in present if present.count(f) > 1]
                if missing:
                    problem = f"missing {missing}"
                elif extra:
                    problem = f"duplicated {sorted(set(extra))}"
                else:
                    problem = f"out of order: {present}"
                errors.append(f"{kind} card {card_id}: {problem}")
            values = {label: "".join(value).strip() for label, value, _id in fields}
            field_ids = {label: field_id for label, _value, field_id in fields}
            if kind == "experiment":
                actual = values.get("实验类型", "")
                if actual and not any(actual.startswith(t) for t in EXPERIMENT_TYPES):
                    errors.append(
                        f"experiment card {card_id}: 实验类型 {actual[:24]!r} must start"
                        f" with one of {EXPERIMENT_TYPES}"
                    )
                # 无 may arrive quoted or punctuated; the fragment library says
                # "write 无" in prose and a writer copying it reasonably keeps the
                # brackets. Rejecting that would be the gate contradicting the
                # instruction, which is the bug class this contract exists to kill.
                boundary = values.get("证据边界", "").strip("「」“”\"'。. \t")
                boundary_id = field_ids.get("证据边界", "")
                if boundary and boundary != "无" and not BOUNDARY_ID.match(boundary_id):
                    errors.append(
                        f"experiment card {card_id}: the 证据边界 field needs its own"
                        " Bnn id, or the whole value must be 无"
                    )
            else:
                actual = values.get("对中心结论的影响", "")
                if actual and not any(actual.startswith(c) for c in IMPACT_CALIBRATIONS):
                    errors.append(
                        f"review card {card_id}: 对中心结论的影响 {actual[:24]!r} must"
                        f" start with one of {IMPACT_CALIBRATIONS}"
                    )

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

    # 10. declared mode and completion status.
    # The report carries exactly two badges. A third one — the footer copy that
    # drifted into one shipped report, or a figure badge the contract forbids —
    # means the status is being restated somewhere it can fall out of sync.
    declared = dict(
        part.strip().split("=", 1) for part in index.build_meta.split(";") if "=" in part
    )
    mode = declared.get("mode", "")
    if mode not in ("standard", "audit"):
        errors.append(
            f'<meta name="{BUILD_META}"> must declare mode=standard|audit,'
            f" found {index.build_meta!r} — scaffold with scripts/new_report.py"
        )
    badges = [b.strip() for b in index.status_badges]
    if badges[:1] != [f"mode: {mode}"] or len(badges) != 2:
        errors.append(
            f'expected exactly two status badges, "mode: {mode}" then'
            f" complete|partial, found {badges}"
        )
    elif badges[1] not in ("complete", "partial"):
        errors.append(f"second status badge must be complete|partial, found {badges[1]!r}")

    # 10b. audit mode ships exactly the four panels, collapsed; standard ships none
    for panel in AUDIT_PANELS:
        present = panel in known
        if mode == "audit" and not present:
            errors.append(f"mode=audit but the #{panel} panel is missing")
        elif mode == "standard" and present:
            errors.append(
                f"mode=standard but #{panel} is present —"
                " audit panels belong in the audit deliverable"
            )
        elif mode == "audit" and index.details_open.get(panel, False):
            errors.append(
                f"#{panel} must ship collapsed; the print rules already expose it"
            )

    # 11. figure output must match the declared figure mode, in both directions.
    # The mode is read from the file, not from a flag the caller supplies: a
    # report validated against the mode it was not built in checks nothing.
    declared_figure = declared.get("figure", "")
    if declared_figure not in ("off", "brief", "generate"):
        errors.append(
            f'<meta name="{BUILD_META}"> must declare figure=off|brief|generate,'
            f" found {index.build_meta!r}"
        )
    elif figure is not None and figure != declared_figure:
        errors.append(
            f"--figure {figure} contradicts the report's own figure={declared_figure}"
        )
    has_figure_block = FIGURE_OUTPUT in known
    if declared_figure == "off":
        if has_figure_block:
            errors.append(f"figure=off but #{FIGURE_OUTPUT} is present")
        if index.images:
            errors.append(f"figure=off but the report embeds images: {index.images}")
    elif declared_figure in ("brief", "generate"):
        if not has_figure_block:
            errors.append(
                f"figure={declared_figure} but the report has no #{FIGURE_OUTPUT} section"
            )
        elif declared_figure == "generate" and not index.images:
            errors.append("figure=generate but no image was embedded")

    # 12. readability — the deliverable is read by a person, not compiled
    sentences = prose_sentences(index.prose_blocks)
    if not sentences:
        errors.append("no prose paragraphs found in <main>")
    else:
        lengths = sorted(len(s) for s in sentences)
        median = lengths[len(lengths) // 2]
        p90 = lengths[min(len(lengths) - 1, int(len(lengths) * 0.9))]
        runons = [s for s in sentences if len(s) > SENTENCE_HARD_CAP]
        for sentence in runons[:5]:
            errors.append(f"run-on sentence, {len(sentence)} chars: {sentence[:36]}…")
        if len(runons) > 5:
            errors.append(
                f"and {len(runons) - 5} more sentences over {SENTENCE_HARD_CAP} characters"
            )
        if p90 > SENTENCE_P90_CAP:
            errors.append(
                f"90th-percentile sentence is {p90} characters, limit {SENTENCE_P90_CAP};"
                " the long tail is what makes a report read as dense"
            )
        if median > SENTENCE_MEDIAN_TARGET:
            warnings.append(
                f"median sentence is {median} characters; aim for {SENTENCE_MEDIAN_TARGET}"
            )
    terms, prose_cjk = prose_terms(index.prose_blocks)
    if prose_cjk:
        density = 1000 * len(terms) / prose_cjk
        if density > TERM_DENSITY_WARN:
            # used once, all lower case, no digits or hyphens: almost never a
            # proper name or a metric, almost always a word Chinese could carry
            ordinary = sorted(
                term for term, uses in terms.items()
                if uses == 1 and term.isalpha() and len(term) > 3
            )
            report = (
                f"{len(terms)} distinct English terms in {prose_cjk} Chinese characters"
                f" ({density:.0f} per 1000, limit {TERM_DENSITY_FAIL});"
                f" {len(ordinary)} appear once as ordinary words —"
                f" say those in Chinese, e.g. {', '.join(ordinary[:8])}"
            )
            (errors if density > TERM_DENSITY_FAIL else warnings).append(report)

    # 13. the ledger is a table with a fixed shape and a closed label set
    for row_id, cells in index.ledger_rows:
        if len(cells) != LEDGER_COLUMNS:
            errors.append(
                f"ledger row {row_id} has {len(cells)} cells, expected {LEDGER_COLUMNS}"
                " (ID/类型/来源/版本/定位/支持的陈述/获取状态)"
            )
        elif cells[1] not in LEDGER_LABELS:
            errors.append(
                f"ledger row {row_id} is labelled {cells[1]!r};"
                f" the evidence label must be one of {sorted(LEDGER_LABELS)}"
            )

    # 14. graded verdicts use the contract's four terms, and the colour matches
    for classes, heading, line in index.verdict_cards:
        term = next((v for v in VERDICTS if heading.startswith(v)), None)
        if term is None:
            errors.append(
                f"line {line}: verdict card heading {heading[:20]!r} must start with"
                f" one of {list(VERDICTS)}"
            )
        elif classes != {VERDICTS[term]}:
            errors.append(
                f"line {line}: {term!r} must carry {VERDICTS[term]},"
                f" found {sorted(classes)}"
            )

    # 15. the interpretation/critique wall — Sections 1–6 explain, Section 7 judges.
    # This is the skill's central structural claim, so it gets a mechanical check
    # rather than a paragraph of prose nobody can verify after the fact.
    # The audit panels sit on the same side of the wall as Sections 1–6: they add
    # traceability, not a second verdict. Leaving them out let a graded judgement
    # reappear in an appendix where nothing could check it against the boundaries.
    graded = [(f"section {n}", index.section_text.get(n, [])) for n in range(1, 7)]
    graded += [(f"#{p}", text) for p, text in index.panel_text.items()]
    for where, chunks in graded:
        body = "".join(chunks)
        for term in VERDICTS:
            if term in body:
                errors.append(
                    f"{where} contains the verdict {term!r};"
                    " graded judgement belongs in Section 7"
                )

    # 16. only classes the template's stylesheet actually defines
    if template_style:
        defined = set(re.findall(r"\.([A-Za-z][\w-]*)", template_style))
        invented = sorted(index.used_classes - defined)
        if invented:
            errors.append(
                f"classes with no rule in the template stylesheet: {invented}"
                " — express report-specific needs with the classes it already defines"
            )

    # 17. Section 7 always closes its bookkeeping, even when the list is short
    if NO_EFFECT_BLOCK not in known:
        errors.append(
            f"missing #{NO_EFFECT_BLOCK} — Section 7 states which boundaries"
            " changed nothing, rather than leaving that silent"
        )

    # 18. no section may be a stub: a truncated write is otherwise invisible
    for number in range(1, 9):
        size = len(CJK.findall("".join(index.section_text.get(number, []))))
        if size < SECTION_MIN_CJK:
            errors.append(
                f"section {number} holds {size} CJK characters, below the"
                f" {SECTION_MIN_CJK} floor — it reads as truncated, not concise"
            )

    # -- warnings --------------------------------------------------------
    # Every boundary costs roughly one paragraph to state and another to discharge,
    # so a boundary-dense paper is legitimately longer than a thin one.
    # The 15–20 minute path is the eight sections. Audit panels and figure output
    # are lookup material — counting them would make every audit run trip a band
    # that was calibrated on the reading itself.
    reading = "".join("".join(index.section_text.get(n, [])) for n in range(1, 9))
    body_cjk = len(CJK.findall(reading))
    ceiling = max(
        READING_LENGTH_MAX,
        READING_LENGTH_BASE + READING_LENGTH_PER_BOUNDARY * len(index.boundary_ids),
    )
    if not READING_LENGTH_MIN <= body_cjk <= ceiling:
        warnings.append(
            f"main report is {body_cjk} CJK characters; with {len(index.boundary_ids)}"
            f" evidence boundaries the 15–20 minute reading path is roughly"
            f" {READING_LENGTH_MIN}–{ceiling}"
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
    parser.add_argument(
        "--figure",
        choices=("off", "brief", "generate"),
        default=None,
        help="optional cross-check against the figure mode recorded in the report",
    )
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
