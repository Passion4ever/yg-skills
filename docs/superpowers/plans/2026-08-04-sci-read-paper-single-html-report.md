# SCI Read Paper Single-File HTML Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the multi-Markdown `sci-read-paper` deliverable with one polished, offline, self-contained HTML report that implements the approved eight-section expert reading path.

**Architecture:** The skill contract defines one standard or audit HTML artifact. A reusable semantic HTML/CSS asset provides stable publication-style UI, while the report content embeds the evidence ledger and optional audit panels in the same document. Contract tests protect file count, section responsibilities, self-containment, anchor integrity, accessibility, and the complete SiamProm showcase.

**Tech Stack:** Markdown skill instructions, semantic HTML5, inline CSS, optional minimal inline JavaScript, inline SVG, Python `unittest` and standard-library `html.parser`, `tidy` for local diagnostics, Chromium headless screenshots for visual inspection.

## Global Constraints

- Standard output is exactly `<paper-slug>.html`; audit output is exactly `<paper-slug>-audit.html`.
- The final report must work offline without external CSS, fonts, scripts, Mermaid, MathJax, or non-data-URI images.
- Use the eight approved Chinese section titles in exact order; no standalone `阅读导航` section.
- Sections 1–6 explain authors, Section 7 reviews evidence, and Section 8 synthesizes; conclusion-changing facts remain visible early as neutral boundaries.
- The UI is a scholarly publication-style long-read, not a dashboard: 240–280 px desktop navigation, 820–900 px text column, responsive single-column mode below about 900 px, and print CSS.
- Preserve Chinese-first prose, lightweight evidence IDs, all six evidence labels, standard/audit research bounds, code auditing, and bio/chem validity requirements.
- Do not rerun SiamProm paper retrieval; reuse the committed report and evidence ledger as scientific source material.
- Use `apply_patch` for repository edits and commit each independently reviewable task.

---

### Task 1: Define the Single-HTML Contract in Failing Tests

**Files:**
- Modify: `tests/test_sci_read_paper.py`
- Test: `tests/test_sci_read_paper.py`

**Interfaces:**
- Consumes: current `SKILL.md`, output contract, evals, and Markdown showcase.
- Produces: test contracts for `skills/sci-read-paper/assets/report-template.html` and `tests/sci-read-paper/outputs/siamprom-cyanobacteria-promoters.html`.

- [ ] **Step 1: Replace multi-file output assertions with literal single-file expectations**

Add constants:

```python
HTML_TEMPLATE = SKILL_DIR / "assets" / "report-template.html"
SIAMPROM_HTML = ROOT / "tests" / "sci-read-paper" / "outputs" / "siamprom-cyanobacteria-promoters.html"
```

Replace standard/audit tree expectations with:

```python
self.assertEqual(html_paths, ["<paper-slug>.html"])
self.assertEqual(audit_html_paths, ["<paper-slug>-audit.html"])
self.assertNotIn("deep-reading.md", standard)
self.assertNotIn("evidence-ledger.md", standard)
```

- [ ] **Step 2: Assert the exact eight-section reading path and absence of a reading-guide section**

Use these literals:

```python
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
```

Assert every title occurs in order in the contract and `## 阅读导航` does not occur in the primary structure.

- [ ] **Step 3: Add template UI/self-containment assertions**

Test that `report-template.html` contains `<!doctype html>`, `header`, `nav`, `main`, `footer`, `--paper`, `position: sticky`, `@media (max-width: 900px)`, `@media print`, `prefers-reduced-motion`, `details`, `summary`, `evidence-boundary`, and `review-card`. Reject `<link rel="stylesheet"`, `<script src=`, `@import`, and `<img src="http`.

- [ ] **Step 4: Add showcase structure and evidence-link integrity checks**

Parse the final SiamProm HTML with a small `HTMLParser` subclass that records IDs and internal `href="#..."` targets. Assert:

```python
self.assertEqual(section_ids, [f"section-{i}" for i in range(1, 9)])
self.assertTrue(internal_targets <= ids)
self.assertIn("evidence-ledger", ids)
self.assertIn("E01", ids)
self.assertIn("E24", ids)
```

Also assert the known task distinction: promoter/non-promoter is the prediction target and TSS is the sampling anchor.

- [ ] **Step 5: Run focused tests and verify RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_sci_read_paper.SkillContractTests.test_standard_mode_has_one_html_output \
  tests.test_sci_read_paper.SkillContractTests.test_report_template_is_self_contained_and_polished \
  tests.test_sci_read_paper.SkillContractTests.test_siamprom_showcase_has_complete_internal_links -v
```

Expected: FAIL because the template and HTML showcase do not exist and the current contract still declares Markdown outputs.

- [ ] **Step 6: Commit the RED contract**

```bash
git add tests/test_sci_read_paper.py
git commit -m "test: define single HTML paper report"
```

---

### Task 2: Add the Polished HTML Template and Output Contract

**Files:**
- Create: `skills/sci-read-paper/assets/report-template.html`
- Modify: `skills/sci-read-paper/SKILL.md`
- Modify: `skills/sci-read-paper/references/output-contract.md`
- Test: `tests/test_sci_read_paper.py`

**Interfaces:**
- Consumes: exact titles and HTML constraints from Task 1.
- Produces: a reusable template with placeholders `{{PAPER_TITLE}}`, `{{REPORT_META}}`, `{{SUMMARY_CARDS}}`, `{{REPORT_BODY}}`, `{{FIGURE_BRIEFS}}`, `{{AUDIT_PANELS}}`, and `{{EVIDENCE_LEDGER}}`.

- [ ] **Step 1: Create a valid semantic template shell**

The template must contain this structural contract:

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{PAPER_TITLE}}</title>
  <style>/* all UI tokens and responsive/print CSS inline */</style>
</head>
<body>
  <header class="paper-hero">{{REPORT_META}}{{SUMMARY_CARDS}}</header>
  <div class="page-shell">
    <nav class="toc" aria-label="论文精读目录">...</nav>
    <main id="main-content">{{REPORT_BODY}}{{FIGURE_BRIEFS}}{{AUDIT_PANELS}}</main>
  </div>
  <footer>{{EVIDENCE_LEDGER}}</footer>
</body>
</html>
```

- [ ] **Step 2: Implement the publication-style component system**

Define CSS tokens for paper/background/text/muted/accent/warning/danger colors, serif/sans/mono stacks, spacing, radii, and shadows. Add styles for hero metadata, three summary cards, sticky numbered TOC, readable prose, evidence badges, evidence boundaries, experiment cards, review cards, graded conclusions, code/formula blocks, responsive tables, focus states, `prefers-reduced-motion`, narrow-screen layout, and print layout.

- [ ] **Step 3: Rewrite the output contract around one HTML artifact**

Replace Markdown output trees and appendix files with the standard/audit HTML names. Specify semantic structure, top cards, internal evidence links, embedded ledger, audit-only panels, offline rules, HTML escaping, print behavior, and optional base64 figure embedding.

- [ ] **Step 4: Compact `SKILL.md` without exceeding 500 body words**

Change the workflow/output language to one selected HTML artifact and link to the template through the output contract. Preserve standard/audit selection, Chinese-first prose, evidence collection, concrete-sample tracing, and figure explicit-request behavior.

- [ ] **Step 5: Run focused tests and verify template/contract GREEN**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_sci_read_paper.SkillContractTests.test_standard_mode_has_one_html_output \
  tests.test_sci_read_paper.SkillContractTests.test_audit_mode_has_one_html_output \
  tests.test_sci_read_paper.SkillContractTests.test_report_template_is_self_contained_and_polished \
  tests.test_sci_read_paper.SkillContractTests.test_output_contract_has_guided_reading_layers -v
```

Expected: PASS. Also run `tail -n +6 skills/sci-read-paper/SKILL.md | wc -w`; expected `<= 500`.

- [ ] **Step 6: Commit template and contract**

```bash
git add skills/sci-read-paper/SKILL.md skills/sci-read-paper/assets/report-template.html skills/sci-read-paper/references/output-contract.md
git commit -m "feat: add single-file HTML report contract"
```

---

### Task 3: Align Reading, Evidence, Evals, and Rubrics

**Files:**
- Modify: `skills/sci-read-paper/references/ai-ml-reading-guide.md`
- Modify: `skills/sci-read-paper/references/evidence-policy.md`
- Modify: `tests/sci-read-paper/evals.json`
- Modify: `tests/sci-read-paper/rubric.md`
- Modify: `tests/sci-read-paper/readability-rubric.md`
- Test: `tests/test_sci_read_paper.py`

**Interfaces:**
- Consumes: eight-section responsibilities and embedded-ledger contract from Task 2.
- Produces: behavioral instructions and evaluation criteria that prevent section overlap and weak HTML delivery.

- [ ] **Step 1: Encode every section's role and adjacent boundary**

Update the guide to require background → progress → gap → author entry in Section 1; map-only behavior in Section 2; reconstructed rather than mind-read design logic in Section 3; model-entry boundary between Sections 4/5; observation/author-interpretation separation in Section 6; ranked claim calibration in Section 7; and contribution/verdict/next-step synthesis in Section 8.

- [ ] **Step 2: Move ledger rules into one-file internal anchors**

Require every main-report `〔E…〕` link to resolve to a unique embedded ledger row; retain label, source, version/commit, locator, supported statement, and access status. Preserve neutral early facts and concentrated Section 7 impact judgments.

- [ ] **Step 3: Update eval assertions and rubrics**

Add positive assertions for one offline HTML, exact section responsibilities, polished readable UI, embedded evidence, and no second required file. Add rubric criteria for literal task definition, causal background, experiment typing, claim calibration, and internal citation resolution.

- [ ] **Step 4: Run all contract tests**

Run:

```bash
.venv/bin/python tests/test_sci_read_paper.py -v
```

Expected: all tests except the not-yet-created SiamProm showcase test pass.

- [ ] **Step 5: Commit reading/evidence behavior**

```bash
git add skills/sci-read-paper/references/ai-ml-reading-guide.md skills/sci-read-paper/references/evidence-policy.md tests/sci-read-paper/evals.json tests/sci-read-paper/rubric.md tests/sci-read-paper/readability-rubric.md tests/test_sci_read_paper.py
git commit -m "feat: align expert reading with HTML report"
```

---

### Task 4: Build the Complete SiamProm HTML Showcase

**Files:**
- Create: `tests/sci-read-paper/outputs/siamprom-cyanobacteria-promoters.html`
- Delete after parity checks: `tests/sci-read-paper/outputs/siamprom-cyanobacteria-promoters/deep-reading.md`
- Delete after parity checks: `tests/sci-read-paper/outputs/siamprom-cyanobacteria-promoters/evidence-ledger.md`
- Test: `tests/test_sci_read_paper.py`

**Interfaces:**
- Consumes: committed Markdown report/ledger at `3737991` and template from Task 2.
- Produces: one polished standard-mode HTML with Sections 1–8 and evidence IDs E01–E24.

- [ ] **Step 1: Rewrite the narrative headings and section boundaries before conversion**

Use the approved titles. Rework Section 1 into background → existing progress → decisive limitation → author entry. Add the reconstruction disclaimer to Section 3. Keep one sample continuous through Sections 4/5. Add experiment type and author interpretation to every Section 6 card. Add missing-evidence and impact fields to Section 7 cards. Split Section 8 into contribution, calibrated verdict, and decisive next step.

- [ ] **Step 2: Assemble the semantic HTML using the template UI**

Populate the hero metadata, status badges, author-mainline/evidence-status/review-entry cards, exact eight sections, inline SVG data flow, collapsible figure brief, report/version details, and embedded evidence ledger. Make every `〔E…〕` citation an internal anchor and give ledger entries `id="E01"` through `id="E24"`.

- [ ] **Step 3: Run structural and content tests before deleting Markdown**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_sci_read_paper.SkillContractTests.test_siamprom_showcase_has_complete_internal_links \
  tests.test_sci_read_paper.SkillContractTests.test_siamprom_showcase_preserves_scientific_depth -v
tidy -qe tests/sci-read-paper/outputs/siamprom-cyanobacteria-promoters.html
```

Expected: tests PASS. `tidy` may report HTML5 element warnings depending on local version, but must report no unclosed, duplicate-ID, or malformed-table errors.

- [ ] **Step 4: Capture and inspect desktop and mobile screenshots**

Run Chromium headless at `1440x1200` and `390x844` against the local `file://` URL. Inspect both images for title hierarchy, readable line length, card spacing, TOC behavior, table overflow, and evidence/review contrast. Fix CSS in the reusable template and showcase together if a visual defect is found.

- [ ] **Step 5: Remove superseded Markdown artifacts**

Use `apply_patch` to delete the two Markdown showcase files only after the HTML contains all E01–E24 rows, all eight sections, the model flow, five experiment questions, six critical issues, and the final synthesis. Git history remains the recovery path.

- [ ] **Step 6: Re-run showcase and full tests**

```bash
.venv/bin/python tests/test_sci_read_paper.py -v
.venv/bin/python /Users/yangguang/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sci-read-paper
git diff --check
```

Expected: all tests pass, validator reports `Skill is valid!`, and diff check is clean.

- [ ] **Step 7: Commit the complete visible result**

```bash
git add tests/sci-read-paper/outputs/siamprom-cyanobacteria-promoters.html tests/sci-read-paper/outputs/siamprom-cyanobacteria-promoters/deep-reading.md tests/sci-read-paper/outputs/siamprom-cyanobacteria-promoters/evidence-ledger.md skills/sci-read-paper/assets/report-template.html
git commit -m "docs: publish complete SiamProm HTML reading"
```

---

### Task 5: Final Regression, Diff Audit, and Handoff

**Files:**
- Verify all files changed in Tasks 1–4.
- Update only if verification exposes a defect.

**Interfaces:**
- Consumes: completed single-HTML skill and showcase.
- Produces: a clean feature branch with verified files and a direct user-visible HTML result.

- [ ] **Step 1: Run final verification from a clean command invocation**

```bash
.venv/bin/python tests/test_sci_read_paper.py -v
.venv/bin/python /Users/yangguang/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sci-read-paper
tidy -qe tests/sci-read-paper/outputs/siamprom-cyanobacteria-promoters.html
git diff --check
git status --short
```

Expected: all unit tests pass, skill validator passes, HTML has no structural errors, diff check is clean, and the worktree has no uncommitted changes.

- [ ] **Step 2: Audit requirements line by line**

Confirm: one output file per mode; eight exact titles; no reading-guide section; polished offline UI; responsive/print CSS; evidence anchors; Sections 1–6/7/8 boundary; task/label/proxy separation; standard/audit bounds; explicit-only figure handoff; complete SiamProm scientific content.

- [ ] **Step 3: Report the result**

Provide a clickable absolute path to `siamprom-cyanobacteria-promoters.html`, the final commit hash, exact test count, validator result, and whether the feature remains in the worktree/branch without merge or installation.
