import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "sci-read-paper"
SKILL_MD = SKILL_DIR / "SKILL.md"
OPENAI_YAML = SKILL_DIR / "agents" / "openai.yaml"
EVALS_JSON = ROOT / "tests" / "sci-read-paper" / "evals.json"
READABILITY_RUBRIC = ROOT / "tests" / "sci-read-paper" / "readability-rubric.md"
HTML_TEMPLATE = SKILL_DIR / "assets" / "report-template.html"
SIAMPROM_HTML = (
    ROOT / "tests" / "sci-read-paper" / "outputs" / "siamprom-cyanobacteria-promoters.html"
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

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        attributes = dict(attrs)
        element_id = attributes.get("id")
        if element_id:
            self.ids.append(element_id)
            if tag == "section" and re.fullmatch(r"section-[1-8]", element_id):
                self.section_ids.append(element_id)
        href = attributes.get("href")
        if tag == "a" and href and href.startswith("#"):
            self.internal_targets.append(href[1:])
        self.classes.extend((attributes.get("class") or "").split())


def read_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not match:
        raise AssertionError("SKILL.md must have YAML frontmatter")
    return yaml.safe_load(match.group(1)), match.group(2)


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
        self.assertIn("sci-ai-figure", contract)

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
        self.assertIn("sparse or blob-filtered repository retrieval", guide)

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
        self.assertIn("〔E12–E15〕", policy)
        self.assertIn("never hide inference, missing information, or conflict", policy)

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
            "position: sticky",
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


if __name__ == "__main__":
    unittest.main()
