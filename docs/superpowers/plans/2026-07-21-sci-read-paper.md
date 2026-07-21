# `sci-read-paper` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and behaviorally validate a compact `sci-read-paper` skill that reconstructs one AI/ML paper's research logic, implementation, model data flow, experiments, and scientific validity.

**Architecture:** Keep orchestration and quality gates in one sub-500-word `SKILL.md`. Put evidence rules, AI/ML reading checks, protein/small-molecule validity checks, and the output contract in four directly linked on-demand references; do not add a manifest, runtime router, or helper script until real use proves one is needed.

**Tech Stack:** Markdown, YAML, JSON, Python 3 standard-library `unittest`, PyYAML 6.x for metadata validation, Codex skill-creator scripts.

## Global Constraints

- Skill and folder name: `sci-read-paper`.
- Repository location: `skills/sci-read-paper/` inside `sci-skills`.
- Target AI/ML papers, especially deep-learning work involving proteins, small molecules, and drug discovery.
- Default output language is Chinese; preserve precise English terminology, module names, metrics, formulas, and short evidence excerpts.
- Proactively retrieve paper, supplement, official code/configuration, dataset documentation, and necessary first-party sources.
- Pause only for authentication/payment, ambiguous source identity, conclusion-changing version conflict, or a material user choice.
- Produce one self-contained `deep-reading.md`; appendices are supporting evidence, not required reading for the core explanation.
- `sci-ai-figure` is optional, not a runtime dependency, and is never invoked without a user request.
- Do not add a skill README, manifest, assets, executable scripts, broad literature-review behavior, or non-AI/ML domain support.
- Follow RED→GREEN: capture fresh-context baseline failures before creating `skills/sci-read-paper/`.

---

## File Map

| Path | Responsibility |
|---|---|
| `.gitignore` | Keep local virtual environments and Python caches out of version control. |
| `requirements-dev.txt` | Pin the only development dependency used by validation. |
| `tests/__init__.py` | Make the project tests importable by `unittest`. |
| `tests/test_sci_read_paper.py` | Validate skill metadata, compactness, direct references, UI metadata, output contract, and eval schema. |
| `tests/sci-read-paper/evals.json` | Store positive, partial-source, trigger, and non-trigger evaluation requests without leaking expected answers into agent prompts. |
| `tests/sci-read-paper/rubric.md` | Define the human/reviewer scoring contract for baseline and skill-assisted outputs. |
| `tests/sci-read-paper/baseline-findings.md` | Preserve observed baseline omissions and short verbatim evidence before the skill exists. |
| `skills/sci-read-paper/SKILL.md` | Own discovery, staged workflow, pause behavior, reference routing, and final quality gates. |
| `skills/sci-read-paper/agents/openai.yaml` | Provide the Codex UI display name, description, and default invocation prompt. |
| `skills/sci-read-paper/references/evidence-policy.md` | Define source priority, evidence labels, conflicts, uncertainty, and completion status. |
| `skills/sci-read-paper/references/ai-ml-reading-guide.md` | Define problem-chain, data/training, data-flow, code, and experiment reconstruction checks. |
| `skills/sci-read-paper/references/bio-chem-validity.md` | Define protein, small-molecule, generative-model, proxy-metric, and scientific-calibration checks. |
| `skills/sci-read-paper/references/output-contract.md` | Define the primary report, appendices, matrices, diagrams, and optional figure briefs. |

## Interfaces Between Tasks

- Evaluation cases expose `id`, `kind`, `prompt`, and `assertions` fields.
- Behavioral reviewers score each positive or partial-source run with the rubric's ten `0|1|2` criteria; GREEN requires at least 16/20 and no zero on a critical criterion.
- `SKILL.md` links directly to all four `references/*.md` files and states the observable condition for loading each.
- `output-contract.md` is the sole owner of generated dossier paths and report section order.
- `evidence-policy.md` is the sole owner of source labels and `complete|partial` semantics.
- `sci-ai-figure` handoff consists only of an optional structured brief in `deep-reading.md`; no tool or skill dependency is declared.

---

### Task 1: Create the Evaluation Contract and Observe RED

**Files:**
- Create: `.gitignore`
- Create: `requirements-dev.txt`
- Create: `tests/__init__.py`
- Create: `tests/test_sci_read_paper.py`
- Create: `tests/sci-read-paper/evals.json`
- Create after baseline runs: `tests/sci-read-paper/baseline-findings.md`

**Interfaces:**
- Consumes: approved design at `docs/superpowers/specs/2026-07-21-sci-read-paper-design.md`.
- Produces: stable eval case IDs, a 20-point rubric, observed baseline failures, and a failing structural test proving the skill does not yet exist.

- [ ] **Step 1: Create the local development environment files**

Create `.gitignore`:

```gitignore
.venv/
__pycache__/
*.py[cod]
.DS_Store
```

Create `requirements-dev.txt`:

```text
PyYAML>=6.0,<7.0
```

Create an empty `tests/__init__.py`.

- [ ] **Step 2: Write the behavioral evaluation cases**

Create `tests/sci-read-paper/evals.json` with exactly:

```json
{
  "version": 1,
  "skill": "sci-read-paper",
  "cases": [
    {
      "id": "siamprom-deep-read",
      "kind": "positive",
      "prompt": "请帮我精读论文 Recognition of cyanobacteria promoters via Siamese network-based contrastive learning under novel non-promoter generation（DOI: 10.1093/bib/bbae193）。我想真正理解作者为什么这样设计，而不是只看摘要。",
      "assertions": [
        "identifies negative-sample construction as a central methodological problem",
        "traces promoter, non-promoter, contrastive-pair, and classifier-label construction",
        "explains the relationship between representation learning and the final predictor",
        "maps phantom sampling, architecture, ablations, and motif discovery to claims",
        "calibrates the biological evidence for the reported motif"
      ]
    },
    {
      "id": "cpromg-deep-read",
      "kind": "positive",
      "prompt": "请帮我精读 CProMG: controllable protein-oriented molecule generation with desired binding affinity and drug-like properties（DOI: 10.1093/bioinformatics/btad222）。重点是让我理解作者的思考过程、模型内部数据流和实验到底证明了什么。",
      "assertions": [
        "reconstructs residue-graph and atom-graph data flow through the dual-view encoder",
        "traces affinity and physicochemical conditions into molecule generation",
        "distinguishes baseline, control, ablation, and case-study evidence",
        "separates docking, QED, and SA proxies from experimental biological claims",
        "marks unavailable code or configuration details as missing rather than inventing them"
      ]
    },
    {
      "id": "partial-source-doi-only",
      "kind": "partial-source",
      "prompt": "我只有 CProMG 这篇 AI 药物发现论文的 DOI（10.1093/bioinformatics/btad222）。请精读它；如果补充材料或官方代码找不到，也继续完成能可靠完成的部分。",
      "assertions": [
        "records attempted source resolution",
        "continues with a partial dossier when non-critical artifacts are unavailable",
        "labels missing implementation details",
        "does not fabricate code paths, splits, or hyperparameters"
      ]
    },
    {
      "id": "trigger-deep-model-question",
      "kind": "trigger",
      "prompt": "这篇蛋白质深度学习论文的输入经过哪些张量和模块才得到最终输出？论文和 GitHub 代码是否一致？",
      "assertions": [
        "selects sci-read-paper"
      ]
    },
    {
      "id": "nontrigger-quick-summary",
      "kind": "non-trigger",
      "prompt": "用五句话总结这篇论文。",
      "assertions": [
        "does not select sci-read-paper"
      ]
    },
    {
      "id": "nontrigger-translation",
      "kind": "non-trigger",
      "prompt": "把这个英文摘要翻译成中文。",
      "assertions": [
        "does not select sci-read-paper"
      ]
    },
    {
      "id": "nontrigger-literature-review",
      "kind": "non-trigger",
      "prompt": "比较这二十篇蛋白质设计论文并写一篇文献综述。",
      "assertions": [
        "does not select sci-read-paper"
      ]
    },
    {
      "id": "nontrigger-simple-fact",
      "kind": "non-trigger",
      "prompt": "这篇论文使用了哪个数据集？只告诉我数据集名称。",
      "assertions": [
        "does not select sci-read-paper"
      ]
    }
  ]
}
```

- [ ] **Step 3: Write the scoring rubric**

Create `tests/sci-read-paper/rubric.md` with exactly:

```markdown
# `sci-read-paper` Behavioral Rubric

Score each positive or partial-source output from 0 to 2 on every criterion.

- `0`: absent, invented, or materially wrong.
- `1`: present but incomplete, weakly traced, or insufficiently calibrated.
- `2`: explicit, technically useful, and traceable to identified evidence.

## Criteria

| Criterion | Critical | A score of 2 requires |
|---|---:|---|
| Research problem chain | Yes | Background, prior limitation, gap, hypothesis, design choice, and contribution form a causal chain. |
| Source completion | No | Paper, supplement, official code/configuration, and dataset sources are sought and their availability recorded. |
| Data and training | Yes | Provenance, sample construction, split, preprocessing, objectives, stages, and missing details are distinguished. |
| Model data flow | Yes | Inputs are traced through representations, transformations, interactions or conditioning, and outputs; module lists alone do not pass. |
| Experiment-to-claim mapping | Yes | Baseline, ablation, analysis, case study, and external validation are tied to questions, controls, results, and claims. |
| Paper-code comparison | No | Code-only behavior, paper-only claims, and conflicts are separated without invented reconciliation. |
| Evidence calibration | Yes | Paper facts, code facts, external evidence, inference, missing information, and conflicts are distinguishable. |
| Bio/chemical validity | Yes | Relevant leakage, split, proxy-metric, assay, docking, synthesis, or wet-lab limitations are examined. |
| Main-report usability | No | One Chinese primary report tells the complete research story while preserving precise English technical terms. |
| Reproducibility and boundaries | No | The output states what can be reproduced, what cannot, the real contribution, applicability, and unresolved questions. |

GREEN requires at least 16/20 and no `0` on a critical criterion. A run with fabricated evidence fails regardless of total score.

For trigger cases, show the case prompt and the metadata descriptions available to the agent, but do not show the expected selection. A trigger run passes only when the agent selects `sci-read-paper`; a non-trigger run passes only when it rejects it.
```

- [ ] **Step 4: Write the structural contract test before the skill exists**

Create `tests/test_sci_read_paper.py`:

```python
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
```

- [ ] **Step 5: Install the development dependency in an isolated environment**

Run:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
```

Expected: PyYAML 6.x installs successfully. If dependency download is blocked by sandboxed networking, request approval for this exact install rather than changing the dependency strategy.

- [ ] **Step 6: Run the structural RED test**

Run:

```bash
.venv/bin/python tests/test_sci_read_paper.py SkillContractTests.test_skill_exists -v
```

Expected: `FAIL` with `sci-read-paper has not been implemented`.

- [ ] **Step 7: Run fresh-context behavioral baselines without the skill**

For `siamprom-deep-read`, `cpromg-deep-read`, and `partial-source-doi-only`, dispatch one fresh agent per case with no inherited conversation context and without exposing `sci-read-paper`, the rubric, assertions, expected answer, or design document. Give the agent only the case's `prompt` and normal research tools. Keep raw outputs in a unique temporary directory outside the repository.

Score each output independently with `rubric.md`. Behavioral RED is established when at least one positive control fails the complete GREEN gate: total score below 16/20, any critical criterion scored `0`, or fabricated evidence. If both positive controls pass the full GREEN gate, stop: the proposed skill has not demonstrated a need, so do not create it. Retain any passing positive control as a pressure test; do not rerun or down-score it to manufacture RED.

- [ ] **Step 8: Record baseline failures verbatim**

Create `tests/sci-read-paper/baseline-findings.md`. For each evaluated case, record the run date, score, critical failures, and the shortest verbatim excerpts that demonstrate each omission or overclaim. End with a cross-case list of only the observed failure patterns; do not copy anticipated failures from the design.

- [ ] **Step 9: Commit the RED evidence**

Run:

```bash
git add .gitignore requirements-dev.txt tests
git commit -m "test: capture sci-read-paper baseline behavior"
```

Expected: one commit containing tests and observed baseline evidence, with no `skills/sci-read-paper/` directory.

---

### Task 2: Implement the Minimal Skill and On-Demand References

**Files:**
- Create: `skills/sci-read-paper/SKILL.md`
- Create: `skills/sci-read-paper/agents/openai.yaml`
- Create: `skills/sci-read-paper/references/evidence-policy.md`
- Create: `skills/sci-read-paper/references/ai-ml-reading-guide.md`
- Create: `skills/sci-read-paper/references/bio-chem-validity.md`
- Create: `skills/sci-read-paper/references/output-contract.md`

**Interfaces:**
- Consumes: only failure patterns actually recorded in `tests/sci-read-paper/baseline-findings.md`, plus the approved design.
- Produces: a discoverable skill with four directly linked reference modules and no runtime dependency.

- [ ] **Step 1: Initialize the skill with the official scaffold**

Run:

```bash
python3 /Users/yangguang/.codex/skills/.system/skill-creator/scripts/init_skill.py sci-read-paper \
  --path skills \
  --resources references \
  --interface display_name="SCI Read Paper" \
  --interface short_description="Deeply reconstruct and audit AI/ML research papers" \
  --interface 'default_prompt=Use $sci-read-paper to deeply analyze this AI/ML paper and produce a traceable Chinese reading dossier.'
```

Expected: `skills/sci-read-paper/` contains `SKILL.md`, `agents/openai.yaml`, and an empty `references/` directory. Do not use `--examples`.

- [ ] **Step 2: Replace the generated template with the compact orchestrator**

Replace `skills/sci-read-paper/SKILL.md` with:

```markdown
---
name: sci-read-paper
description: Use when deeply analyzing one AI/ML paper beyond summary, including its research logic, datasets, training, model data flow, experiments, reproducibility, code, or scientific validity, especially in protein, small-molecule, or drug-discovery research. Do not use for direct single-fact extraction.
---

# Deep Read Paper

Reconstruct the research argument and implementation from evidence. Detail-shaped prose is not understanding: explain why each choice exists, how it works, and what supports it.

## Workflow

1. Resolve the paper from a PDF/path, title, DOI, arXiv ID, journal page, or official repository; then collect its supplement, official code/configuration, and dataset sources. Read [evidence-policy.md](references/evidence-policy.md). Ask only for authentication/payment, ambiguous source identity, conclusion-changing version conflicts, or a material user choice.
2. Map the task, prior limitation, gap, hypothesis, contributions, evidence, and conclusion.
3. Reconstruct why prior limitations lead to each design choice and whether the claimed innovation addresses the gap.
4. Trace data provenance, sample construction, splits, leakage, preprocessing, objectives, training stages, hyperparameters, and paper-code differences. Read [ai-ml-reading-guide.md](references/ai-ml-reading-guide.md).
5. Trace input through representations, tensor transformations, interactions or conditioning, fusion, and output. Explain design motivation first; then give formulas, shapes, module interfaces, and code anchors.
6. Classify baseline, ablation, analysis, case-study, and external-validation experiments. Map each to its question, controls, result, and supported claim.
7. Audit internal validity, then verify only conclusion-critical scientific claims with first-party literature. For protein, small-molecule, or drug-discovery work, read [bio-chem-validity.md](references/bio-chem-validity.md).
8. Write the dossier exactly as [output-contract.md](references/output-contract.md) defines.

Run stages continuously. Continue with a `partial` dossier when non-critical artifacts are unavailable; never fill evidence gaps by guessing.

## Communication

For every core point, provide:

1. Chinese intuitive reasoning: why the authors made the choice.
2. Technical reconstruction: formulas, tensors, configuration, and data flow.
3. Traceable support using the evidence labels.

Preserve precise English terms, names, metrics, formulas, and short source excerpts.

## Final Gates

- The problem chain is causal, not a background list.
- Data and training details distinguish reported, implemented, inferred, missing, and conflicting information.
- Model explanation follows data; a module inventory does not pass.
- Every experiment maps to a claim and an honest evidence strength.
- Computational proxies never become experimental biological or chemical facts.
- `deep-reading.md` stands alone; appendices provide traceability.
- Mark the dossier `complete` or `partial` and list unresolved gaps.

Generate figure briefs only when a visual materially improves understanding. Do not invoke `sci-ai-figure` unless it is available and the user asks for a figure.
```

- [ ] **Step 3: Add the evidence policy**

Create `skills/sci-read-paper/references/evidence-policy.md`:

```markdown
# Evidence Policy

## Source Order

Use sources in this order:

1. Paper and supplementary material.
2. Author-maintained official code, configuration, releases, and issue clarifications.
3. Official dataset documentation and version records.
4. First-party literature needed to test a conclusion-critical domain claim.
5. Secondary sources only when first-party evidence is unavailable; label them as secondary.

Record the URL or local path, version or commit when available, access date, and which claims each source supports. Search actively, but do not bypass authentication, payment, or access controls.

## Evidence Labels

- `[论文]`: the paper or supplement states it explicitly.
- `[代码]`: official code, configuration, or processing demonstrates it.
- `[外部核验]`: a first-party external source supports or challenges it.
- `[推断]`: a reasoned reconstruction from cited evidence.
- `[缺失]`: the available sources do not report it.
- `[冲突]`: paper, supplement, code, dataset, or versions disagree.

Attach a label to every conclusion-changing statement. Nearby sentences may share one label only when their source and epistemic status are identical.

## Conflict Rules

- Report paper-code conflicts without choosing the more convenient version or inventing author intent.
- Code-only behavior can explain implementation; it is not automatically a claimed contribution.
- Paper-only behavior absent from released code is a reproducibility limitation.
- For version conflicts, identify the versions and determine whether the difference changes a conclusion. Pause only when the choice changes the analysis materially.

## Calibration

Rewrite author language into evidence-calibrated language when needed:

- `demonstrates` requires a design that excludes credible alternatives.
- `improves` requires a fair comparison under matched data, tuning, and evaluation.
- `generalizes` requires an appropriate distribution, family, scaffold, temporal, or external test.
- `novel` requires a declared comparison scope and defensible similarity criterion.

Missing splits, hyperparameters, seeds, preprocessing, or training stages remain `[缺失]`; never reconstruct them from convention alone.

## Completion Status

Use `complete` only when the paper, essential supplement, and conclusion-changing implementation evidence were accessible and the required audits were performed. Otherwise use `partial` and list:

- unavailable artifacts;
- affected sections;
- conclusions whose confidence is reduced;
- the smallest action that would resolve each gap.
```

- [ ] **Step 4: Add the AI/ML reconstruction guide**

Create `skills/sci-read-paper/references/ai-ml-reading-guide.md`:

```markdown
# AI/ML Reading Guide

## Research Logic

Build one causal chain:

```text
task and stakes
→ limitation of prior data, assumptions, representation, optimization, or evaluation
→ unresolved gap
→ author hypothesis
→ design choice intended to test it
→ evidence
→ bounded conclusion
```

Separate a genuinely new capability from a new combination, new dataset construction, engineering improvement, or evaluation change. Test whether the proposed method addresses the stated gap rather than a nearby easier problem.

## Data and Training

Recover and cross-check:

- dataset origin, version, license, inclusion/exclusion, labels, units, and sample counts;
- sample construction, negatives or decoys, augmentation, deduplication, and preprocessing order;
- train/validation/test split unit and strategy; group, identity, scaffold, temporal, and external separation;
- leakage through duplicates, related entities, preprocessing fit, target knowledge, pretrained data, or test-guided selection;
- objective terms, weighting, optimization, schedules, freezing, early stopping, seeds, precision, hardware, and checkpoint selection;
- differences among paper prose, supplement, default config, training command, and released checkpoint.

Do not infer an unreported value from a library default without labeling it `[推断]` and proving that the released version used that default.

## Model Data Flow

Start from one concrete sample. Track:

| Stage | Record |
|---|---|
| Input | semantic meaning, raw type, shape, and preprocessing |
| Representation | tokenizer/featurizer, embedding, positional or geometric information |
| Transformation | operation, input/output shape, parameters, and information gained or lost |
| Interaction | attention, message passing, pairing, cross-view exchange, or conditioning |
| Fusion | concatenation, sum, pooling, gating, or decoder context |
| Output | prediction/generation target, decoding, calibration, and postprocessing |
| Training signal | loss path and which modules receive gradients |

Explain motivation before equations. Define symbols and shapes before manipulating them. When shapes are not reported, derive only those forced by code or equations and label them `[推断]`.

## Code Audit

Locate the actual data loader, split generator, model entry point, loss computation, training loop, evaluation command, and default configuration. Cite file paths and commit IDs. Distinguish executable paths from dead code, examples, or unused options.

## Experiment Reasoning

Classify each result as baseline, ablation, analysis, robustness/generalization, case study, or external validation. For each experiment record:

1. Question or claim under test.
2. Changed and controlled variables.
3. Data split and metric.
4. Fairness of baselines and tuning.
5. Result with uncertainty or statistical support.
6. What the result supports.
7. What it does not establish.

Check whether ablations isolate one factor, whether baseline implementations and compute budgets are comparable, whether multiple seeds or confidence intervals matter, and whether analysis plots are explanatory evidence or illustrations.
```

- [ ] **Step 5: Add the protein and small-molecule validity guide**

Create `skills/sci-read-paper/references/bio-chem-validity.md`:

```markdown
# Protein and Small-Molecule Validity

Load only for protein, small-molecule, molecular-generation, binding, or drug-discovery work.

## Protein and Sequence Tasks

Check:

- split unit: sequence, chain, complex, protein, family, species, structure, or time;
- sequence identity and homology thresholds, clustering order, and cross-split relatives;
- redundancy among chains, complexes, structures, and augmented samples;
- whether pretrained representations may include benchmark proteins or close homologs;
- label provenance, assay conditions, organism context, and negative-label validity;
- whether motif or mechanism claims have experimental, comparative-genomic, or only model-attribution support.

Random sequence splits rarely establish family- or species-level generalization. A discovered motif is a computational candidate until independent biological evidence supports function.

## Small Molecules and Binding

Check:

- molecule, scaffold, target, protein-family, complex, and temporal separation;
- duplicate structures, stereochemistry, tautomers, protonation, salts, conformers, and assay units;
- pocket definition and whether ligand or test-complex information leaks into input construction;
- affinity-label provenance and comparability across assays;
- docking engine, receptor preparation, search box, protonation, seeds, pose selection, and rescoring;
- whether train/test targets or chemotypes are genuinely novel.

Docking scores are model-dependent ranking proxies, not measured affinity. QED is a heuristic desirability score. SA scores are computational proxies, not proof that a compound can be synthesized. Predicted ADMET is not experimental safety or efficacy.

## Molecular Generation

Separate:

- syntactic validity;
- uniqueness within generated samples;
- novelty relative to the declared reference set;
- structural and scaffold diversity;
- property-distribution matching or conditional control;
- target relevance and binding proxies;
- retrosynthetic or experimental synthesizability;
- wet-lab validation.

Check whether selection and reporting use the same predictor that supplied the conditioning signal. Improvement under a reused oracle can reflect oracle exploitation. Case studies chosen from top docking scores demonstrate examples, not population-level efficacy.

## Scientific Claim Calibration

For every biological or chemical conclusion, state the strongest justified level:

1. observed experimental fact;
2. supported computational association;
3. model-based prediction;
4. plausible hypothesis;
5. unsupported speculation.

Use external first-party literature only for claims that change the paper's credibility or interpretation. Record disagreement and evidence limits instead of forcing consensus.
```

- [ ] **Step 6: Add the output contract**

Create `skills/sci-read-paper/references/output-contract.md`:

```markdown
# Output Contract

Create one directory named from a stable paper slug:

```text
<paper-slug>/
├── deep-reading.md
├── appendices/
│   ├── evidence-ledger.md
│   ├── data-training.md
│   ├── model-dataflow.md
│   ├── experiment-matrix.md
│   └── critical-review.md
└── assets/
```

`deep-reading.md` is self-contained and is the only file a normal reader must open. Appendices preserve detail and traceability without duplicating the main narrative.

## Primary Report

Use exactly these top-level sections:

```markdown
# <Paper Title>

## 阅读状态
## 一页理解整篇论文
## 1. 作者为什么做这项研究
## 2. 数据与训练到底怎样完成
## 3. 模型内部的数据怎样流动
## 4. 每项实验究竟想证明什么
## 5. 作者的结论是否成立
## 6. 我们最终应该怎样理解这篇论文
## 可选科研绘图 Briefs
```

`阅读状态` records `complete|partial`, source availability, paper/code versions, and unresolved gaps. `一页理解整篇论文` gives orientation, not a substitute abstract.

The model section contains at least one reconstructed data-flow diagram when evidence supports it. Prefer Mermaid for explicit entities and edges. Mark inferred edges or shapes in the prose; do not make uncertain content look authoritative through visual polish.

## Appendices

### `appendices/evidence-ledger.md`

Use columns: evidence ID, label, source, version/commit, locator, supported statement, and access status.

### `appendices/data-training.md`

Record provenance, construction, counts, splits, preprocessing, leakage checks, objectives, stages, hyperparameters, compute, checkpoint selection, and paper-code differences.

### `appendices/model-dataflow.md`

Record a concrete sample trace plus a table with stage, semantic object, shape, operation, output, code anchor, and evidence label.

### `appendices/experiment-matrix.md`

Use columns: experiment ID, type, question/claim, changed variable, controls, data/split, metric, result, supported conclusion, unsupported conclusion, evidence IDs.

### `appendices/critical-review.md`

Separate internal validity, reproducibility, domain validity, external claim checks, alternative explanations, applicability, and unresolved questions. Rank issues by effect on the central conclusion rather than by writing style.

## Optional Figure Handoff

Include at most three briefs, and only when a visual materially improves understanding. Each brief contains:

- purpose and target reader;
- figure type;
- required entities and relationships;
- evidence IDs;
- visual hierarchy;
- content that must not be inferred or invented.

Do not generate images automatically. If `sci-ai-figure` is installed and the user explicitly asks for a figure, pass the brief as the handoff contract.
```

- [ ] **Step 7: Regenerate and inspect Codex UI metadata**

Run:

```bash
python3 /Users/yangguang/.codex/skills/.system/skill-creator/scripts/generate_openai_yaml.py \
  skills/sci-read-paper \
  --interface display_name="SCI Read Paper" \
  --interface short_description="Deeply reconstruct and audit AI/ML research papers" \
  --interface 'default_prompt=Use $sci-read-paper to deeply analyze this AI/ML paper and produce a traceable Chinese reading dossier.'
```

Expected `skills/sci-read-paper/agents/openai.yaml`:

```yaml
interface:
  display_name: "SCI Read Paper"
  short_description: "Deeply reconstruct and audit AI/ML research papers"
  default_prompt: "Use $sci-read-paper to deeply analyze this AI/ML paper and produce a traceable Chinese reading dossier."
```

- [ ] **Step 8: Run structural GREEN checks**

Run:

```bash
.venv/bin/python tests/test_sci_read_paper.py -v
.venv/bin/python /Users/yangguang/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sci-read-paper
```

Expected: nine unit tests pass and `Skill is valid!`.

- [ ] **Step 9: Commit the minimal skill**

Run:

```bash
git add skills/sci-read-paper
git commit -m "feat: add sci-read-paper skill"
```

Expected: the commit contains only the skill directory and its six authored files.

---

### Task 3: Verify GREEN on the Two Real Papers

**Files:**
- Modify with observed results: `tests/sci-read-paper/baseline-findings.md`
- Modify only if a real GREEN failure identifies a precise gap: one of the four `skills/sci-read-paper/references/*.md` files or `SKILL.md`

**Interfaces:**
- Consumes: the unchanged prompts in `evals.json`, implemented skill, and rubric.
- Produces: independent evidence that the skill improves both sequence-classification and protein-conditioned molecular-generation reading.

- [ ] **Step 1: Run fresh skill-assisted evaluations**

Dispatch one fresh agent for `siamprom-deep-read` and one for `cpromg-deep-read`. Give each agent only its case prompt, access to `skills/sci-read-paper/`, and normal research tools. Do not provide the rubric, assertions, baseline findings, design document, or the other agent's output.

Keep raw outputs in a new temporary directory outside the repository so later agents cannot discover them.

- [ ] **Step 2: Score without trusting agent self-reports**

Review each output against `rubric.md` and its case assertions. For every score, cite a concrete output location. Confirm:

- total score is at least 16/20;
- no critical criterion scores `0`;
- every case-specific assertion is present;
- no source, code path, hyperparameter, shape, split, or external conclusion is fabricated;
- `deep-reading.md` is usable without opening appendices.

Expected: both cases meet all GREEN conditions. If either fails, record the exact observed failure and stop before generalizing the skill as ready.

- [ ] **Step 3: Make only evidence-driven wording changes if GREEN exposes a gap**

For a failed criterion, identify whether the baseline failure persists because discovery, routing, the relevant reference, or the output contract is unclear. Change only that owning file. Do not add a general prohibition list for an output-shape failure; add a positive required field or recipe. Re-run the failed case in a fresh context after each single change.

If no precise minimal change can be derived from the observed output, stop and return the evidence to the user instead of guessing.

- [ ] **Step 4: Preserve before/after evidence**

Append a `## GREEN results` section to `tests/sci-read-paper/baseline-findings.md`. Record the skill commit, score changes per criterion, resolved baseline failures, remaining limitations, and short verbatim evidence. Do not store complete agent outputs in the repository.

- [ ] **Step 5: Run regression checks and commit evaluation evidence**

Run:

```bash
.venv/bin/python tests/test_sci_read_paper.py -v
.venv/bin/python /Users/yangguang/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sci-read-paper
git diff --check
```

Expected: all checks pass with no whitespace errors.

Then run:

```bash
git add skills/sci-read-paper tests/sci-read-paper/baseline-findings.md
git commit -m "test: verify sci-read-paper on reference papers"
```

If no skill files changed during GREEN, the commit contains only evaluation evidence.

---

### Task 4: Verify Partial-Source Behavior and Trigger Precision

**Files:**
- Modify with observed results: `tests/sci-read-paper/baseline-findings.md`
- Modify only for an observed metadata failure: `skills/sci-read-paper/SKILL.md`
- Modify only for an observed partial-output failure: `skills/sci-read-paper/references/evidence-policy.md` or `skills/sci-read-paper/references/output-contract.md`

**Interfaces:**
- Consumes: `partial-source-doi-only`, `trigger-deep-model-question`, and the four non-trigger cases.
- Produces: evidence that the skill degrades honestly and that its metadata selects narrowly.

- [ ] **Step 1: Test partial-source degradation**

Run `partial-source-doi-only` exactly as stored in `evals.json`; do not tell the agent whether code is available. Task 3 established an official CProMG repository, so this fixture now tests whether a DOI-only request discovers that repository and distinguishes available code from genuinely unresolved release artifacts. Do not manufacture missing-code conditions.

Expected behavior:

- source-resolution attempts and the resolved official repository version are recorded;
- the dossier is marked `complete` only if all material claims can be verified, otherwise `partial` with each genuinely unavailable or unverified artifact named;
- missing evaluation scripts, configuration, supplement, checkpoint verification, or other release artifacts affect confidence only when execution-time evidence shows that gap;
- no implementation detail or missing-source condition is invented;
- reliable paper-and-code analysis continues despite non-critical gaps.

- [ ] **Step 2: Test metadata selection without exposing expected answers**

For each trigger and non-trigger case, dispatch five fresh metadata-selection samples. Give each sample the case prompt and a catalog containing the exact `sci-read-paper` name/description plus at least these distractor descriptions:

```text
summarize-paper — Use when a user wants a short overview or key takeaways from one paper.
translate-academic-text — Use when translating academic prose between English and Chinese.
review-literature — Use when synthesizing findings across multiple papers into a literature review.
sci-read-paper — Use when deeply analyzing one AI/ML paper beyond summary, including its research logic, datasets, training, model data flow, experiments, reproducibility, code, or scientific validity, especially in protein, small-molecule, or drug-discovery research. Do not use for direct single-fact extraction.
```

Ask only: `Which single skill, if any, applies? Return its name or none.` Do not expose `kind` or assertions.

Expected across all five repetitions:

- `trigger-deep-model-question` selects `sci-read-paper` five times;
- the quick-summary, translation, and literature-review controls select their matching distractors five times and never select `sci-read-paper`;
- `nontrigger-simple-fact` may select any alternative or `none`, but never `sci-read-paper`.

- [ ] **Step 3: Tighten only the metadata if selection fails**

If a selection failure occurs, preserve the exact mistaken choice, change only the frontmatter description, and repeat five fresh samples for the failed case, the three prior non-trigger controls, and `trigger-deep-model-question`. Do not summarize the workflow in the description.

- [ ] **Step 4: Record and commit trigger/partial evidence**

Append `## Partial-source and trigger results` to `baseline-findings.md`, including the DOI used, source availability, partial-output verdict, repetition counts, and any metadata revision.

Run:

```bash
.venv/bin/python tests/test_sci_read_paper.py -v
git diff --check
git add skills/sci-read-paper tests/sci-read-paper/baseline-findings.md
git commit -m "test: verify sci-read-paper boundaries"
```

Expected: all structural tests pass and the committed evidence reports 5/5 correct selection for every trigger-control case.

---

### Task 5: Final Repository and Deployment Readiness Audit

**Files:**
- Modify only if validation finds a concrete mismatch: files already created by Tasks 1–4.

**Interfaces:**
- Consumes: all skill files and RED/GREEN evidence.
- Produces: a clean, repository-local, validated skill ready for user review and optional installation.

- [ ] **Step 1: Run the complete validation set**

Run:

```bash
.venv/bin/python tests/test_sci_read_paper.py -v
.venv/bin/python /Users/yangguang/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sci-read-paper
git diff --check
wc -w skills/sci-read-paper/SKILL.md
rg -n 'TBD|TODO|FIXME|PLACEHOLDER|待定' skills tests
```

Expected:

- nine unit tests pass;
- `Skill is valid!`;
- `git diff --check` emits no output;
- `SKILL.md` body remains within the 500-word contract enforced by the unit test;
- placeholder scan emits no matches.

- [ ] **Step 2: Review spec coverage line by line**

Compare the implementation with every section in `docs/superpowers/specs/2026-07-21-sci-read-paper-design.md`. Confirm the implemented files cover goals, non-goals, trigger boundary, source policy, all eight workflow stages, primary-report priority, six evidence labels, optional figure handoff, pause behavior, both positive fixtures, failure scenarios, and non-trigger scenarios.

Record any uncovered requirement as a failing test before changing the skill.

- [ ] **Step 3: Inspect the final diff and history**

Run:

```bash
git status --short --branch
git log --oneline --decorate -6
git diff HEAD~1 --stat
```

Expected: no uncommitted files, small focused commits, and no generated raw paper/evaluation artifacts in the repository.

- [ ] **Step 4: Stop for user review before installation**

Report the validated repository-local path, test counts, baseline-to-GREEN evidence, remaining limitations, and exact commit history. Do not copy to `~/.codex/skills`, publish, push, or begin `sci-ai-figure` without explicit user approval.
