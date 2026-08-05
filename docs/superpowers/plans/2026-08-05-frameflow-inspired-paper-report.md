# FrameFlow-Inspired Paper Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the desktop paper report from centered section cards into a FrameFlow-inspired technical monograph with a fixed dark sidebar, compact bilingual hero, continuous chapters, and semantic callouts only.

**Architecture:** Preserve the one-file HTML and eight-section evidence contract while replacing the page shell. A fixed grouped sidebar sits outside a bounded `content-shell`; header, report, figure brief, provenance, and ledger share that content axis. Regression tests inspect both the reusable template and committed SiamProm showcase before visual verification in Chromium.

**Tech Stack:** HTML5, inline CSS, Python `unittest`/`HTMLParser`, HTML Tidy, headless Chromium.

## Global Constraints

- Desktop is the acceptance target; keep only a basic narrow-screen fallback and do not add a mobile navigation drawer.
- Sidebar is fixed, dark `#1a1a2e`, and exactly `280px` on desktop.
- Use local system font stacks only; no Google Fonts, Three.js, Molstar, external stylesheet, script, iframe, or network image.
- Preserve one offline HTML file, Sections 1–8, E01–E24, standard/audit naming, print behavior, and all scientific wording.
- Whole chapters are continuous prose; cards remain only for experiment, evidence, review, takeaway, flow, table, code, and formula components.
- The template and committed SiamProm showcase must change together.

---

### Task 1: Define the FrameFlow-Inspired Contract in Tests

**Files:**
- Modify: `tests/test_sci_read_paper.py`

**Interfaces:**
- Consumes: `HTML_TEMPLATE`, `SIAMPROM_HTML`, `extract_css_rule()`, and `DocumentIndex`.
- Produces: `assert_frameflow_inspired_layout()`, an updated template layout test, and an updated showcase layout test.

- [ ] **Step 1: Replace the obsolete compact-rail helper**

Replace `assert_compact_reading_layout()` with assertions against observable template/showcase structure:

```python
def assert_frameflow_inspired_layout(testcase: unittest.TestCase, text: str):
    sidebar_rule = extract_css_rule(text, ".sidebar")
    content_rule = extract_css_rule(text, ".content-shell")
    chapter_rule = extract_css_rule(text, "main > section.report-section")
    for declaration in (
        "width: 280px",
        "position: fixed",
        "background: var(--nav)",
    ):
        testcase.assertIn(declaration, sidebar_rule)
    testcase.assertIn("margin-left: 280px", content_rule)
    testcase.assertIn("max-width: 980px", content_rule)
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
```

Update the two existing test methods to call the renamed helper. Add showcase-only assertions for the display title, full original subtitle, and sequential chapter labels:

```python
self.assertIn('<h1 class="paper-title">SiamProm 深度精读</h1>', text)
self.assertIn('<p class="paper-subtitle">Recognition of cyanobacteria promoters', text)
self.assertEqual(
    re.findall(r'<p class="chapter-label">CHAPTER (\d\d)</p>', text),
    [f"{index:02d}" for index in range(1, 9)],
)
```

- [ ] **Step 2: Run the two layout tests and verify RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_sci_read_paper.SkillContractTests.test_report_template_uses_compact_reading_layout \
  tests.test_sci_read_paper.SkillContractTests.test_siamprom_showcase_uses_compact_reading_layout -v
```

Expected: both fail because `.sidebar` and `.content-shell` do not exist and the old summary cards remain.

- [ ] **Step 3: Commit the RED contract**

```bash
git add tests/test_sci_read_paper.py
git commit -m "test: define monograph paper report layout"
```

### Task 2: Implement the Reusable Monograph Template

**Files:**
- Modify: `skills/sci-read-paper/assets/report-template.html`
- Modify: `skills/sci-read-paper/references/output-contract.md`
- Test: `tests/test_sci_read_paper.py`

**Interfaces:**
- Consumes: the layout structure and CSS contracts from Task 1.
- Produces: `{{DISPLAY_TITLE}}`, `{{PAPER_SUBTITLE}}`, `{{SUMMARY_ROWS}}`, `.sidebar`, `.content-shell`, `.quick-view`, `.chapter-label`, and `.chapter-intro` template interfaces.

- [ ] **Step 1: Replace the layout tokens and primary shell**

Define the restrained local palette and desktop shell:

```css
:root {
  --paper: #fafaf8;
  --paper-strong: #ffffff;
  --ink: #2c2c2c;
  --muted: #6b6b6b;
  --line: #e2e0d8;
  --accent: #4a6fa5;
  --accent-soft: #e8eef6;
  --nav: #1a1a2e;
}
.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  width: 280px;
  overflow-y: auto;
  background: var(--nav);
}
.content-shell {
  margin-left: 280px;
  max-width: 980px;
  padding: 48px 56px 120px;
}
main > section.report-section {
  margin: 0 0 72px;
  padding: 0;
  background: transparent;
  border: 0;
  border-radius: 0;
  box-shadow: none;
}
```

Remove the old `.page-shell`, `.toc`, `.summary-grid`, `.summary-card`, and broad `.report-section` container rules. Keep semantic component styles and scope them independently.

- [ ] **Step 2: Replace the template body structure**

Use one fixed sidebar followed by one content shell:

```html
<nav class="sidebar" aria-label="论文精读目录">
  <div class="sidebar-header">
    <strong>{{DISPLAY_TITLE}}</strong>
    <span>{{SIDEBAR_SUBTITLE}}</span>
  </div>
  <!-- five grouped link blocks covering section-1..8, report-info, evidence-ledger -->
</nav>
<div class="content-shell">
  <header class="paper-hero">
    <p class="eyebrow">SCI · DEEP READING</p>
    <h1 class="paper-title">{{DISPLAY_TITLE}}</h1>
    <p class="paper-subtitle">{{PAPER_SUBTITLE}}</p>
    <div class="paper-meta">{{REPORT_META}}</div>
    <section class="quick-view" aria-labelledby="quick-view-title">
      <h2 id="quick-view-title">论文速览</h2>
      {{SUMMARY_ROWS}}
    </section>
  </header>
  <main id="main-content">{{REPORT_BODY}}...</main>
  <footer>...provenance and ledger...</footer>
</div>
```

Keep basic `@media (max-width: 900px)` fallback rules that hide the fixed sidebar and reset `.content-shell` margin, width, and padding. Do not add a hamburger or script.

- [ ] **Step 3: Update the written output contract**

Require a short Chinese display title, complete original paper subtitle, three labeled quick-view rows, five sidebar groups, and a `CHAPTER 01–08` label plus one-sentence `chapter-intro` in each report section. Replace descriptions of the old header cards and light sticky TOC. State explicitly that primary chapters have no card container.

- [ ] **Step 4: Run template-focused tests and verify GREEN**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_sci_read_paper.SkillContractTests.test_report_template_is_self_contained_and_polished \
  tests.test_sci_read_paper.SkillContractTests.test_report_template_uses_compact_reading_layout \
  tests.test_sci_read_paper.SkillContractTests.test_output_contract_has_guided_reading_layers -v
```

Expected: all three pass.

- [ ] **Step 5: Commit the reusable contract**

```bash
git add skills/sci-read-paper/assets/report-template.html skills/sci-read-paper/references/output-contract.md
git commit -m "feat: add monograph paper report template"
```

### Task 3: Convert the SiamProm Acceptance Showcase

**Files:**
- Modify: `tests/sci-read-paper/outputs/siamprom-cyanobacteria-promoters.html`
- Test: `tests/test_sci_read_paper.py`

**Interfaces:**
- Consumes: the final template components and styles from Task 2.
- Produces: `SiamProm 深度精读`, the complete English subtitle, grouped sidebar, compact quick view, and eight continuous labeled chapters while retaining E01–E24.

- [ ] **Step 1: Mirror the reusable shell and visual tokens**

Replace the old centered hero, three summary cards, light TOC, page shell, and chapter container CSS. Move the hero, main, figure brief, provenance, and ledger into `.content-shell`. Add sidebar links to Sections 1–8, `#report-info`, and `#evidence-ledger`.

- [ ] **Step 2: Add the display title, quick view, and chapter openings**

Use:

```html
<h1 class="paper-title">SiamProm 深度精读</h1>
<p class="paper-subtitle">Recognition of cyanobacteria promoters via Siamese network-based contrastive learning under novel non-promoter generation</p>
```

Convert the three existing summary-card contents into three `.quick-view-row` elements without changing their wording. Add `CHAPTER 01` through `CHAPTER 08` and a concise neutral `chapter-intro` immediately after each section heading. Remove the copied `report-section` class from each `<h2>`.

- [ ] **Step 3: Run the focused structural tests**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_sci_read_paper.SkillContractTests.test_siamprom_showcase_uses_compact_reading_layout \
  tests.test_sci_read_paper.SkillContractTests.test_siamprom_showcase_has_complete_internal_links \
  tests.test_sci_read_paper.SkillContractTests.test_siamprom_showcase_preserves_scientific_depth -v
```

Expected: all three pass, all sidebar links resolve, Section IDs stay ordered 1–8, and E01/E24 remain present.

- [ ] **Step 4: Validate and visually inspect desktop output**

Run:

```bash
/opt/homebrew/bin/tidy -quiet -errors tests/sci-read-paper/outputs/siamprom-cyanobacteria-promoters.html
```

Render at `1440x1200` in Chromium. Confirm the sidebar occupies 280px, the article begins immediately to its right, the short Chinese title dominates over the English subtitle, the quick view is compact, Sections 1–8 read as continuous prose, and semantic cards remain distinct. Mobile screenshot is not an acceptance requirement.

- [ ] **Step 5: Run full verification**

Run:

```bash
.venv/bin/python -m unittest tests.test_sci_read_paper -v
.venv/bin/python /Users/yangguang/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sci-read-paper
git diff --check
```

Expected: 25 tests pass, the validator prints `Skill is valid!`, and diff checking is silent.

- [ ] **Step 6: Commit the showcase**

```bash
git add tests/sci-read-paper/outputs/siamprom-cyanobacteria-promoters.html
git commit -m "feat: restyle SiamProm as technical monograph"
```
