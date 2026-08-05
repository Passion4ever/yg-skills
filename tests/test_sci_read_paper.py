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
        contract = (SKILL_DIR / "references" / "output-contract.md").read_text(encoding="utf-8")
        self.assertIn("<paper-slug>.html", contract)
        self.assertIn("<paper-slug>-audit.html", contract)
        self.assertIn("embedded evidence ledger", contract)
        self.assertIn("audit panels", contract)
        self.assertIn("sci-diagram", contract)
        self.assertNotIn("sci-ai-figure", contract, "handoff names a skill that does not exist")

    def test_figure_mode_is_explicit_and_defaults_off(self):
        skill = SKILL_MD.read_text(encoding="utf-8")
        contract = (SKILL_DIR / "references" / "output-contract.md").read_text(
            encoding="utf-8"
        )
        for state in ("figure=off", "figure=brief", "figure=generate"):
            self.assertIn(state, skill)
            self.assertIn(state, contract)
        self.assertIn("default", skill)
        self.assertIn("fall back to `figure=brief`", contract)
        self.assertIn("does not change the paper-reading completion status", contract)

    def test_standard_mode_has_one_html_output(self):
        contract = (SKILL_DIR / "references" / "output-contract.md").read_text(encoding="utf-8")
        standard = contract.split("## Standard Mode — Default", 1)[1].split(
            "## Audit Mode — Explicit", 1
        )[0]
        tree = re.search(r"```text\n(.*?)\n```", standard, re.DOTALL)
        self.assertIsNotNone(tree)
        output_paths = [line.strip() for line in tree.group(1).splitlines() if line.strip()]
        self.assertEqual(output_paths, ["<paper-slug>.html"])
        self.assertNotIn("deep-reading.md", standard)
        self.assertNotIn("evidence-ledger.md", standard)

    def test_audit_mode_has_one_html_output(self):
        contract = (SKILL_DIR / "references" / "output-contract.md").read_text(encoding="utf-8")
        audit = contract.split("## Audit Mode — Explicit", 1)[1].split("## Primary Report", 1)[0]
        tree = re.search(r"```text\n(.*?)\n```", audit, re.DOTALL)
        self.assertIsNotNone(tree)
        output_paths = [line.strip() for line in tree.group(1).splitlines() if line.strip()]
        self.assertEqual(output_paths, ["<paper-slug>-audit.html"])
        for panel in ("data-training", "model-dataflow", "experiment-matrix", "critical-review"):
            self.assertIn(panel, audit)

    def test_standard_mode_bounds_research_scope(self):
        skill = SKILL_MD.read_text(encoding="utf-8")
        policy = (SKILL_DIR / "references" / "evidence-policy.md").read_text(encoding="utf-8")
        guide = (SKILL_DIR / "references" / "ai-ml-reading-guide.md").read_text(encoding="utf-8")
        self.assertIn("standard", skill)
        self.assertIn("audit", skill)
        self.assertIn("at most three conclusion-critical claim families", policy)
        self.assertIn("shortest conclusion-relevant path", guide)
        self.assertIn("Do not download weights", guide)
        # The workflow acquires the repository at step 2, which loads evidence-policy.
        # A guardrail that only lives in the step-4 guide fires after the clone.
        for text in (policy, guide):
            self.assertIn("sparse or blob-filtered repository retrieval", text)
        self.assertIn("never download weights", policy)

    def test_report_records_selected_mode(self):
        contract = (SKILL_DIR / "references" / "output-contract.md").read_text(encoding="utf-8")
        self.assertIn("mode: standard|audit", contract)
        self.assertIn("complete|partial", contract)

    def test_readability_rubric_contract(self):
        text = READABILITY_RUBRIC.read_text(encoding="utf-8")
        for criterion in (
            "Background orientation",
            "Three-minute map",
            "Causal narrative",
            "Concrete sample",
            "Progressive technical depth",
            "Chinese-first prose",
            "Readable evidence",
            "Main/audit separation",
            "HTML reading experience",
        ):
            self.assertIn(f"| {criterion} |", text)
        self.assertIn("at least 16/18", text)
        self.assertIn("scientific-depth score", text)

    def test_output_contract_has_guided_reading_layers(self):
        contract = (SKILL_DIR / "references" / "output-contract.md").read_text(encoding="utf-8")
        positions = [contract.index(title) for title in EXPECTED_SECTION_TITLES]
        self.assertEqual(positions, sorted(positions))
        primary_structure = re.search(
            r"## Primary Report.*?```html\n(.*?)\n```", contract, re.DOTALL
        )
        self.assertIsNotNone(primary_structure)
        self.assertNotIn("阅读导航", primary_structure.group(1))

    def test_output_contract_separates_interpretation_and_critique(self):
        contract = (SKILL_DIR / "references" / "output-contract.md").read_text(encoding="utf-8")
        self.assertIn(
            "理解作者（Sections 1–6） → 集中审查作者（Section 7） → 形成自己的结论（Section 8）",
            contract,
        )
        self.assertIn("any conclusion-changing fact", contract)
        for boundary_type in ("missing material", "external correction", "direct logical fact"):
            self.assertIn(boundary_type, contract)
        self.assertIn("其对结论的影响在第 7 节集中评估", contract)
        for descriptive_step in (
            "本节要理解什么",
            "作者为什么这样设计",
            "必要的技术展开",
            "这一部分在作者论证中的作用",
        ):
            self.assertIn(descriptive_step, contract)
        self.assertNotIn("本节结论", contract)
        self.assertNotIn("one main judgment", contract)

        experiment = re.search(
            r"Organize experiments by question.*?```text\n(.*?)\n```",
            contract,
            re.DOTALL,
        )
        self.assertIsNotNone(experiment)
        for field in ("作者要回答什么", "实验怎样设计", "实际观察到什么", "证据边界"):
            self.assertIn(field, experiment.group(1))
        self.assertNotIn("我们的判断", experiment.group(1))

        for field in (
            "审查议题",
            "作者主张",
            "支持证据",
            "反证或替代解释",
            "对中心结论的影响",
            "最小解决实验",
        ):
            self.assertIn(field, contract)
        self.assertIn("论文真正贡献了什么", contract)
        self.assertIn("最终可以相信到哪里", contract)

    def test_skill_enforces_chinese_first_progressive_reading(self):
        text = SKILL_MD.read_text(encoding="utf-8")
        for phrase in (
            "Chinese-first",
            "question → author rationale → technical detail → role in the argument",
            "3–5 sentences",
            "15–20 minutes",
        ):
            self.assertIn(phrase, text)

    def test_evidence_policy_supports_lightweight_ids(self):
        policy = (SKILL_DIR / "references" / "evidence-policy.md").read_text(encoding="utf-8")
        self.assertIn("Evidence IDs", policy)
        self.assertIn("never hide inference, missing information, or conflict", policy)

    def test_evidence_citation_markup_is_shown_literally(self):
        """The one citation form the reports must emit has to be copyable, not described."""
        canonical = '〔<a class="evidence-link" href="#E01">E01</a>、'
        for name in ("evidence-policy.md", "output-contract.md"):
            text = (SKILL_DIR / "references" / name).read_text(encoding="utf-8")
            self.assertIn(canonical, text, f"{name} must show the literal citation markup")
            self.assertNotIn(
                "E12–E15", text, f"{name} still teaches the unrenderable range form"
            )

    def test_boundary_closure_is_contractual(self):
        contract = (SKILL_DIR / "references" / "output-contract.md").read_text(encoding="utf-8")
        policy = (SKILL_DIR / "references" / "evidence-policy.md").read_text(encoding="utf-8")
        skill = SKILL_MD.read_text(encoding="utf-8")
        self.assertIn("处理的证据边界", contract)
        self.assertIn('class="boundary-link"', contract)
        self.assertIn("无实质影响的证据边界", contract)
        self.assertIn('id="B02"', contract)
        # the experiment card's own 证据边界 field is a boundary, not a pointer to one
        self.assertIn('<li id="B06"><strong>证据边界：</strong>', contract)
        self.assertIn("证据边界：无", contract)
        for text in (policy, skill):
            self.assertIn("B01", text)
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

        self.assertIn("promoter 或 non-promoter", text)
        self.assertIn("TSS 只是正样本的采样锚点", text)
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
        for fact in (
            "CrossDocked2020",
            "prepared 3D binding pocket",
            "1c9fc00",
            "AutoDock Vina",
            "QED",
            "SA score",
            "AddLaplacianEigenvectorPE",
            "50 iterations",
        ):
            self.assertIn(fact, text)
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

    def corrupt(self, source: Path, *replacements: tuple[str, str]) -> Path:
        text = source.read_text(encoding="utf-8")
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

    def test_build_procedure_resolves_every_template_placeholder(self):
        """Any placeholder the procedure forgets becomes an unreplaced-token failure."""
        template = HTML_TEMPLATE.read_text(encoding="utf-8")
        contract = (SKILL_DIR / "references" / "output-contract.md").read_text(encoding="utf-8")
        procedure = contract.split("## Build Procedure", 1)[1].split("\n## ", 1)[0]
        for token in sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", template))):
            self.assertIn(
                token,
                procedure,
                f"Build Procedure never tells the model what to do with {token}",
            )
        # the two that must be deleted rather than filled
        for token in ("{{FIGURE_OUTPUT}}", "{{AUDIT_PANELS}}"):
            row = next(line for line in procedure.splitlines() if token in line)
            self.assertIn("delete", row.lower(), f"{token} row must say to delete the line")

    def test_validator_field_lists_match_the_contract(self):
        """The gate and the instruction must not drift apart — that is the whole bug class."""
        contract = (SKILL_DIR / "references" / "output-contract.md").read_text(encoding="utf-8")
        source = VALIDATOR.read_text(encoding="utf-8")
        for constant in ("REVIEW_CARD_FIELDS", "EXPERIMENT_CARD_FIELDS"):
            block = re.search(rf"{constant} = \[(.*?)\]", source, re.DOTALL)
            self.assertIsNotNone(block, f"{constant} not found in the validator")
            fields = re.findall(r'"([^"]+)"', block.group(1))
            self.assertGreaterEqual(len(fields), 7)
            for field in fields:
                self.assertIn(
                    field, contract, f"{constant} field {field!r} is not in the contract"
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
            CPROMG_HTML, ("<strong>数据与指标：</strong>", "<strong>指标：</strong>")
        )
        result = self.run_validator(broken)
        self.assertEqual(result.returncode, 1)
        self.assertIn("experiment card", result.stderr)
        self.assertIn("数据与指标", result.stderr)

    def test_validator_rejects_a_duplicated_card_field(self):
        source = CPROMG_HTML.read_text(encoding="utf-8")
        label = "<strong>实验类型：</strong>"
        self.assertIn(label, source)
        broken = self.corrupt(CPROMG_HTML, (label, label + "占位</li><li>" + label))
        result = self.run_validator(broken)
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicated", result.stderr)

    def test_validator_allows_a_boundary_field_that_raises_nothing(self):
        """证据边界：无 is a valid statement and needs no B-id."""
        pattern = re.compile(
            r'<li id="(B\d{2})"><strong>证据边界：</strong>.*?</li>', re.DOTALL
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
                (field.group(0), "<li><strong>证据边界：</strong> 无</li>"),
                (link.group(0), ""),
            )
            result = self.run_validator(clean)
            self.assertEqual(result.returncode, 0, result.stderr)
            return
        self.skipTest("no experiment-card boundary field in any shipped report")

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
            ("<strong>证据缺少什么：</strong>", "<strong>补充：</strong>"),
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
                result = subprocess.run(
                    [sys.executable, str(VALIDATOR), "--figure", mode, str(CPROMG_HTML)],
                    capture_output=True,
                    text=True,
                )
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


if __name__ == "__main__":
    unittest.main()
