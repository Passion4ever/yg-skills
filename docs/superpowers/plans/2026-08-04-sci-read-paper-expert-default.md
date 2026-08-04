# `sci-read-paper` Expert-Default Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make expert-style two-file paper reading the default while preserving the six-file dossier as an explicit audit mode.

**Architecture:** `SKILL.md` selects `standard` or `audit` before retrieval. `output-contract.md` defines the two shapes; `evidence-policy.md` and `ai-ml-reading-guide.md` bound standard-mode research. Structural RED/GREEN tests protect the boundary, followed by exactly one fresh SiamProm behavior trial.

**Tech Stack:** Markdown Agent Skill, Python `unittest`, YAML/JSON fixtures, Git, one Codex forward-test agent.

## Global Constraints

- Follow `docs/superpowers/specs/2026-08-04-sci-read-paper-expert-default-design.md`.
- Optimize for expert understanding, not abstract summarization, field extraction, or exhaustive inventory.
- Standard mode requires `deep-reading.md` and `evidence-ledger.md`; it may add at most one targeted appendix.
- Audit mode preserves all six dossier files.
- Preserve the eight-section Chinese-first narrative, causal thought chain, concrete sample, question-driven experiments, and critical review.
- Standard mode checks at most three conclusion-critical claim families and only the shortest conclusion-relevant code path.
- Preserve the existing uncommitted motif/sequence novelty rule.
- Do not change `bio-chem-validity.md`, trigger boundaries, `partial`, pause rules, evidence labels, or explicit-only `sci-ai-figure` handoff.
- Run the unchanged SiamProm request once. Do not regenerate to improve output.
- Keep generated dossiers outside Git.

---

### Task 1: Define the Two-Mode Contract with RED Tests

**Files:**
- Modify: `tests/test_sci_read_paper.py`

**Interfaces:**
- Consumes: current six-file-only contract.
- Produces: four failing tests for the standard/audit boundary.

- [ ] **Step 1: Add four contract tests**

Add these methods to `SkillContractTests`:

```python
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
```

- [ ] **Step 2: Verify RED**

Run the four named tests with `.venv/bin/python -m unittest ... -v`.

Expected: four assertion failures caused by missing mode contracts, with no syntax or import error.

- [ ] **Step 3: Record the observed behavioral RED**

Write `.superpowers/sdd/expert-default-red.md` with the already observed facts: current six-file default, two CProMG zero-output stalls, a six-file SiamProm default result, an 18-minute zero-byte rerun, and the user's report that ordinary reading felt over-complex.

- [ ] **Step 4: Commit**

```bash
git add tests/test_sci_read_paper.py
git commit -m "test: define expert-default paper reading"
```

---

### Task 2: Implement Standard and Audit Modes

**Files:**
- Modify: `skills/sci-read-paper/SKILL.md`
- Modify: `skills/sci-read-paper/references/output-contract.md`
- Modify: `skills/sci-read-paper/references/evidence-policy.md`
- Modify: `skills/sci-read-paper/references/ai-ml-reading-guide.md`
- Do not modify: `skills/sci-read-paper/references/bio-chem-validity.md`

**Interfaces:**
- Consumes: Task 1 RED tests and the approved design.
- Produces: bounded standard mode and full explicit audit mode.

- [ ] **Step 1: Select mode first in `SKILL.md`**

Make `standard` the default. Select `audit` only for explicit exhaustive audit, reproduction preparation, full experiment matrix, or file-by-file code comparison. In standard mode, write the main report and ledger before optional corroboration; permit one targeted appendix only for a central conflict. In audit mode, produce all six files. Preserve expert-reading gates and `partial` behavior.

- [ ] **Step 2: Define both shapes in `output-contract.md`**

Add `## Standard Mode — Default` with root-level `deep-reading.md` and `evidence-ledger.md`, and `## Audit Mode — Explicit` with the four audit appendices. State that standard mode does not require them. Keep the eight main headings and require the reading guide to record `mode: standard|audit` and `complete|partial`.

- [ ] **Step 3: Bound evidence in `evidence-policy.md`**

Add a standard-mode boundary of at most three conclusion-critical claim families. Resolve selected checks, then mark additional checks unresolved and offer audit instead of extending retrieval. Preserve the motif/sequence novelty rule exactly. Judge `complete` against the selected mode.

- [ ] **Step 4: Bound code inspection in `ai-ml-reading-guide.md`**

Standard mode follows the shortest conclusion-relevant path through dataset construction/loading, split logic, model entry/primary `forward`, loss/training, evaluation entry, and active configuration. It does not download weights, inspect every utility, enumerate every setting, or reconstruct secondary experiments unless central interpretation depends on it. Audit mode expands to the full inventory.

- [ ] **Step 5: Verify GREEN and regressions**

Run:

```bash
.venv/bin/python tests/test_sci_read_paper.py -v
.venv/bin/python /Users/yangguang/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sci-read-paper
git diff --check
git diff -- skills/sci-read-paper/references/bio-chem-validity.md
find skills/sci-read-paper -type f | sort
```

Expected: eighteen tests pass, validator prints `Skill is valid!`, diff checks are clean, `bio-chem-validity.md` is unchanged, and the skill still has six authored files/four references.

- [ ] **Step 6: Commit**

```bash
git add skills/sci-read-paper/SKILL.md skills/sci-read-paper/references/output-contract.md
git add skills/sci-read-paper/references/evidence-policy.md skills/sci-read-paper/references/ai-ml-reading-guide.md
git commit -m "feat: default to expert paper reading"
```

---

### Task 3: Run One Normal SiamProm Trial

**Files:**
- Create: `tests/sci-read-paper/expert-default-findings.md`
- Do not commit: raw generated dossier.

**Interfaces:**
- Consumes: unchanged `siamprom-deep-read` prompt and implemented skill.
- Produces: one standard-mode dossier and factual evidence of its behavior.

- [ ] **Step 1: Create trial state**

Create a unique `/tmp/sci-read-paper-expert-default-siamprom.XXXXXX` root and record `date +%s` plus the root in `.superpowers/sdd/expert-default-trial-state.md`.

- [ ] **Step 2: Dispatch exactly one fresh evaluation**

Give a fresh agent only the unchanged SiamProm prompt, absolute skill path, output root, and normal research tools. Do not provide rubrics, expected HIP1 wording, assertions, previous outputs, design, scores, or retry instructions. Do not rerun a weak result.

- [ ] **Step 3: Inspect observed output**

Record end epoch, elapsed seconds, Markdown file paths/count, line counts, reported mode/status, and any optional appendix. Read the main report and ledger directly.

- [ ] **Step 4: Write `expert-default-findings.md`**

Record date, implementation commit, unchanged prompt ID, output root, elapsed time, mode/status, and files. Add a table with PASS/FAIL plus exact line citations for: field background, author reasoning, concrete sample/data flow, question-driven experiments, and critical conclusions. Separately record negative-sample construction, phantom-plus-contrastive logic, label/gradient flow, motif identity calibration, paper-code conflicts, and observed limitations. Never use placeholders or prescribe a retry.

- [ ] **Step 5: Run final verification**

```bash
.venv/bin/python tests/test_sci_read_paper.py -v
.venv/bin/python /Users/yangguang/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sci-read-paper
git diff --check
rg -n 'TBD|TODO|FIXME|PLACEHOLDER|<line citations>|<seconds>' skills tests/sci-read-paper/expert-default-findings.md
find skills/sci-read-paper -type f | sort
git status --short --branch
```

Expected: eighteen tests and validator pass; no placeholders, generated dossier, or unexpected skill file is tracked.

- [ ] **Step 6: Commit evidence**

```bash
git add tests/sci-read-paper/expert-default-findings.md
git commit -m "test: exercise expert-default paper reading"
```

- [ ] **Step 7: Give the user the result**

Report clickable main/ledger paths, elapsed time, file count, expert-understanding checks, scientific findings, exact commits, and observed limitations. Do not merge, install, push, remove the worktree, or start `sci-ai-figure`.
