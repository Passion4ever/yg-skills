import json
import re
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "sci-read-paper"
SKILL_MD = SKILL_DIR / "SKILL.md"
VALIDATOR = SKILL_DIR / "scripts" / "validate_report.py"
OPENAI_YAML = SKILL_DIR / "agents" / "openai.yaml"
EVALS_JSON = ROOT / "tests" / "sci-read-paper" / "evals.json"
READABILITY_RUBRIC = ROOT / "tests" / "sci-read-paper" / "readability-rubric.md"
HTML_TEMPLATE = SKILL_DIR / "assets" / "report-template.html"
FRAGMENTS = SKILL_DIR / "assets" / "fragments.html"
SCAFFOLD = SKILL_DIR / "scripts" / "new_report.py"
SIAMPROM_HTML = (
    ROOT / "tests" / "sci-read-paper" / "outputs" / "siamprom-cyanobacteria-promoters.html"
)
CPROMG_HTML = (
    ROOT
    / "tests"
    / "sci-read-paper"
    / "outputs"
    / "cpromg-protein-oriented-molecule-generation.html"
)
EXPECTED_SECTION_TITLES = [
    "为什么要做这项研究：背景、现状与本文切入点",
    "三分钟建立论文全局地图",
    "从问题到方法：作者为什么这样设计",
    "数据从哪里来，又怎样进入训练",
    "模型内部：数据怎样一步步变成输出",
    "实验逻辑：每项实验在回答什么问题",
    "批判性审查：证据究竟支持到哪里",
    "读完这篇论文，真正应该带走什么",
]
EXPECTED_REFERENCES = {
    "evidence-policy.md",
    "ai-ml-reading-guide.md",
    "bio-chem-validity.md",
    "output-contract.md",
}


class DocumentIndex(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids: list[str] = []
        self.internal_targets: list[str] = []
        self.section_ids: list[str] = []
        self.classes: list[str] = []
        self._main_depth = 0
        self._active_evidence_link: tuple[str, list[str]] | None = None
        self.main_report_evidence_links: list[tuple[str, str]] = []
        self._active_evidence_citation: list[tuple[str, str]] = []
        self.main_report_evidence_citations: list[list[tuple[str, str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        attributes = dict(attrs)
        if tag == "main":
            self._main_depth += 1
        element_id = attributes.get("id")
        if element_id:
            self.ids.append(element_id)
            if tag == "section" and re.fullmatch(r"section-[1-8]", element_id):
                self.section_ids.append(element_id)
        href = attributes.get("href")
        if tag == "a" and href and href.startswith("#"):
            self.internal_targets.append(href[1:])
        self.classes.extend((attributes.get("class") or "").split())
        if (
            tag == "a"
            and self._main_depth
            and "evidence-link" in (attributes.get("class") or "").split()
        ):
            self._active_evidence_link = (href or "", [])

    def handle_data(self, data: str):
        if self._active_evidence_link is not None:
            self._active_evidence_link[1].append(data)

    def handle_endtag(self, tag: str):
        if tag == "a" and self._active_evidence_link is not None:
            href, text = self._active_evidence_link
            evidence_link = (href, "".join(text))
            self.main_report_evidence_links.append(evidence_link)
            self._active_evidence_citation.append(evidence_link)
            if evidence_link[1].endswith("〕"):
                self.main_report_evidence_citations.append(self._active_evidence_citation)
                self._active_evidence_citation = []
            self._active_evidence_link = None
        if tag == "main":
            self._main_depth -= 1


def read_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not match:
        raise AssertionError("SKILL.md must have YAML frontmatter")
    return yaml.safe_load(match.group(1)), match.group(2)


def extract_css_rule(text: str, selector: str) -> str:
    match = re.search(rf"{re.escape(selector)}\s*\{{(.*?)\}}", text, re.DOTALL)
    if not match:
        raise AssertionError(f"missing CSS rule: {selector}")
    return match.group(1)


def extract_single_style(text: str) -> str:
    """Return the one stylesheet a contract-conforming document may carry.

    The old implementation sliced from the first ``:root``, which silently
    discarded a foreign stylesheet sitting above it. Raising here is the point.
    """
    blocks = re.findall(r"<style>(.*?)</style>", text, re.DOTALL)
    if len(blocks) != 1:
        raise AssertionError(
            f"expected exactly one <style> block, found {len(blocks)}"
        )
    return blocks[0]


def assert_frameflow_inspired_layout(testcase: unittest.TestCase, text: str):
    custom_styles = extract_single_style(text)
    sidebar_rule = extract_css_rule(text, ".sidebar")
    visited_nav_rule = extract_css_rule(text, ".nav-link:visited")
    content_rule = extract_css_rule(text, ".content-shell")
    chapter_rule = extract_css_rule(text, "main > section.report-section")
    root_rule = extract_css_rule(custom_styles, "html")
    body_rule = extract_css_rule(custom_styles, "body")

    for declaration in (
        "width: 280px",
        "position: fixed",
        "background: var(--nav)",
    ):
        testcase.assertIn(declaration, sidebar_rule)
    testcase.assertIn("margin-left: 280px", content_rule)
    testcase.assertIn("max-width: 980px", content_rule)
    testcase.assertIn("color: rgba(255, 255, 255, 0.56)", visited_nav_rule)
    for declaration in (
        "background: transparent",
        "border: 0",
        "border-radius: 0",
        "box-shadow: none",
    ):
        testcase.assertIn(declaration, chapter_rule)

    for group in ("论文概览", "问题与方法", "实验与审查", "最终结论", "报告附录"):
        testcase.assertIn(group, text)
    testcase.assertIn("论文速览", text)
    testcase.assertNotIn('class="summary-grid"', text)
    testcase.assertNotIn('class="summary-card', text)
    testcase.assertNotIn("overflow-x: clip", root_rule)
    testcase.assertNotIn("overflow-x: clip", body_rule)


class SkillContractTests(unittest.TestCase):

    def contract(self) -> str:
        """Line wrapping is not a contract change; assert on collapsed whitespace."""
        raw = (SKILL_DIR / "references" / "output-contract.md").read_text(encoding="utf-8")
        return " ".join(raw.split())

    def test_skill_exists(self):
        self.assertTrue(SKILL_MD.is_file(), "sci-read-paper has not been implemented")

    def test_frontmatter_is_minimal_and_discoverable(self):
        frontmatter, _body = read_frontmatter(SKILL_MD)
        self.assertEqual(set(frontmatter), {"name", "description"})
        self.assertEqual(frontmatter["name"], "sci-read-paper")
        description = frontmatter["description"]
        self.assertTrue(description.startswith("Use when "))
        self.assertLessEqual(len(description), 500)
        for keyword in ("AI/ML", "paper", "protein", "small-molecule"):
            self.assertIn(keyword, description)

    def test_skill_body_is_compact(self):
        _frontmatter, body = read_frontmatter(SKILL_MD)
        self.assertLessEqual(len(body.split()), 500)

    def test_skill_lists_supported_starting_inputs(self):
        text = SKILL_MD.read_text(encoding="utf-8")
        for starting_input in (
            "PDF",
            "title",
            "DOI",
            "arXiv",
            "journal page",
            "official repository",
        ):
            self.assertIn(starting_input, text)

    def test_references_are_direct_and_complete(self):
        text = SKILL_MD.read_text(encoding="utf-8")
        reference_dir = SKILL_DIR / "references"
        actual = {path.name for path in reference_dir.glob("*.md")}
        self.assertEqual(actual, EXPECTED_REFERENCES)
        for name in EXPECTED_REFERENCES:
            self.assertIn(f"(references/{name})", text)

    def test_openai_metadata_matches_skill(self):
        metadata = yaml.safe_load(OPENAI_YAML.read_text(encoding="utf-8"))
        interface = metadata["interface"]
        self.assertEqual(interface["display_name"], "SCI Read Paper")
        self.assertGreaterEqual(len(interface["short_description"]), 25)
        self.assertLessEqual(len(interface["short_description"]), 64)
        self.assertIn("$sci-read-paper", interface["default_prompt"])


    def test_output_contract_has_one_primary_report(self):
        contract = self.contract()
        self.assertIn("`<paper-slug>.html`", contract)
        self.assertIn("`<paper-slug>-audit.html`", contract)
        self.assertIn("embedded ledger", contract)
        self.assertIn("panels", contract)
        self.assertIn("sci-diagram", contract)
        self.assertNotIn("sci-ai-figure", contract, "handoff names a skill that does not exist")

    def test_figure_mode_is_explicit_and_defaults_off(self):
        skill = " ".join(SKILL_MD.read_text(encoding="utf-8").split())
        contract = self.contract()
        for state in ("figure=off", "figure=brief", "figure=generate"):
            self.assertIn(state, skill)
            self.assertIn(state, contract)
        self.assertIn("default", skill)
        self.assertIn("fall back to `figure=brief`", contract)
        self.assertIn("does not change the completion status", contract)


    def test_standard_mode_has_one_html_output(self):
        contract = self.contract()
        self.assertIn("`standard` delivers `<paper-slug>.html`", contract)
        self.assertNotIn("deep-reading.md", contract)
        self.assertNotIn("evidence-ledger.md", contract)

    def test_audit_mode_has_one_html_output(self):
        contract = self.contract()
        self.assertIn("`<paper-slug>-audit.html`", contract)
        for panel in ("data-training", "model-dataflow", "experiment-matrix", "critical-review"):
            self.assertIn(panel, contract)
        self.assertIn("not a second narrative", contract)


    def test_standard_mode_bounds_research_scope(self):
        skill = SKILL_MD.read_text(encoding="utf-8")
        policy = (SKILL_DIR / "references" / "evidence-policy.md").read_text(encoding="utf-8")
        guide = (SKILL_DIR / "references" / "ai-ml-reading-guide.md").read_text(encoding="utf-8")
        self.assertIn("standard", skill)
        self.assertIn("audit", skill)
        self.assertIn("at most three conclusion-critical claim families", policy)
        self.assertIn("shortest conclusion-relevant path", guide)
        # The workflow acquires the repository at step 2, which loads evidence-policy,
        # so the guardrail has to be there rather than in the step-4 guide.
        self.assertIn("sparse or blob-filtered repository retrieval", policy)
        self.assertIn("never download weights", policy)
        self.assertIn("evidence-policy.md", guide)

    def test_report_records_selected_mode(self):
        """Recorded in the file by the scaffolder, not retyped by the writer."""
        template = HTML_TEMPLATE.read_text(encoding="utf-8")
        validator = VALIDATOR.read_text(encoding="utf-8")
        self.assertIn('content="mode={{MODE}}; figure={{FIGURE}}"', template)
        self.assertIn('<span class="status-badge">mode: {{MODE}}</span>', template)
        self.assertIn("complete|partial", validator)
        self.assertIn("mode=standard|audit", validator)

    def test_readability_rubric_contract(self):
        text = READABILITY_RUBRIC.read_text(encoding="utf-8")
        for criterion in (
            "Background orientation",
            "Three-minute map",
            "Causal narrative",
            "Concrete sample",
            "Progressive technical depth",
            "Chinese-first prose",
            "Plain language",
            "Readable evidence",
            "Main/audit separation",
            "HTML reading experience",
        ):
            self.assertIn(f"| {criterion} |", text)
        self.assertIn("at least 18/20", text)
        self.assertIn("scientific-depth score", text)


    def test_output_contract_has_guided_reading_layers(self):
        """The eight titles are the template's job now; the contract explains them."""
        template = HTML_TEMPLATE.read_text(encoding="utf-8")
        positions = [template.index(f"<h2>{title}</h2>") for title in EXPECTED_SECTION_TITLES]
        self.assertEqual(positions, sorted(positions), "sections are out of order")
        self.assertNotIn("阅读导航", template)
        contract = self.contract()
        for number in range(1, 9):
            self.assertIn(f"**{number} — ", contract, f"section {number} is unexplained")


    def test_output_contract_separates_interpretation_and_critique(self):
        contract = self.contract()
        fragments = FRAGMENTS.read_text(encoding="utf-8")
        validator = VALIDATOR.read_text(encoding="utf-8")

        self.assertIn("Sections 1–6 explain the paper as its authors would", contract)
        self.assertIn("may not appear before Section 7", contract)
        # the wall is not a request: the validator fails a report that leaks a verdict
        self.assertIn("graded judgement belongs in Section 7", validator)

        self.assertIn("any conclusion-changing fact", contract.lower())
        for boundary_type in ("missing material", "external correction", "direct logical fact"):
            self.assertIn(boundary_type, contract)
        for descriptive_step in (
            "本节要理解什么",
            "作者为什么这样设计",
            "必要的技术展开",
            "这一部分在作者论证中的作用",
        ):
            self.assertIn(descriptive_step, contract)
        self.assertNotIn("本节结论", contract)
        self.assertIn("do not add `我们的判断`", contract)

        experiment = re.search(
            r'class="experiment-card">(.*?)</section>', fragments, re.DOTALL
        )
        self.assertIsNotNone(experiment, "fragments.html has no experiment card")
        for field in ("作者要回答什么", "实验怎样设计", "实际观察到什么", "证据边界"):
            self.assertIn(f"<dt>{field}</dt>", experiment.group(1))
        self.assertNotIn("我们的判断", experiment.group(1))

        review = re.search(r'class="review-card">(.*?)</section>', fragments, re.DOTALL)
        self.assertIsNotNone(review, "fragments.html has no review card")
        for field in (
            "作者主张",
            "支持证据",
            "反证或替代解释",
            "对中心结论的影响",
            "最小解决实验",
        ):
            self.assertIn(f"<dt>{field}</dt>", review.group(1))

        template = HTML_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("论文真正贡献了什么", template)
        self.assertIn("最终可以相信到哪里", template)


    def test_skill_enforces_chinese_first_progressive_reading(self):
        text = " ".join(SKILL_MD.read_text(encoding="utf-8").split())
        for phrase in (
            "Chinese-first",
            "question → author rationale → technical detail → role in the argument",
            "3–5 sentences",
        ):
            self.assertIn(phrase, text)
        self.assertRegex(text, r"15–20 minutes?")

    def test_evidence_policy_supports_lightweight_ids(self):
        policy = (SKILL_DIR / "references" / "evidence-policy.md").read_text(encoding="utf-8")
        self.assertIn("Evidence IDs", policy)
        self.assertIn("never hide inference, missing information, or conflict", policy)


    def test_evidence_citation_markup_is_shown_literally(self):
        """The one citation form the reports must emit has to be copyable, not described."""
        canonical = '〔<a class="evidence-link" href="#E01">E01</a>、'
        self.assertIn(canonical, FRAGMENTS.read_text(encoding="utf-8"))
        for name in ("evidence-policy.md", "output-contract.md"):
            text = (SKILL_DIR / "references" / name).read_text(encoding="utf-8")
            self.assertNotIn(
                "E12–E15", text, f"{name} still teaches the unrenderable range form"
            )

    def test_boundary_closure_is_contractual(self):
        """The rule is prose; the markup that obeys it is a fragment; the gate is code."""
        contract = self.contract()
        fragments = FRAGMENTS.read_text(encoding="utf-8")
        skill = SKILL_MD.read_text(encoding="utf-8")
        self.assertIn("处理的证据边界", fragments)
        self.assertIn('class="boundary-link"', fragments)
        self.assertIn("无实质影响的证据边界", HTML_TEMPLATE.read_text(encoding="utf-8"))
        # a card's own 证据边界 field is a boundary, not a pointer to one
        self.assertIn('<dt>证据边界</dt><dd class="evidence-boundary" id="B', fragments)
        self.assertIn("「无」", fragments)
        self.assertIn("discharged in Section 7", contract)
        self.assertIn("a passing mention is not a discharge", contract)
        self.assertIn("boundary", skill)
        self.assertIn("validate_report.py", skill)

    def test_ai_ml_guide_is_sample_and_question_driven(self):
        guide = (SKILL_DIR / "references" / "ai-ml-reading-guide.md").read_text(encoding="utf-8")
        self.assertIn("Start data, training, and model explanations from one concrete sample.", guide)
        self.assertIn("Organize experiments by research question rather than paper table order.", guide)

    def test_task_definition_separates_target_from_sampling_proxy(self):
        guide = (SKILL_DIR / "references" / "ai-ml-reading-guide.md").read_text(encoding="utf-8")
        for concept in (
            "prediction target",
            "sampling or annotation proxy",
            "biological mechanism",
        ):
            self.assertIn(concept, guide)

        data = json.loads(EVALS_JSON.read_text(encoding="utf-8"))
        siamprom = next(case for case in data["cases"] if case["id"] == "siamprom-deep-read")
        self.assertIn(
            "defines the prediction target as promoter/non-promoter sequence classification and separately explains TSS-aligned positive-sample construction",
            siamprom["assertions"],
        )

    def test_report_template_is_self_contained_and_polished(self):
        self.assertTrue(HTML_TEMPLATE.is_file(), "reusable HTML report template is missing")
        text = HTML_TEMPLATE.read_text(encoding="utf-8")
        for required in (
            "<!doctype html>",
            "<header",
            "<nav",
            "<main",
            "<footer",
            "--paper",
            "position: fixed",
            "@media (max-width: 900px)",
            "@media print",
            "prefers-reduced-motion",
            "<details",
            "<summary",
            "evidence-boundary",
            "experiment-card",
            "review-card",
        ):
            self.assertIn(required, text)
        for external_resource in (
            '<link rel="stylesheet"',
            "<script src=",
            "@import",
            '<img src="http',
        ):
            self.assertNotIn(external_resource, text)

    def test_report_template_uses_compact_reading_layout(self):
        self.assertTrue(HTML_TEMPLATE.is_file(), "reusable HTML report template is missing")
        assert_frameflow_inspired_layout(
            self, HTML_TEMPLATE.read_text(encoding="utf-8")
        )

    def test_template_uses_conditional_figure_output(self):
        text = HTML_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("{{FIGURE_OUTPUT}}", text)
        self.assertNotIn("{{FIGURE_BRIEFS}}", text)
        self.assertNotIn("可选科研绘图 Briefs", text)

    def test_siamprom_default_report_omits_figure_output(self):
        text = SIAMPROM_HTML.read_text(encoding="utf-8")
        self.assertNotIn('id="figure-briefs"', text)
        self.assertNotIn("可选科研绘图 Brief", text)
        self.assertNotIn("sci-ai-figure 的交接契约", text)

    def test_siamprom_showcase_has_complete_internal_links(self):
        self.assertTrue(SIAMPROM_HTML.is_file(), "complete SiamProm HTML showcase is missing")
        text = SIAMPROM_HTML.read_text(encoding="utf-8")
        parser = DocumentIndex()
        parser.feed(text)

        self.assertEqual(parser.section_ids, [f"section-{i}" for i in range(1, 9)])
        self.assertEqual(len(parser.ids), len(set(parser.ids)), "HTML IDs must be unique")
        self.assertLessEqual(set(parser.internal_targets), set(parser.ids))
        for required_id in ("evidence-ledger", "E01", "E24"):
            self.assertIn(required_id, parser.ids)
        for title in EXPECTED_SECTION_TITLES:
            self.assertIn(title, text)
        self.assertNotIn("<h2>阅读导航</h2>", text)

    def test_siamprom_main_report_evidence_links_target_each_visible_id(self):
        """Each anchor shows exactly one evidence ID and navigates to its ledger row."""
        parser = DocumentIndex()
        parser.feed(SIAMPROM_HTML.read_text(encoding="utf-8"))

        self.assertTrue(parser.main_report_evidence_links)
        for href, visible_citation in parser.main_report_evidence_links:
            self.assertRegex(
                visible_citation.strip(),
                r"^E\d{2,}$",
                f"{visible_citation!r} must be one bare evidence ID —"
                " keep 〔 、 〕 outside the anchor",
            )
            self.assertEqual(
                visible_citation.strip(),
                href.removeprefix("#"),
                f"{visible_citation!r} points at {href!r}",
            )

    def test_siamprom_showcase_preserves_scientific_depth(self):
        self.assertTrue(SIAMPROM_HTML.is_file(), "complete SiamProm HTML showcase is missing")
        text = SIAMPROM_HTML.read_text(encoding="utf-8")
        parser = DocumentIndex()
        parser.feed(text)

        # Assert the fact, not the phrasing: the readability rule inserts a Chinese
        # gloss at first use, which splits any verbatim phrase it lands inside.
        self.assertRegex(text, r"promoter(（[^）]*）)?\s*或\s*non-promoter")
        self.assertRegex(text, r"TSS\s*只是正样本的采样锚点")
        for fact in ("HIP1", "10-fold", "90/10", "33 条", "AAA", "margin", "E24"):
            self.assertIn(fact, text)
        self.assertGreaterEqual(parser.classes.count("experiment-card"), 5)
        self.assertGreaterEqual(parser.classes.count("review-card"), 6)

    def test_cpromg_showcase_is_complete_traceable_and_scientifically_grounded(self):
        """The CProMG example must remain a navigable expert reading, not a summary."""
        self.assertTrue(CPROMG_HTML.is_file(), "complete CProMG HTML showcase is missing")
        text = CPROMG_HTML.read_text(encoding="utf-8")
        parser = DocumentIndex()
        parser.feed(text)

        self.assertNotRegex(text, r"\{\{[A-Z_]+\}\}", "rendered HTML contains a template token")
        self.assertEqual(parser.section_ids, [f"section-{i}" for i in range(1, 9)])
        self.assertEqual(len(parser.ids), len(set(parser.ids)), "HTML IDs must be unique")
        self.assertLessEqual(set(parser.internal_targets), set(parser.ids))
        self.assertIn("evidence-ledger", parser.ids)
        self.assertNotIn('id="figure-briefs"', text)
        self.assertNotIn("可选科研绘图 Brief", text)
        assert_frameflow_inspired_layout(self, text)
        for title in EXPECTED_SECTION_TITLES:
            self.assertIn(title, text)
        # Identifiers are pinned verbatim: they are how a reader re-finds the source.
        for identifier in (
            "CrossDocked2020",
            "1c9fc00",
            "AutoDock Vina",
            "QED",
            "SA",
            "AddLaplacianEigenvectorPE",
            "50 iterations",
        ):
            self.assertIn(identifier, text)
        # Facts are pinned by content, not by the wording that happens to carry them.
        # Saying `prepared 3D binding pocket` in Chinese is an improvement, and a test
        # that fails on it is testing the phrasing rather than the reading.
        self.assertRegex(text, r"(预先准备好的|预处理过的|已准备好的)三维结合口袋")
        self.assertGreaterEqual(parser.classes.count("experiment-card"), 5)
        self.assertGreaterEqual(parser.classes.count("review-card"), 6)
        self.assertTrue(parser.main_report_evidence_links)
        for href, visible_citation in parser.main_report_evidence_links:
            visible_ids = re.findall(r"E\d{2}", visible_citation)
            self.assertEqual(
                visible_ids,
                [href.removeprefix("#")],
                f"{visible_citation!r} must link one visible Evidence ID to its own row",
            )

    def test_siamprom_showcase_uses_compact_reading_layout(self):
        self.assertTrue(SIAMPROM_HTML.is_file(), "complete SiamProm HTML showcase is missing")
        text = SIAMPROM_HTML.read_text(encoding="utf-8")
        assert_frameflow_inspired_layout(self, text)
        self.assertIn('<h1 class="paper-title">SiamProm 深度精读</h1>', text)
        self.assertIn(
            '<p class="paper-subtitle">Recognition of cyanobacteria promoters', text
        )
        self.assertEqual(
            re.findall(r'<p class="chapter-label">CHAPTER (\d\d)</p>', text),
            [f"{index:02d}" for index in range(1, 9)],
        )

    def test_eval_schema_and_case_coverage(self):
        data = json.loads(EVALS_JSON.read_text(encoding="utf-8"))
        self.assertEqual(data["skill"], "sci-read-paper")
        ids = [case["id"] for case in data["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(
            {case["kind"] for case in data["cases"]},
            {"positive", "partial-source", "trigger", "non-trigger"},
        )
        self.assertEqual(
            {case["id"] for case in data["cases"] if case["kind"] == "positive"},
            {"siamprom-deep-read", "cpromg-deep-read"},
        )
        for case in data["cases"]:
            self.assertTrue(case["prompt"].strip())
            self.assertTrue(case["assertions"])

    def test_eval_nontrigger_coverage(self):
        data = json.loads(EVALS_JSON.read_text(encoding="utf-8"))
        self.assertEqual(
            {case["id"] for case in data["cases"] if case["kind"] == "non-trigger"},
            {
                "nontrigger-quick-summary",
                "nontrigger-translation",
                "nontrigger-literature-review",
                "nontrigger-simple-fact",
            },
        )


class ReportValidatorTests(unittest.TestCase):
    """The validator is the only gate that runs against generated reports.

    These tests check that it exists, that it passes the shipped showcases, and
    that it actually fails on a broken report — a validator nobody tests is the
    same blind spot as no validator.
    """

    def run_validator(self, path: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), str(path)],
            capture_output=True,
            text=True,
        )

    def write_temp(self, text: str) -> Path:
        handle = tempfile.NamedTemporaryFile(
            "w", suffix=".html", delete=False, encoding="utf-8"
        )
        handle.write(text)
        handle.close()  # validate() reopens the path; an unflushed handle reads empty
        self.addCleanup(Path(handle.name).unlink, missing_ok=True)
        return Path(handle.name)

    def corrupt(self, source: Path, *replacements: tuple[str, str]) -> Path:
        text = source.read_text(encoding="utf-8")
        for old, new in replacements:
            self.assertIn(old, text, f"fixture no longer contains {old!r}")
            text = text.replace(old, new, 1)
        return self.write_temp(text)

    def test_scaffolder_resolves_every_flag_determined_placeholder(self):
        """Deciding these by hand shipped a broken build procedure once already."""
        for mode in ("standard", "audit"):
            for figure in ("off", "brief", "generate"):
                with self.subTest(mode=mode, figure=figure):
                    outdir = tempfile.mkdtemp()
                    result = subprocess.run(
                        [
                            sys.executable, str(SCAFFOLD), "--slug", "probe",
                            "--outdir", outdir, "--mode", mode, "--figure", figure,
                        ],
                        capture_output=True, text=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    suffix = "-audit" if mode == "audit" else ""
                    written = Path(outdir) / f"probe{suffix}.html"
                    self.assertTrue(written.is_file(), result.stdout)
                    text = written.read_text(encoding="utf-8")
                    self.addCleanup(written.unlink, missing_ok=True)

                    for resolved in ("{{MODE}}", "{{FIGURE}}"):
                        self.assertNotIn(resolved, text, "the flags must be baked in")
                    self.assertIn(f"mode={mode}; figure={figure}", text)
                    self.assertEqual(
                        "{{FIGURE_OUTPUT}}" in text, figure != "off",
                        "the figure line must be present exactly when it applies",
                    )
                    self.assertEqual("{{AUDIT_PANELS}}" in text, mode == "audit")

    def test_scaffolded_skeleton_has_no_placeholder_the_validator_cannot_see(self):
        """An unfilled slot must fail as an unreplaced token, never pass unnoticed."""
        template = HTML_TEMPLATE.read_text(encoding="utf-8")
        source = VALIDATOR.read_text(encoding="utf-8")
        pattern = re.search(r're\.findall\(r"(\\\{\\\{\[[^"]+)"', source)
        self.assertIsNotNone(pattern, "the unreplaced-token regex is gone")
        seen = set(re.findall(pattern.group(1).replace("\\\\", "\\"), template))
        self.assertEqual(
            seen,
            set(re.findall(r"\{\{[^}]+\}\}", template)),
            "the template holds a placeholder shape the validator does not match",
        )

    def test_validator_field_lists_match_the_fragments(self):
        """The gate and the thing the writer copies must not drift apart."""
        fragments = FRAGMENTS.read_text(encoding="utf-8")
        source = VALIDATOR.read_text(encoding="utf-8")
        for constant in ("REVIEW_CARD_FIELDS", "EXPERIMENT_CARD_FIELDS"):
            block = re.search(rf"{constant} = \[(.*?)\]", source, re.DOTALL)
            self.assertIsNotNone(block, f"{constant} not found in the validator")
            fields = re.findall(r'"([^"]+)"', block.group(1))
            self.assertGreaterEqual(len(fields), 7)
            for field in fields:
                self.assertIn(
                    f"<dt>{field}</dt>",
                    fragments,
                    f"{constant} field {field!r} has no slot in fragments.html",
                )

    def test_closed_vocabularies_are_published_where_the_writer_looks(self):
        """A term only the validator knows is a rule discovered by failing the build."""
        fragments = FRAGMENTS.read_text(encoding="utf-8")
        source = VALIDATOR.read_text(encoding="utf-8")
        for constant in ("EXPERIMENT_TYPES", "IMPACT_CALIBRATIONS", "LEDGER_LABELS"):
            # the labels themselves contain brackets, so stop at the line that closes
            # the literal rather than at the first bracket character
            block = re.search(rf"{constant} = .*?\n(?=[A-Z_]+ =|\n)", source, re.DOTALL)
            self.assertIsNotNone(block, f"{constant} not found in the validator")
            terms = re.findall(r'"([^"]+)"', block.group(0))
            self.assertGreaterEqual(len(terms), 5)
            for term in terms:
                self.assertIn(
                    term, fragments, f"{constant} term {term!r} is not in fragments.html"
                )
        verdicts = re.search(r"VERDICTS = \{(.*?)\n\}", source, re.DOTALL)
        self.assertIsNotNone(verdicts)
        for term, css in re.findall(r'"([^"]+)": "([^"]+)"', verdicts.group(1)):
            self.assertIn(term, fragments, f"verdict {term!r} is not in fragments.html")
            self.assertIn(css, fragments, f"verdict class {css!r} is not in fragments.html")

    def test_no_dead_css_in_the_template_stylesheet(self):
        """A rule nothing uses is where the markup silently drifts away from the design.

        This has already happened three times: cards were styled as dl/dt/dd and every
        report wrote <p><strong>; verdict cards were styled .takeaway-card h3 and every
        report wrote <p><strong>, which left a validator check that could never fire.
        """
        style = re.search(
            r"<style>(.*?)</style>", HTML_TEMPLATE.read_text(encoding="utf-8"), re.DOTALL
        ).group(1)
        defined = set(re.findall(r"\.([A-Za-z][\w-]*)", style))
        used: set[str] = set()
        sources = [HTML_TEMPLATE, FRAGMENTS]
        sources += sorted((ROOT / "tests" / "sci-read-paper" / "outputs").rglob("*.html"))
        for source in sources:
            text = source.read_text(encoding="utf-8")
            body = text.split("</style>", 1)[-1]
            for attribute in re.findall(r'class="([^"]+)"', body):
                used.update(attribute.split())
        self.assertEqual(
            sorted(defined - used),
            [],
            "the stylesheet defines classes nothing uses — delete them or use them",
        )

    def test_validator_is_shipped_with_the_skill(self):
        self.assertTrue(VALIDATOR.is_file(), "scripts/validate_report.py is missing")
        skill = SKILL_MD.read_text(encoding="utf-8")
        contract = (SKILL_DIR / "references" / "output-contract.md").read_text(encoding="utf-8")
        self.assertIn("validate_report.py", skill)
        self.assertIn("validate_report.py", contract)

    def test_validator_accepts_every_shipped_report(self):
        """Globbed, not enumerated: a new report must be gated the day it lands."""
        reports = sorted((ROOT / "tests" / "sci-read-paper" / "outputs").rglob("*.html"))
        self.assertGreaterEqual(len(reports), 2, "no showcase reports found")
        for showcase in reports:
            with self.subTest(showcase=showcase.name):
                result = self.run_validator(showcase)
                self.assertEqual(
                    result.returncode,
                    0,
                    f"{showcase.name} violates the output contract:\n{result.stderr}",
                )

    def test_validator_enforces_experiment_card_fields(self):
        """Whatever the validator does not check drifts — experiment cards proved it."""
        broken = self.corrupt(
            CPROMG_HTML, ("<dt>数据与指标</dt>", "<dt>指标</dt>")
        )
        result = self.run_validator(broken)
        self.assertEqual(result.returncode, 1)
        self.assertIn("experiment card", result.stderr)
        self.assertIn("数据与指标", result.stderr)

    def test_validator_rejects_a_duplicated_card_field(self):
        source = CPROMG_HTML.read_text(encoding="utf-8")
        label = "<dt>实验类型</dt>"
        self.assertIn(label, source)
        broken = self.corrupt(CPROMG_HTML, (label, label + "<dd>占位</dd>" + label))
        result = self.run_validator(broken)
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicated", result.stderr)

    def test_validator_allows_a_boundary_field_that_raises_nothing(self):
        """证据边界：无 is a valid statement and needs no B-id."""
        pattern = re.compile(
            r'<dt>证据边界</dt><dd class="evidence-boundary" id="(B\d{2})">.*?</dd>',
            re.DOTALL,
        )
        for report in sorted((ROOT / "tests" / "sci-read-paper" / "outputs").rglob("*.html")):
            source = report.read_text(encoding="utf-8")
            field = pattern.search(source)
            if not field:
                continue
            target = field.group(1)
            link = re.search(
                rf'<a class="boundary-link" href="#{target}">{target}</a>[、]?', source
            )
            self.assertIsNotNone(link, f"{target} is defined but never discharged")
            clean = self.corrupt(
                report,
                (field.group(0), "<dt>证据边界</dt><dd>无</dd>"),
                (link.group(0), ""),
            )
            result = self.run_validator(clean)
            self.assertEqual(result.returncode, 0, result.stderr)
            return
        self.skipTest("no experiment-card boundary field in any shipped report")

    def test_a_boundary_that_raises_nothing_may_be_quoted_or_punctuated(self):
        """The gate must not reject what the fragment library tells the writer to do.

        fragments.html says to write 无 in the field; a writer copying that prose kept
        the quotation marks and the validator failed the report. The instruction and
        the gate disagreeing is the exact bug class this contract exists to remove.
        """
        plain = "<dt>证据边界</dt><dd>无</dd>"
        reports = sorted((ROOT / "tests" / "sci-read-paper" / "outputs").rglob("*.html"))
        showcase = next(
            (r for r in reports if plain in r.read_text(encoding="utf-8")), None
        )
        self.assertIsNotNone(showcase, "no shipped report has an empty boundary field")
        for form in ("无", "「无」", "无。", "“无”"):
            with self.subTest(form=form):
                variant = self.corrupt(
                    showcase, (plain, f"<dt>证据边界</dt><dd>{form}</dd>")
                )
                result = self.run_validator(variant)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_validator_rejects_a_run_on_sentence(self):
        run_on = "这是一个被故意写得非常冗长的句子" * 9  # 135 CJK characters
        broken = self.corrupt(
            CPROMG_HTML,
            ('<main id="main-content">', f'<main id="main-content"><p>{run_on}。</p>'),
        )
        result = self.run_validator(broken)
        self.assertEqual(result.returncode, 1)
        self.assertIn("run-on sentence", result.stderr)

    def test_audit_mode_is_gated_at_all(self):
        """Until the first audit run, this mode had no contract: a report declaring
        mode=audit with zero panels passed."""
        audit = next(
            (
                r
                for r in sorted((ROOT / "tests" / "sci-read-paper" / "outputs").rglob("*.html"))
                if "mode=audit" in r.read_text(encoding="utf-8")
            ),
            None,
        )
        self.assertIsNotNone(audit, "no audit-mode showcase to gate against")
        source = audit.read_text(encoding="utf-8")
        self.assertEqual(self.run_validator(audit).returncode, 0)

        stripped = re.sub(
            r'      <details class="provenance" id="(?:data-training|model-dataflow'
            r'|experiment-matrix|critical-review)">.*?</details>\n',
            "",
            source,
            flags=re.DOTALL,
        )
        self.assertNotEqual(stripped, source, "the panels are no longer where we look")
        result = self.run_validator(self.write_temp(stripped))
        self.assertEqual(result.returncode, 1, "audit with no panels must fail")
        self.assertIn("panel is missing", result.stderr)

        loosened = source.replace(
            '<details class="provenance" id="data-training">',
            '<details class="provenance" id="data-training" open>',
            1,
        )
        result = self.run_validator(self.write_temp(loosened))
        self.assertEqual(result.returncode, 1)
        self.assertIn("must ship collapsed", result.stderr)

    def test_standard_mode_rejects_audit_panels(self):
        panel = (
            '      <details class="provenance" id="data-training"><summary>x</summary>'
            '<div class="details-body">占位内容占位内容</div></details>\n'
        )
        broken = self.corrupt(CPROMG_HTML, ("    </main>", panel + "    </main>"))
        result = self.run_validator(broken)
        self.assertEqual(result.returncode, 1)
        self.assertIn("audit panels belong in the audit deliverable", result.stderr)

    def test_the_wall_covers_audit_panels_too(self):
        """A verdict in an appendix is a verdict nothing can check against a boundary."""
        audit = next(
            r
            for r in sorted((ROOT / "tests" / "sci-read-paper" / "outputs").rglob("*.html"))
            if "mode=audit" in r.read_text(encoding="utf-8")
        )
        source = audit.read_text(encoding="utf-8")
        leaked = source.replace(
            '<summary>可复现性清单</summary>',
            '<summary>可复现性清单</summary><p>这一条可以相信。</p>',
            1,
        )
        self.assertNotEqual(leaked, source)
        result = self.run_validator(self.write_temp(leaked))
        self.assertEqual(result.returncode, 1)
        self.assertIn("graded judgement belongs in Section 7", result.stderr)

    def test_audit_sidebar_group_exists_only_in_audit_mode(self):
        """Those nav links would be dead — and fail validation — in a standard report."""
        for mode, expected in (("standard", False), ("audit", True)):
            with self.subTest(mode=mode):
                outdir = tempfile.mkdtemp()
                subprocess.run(
                    [sys.executable, str(SCAFFOLD), "--slug", "nav",
                     "--outdir", outdir, "--mode", mode],
                    capture_output=True, text=True, check=True,
                )
                suffix = "-audit" if mode == "audit" else ""
                text = (Path(outdir) / f"nav{suffix}.html").read_text(encoding="utf-8")
                self.assertEqual('href="#data-training"' in text, expected)
                self.assertNotIn("{{AUDIT_NAV}}", text, "the marker must never ship")

    def test_reading_band_measures_the_reading_not_the_appendices(self):
        """Audit panels are lookup material; counting them trips a band calibrated
        on the eight-section path."""
        source = VALIDATOR.read_text(encoding="utf-8")
        self.assertIn("index.section_text.get(n, [])", source)
        self.assertNotIn('CJK.findall("".join(index.main_text))', source)

    def test_term_dumping_fails_the_build_rather_than_only_warning(self):
        """The old Latin-share warning fired for two rounds and the report shipped."""
        sys.path.insert(0, str(VALIDATOR.parent))
        import validate_report

        flood = " ".join(f"term{n}" for n in range(400))
        broken = self.corrupt(
            CPROMG_HTML, ("</main>", f"<p>下面是一段说明。{flood}。</p></main>")
        )
        result = self.run_validator(broken)
        self.assertEqual(result.returncode, 1, "term dumping must fail, not warn")
        self.assertIn("distinct English terms", result.stderr)
        self.assertGreater(
            validate_report.TERM_DENSITY_FAIL, validate_report.TERM_DENSITY_WARN
        )

    def test_term_density_counts_variety_not_repetition(self):
        """Repeating one glossed term is healthy; the metric must not punish it."""
        sys.path.insert(0, str(VALIDATOR.parent))
        from validate_report import prose_terms

        repeated = ["模型把 motif 交给 scaffold。" * 30]
        varied = [
            "模型 " + " ".join(f"term{n}" for n in range(30)) + " 交给下一层。" * 8
        ]
        few, _ = prose_terms(repeated)
        many, _ = prose_terms(varied)
        self.assertLess(len(few), len(many))
        self.assertEqual(sorted(few), ["motif", "scaffold"])

    def test_term_density_survives_the_whitespace_that_sentence_length_removes(self):
        """Stripping spaces welds `ablation study` into one token and hides a term."""
        sys.path.insert(0, str(VALIDATOR.parent))
        from validate_report import prose_terms

        terms, _ = prose_terms(["这是一次 ablation study 的说明。"])
        self.assertIn("ablation", terms)
        self.assertIn("study", terms)
        self.assertNotIn("ablationstudy", terms)

    def test_term_density_ignores_evidence_and_boundary_ids(self):
        """E01 and B07 are references, not vocabulary the reader has to learn."""
        sys.path.insert(0, str(VALIDATOR.parent))
        from validate_report import prose_terms

        terms, _ = prose_terms(["见边界 B07 与证据〔E01、E02〕的说明。"])
        self.assertEqual(sorted(terms), [])

    def test_readability_measures_prose_not_tables(self):
        """A long table cell is data, not a sentence — measuring it flagged clean reports."""
        cell = "阶段形状操作说明" * 40  # 320 characters, far past the sentence cap
        clean = self.corrupt(
            CPROMG_HTML,
            (
                '<main id="main-content">',
                f'<main id="main-content"><table><tr><td>{cell}</td></tr></table>',
            ),
        )
        result = self.run_validator(clean)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_contract_states_the_readability_limits(self):
        """One number, in one place, next to the gate that enforces it."""
        contract = (SKILL_DIR / "references" / "output-contract.md").read_text(encoding="utf-8")
        source = VALIDATOR.read_text(encoding="utf-8")
        for limit in ("SENTENCE_HARD_CAP", "SENTENCE_P90_CAP", "TERM_DENSITY_FAIL"):
            self.assertIn(limit, source)
        for constant in (
            "SENTENCE_HARD_CAP",
            "SENTENCE_P90_CAP",
            "SENTENCE_MEDIAN_TARGET",
            "TERM_DENSITY_WARN",
            "TERM_DENSITY_FAIL",
        ):
            value = re.search(rf"{constant} = (\d+)", source).group(1)
            self.assertIn(value, contract, f"{constant} is enforced but never stated")
        self.assertIn("Readability", contract)

    def test_reading_length_ceiling_scales_with_boundary_count(self):
        """A boundary-dense paper is legitimately longer; the band must say so."""
        result = self.run_validator(CPROMG_HTML)
        self.assertEqual(result.returncode, 0, result.stderr)
        source = VALIDATOR.read_text(encoding="utf-8")
        self.assertIn("READING_LENGTH_PER_BOUNDARY", source)
        ceiling = re.search(r"READING_LENGTH_PER_BOUNDARY = (\d+)", source)
        self.assertIsNotNone(ceiling)
        self.assertGreater(int(ceiling.group(1)), 0)

    def test_validator_rejects_a_broken_evidence_citation(self):
        broken = self.corrupt(
            CPROMG_HTML,
            (
                '<a class="evidence-link" href="#E08">E08</a>',
                '<a class="evidence-link" href="#E08">〔E08、</a>',
            ),
        )
        result = self.run_validator(broken)
        self.assertEqual(result.returncode, 1)
        self.assertIn("must be exactly one evidence ID", result.stderr)

    def test_validator_rejects_a_dropped_evidence_boundary(self):
        """The defect that shipped in a showcase must now fail the build."""
        source = CPROMG_HTML.read_text(encoding="utf-8")
        link = re.search(r'<a class="boundary-link" href="#(B\d{2})">\1</a>', source)
        self.assertIsNotNone(link, "no boundary links found in the showcase")
        broken = self.corrupt(CPROMG_HTML, (link.group(0), "无"))
        result = self.run_validator(broken)
        self.assertEqual(result.returncode, 1)
        self.assertIn("never discharged in Section 7", result.stderr)

    def test_validator_rejects_a_mention_that_is_not_a_discharge(self):
        """A boundary link outside a review card must not count as handling it."""
        source = CPROMG_HTML.read_text(encoding="utf-8")
        link = re.search(r'<a class="boundary-link" href="#(B\d{2})">\1</a>', source)
        self.assertIsNotNone(link)
        intro = re.search(r'<section id="section-7"[^>]*>', source)
        self.assertIsNotNone(intro)
        broken = self.corrupt(
            CPROMG_HTML,
            (link.group(0), "无"),
            (intro.group(0), intro.group(0) + f"<p>{link.group(0)}</p>"),
        )
        result = self.run_validator(broken)
        self.assertEqual(result.returncode, 1)
        self.assertIn("not from a review card", result.stderr)

    def test_validator_rejects_an_unlabelled_boundary(self):
        """Dropping the B-id must not make a boundary invisible to the gate."""
        source = CPROMG_HTML.read_text(encoding="utf-8")
        first = re.search(r'\s?id="B\d{2}"', source)
        self.assertIsNotNone(first)
        broken = self.corrupt(CPROMG_HTML, (first.group(0), ""))
        result = self.run_validator(broken)
        self.assertEqual(result.returncode, 1)
        self.assertIn("with no B-id", result.stderr)

    def test_validator_rejects_a_review_card_missing_a_field(self):
        broken = self.corrupt(
            CPROMG_HTML,
            ("<dt>证据缺少什么</dt>", "<dt>补充</dt>"),
        )
        result = self.run_validator(broken)
        self.assertEqual(result.returncode, 1)
        self.assertIn("证据缺少什么", result.stderr)

    def test_validator_rejects_a_foreign_stylesheet(self):
        broken = self.corrupt(
            CPROMG_HTML,
            ("<body>", "<style>body { max-width: 36em; }</style>\n<body>"),
        )
        result = self.run_validator(broken)
        self.assertEqual(result.returncode, 1)
        self.assertIn("expected exactly 1 <style> element", result.stderr)

    def test_validator_rejects_a_truncated_report(self):
        broken = self.corrupt(CPROMG_HTML, ("<footer>", "{{REPORT_BODY}}<footer>"))
        result = self.run_validator(broken)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unreplaced template token", result.stderr)

    def test_validator_rejects_a_collapsed_ledger(self):
        broken = self.corrupt(
            CPROMG_HTML, ('id="evidence-ledger" open>', 'id="evidence-ledger">')
        )
        result = self.run_validator(broken)
        self.assertEqual(result.returncode, 1)
        self.assertIn("must carry the open attribute", result.stderr)

    def test_validator_reports_a_stray_close_tag_as_a_structural_error(self):
        """A stray tag must not masquerade as ten dropped boundaries."""
        broken = self.corrupt(
            CPROMG_HTML,
            ('<section id="section-7"', '</div><section id="section-7"'),
        )
        result = self.run_validator(broken)
        self.assertEqual(result.returncode, 1)
        self.assertIn("stray </div>", result.stderr)
        self.assertNotIn("never discharged", result.stderr)

    def test_validator_tolerates_a_section_title_quoted_in_prose(self):
        """Section 2's contract requires a forward reference to Section 7."""
        clean = self.corrupt(
            CPROMG_HTML,
            (
                '<section id="section-3"',
                "<p>第 7 章「批判性审查：证据究竟支持到哪里」会集中判断。</p>"
                '<section id="section-3"',
            ),
        )
        result = self.run_validator(clean)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_validator_checks_figure_mode_in_both_directions(self):
        for mode in ("brief", "generate"):
            with self.subTest(mode=mode):
                declared = self.corrupt(
                    CPROMG_HTML, ("mode=standard; figure=off", f"mode=standard; figure={mode}")
                )
                result = self.run_validator(declared)
                self.assertEqual(
                    result.returncode, 1, "missing figure UI must fail brief/generate"
                )
                self.assertIn("figure-output", result.stderr)
        broken = self.corrupt(
            CPROMG_HTML, ("</main>", '<section id="figure-output"></section></main>')
        )
        result = self.run_validator(broken)
        self.assertEqual(result.returncode, 1, "figure=off must reject figure UI")
        self.assertIn("figure=off but #figure-output is present", result.stderr)

    def test_figure_flag_cannot_contradict_the_report(self):
        """A mode the caller supplies is a mode the caller can get wrong."""
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "--figure", "brief", str(CPROMG_HTML)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("contradicts the report's own figure=off", result.stderr)


class ClosedVocabularyTests(unittest.TestCase):
    """Every closed set the validator did not police had already drifted.

    Across three shipped reports the experiment-type field appeared as 控制实验,
    control and 对照; the graded verdicts as 被论文表格自身否定 and 不能由本文推出;
    and pandoc's level1–level4 classes survived in all three. Each test below
    corrupts a passing report in one of those directions, so a check that stops
    firing shows up as a green test that should have been red.
    """

    def run_validator(self, path: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), str(path)], capture_output=True, text=True
        )

    def corrupt(self, *replacements: tuple[str, str]) -> Path:
        text = CPROMG_HTML.read_text(encoding="utf-8")
        for old, new in replacements:
            self.assertIn(old, text, f"fixture no longer contains {old!r}")
            text = text.replace(old, new, 1)
        handle = tempfile.NamedTemporaryFile(
            "w", suffix=".html", delete=False, encoding="utf-8"
        )
        handle.write(text)
        handle.close()
        self.addCleanup(Path(handle.name).unlink, missing_ok=True)
        return Path(handle.name)

    def assert_rejected(self, needle: str, *replacements: tuple[str, str]) -> None:
        result = self.run_validator(self.corrupt(*replacements))
        self.assertEqual(result.returncode, 1, f"expected a failure mentioning {needle!r}")
        self.assertIn(needle, result.stderr)

    def test_experiment_type_must_come_from_the_vocabulary(self):
        self.assert_rejected(
            "实验类型",
            ("<dt>实验类型</dt><dd>消融", "<dt>实验类型</dt><dd>ablation study"),
        )

    def test_impact_must_open_with_one_of_the_five_calibrations(self):
        self.assert_rejected(
            "对中心结论的影响",
            ("<dt>对中心结论的影响</dt><dd>收窄范围——", "<dt>对中心结论的影响</dt><dd>大概还行，"),
        )

    def test_verdict_heading_must_come_from_the_vocabulary(self):
        self.assert_rejected("must start with one of", ("<h3>可以相信</h3>", "<h3>基本靠谱</h3>"))

    def test_verdict_colour_must_match_the_verdict(self):
        self.assert_rejected(
            "must carry verdict-supported",
            ("takeaway-card verdict-supported", "takeaway-card verdict-rejected"),
        )

    def test_a_graded_verdict_may_not_leak_into_the_explaining_sections(self):
        self.assert_rejected(
            "graded judgement belongs in Section 7",
            (
                "<h2>从问题到方法：作者为什么这样设计</h2>",
                "<h2>从问题到方法：作者为什么这样设计</h2><p>这一点可以相信。</p>",
            ),
        )

    def test_ledger_rows_keep_all_seven_columns(self):
        self.assert_rejected(
            "cells, expected 7",
            ("<td>[论文]</td>", ""),
        )

    def test_ledger_labels_come_from_the_closed_set(self):
        self.assert_rejected(
            "evidence label must be one of",
            ("<td>[论文]</td>", "<td>[文献]</td>"),
        )

    def test_classes_outside_the_template_stylesheet_are_rejected(self):
        """pandoc's level1–level4 survived in every shipped report until now."""
        self.assert_rejected(
            "no rule in the template stylesheet",
            ('id="section-4" class="report-section"', 'id="section-4" class="report-section level2"'),
        )

    def test_the_no_material_effect_block_is_never_optional(self):
        self.assert_rejected(
            "missing #no-effect-boundaries",
            ('id="no-effect-boundaries"', 'id="other-boundaries"'),
        )

    def test_a_boundary_must_carry_the_class_that_makes_it_visible(self):
        self.assert_rejected(
            'does not carry class="evidence-boundary"',
            ('<aside class="evidence-boundary" id="B01">', '<aside id="B01">'),
        )

    def test_a_card_boundary_needs_its_own_id(self):
        self.assert_rejected(
            "needs its own Bnn id",
            ('<dd class="evidence-boundary" id="B06">', '<dd class="evidence-boundary">'),
        )

    def test_the_status_badges_are_never_restated(self):
        """One report carried a duplicate pair plus a figure badge the contract forbids."""
        self.assert_rejected(
            "exactly two status badges",
            (
                '<span class="status-badge">complete</span>',
                '<span class="status-badge">complete</span>'
                '<span class="status-badge">figure: off</span>',
            ),
        )

    def test_the_report_declares_the_mode_it_was_built_in(self):
        self.assert_rejected(
            "must declare mode",
            ('<meta name="sci-read-paper" content="mode=standard; figure=off">', ""),
        )

    def test_a_truncated_section_is_not_mistaken_for_a_concise_one(self):
        source = CPROMG_HTML.read_text(encoding="utf-8")
        body = re.search(
            r'<section id="section-3"[^>]*>(.*?)</section>\s*<section id="section-4"',
            source,
            re.DOTALL,
        )
        self.assertIsNotNone(body, "section 3 is no longer where the fixture puts it")
        kept = body.group(1)[: body.group(1).index("</p>") + 4]
        self.assert_rejected("below the", (body.group(1), kept))


if __name__ == "__main__":
    unittest.main()
