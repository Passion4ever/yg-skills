# `sci-read-paper` Readability Overhaul Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `deep-reading.md` read like a Chinese research mentor guiding the reader through a paper, while preserving the existing evidence depth, code audit, scientific criticism, and reproducibility boundaries.

**Architecture:** Keep the six-file skill architecture unchanged. Add a readability evaluation contract, then revise only the orchestrator plus the evidence, AI/ML reading, and output-contract references; preserve full audit detail in appendices and validate the new progressive main report on CProMG with a SiamProm regression.

**Tech Stack:** Markdown, YAML, JSON, Python 3 standard-library `unittest`, PyYAML 6.x, Codex skill-creator validation, fresh-context behavioral evaluations.

## Global Constraints

- The controlling design is `docs/superpowers/specs/2026-07-22-sci-read-paper-readability-design.md`; the original scientific-depth design remains binding.
- Keep the skill and folder name `sci-read-paper` and the repository path `skills/sci-read-paper/`.
- Keep exactly six authored skill files and exactly four references; do not add a README, manifest, assets, scripts, router, or runtime dependency.
- Modify only `SKILL.md`, `references/evidence-policy.md`, `references/ai-ml-reading-guide.md`, and `references/output-contract.md`; do not modify `references/bio-chem-validity.md`.
- Main-report prose is Chinese-first. Use English only for proper names, code identifiers, metrics, author-defined modules, or terms whose Chinese translation would lose precision.
- The main report uses progressive disclosure: field background, three-minute map, guided deep reading, and audit appendices.
- `deep-reading.md` remains self-contained, but self-contained does not mean copying exhaustive appendix inventories into the main narrative.
- Use lightweight evidence IDs in main prose while preserving the six canonical evidence labels and full locators in the evidence ledger.
- Existing trigger boundaries, pause behavior, `complete|partial` semantics, proactive retrieval, and optional `sci-ai-figure` handoff must not regress.
- Readability GREEN requires at least 14/16 with no criterion at `0`.
- Scientific-depth GREEN remains at least 16/20 with no critical criterion at `0`, all case assertions present, and no fabricated evidence.
- Behavioral evaluators receive only the unchanged case prompt, access to the skill, an operational output directory, and normal research tools; never expose rubrics, expected scores, prior outputs, assertions, design documents, or another evaluator's output.

---

## File Map

| Path | Responsibility |
|---|---|
| `tests/sci-read-paper/readability-rubric.md` | Define the eight 0–2 readability criteria and joint GREEN gate. |
| `tests/sci-read-paper/readability-findings.md` | Preserve observed current-output RED evidence, new-output scores, before/after excerpts, and remaining limitations. |
| `tests/test_sci_read_paper.py` | Enforce the new guided sections, Chinese-first rules, lightweight evidence IDs, sample-first method, and readability rubric schema. |
| `skills/sci-read-paper/SKILL.md` | Own Chinese-first communication, progressive disclosure, paragraph-level readability, and final gates. |
| `skills/sci-read-paper/references/evidence-policy.md` | Own evidence IDs, six labels, paragraph-level citation, conflicts, calibration, and completion status. |
| `skills/sci-read-paper/references/ai-ml-reading-guide.md` | Own field orientation, causal thought chain, concrete-sample reconstruction, model flow, and question-driven experiments. |
| `skills/sci-read-paper/references/output-contract.md` | Own the new report hierarchy, exact headings, judgment cards, appendix separation, and optional figure handoff. |

## Interfaces Between Tasks

- The readability rubric has eight criteria scored `0|1|2`; GREEN is `>=14/16` with no zero.
- Existing scientific-depth scoring in `tests/sci-read-paper/rubric.md` remains unchanged and is applied alongside readability scoring.
- Evidence IDs use stable dossier-local identifiers such as `E01`, `E02`, and paragraph citations such as `〔E12–E15〕`.
- The evidence ledger remains the only owner of label, source, version, locator, supported statement, and access status for each evidence ID.
- Behavioral raw outputs stay outside Git in a unique temporary directory; only concise scores and short excerpts enter `readability-findings.md`.
- A behavioral wording change is permitted only after a concrete failed criterion identifies its owning file; rerun only the failed paper in a fresh context after each single change.

---

### Task 1: Add the Readability Contract and Capture RED

**Files:**
- Create: `tests/sci-read-paper/readability-rubric.md`
- Create after scoring current outputs: `tests/sci-read-paper/readability-findings.md`
- Modify: `tests/test_sci_read_paper.py`

**Interfaces:**
- Consumes: the approved readability design and the current CProMG/SiamProm dossiers generated by skill commit `5e93f46`.
- Produces: deterministic failing contract tests plus observed readability baseline evidence without changing any skill file.

- [ ] **Step 1: Create the readability rubric**

Create `tests/sci-read-paper/readability-rubric.md` with exactly:

```markdown
# `sci-read-paper` Readability Rubric

Score the primary `deep-reading.md` from 0 to 2 on every criterion. Judge the reading experience of the main report; use appendices only to check whether detail was moved rather than lost.

- `0`: absent, misleading, or seriously obstructs understanding.
- `1`: present but dense, fragmented, inconsistently applied, or dependent on appendices.
- `2`: clear, progressive, concise enough to follow, and scientifically faithful.

| Criterion | A score of 2 requires |
|---|---|
| Background orientation | Explains the real task, importance, difficulty, mainstream approach, and the paper's entry gap without turning into a broad literature review. |
| Three-minute map | Independently gives the task, central tension, author thought chain, minimal data flow, overall experimental verdict, and largest credibility risk. |
| Causal narrative | Prior limitations lead naturally to hypotheses and design choices; the report is not a section-by-section inventory. |
| Concrete sample | Data, training, and model flow begin from one traceable sample before aggregate counts and exhaustive configuration. |
| Progressive technical depth | Gives conclusion and intuition before equations, tensor shapes, configuration, and code; technical detail does not interrupt the main line. |
| Chinese-first prose | Uses natural Chinese by default and retains English only for precise mapping, proper names, code identifiers, metrics, or author-defined modules. |
| Readable evidence | Uses light paragraph-level evidence IDs and explicit epistemic language without dense repeated source-label clusters. |
| Main/appendix separation | The main report contains the complete research story but does not copy exhaustive ledgers, configuration inventories, or conflict lists from appendices. |

Readability GREEN requires at least 14/16 and no criterion at `0`.

Joint GREEN additionally requires the existing scientific-depth score to remain at least 16/20 with no critical criterion at `0`, all case-specific assertions present, and no fabricated evidence.
```

- [ ] **Step 2: Add deterministic readability tests before changing the skill**

In `tests/test_sci_read_paper.py`, add this constant after `EVALS_JSON`:

```python
READABILITY_RUBRIC = ROOT / "tests" / "sci-read-paper" / "readability-rubric.md"
```

Add these methods to `SkillContractTests` before `test_eval_schema_and_case_coverage`:

```python
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
```

- [ ] **Step 3: Run focused structural RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_sci_read_paper.SkillContractTests.test_output_contract_has_guided_reading_layers \
  tests.test_sci_read_paper.SkillContractTests.test_skill_enforces_chinese_first_progressive_reading \
  tests.test_sci_read_paper.SkillContractTests.test_evidence_policy_supports_lightweight_ids \
  tests.test_sci_read_paper.SkillContractTests.test_ai_ml_guide_is_sample_and_question_driven -v
```

Expected: four failures because the current skill lacks the new headings, progressive-reading phrases, evidence-ID policy, and sample/question-driven instructions. The readability-rubric test itself should pass.

- [ ] **Step 4: Score the current reports without changing them**

Use these existing raw reports when present:

```text
/tmp/sci-read-paper-green.uaO99b/cpromg-raw-created/deep-reading.md
/tmp/sci-read-paper-green.uaO99b/siamprom-raw-created/deep-reading.md
```

If either path is unavailable, create a temporary baseline checkout at commit `52604ba`, run the unchanged positive prompt with a fresh agent using that checkout's skill, and keep the output outside the repository.

Dispatch one fresh read-only reviewer per report. Give each reviewer only the raw `deep-reading.md`, `readability-rubric.md`, and the instruction to score every criterion with concrete line citations. Do not provide the design, expected total, user feedback, the other paper, or the existing scientific score.

Verify RED by observing at least one report below 14/16 or with a zero. If both current reports pass 14/16 with no zero, stop and revise the rubric with the user rather than manufacturing a failure.

- [ ] **Step 5: Record current-output evidence**

Create `tests/sci-read-paper/readability-findings.md` with these fixed headings:

```markdown
# Readability Findings

## Current-output baseline

Run date: 2026-07-22. Evaluated skill state: `52604ba` plus no readability changes.

### CProMG

### SiamProm

### Observed patterns
```

Under each paper heading, add a table with columns `Criterion`, `Score`, and `Concrete evidence`; copy all eight reviewer scores, cite exact `deep-reading.md` lines, and quote the shortest supporting excerpt. State the calculated total and `RED|GREEN` verdict. Under `Observed patterns`, record only patterns visible in both reports rather than anticipated weaknesses from the design. Do not store complete reports in Git.

- [ ] **Step 6: Verify scope and commit RED**

Run:

```bash
git diff --check
git status --short
```

Expected: only the rubric, findings, and test file are changed; no skill file is modified.

Commit:

```bash
git add tests/test_sci_read_paper.py tests/sci-read-paper/readability-rubric.md tests/sci-read-paper/readability-findings.md
git commit -m "test: capture sci-read-paper readability baseline"
```

---

### Task 2: Implement Progressive Chinese-First Reading

**Files:**
- Modify: `skills/sci-read-paper/SKILL.md`
- Modify: `skills/sci-read-paper/references/evidence-policy.md`
- Modify: `skills/sci-read-paper/references/ai-ml-reading-guide.md`
- Modify: `skills/sci-read-paper/references/output-contract.md`
- Test: `tests/test_sci_read_paper.py`

**Interfaces:**
- Consumes: only observed Task 1 readability failures plus both approved designs.
- Produces: a structurally valid skill with progressive main-report layers and unchanged scientific/domain scope.

- [ ] **Step 1: Replace `SKILL.md` with the compact readability orchestrator**

Replace `skills/sci-read-paper/SKILL.md` with exactly:

```markdown
---
name: sci-read-paper
description: Use when deeply analyzing one AI/ML paper beyond summary, including its research logic, datasets, training, model data flow, experiments, reproducibility, code, or scientific validity, especially in protein, small-molecule, or drug-discovery research. Do not use for direct single-fact extraction.
---

# Deep Read Paper

Reconstruct the authors' reasoning and implementation from evidence. The main report should feel like a research mentor guiding the reader, not an audit log with prose between entries.

## Workflow

1. Resolve the paper from a PDF/path, title, DOI, arXiv ID, journal page, or official repository; then collect its supplement, official code/configuration, and dataset sources. Read [evidence-policy.md](references/evidence-policy.md). Ask only for authentication/payment, ambiguous source identity, conclusion-changing version conflicts, or a material user choice.
2. Orient the reader: explain the real scientific task, why it matters, why it is difficult, the mainstream approach, and the precise gap this paper enters.
3. Build the causal thought chain from prior limitation to hypothesis, design choice, evidence, and bounded contribution.
4. Trace one concrete sample through provenance, construction, preprocessing, labels, splits, training stages, objectives, and paper-code differences. Read [ai-ml-reading-guide.md](references/ai-ml-reading-guide.md).
5. Follow that sample through representations, tensor or graph transformations, interactions, fusion or conditioning, and output. Give motivation before formulas, shapes, interfaces, and code anchors.
6. Organize baseline, control, ablation, analysis, case-study, and external-validation evidence by the research question each experiment answers.
7. Audit internal validity, then verify only conclusion-critical scientific claims with first-party literature. For protein, small-molecule, or drug-discovery work, read [bio-chem-validity.md](references/bio-chem-validity.md).
8. Write the dossier exactly as [output-contract.md](references/output-contract.md) defines.

Run continuously. Continue with a `partial` dossier when non-critical artifacts are unavailable; never fill gaps by guessing.

## Communication

- Use Chinese-first prose. At first use, give Chinese with the English term only when it helps paper/code mapping; then prefer Chinese. Preserve proper names, metrics, code identifiers, file paths, and author-defined modules.
- Develop each core section as conclusion → intuition → technical detail → meaning. Start from a concrete object before aggregate inventories.
- Keep a paragraph to one main judgment and usually 3–5 sentences. Aim for a 15–20 minutes main-report reading path; move exhaustive audit detail to appendices.
- Cite paragraphs with lightweight evidence IDs. Explicitly say when the paper reports, code implements, evidence conflicts, information is missing, or the analysis infers.

## Final Gates

- Background makes the paper's problem understandable without becoming a broad review.
- The three-minute map stands alone and includes the task, tension, thought chain, minimal data flow, experimental verdict, and largest risk.
- Data and model explanations follow a concrete sample; module inventories do not pass.
- Every experiment maps to a question, controls, result, supported claim, and unsupported claim.
- Computational proxies never become experimental biological or chemical facts.
- `deep-reading.md` contains the complete research story without copying appendix inventories.
- Mark `complete|partial`, list unresolved gaps once, and repeat them only where they change a judgment.

Generate figure briefs only when a visual materially improves understanding. Do not invoke `sci-ai-figure` unless it is available and the user explicitly asks for a figure.
```

- [ ] **Step 2: Replace `evidence-policy.md` with evidence-ID progressive citation**

Replace `skills/sci-read-paper/references/evidence-policy.md` with exactly:

```markdown
# Evidence Policy

## Source Order

Use sources in this order:

1. Paper and supplementary material.
2. Author-maintained official code, configuration, releases, and issue clarifications.
3. Official dataset documentation and version records.
4. First-party literature needed to test a conclusion-critical domain claim.
5. Secondary sources only when first-party evidence is unavailable; label them as secondary.

Record URL or local path, version or commit, access date, and supported claims. Search actively, but do not bypass authentication, payment, or access controls.

## Evidence Labels

- `[论文]`: the paper or supplement states it explicitly.
- `[代码]`: official code, configuration, or processing demonstrates it.
- `[外部核验]`: a first-party external source supports or challenges it.
- `[推断]`: a reasoned reconstruction from cited evidence.
- `[缺失]`: the available sources do not report it.
- `[冲突]`: paper, supplement, code, dataset, or versions disagree.

These labels define epistemic status and remain mandatory in the evidence ledger.

## Evidence IDs in the Main Report

Assign stable dossier-local IDs such as `E01`, `E02`, and `E03`. Cite a natural paragraph with compact forms such as `〔E03〕` or `〔E12–E15〕`; do not append clusters of source labels to every sentence.

Each ID maps to one ledger row containing label, source, version/commit, locator, supported statement, and access status. Reuse an ID only for the statement it actually supports.

Lightweight IDs never hide inference, missing information, or conflict. When epistemic status changes the interpretation, write it directly in Chinese: “论文报告……”, “公开代码实际执行……”, “我们据此推断……”, or “当前材料无法确定……”.

## Conflict Rules

- Report paper-code conflicts without choosing the convenient version or inventing author intent.
- Code-only behavior can explain implementation; it is not automatically a claimed contribution.
- Paper-only behavior absent from released code is a reproducibility limitation.
- Identify conflicting versions and whether the difference changes a conclusion. Pause only when the choice changes the analysis materially.
- Put conclusion-changing conflicts in `deep-reading.md`; move secondary implementation differences to the relevant appendix.

## Calibration

Rewrite author language when the design does not support it:

- `demonstrates` requires credible alternatives to be excluded.
- `improves` requires matched data, tuning, and evaluation.
- `generalizes` requires an appropriate family, scaffold, temporal, distribution, or external test.
- `novel` requires a declared comparison scope and defensible similarity criterion.

Never reconstruct missing splits, hyperparameters, seeds, preprocessing, or training stages from convention.

## Completion Status

Use `complete` only when the paper, essential supplement, and conclusion-changing implementation evidence were accessible and the required audits were performed. Otherwise use `partial` and state once in the reading guide:

- unavailable artifacts;
- affected conclusions;
- confidence reduction;
- the smallest resolving action.

Repeat a gap later only when it changes the current judgment.
```

- [ ] **Step 3: Replace `ai-ml-reading-guide.md` with mentor-like reasoning**

Replace `skills/sci-read-paper/references/ai-ml-reading-guide.md` with exactly:

```markdown
# AI/ML Reading Guide

## Field Orientation

Before discussing the paper, explain only the domain context needed later:

1. What real scientific or engineering task is being solved?
2. Why does it matter, and what makes it difficult?
3. How do mainstream approaches usually frame it?
4. Which precise limitation creates the opening for this paper?

Distinguish field consensus from the authors' framing and from claims that still require verification. Do not turn this section into a broad literature review.

## Research Logic

Build one causal chain:

```text
task and stakes
→ prior approach
→ decisive limitation
→ unresolved gap
→ author hypothesis
→ design choice intended to address it
→ evidence
→ bounded contribution
```

Explain how each major design choice answers a named limitation. Separate a new capability from a new combination, dataset construction, engineering improvement, or evaluation change.

## Concrete Sample First

Start data, training, and model explanations from one concrete sample. Follow its semantic identity before listing aggregate statistics:

```text
raw sample
→ inclusion and label construction
→ preprocessing and representation
→ split membership and batch
→ model path
→ loss or decoding
→ prediction, generated object, or metric
```

After the sample is clear, add dataset origin/version, counts, deduplication, augmentation, split unit, leakage checks, objectives, optimization, schedules, seeds, hardware, precision, and checkpoint selection. Put exhaustive configuration and secondary paper-code differences in `appendices/data-training.md`.

Do not infer a library default without proving the released version used it and labeling the inference in the evidence ledger.

## Model Data Flow

Give one simplified Mermaid diagram when evidence supports explicit edges. Then record each main-path stage:

| Question | Record |
|---|---|
| What is it now? | semantic object and raw/encoded type |
| What is its shape? | tensor, sequence, graph, or batch shape |
| What happens? | operation and information gained or lost |
| Why is it needed? | connection to the author's hypothesis |
| Where does it go? | next module, fusion, decoder, or output |
| Can we verify it? | paper/code agreement, inference, missing detail, or conflict |

Explain intuition before equations. Define symbols and connect them to real objects immediately. Keep the main report on the primary path; place exhaustive interfaces, shapes, and code anchors in `appendices/model-dataflow.md`.

## Code Audit

Locate the actual data loader, split generator, model entry point, loss computation, training loop, evaluation command, and default configuration. Cite paths and commits in the evidence ledger. Distinguish executable paths from dead code, examples, or unused options.

## Experiment Reasoning

Organize experiments by research question rather than paper table order. Group baseline, control, ablation, robustness/generalization, case study, and external validation evidence around the claim being tested.

For each core question explain:

```text
what the authors want to prove
→ changed and controlled variables
→ data, split, metric, and result
→ what the evidence supports
→ what it does not establish
```

End a core experiment section with a compact judgment card:

```text
作者想证明：...
当前证据：...
我们的判断：...
```

Check baseline fairness, isolated ablations, uncertainty, seeds, confidence intervals, and whether analysis plots provide evidence or illustration. Store the exhaustive experiment inventory in `appendices/experiment-matrix.md`.
```

- [ ] **Step 4: Replace `output-contract.md` with the guided report contract**

Replace `skills/sci-read-paper/references/output-contract.md` with exactly:

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

`deep-reading.md` contains the complete research story and is the only file a normal reader must open. Appendices preserve exhaustive audit detail without copying it into the main narrative.

## Primary Report

Use exactly these top-level sections:

```markdown
# <论文标题>

## 阅读导航
## 1. 先把论文放回领域里
## 2. 三分钟看懂这篇论文
## 3. 作者是怎样一步步想到这个方法的
## 4. 数据与训练：跟踪一条样本
## 5. 模型：数据怎样一步步变成输出
## 6. 实验：每项实验究竟回答什么问题
## 7. 批判性审查：哪些结论可以相信
## 8. 最终带走什么
## 可选科研绘图 Briefs
```

### `阅读导航`

Keep this compact. Record `complete|partial`, recommended reading path, conclusion-changing source gaps, paper/code versions, and a one-sentence credibility judgment. Do not begin with an exhaustive source inventory.

### `1. 先把论文放回领域里`

In roughly 600–1000 Chinese characters, explain the real task, significance, difficulty, mainstream framing, and the paper's entry gap. Separate field consensus from author framing. Include only concepts used later.

### `2. 三分钟看懂这篇论文`

In roughly 900 Chinese characters, give the task, central tension, thought chain, minimal data flow, overall experimental verdict, and largest credibility risk. This section must stand alone but cannot replace the deep reading.

### Guided deep-reading sections

Develop every core section as:

```text
本节结论
→ 直观解释
→ 必要的技术展开
→ 这对论文结论意味着什么
```

Keep paragraphs to one main judgment and usually 3–5 sentences. Use Chinese-first prose. At first mention, add an English term only when needed for paper/code mapping; preserve proper names, metrics, identifiers, paths, and author-defined modules.

The data and model sections start from one concrete sample. The model section includes one simplified Mermaid data-flow diagram when supported. Mark inferred edges or shapes explicitly in prose.

Organize experiments by question, not table number. A core experiment may end with:

```text
作者想证明：...
当前证据：...
我们的判断：...
```

Rank critical-review issues as: core-conclusion threats, generalization/reproducibility limits, then secondary reporting issues. End by separating what can be believed, provisionally believed, not concluded, and the smallest decisive next experiment.

The final section answers only: the real contribution, the transferable idea, and the most important next experiment.

Use paragraph-level evidence IDs such as `〔E03〕` and `〔E12–E15〕`. Explicitly name paper report, code behavior, inference, missing information, or conflict when that status changes interpretation.

## Appendices

### `appendices/evidence-ledger.md`

Use columns: evidence ID, label, source, version/commit, locator, supported statement, and access status. This file owns the six evidence labels and complete locators.

### `appendices/data-training.md`

Record full provenance, construction, counts, splits, preprocessing, leakage checks, objectives, stages, hyperparameters, compute, checkpoint selection, and paper-code differences.

### `appendices/model-dataflow.md`

Record the concrete sample trace plus a table with stage, semantic object, shape, operation, output, code anchor, and evidence ID.

### `appendices/experiment-matrix.md`

Use columns: experiment ID, type, question/claim, changed variable, controls, data/split, metric, result, supported conclusion, unsupported conclusion, and evidence IDs.

### `appendices/critical-review.md`

Separate internal validity, reproducibility, domain validity, external checks, alternative explanations, applicability, and unresolved questions. Rank issues by effect on the central conclusion.

## Main/Appendix Boundary

The main report keeps background, causal reasoning, primary data flow, core experiment judgments, and conclusion-changing conflicts. Move exhaustive configurations, complete shape/interface inventories, secondary conflicts, all experiment rows, and full source locators to appendices.

Self-contained means the reader can understand the research story and judgments without opening appendices; it does not mean duplicating every audit entry.

## Optional Figure Handoff

Include at most three briefs, only when a visual materially improves understanding. Each brief contains purpose/reader, figure type, entities/relationships, evidence IDs, visual hierarchy, and content that must not be invented.

Do not generate images automatically. If `sci-ai-figure` is installed and the user explicitly asks for a figure, pass the brief as the handoff contract.
```

- [ ] **Step 5: Run focused GREEN and full structural validation**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_sci_read_paper.SkillContractTests.test_output_contract_has_guided_reading_layers \
  tests.test_sci_read_paper.SkillContractTests.test_skill_enforces_chinese_first_progressive_reading \
  tests.test_sci_read_paper.SkillContractTests.test_evidence_policy_supports_lightweight_ids \
  tests.test_sci_read_paper.SkillContractTests.test_ai_ml_guide_is_sample_and_question_driven -v
.venv/bin/python tests/test_sci_read_paper.py -v
.venv/bin/python /Users/yangguang/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sci-read-paper
git diff --check
```

Expected: focused four tests pass, all fourteen unit tests pass, validator prints `Skill is valid!`, and diff check is silent.

- [ ] **Step 6: Verify scope and commit**

Run:

```bash
git status --short
find skills/sci-read-paper -type f | sort
```

Expected: exactly the four planned skill files changed; the skill tree still contains exactly six authored files and four references.

Commit:

```bash
git add skills/sci-read-paper/SKILL.md \
  skills/sci-read-paper/references/evidence-policy.md \
  skills/sci-read-paper/references/ai-ml-reading-guide.md \
  skills/sci-read-paper/references/output-contract.md
git commit -m "feat: improve sci-read-paper reading flow"
```

---

### Task 3: Validate Readability on CProMG

**Files:**
- Modify: `tests/sci-read-paper/readability-findings.md`
- Modify only after an observed failure: the one owning skill/reference file identified by the failed criterion

**Interfaces:**
- Consumes: unchanged `cpromg-deep-read` prompt, the new skill, readability rubric, and scientific-depth rubric.
- Produces: a complete new CProMG dossier plus evidence that readability improved without sacrificing depth.

- [ ] **Step 1: Run one fresh CProMG evaluation**

Create a unique temporary output root with `mktemp -d`. Dispatch one fresh `fork_turns="none"` agent. Give it only:

- the unchanged `cpromg-deep-read` prompt from `evals.json`;
- the absolute path to `skills/sci-read-paper/` and the instruction to use it;
- the exact temporary output root as an operational destination;
- normal research tools.

Do not provide either rubric, current report, design, assertions, expected score, anticipated weaknesses, or SiamProm output. Preserve the complete dossier outside Git and hash all six Markdown files.

- [ ] **Step 2: Score readability and scientific depth independently**

Dispatch two fresh read-only reviewers:

1. Readability reviewer: receives only the new `deep-reading.md` and `readability-rubric.md`.
2. Scientific reviewer: receives the complete dossier, `rubric.md`, and the CProMG case assertions, but not the readability rubric or old scores.

Require concrete line citations for every score. Confirm:

- readability `>=14/16` and no zero;
- scientific depth `>=16/20` and no critical zero;
- all five CProMG assertions pass;
- no fabricated evidence;
- the primary report is understandable without appendices;
- Vina/QED/SA remain computational proxies;
- conclusion-changing paper-code conflicts remain visible.

- [ ] **Step 3: Make at most one evidence-driven wording change at a time**

If readability fails, map the criterion to its owner:

- background, sample-first, experiment narrative → `ai-ml-reading-guide.md`;
- headings, length, judgment cards, main/appendix boundary → `output-contract.md`;
- evidence interruption or hidden epistemic status → `evidence-policy.md`;
- global Chinese-first or progressive-flow compliance → `SKILL.md`.

Change only the owning file. Run all fourteen structural tests, then rerun CProMG in a fresh context. Do not add general prohibition lists or modify `bio-chem-validity.md`.

If scientific depth fails, restore the missing conclusion-changing content without copying exhaustive appendices into the main report. If no precise minimal change follows from the observed output, stop and report the evidence to the user.

- [ ] **Step 4: Record CProMG before/after evidence**

Append the fixed heading `## CProMG readability GREEN` to `tests/sci-read-paper/readability-findings.md`. Add:

- the evaluated skill commit;
- an eight-row table with columns `Readability criterion`, `Current output`, `New output`, and `New evidence`;
- the calculated before/after readability totals;
- the no-skill baseline, previous-skill, and readability-revision scientific-depth totals;
- `### Before/after excerpts` with `#### Opening and background`, `#### Model data flow`, and `#### Experiment and critical judgment` subsections;
- short current/new excerpts plus exact line citations under each subsection;
- `### Remaining limitations` containing only observed report or upstream-release limitations.

Do not commit the complete dossier.

- [ ] **Step 5: Run regression checks and commit CProMG evidence**

Run:

```bash
.venv/bin/python tests/test_sci_read_paper.py -v
.venv/bin/python /Users/yangguang/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sci-read-paper
git diff --check
```

Expected: fourteen tests pass, validator passes, and no whitespace errors.

Commit the evidence and any single-file evidence-driven correction:

```bash
git add tests/sci-read-paper/readability-findings.md skills/sci-read-paper
git commit -m "test: verify readable CProMG deep reading"
```

---

### Task 4: Regress SiamProm and Prepare User Preview

**Files:**
- Modify: `tests/sci-read-paper/readability-findings.md`
- Modify only after an observed failure: the one owning skill/reference file identified by the failed criterion

**Interfaces:**
- Consumes: unchanged `siamprom-deep-read` prompt and the CProMG-validated skill.
- Produces: cross-domain readability evidence, preserved scientific criticism, and directly viewable preview files outside Git.

- [ ] **Step 1: Run one fresh SiamProm evaluation**

Create a new unique temporary output root. Dispatch one fresh `fork_turns="none"` agent with only the unchanged SiamProm prompt, the skill path/instruction, the output root, and normal research tools. Do not expose rubrics, previous reports, assertions, expected HIP1 finding, or CProMG output.

Preserve and hash the six-file dossier outside Git.

- [ ] **Step 2: Score both contracts and fixture assertions**

Use separate fresh readability and scientific reviewers as in Task 3. Confirm:

- readability `>=14/16`, no zero;
- scientific depth `>=16/20`, no critical zero;
- all five SiamProm assertions pass;
- negative-sample construction remains the central methodological issue;
- phantom sampling and contrastive learning remain causally connected;
- promoter, negative, pair, and classifier labels remain traceable;
- the external finding that `GCGATCGC` is known HIP1 remains present and calibrated;
- conclusion-changing paper-code conflicts remain traceable;
- no fabricated evidence.

- [ ] **Step 3: Apply only a measured cross-paper correction if needed**

If SiamProm fails while CProMG passed, identify whether the template is overfit to molecular generation. Change only the owning file, preserve CProMG requirements, rerun all structural tests, then rerun both SiamProm and a focused CProMG readability regression in fresh contexts.

If no precise correction follows from evidence, stop and present the limitation rather than broadening the skill speculatively.

- [ ] **Step 4: Record SiamProm evidence and preview paths**

Append `## SiamProm readability regression`. Record the calculated before/after readability totals, previous-skill and readability-revision scientific-depth totals, and the number of assertions passed out of five. Under `### Preserved critical findings`, cite a short excerpt and exact line for negative-sample construction, phantom/contrastive logic, label and gradient flow, the HIP1 external correction, and the reproducibility boundary. Under `### Preview`, record the absolute temporary paths of both complete dossiers. Record SHA-256 for all twelve Markdown files in the task report.

- [ ] **Step 5: Run the complete final audit**

Run:

```bash
.venv/bin/python tests/test_sci_read_paper.py -v
.venv/bin/python /Users/yangguang/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sci-read-paper
git diff --check
rg -n 'TBD|TODO|FIXME|PLACEHOLDER|待定' skills tests
wc -w skills/sci-read-paper/SKILL.md
find skills/sci-read-paper -type f | sort
git status --short --branch
```

Expected:

- all fourteen unit tests pass;
- validator prints `Skill is valid!`;
- diff check is silent;
- placeholder scan has no matches;
- `SKILL.md` body remains under 500 words;
- exactly six authored skill files and four references remain;
- no raw dossier, transcript, cache, or generated figure is tracked.

- [ ] **Step 6: Commit final evidence**

Commit:

```bash
git add tests/sci-read-paper/readability-findings.md skills/sci-read-paper
git commit -m "test: verify sci-read-paper readability regression"
```

If Task 4 required no skill correction after Task 3, the commit contains only the final evidence file.

- [ ] **Step 7: Stop for user preview**

Report clickable paths to both new `deep-reading.md` files and their appendices, plus:

- current/new opening comparison;
- current/new model-flow comparison;
- current/new experiment/critique comparison;
- both readability scores;
- both scientific-depth scores;
- remaining upstream and evaluation limitations;
- exact commit history.

Do not merge, install globally, publish, push, remove the worktree, or begin `sci-ai-figure` before the user reviews the new reports.
