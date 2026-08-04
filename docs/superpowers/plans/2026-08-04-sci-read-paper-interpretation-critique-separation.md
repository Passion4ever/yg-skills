# Interpretation/Critique Separation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let readers understand the authors through Sections 1–6, concentrate reviewer-mode criticism in Section 7, and synthesize method value versus evidential confidence in Section 8.

**Architecture:** Preserve the existing report headings and two-mode file contract. Add a neutral `证据边界` handoff before Section 7, replace experiment verdict cards with descriptive evidence cards, and define a concentrated review-card schema in Section 7. Validate structurally and show a hand-written before/after preview from the existing SiamProm report without rerunning research.

**Tech Stack:** Markdown Agent Skill, Python `unittest`, Git.

## Global Constraints

- Follow `docs/superpowers/specs/2026-08-04-sci-read-paper-interpretation-critique-separation-design.md`.
- Do not reduce critical depth or hide conclusion-changing conflicts.
- Do not add output files or change standard/audit mode.
- Do not modify `bio-chem-validity.md`, triggers, source limits, `partial`, evidence labels, or figure handoff.
- Do not rerun SiamProm retrieval or generation.

---

### Task 1: Add RED Narrative-Boundary Tests

**Files:**
- Modify: `tests/test_sci_read_paper.py`

- [ ] Add `test_output_contract_separates_interpretation_and_critique`.

The test must isolate the experiment template and assert it contains `作者要回答`, `实验怎么做`, `观察到什么`, and `证据边界`, but not `我们的判断`. It must also require the three-phase sequence, neutral boundary handoff, all six Section 7 review-card fields, and both Section 8 subsection names.

- [ ] Run the focused test.

Expected: FAIL because the current experiment template still contains `我们的判断` and lacks the new review schema.

- [ ] Commit.

```bash
git add tests/test_sci_read_paper.py
git commit -m "test: define interpretation critique boundary"
```

---

### Task 2: Implement Soft Separation

**Files:**
- Modify: `skills/sci-read-paper/SKILL.md`
- Modify: `skills/sci-read-paper/references/output-contract.md`
- Modify: `skills/sci-read-paper/references/evidence-policy.md`
- Modify: `skills/sci-read-paper/references/ai-ml-reading-guide.md`
- Do not modify: `skills/sci-read-paper/references/bio-chem-validity.md`

- [ ] In `SKILL.md`, state the narrative order `understand authors → review authors → synthesize`, require neutral early conflict boundaries, and concentrate severity/alternatives/verdicts in Section 7.

- [ ] In `output-contract.md`, update the reading guide, three-minute map, Sections 3–6, experiment template, Section 7 review-card schema, and Section 8 two-part synthesis exactly as the design specifies.

- [ ] In `evidence-policy.md`, require early conflicts to state paper/code facts neutrally and defer impact ranking to Section 7 without hiding the conflict.

- [ ] In `ai-ml-reading-guide.md`, make research logic author-perspective first and replace the experiment judgment card with the descriptive evidence-boundary card.

- [ ] Run the focused test and full suite.

```bash
.venv/bin/python tests/test_sci_read_paper.py -v
.venv/bin/python /Users/yangguang/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sci-read-paper
git diff --check
git diff -- skills/sci-read-paper/references/bio-chem-validity.md
```

Expected: 19 tests pass, validator passes, diff checks are clean, and `bio-chem-validity.md` is unchanged.

- [ ] Commit.

```bash
git add skills/sci-read-paper tests/test_sci_read_paper.py
git commit -m "feat: separate paper interpretation from critique"
```

---

### Task 3: Produce a Visible Before/After Preview

**Files:**
- Create: `tests/sci-read-paper/interpretation-critique-preview.md`

- [ ] Use the existing SiamProm report only. Create three current/new comparisons: three-minute map, one experiment, and Section 7 transition.

- [ ] The rewritten excerpts must preserve the same evidence IDs and scientific facts, remove developed verdicts from Sections 2/6, and concentrate them in the Section 7 review card.

- [ ] Record that this is a contract preview, not a regenerated behavioral output.

- [ ] Run final tests, validator, placeholder scan, diff check, file-count check, and repository-status check.

- [ ] Commit.

```bash
git add tests/sci-read-paper/interpretation-critique-preview.md
git commit -m "docs: preview interpretation critique separation"
```

- [ ] Report the preview path, changed contract, verification, commits, and remaining limitation that the preview is not a fresh behavioral run.
