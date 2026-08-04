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
        self.assertIn("evidence-ledger.md", contract)
        self.assertIn("appendices/data-training.md", contract)
        self.assertIn("appendices/model-dataflow.md", contract)
        self.assertIn("appendices/experiment-matrix.md", contract)
        self.assertIn("appendices/critical-review.md", contract)
        self.assertIn("sci-ai-figure", contract)

    def test_standard_mode_has_two_required_outputs(self):
        contract = (SKILL_DIR / "references" / "output-contract.md").read_text(encoding="utf-8")
        standard = contract.split("## Standard Mode — Default", 1)[1].split(
            "## Audit Mode — Explicit", 1
        )[0]
        tree = re.search(r"```text\n(.*?)\n```", standard, re.DOTALL)
        self.assertIsNotNone(tree)
        markdown_paths = re.findall(r"[\w/-]+\.md", tree.group(1))
        self.assertEqual(markdown_paths, ["deep-reading.md", "evidence-ledger.md"])
        for appendix in (
            "data-training.md",
            "model-dataflow.md",
            "experiment-matrix.md",
            "critical-review.md",
        ):
            self.assertNotIn(appendix, tree.group(1))
        self.assertIn("at most one targeted appendix", contract)
        self.assertIn("does not require the four audit appendices", contract)

    def test_audit_mode_preserves_full_dossier(self):
        contract = (SKILL_DIR / "references" / "output-contract.md").read_text(encoding="utf-8")
        audit = contract.split("## Audit Mode — Explicit", 1)[1].split("## Primary Report", 1)[0]
        tree = re.search(r"```text\n(.*?)\n```", audit, re.DOTALL)
        self.assertIsNotNone(tree)
        markdown_paths = re.findall(r"[\w/-]+\.md", tree.group(1))
        self.assertEqual(
            markdown_paths,
            [
                "deep-reading.md",
                "evidence-ledger.md",
                "data-training.md",
                "model-dataflow.md",
                "experiment-matrix.md",
                "critical-review.md",
            ],
        )
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
        for field in ("作者要回答", "实验怎么做", "观察到什么", "证据边界"):
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
        self.assertIn("方法上值得带走什么", contract)
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
