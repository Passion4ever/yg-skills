import json
import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "sci-read-paper"
SKILL_MD = SKILL_DIR / "SKILL.md"
OPENAI_YAML = SKILL_DIR / "agents" / "openai.yaml"
EVALS_JSON = ROOT / "tests" / "sci-read-paper" / "evals.json"
READABILITY_RUBRIC = ROOT / "tests" / "sci-read-paper" / "readability-rubric.md"
EXPECTED_REFERENCES = {
    "evidence-policy.md",
    "ai-ml-reading-guide.md",
    "bio-chem-validity.md",
    "output-contract.md",
}


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
        self.assertIn("deep-reading.md", contract)
        self.assertIn("appendices/evidence-ledger.md", contract)
        self.assertIn("appendices/data-training.md", contract)
        self.assertIn("appendices/model-dataflow.md", contract)
        self.assertIn("appendices/experiment-matrix.md", contract)
        self.assertIn("appendices/critical-review.md", contract)
        self.assertIn("sci-ai-figure", contract)

    def test_standard_mode_has_two_required_outputs(self):
        contract = (SKILL_DIR / "references" / "output-contract.md").read_text(encoding="utf-8")
        self.assertIn("## Standard Mode — Default", contract)
        self.assertIn("evidence-ledger.md", contract)
        self.assertIn("at most one targeted appendix", contract)
        self.assertIn("does not require the four audit appendices", contract)

    def test_audit_mode_preserves_full_dossier(self):
        contract = (SKILL_DIR / "references" / "output-contract.md").read_text(encoding="utf-8")
        self.assertIn("## Audit Mode — Explicit", contract)
        for appendix in (
            "appendices/data-training.md",
            "appendices/model-dataflow.md",
            "appendices/experiment-matrix.md",
            "appendices/critical-review.md",
        ):
            self.assertIn(appendix, contract)

    def test_standard_mode_bounds_research_scope(self):
        skill = SKILL_MD.read_text(encoding="utf-8")
        policy = (SKILL_DIR / "references" / "evidence-policy.md").read_text(encoding="utf-8")
        guide = (SKILL_DIR / "references" / "ai-ml-reading-guide.md").read_text(encoding="utf-8")
        self.assertIn("standard", skill)
        self.assertIn("audit", skill)
        self.assertIn("at most three conclusion-critical claim families", policy)
        self.assertIn("shortest conclusion-relevant path", guide)
        self.assertIn("Do not download weights", guide)

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
            "Main/appendix separation",
        ):
            self.assertIn(f"| {criterion} |", text)
        self.assertIn("at least 14/16", text)
        self.assertIn("scientific-depth score", text)

    def test_output_contract_has_guided_reading_layers(self):
        contract = (SKILL_DIR / "references" / "output-contract.md").read_text(encoding="utf-8")
        for heading in (
            "## 阅读导航",
            "## 1. 先把论文放回领域里",
            "## 2. 三分钟看懂这篇论文",
            "## 3. 作者是怎样一步步想到这个方法的",
            "## 4. 数据与训练：跟踪一条样本",
            "## 5. 模型：数据怎样一步步变成输出",
            "## 6. 实验：每项实验究竟回答什么问题",
            "## 7. 批判性审查：哪些结论可以相信",
            "## 8. 最终带走什么",
        ):
            self.assertIn(heading, contract)

    def test_skill_enforces_chinese_first_progressive_reading(self):
        text = SKILL_MD.read_text(encoding="utf-8")
        for phrase in (
            "Chinese-first",
            "conclusion → intuition → technical detail → meaning",
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
