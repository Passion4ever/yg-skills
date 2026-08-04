# SCI Read Paper UI Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refine the single-file paper report so its title is restrained, full provenance moves to the footer, and the TOC becomes a compact left reading rail near the article.

**Architecture:** Keep the existing semantic HTML and eight-section contract. Encode layout requirements in contract tests first, update the reusable template and output contract together, then mirror the same structure and CSS in the committed SiamProm showcase and inspect it in Chromium.

**Tech Stack:** HTML5, inline CSS, Python `unittest`/`HTMLParser`, HTML Tidy, headless Chromium.

## Global Constraints

- Presentation-only change: preserve the eight sections, scientific content, evidence IDs, and standard/audit naming.
- Desktop title maximum is approximately `3.2rem`.
- Desktop TOC is approximately `225px`, its article gap is no more than `32px`, and the article remains approximately `900px`.
- Full provenance appears under `来源、版本与未解决问题` immediately before the evidence ledger.
- Preserve offline self-containment, responsive behavior, accessibility, and print output.

---

### Task 1: Lock the Refined Layout Contract

**Files:**
- Modify: `tests/test_sci_read_paper.py`

**Interfaces:**
- Consumes: `HTML_TEMPLATE` and `SIAMPROM_HTML` path constants plus `DocumentIndex`.
- Produces: `test_report_template_uses_compact_reading_layout` and `test_siamprom_showcase_uses_compact_reading_layout` regression tests.

- [ ] **Step 1: Write failing tests for the template and showcase**

Add a helper that isolates header/footer markup and assertions requiring the compact title token, `1360px` bounded shell, `225px` TOC column, `30px` gap, start alignment, quiet rail styling, absence of `report-info` in the header, and `来源、版本与未解决问题` before `evidence-ledger` in the footer.

```python
def assert_compact_reading_layout(testcase: unittest.TestCase, text: str):
    header = text.split("<header", 1)[1].split("</header>", 1)[0]
    footer = text.split("<footer", 1)[1].split("</footer>", 1)[0]
    for token in (
        "clamp(1.9rem, 3.2vw, 3.2rem)",
        "width: min(calc(100% - 64px), 1360px)",
        "grid-template-columns: 225px minmax(0, 900px)",
        "gap: 30px",
        "justify-content: start",
        "border-left: 3px solid var(--accent)",
        "box-shadow: none",
    ):
        testcase.assertIn(token, text)
    testcase.assertNotIn('class="report-info"', header)
    testcase.assertIn("来源、版本与未解决问题", footer)
    testcase.assertLess(footer.index("来源、版本与未解决问题"), footer.index("evidence-ledger"))
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_sci_read_paper.SkillContractTests.test_report_template_uses_compact_reading_layout \
  tests.test_sci_read_paper.SkillContractTests.test_siamprom_showcase_uses_compact_reading_layout -v
```

Expected: both tests fail because the current title reaches `4.5rem`, the centered grid uses a variable gap, and provenance remains in the hero.

- [ ] **Step 3: Commit the RED contract**

```bash
git add tests/test_sci_read_paper.py
git commit -m "test: define compact paper reading layout"
```

### Task 2: Refine the Reusable Template and Output Contract

**Files:**
- Modify: `skills/sci-read-paper/assets/report-template.html`
- Modify: `skills/sci-read-paper/references/output-contract.md`
- Test: `tests/test_sci_read_paper.py`

**Interfaces:**
- Consumes: the exact CSS and structure tokens defined in Task 1.
- Produces: a reusable header with compact metadata only, a start-aligned desktop shell, a quiet TOC rail, and a footer `details.provenance` block using `{{REPORT_DETAILS}}`.

- [ ] **Step 1: Implement the compact hero and reading rail**

Use these desktop CSS declarations:

```css
.paper-title {
  max-width: 1000px;
  font-size: clamp(1.9rem, 3.2vw, 3.2rem);
  line-height: 1.14;
}
.page-shell {
  width: min(calc(100% - 64px), 1360px);
  margin: 0 auto;
  grid-template-columns: 225px minmax(0, 900px);
  justify-content: start;
  gap: 30px;
}
.toc {
  padding: 17px 12px 18px 15px;
  border: 0;
  border-left: 3px solid var(--accent);
  border-radius: 0 12px 12px 0;
  background: rgba(229, 241, 242, 0.5);
  box-shadow: none;
}
```

Reduce hero vertical padding, remove `details.report-info` from the header, and insert immediately inside `<footer>`:

```html
<details class="provenance" id="report-info">
  <summary>来源、版本与未解决问题</summary>
  <div class="details-body">{{REPORT_DETAILS}}</div>
</details>
```

- [ ] **Step 2: Align the written output contract**

Change `Header and Navigation` so the hero contains only compact metadata and three summary cards. Add a `Footer Provenance` rule requiring the collapsed `来源、版本与未解决问题` block immediately before the embedded ledger. Preserve `mode: standard|audit` and `complete|partial` in the top metadata.

- [ ] **Step 3: Run the template-focused suite and verify GREEN**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_sci_read_paper.SkillContractTests.test_report_template_is_self_contained_and_polished \
  tests.test_sci_read_paper.SkillContractTests.test_report_template_uses_compact_reading_layout \
  tests.test_sci_read_paper.SkillContractTests.test_output_contract_has_guided_reading_layers -v
```

Expected: all three tests pass.

- [ ] **Step 4: Commit the reusable UI**

```bash
git add skills/sci-read-paper/assets/report-template.html skills/sci-read-paper/references/output-contract.md
git commit -m "feat: refine paper report reading layout"
```

### Task 3: Update and Visually Verify the SiamProm Showcase

**Files:**
- Modify: `tests/sci-read-paper/outputs/siamprom-cyanobacteria-promoters.html`
- Test: `tests/test_sci_read_paper.py`

**Interfaces:**
- Consumes: the final template CSS and provenance structure from Task 2.
- Produces: a showcase whose structure and appearance demonstrate the reusable contract without changing E01–E24 or Sections 1–8.

- [ ] **Step 1: Mirror the template changes in the showcase**

Replace the title, hero padding, page-shell, and TOC CSS with the Task 2 declarations. Remove the hero `details.report-info` element and reinsert its existing content as `<details class="provenance" id="report-info">` immediately after `<footer>` and before `<details class="ledger" id="evidence-ledger">`.

- [ ] **Step 2: Run the focused showcase tests**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_sci_read_paper.SkillContractTests.test_siamprom_showcase_uses_compact_reading_layout \
  tests.test_sci_read_paper.SkillContractTests.test_siamprom_showcase_has_complete_internal_links \
  tests.test_sci_read_paper.SkillContractTests.test_siamprom_showcase_preserves_scientific_depth -v
```

Expected: all three tests pass, with Section IDs 1–8 and evidence IDs E01–E24 unchanged.

- [ ] **Step 3: Validate HTML and inspect desktop/mobile screenshots**

Run:

```bash
/opt/homebrew/bin/tidy -quiet -errors tests/sci-read-paper/outputs/siamprom-cyanobacteria-promoters.html
```

Render Chromium screenshots at `1440x1200` and `500x1082`. Confirm the desktop TOC begins near the left edge, the TOC/article gap is compact, the title consumes less vertical space, the hero has no provenance disclosure, and the phone layout remains a single readable column.

- [ ] **Step 4: Run the full verification suite**

Run:

```bash
.venv/bin/python -m unittest tests.test_sci_read_paper -v
.venv/bin/python /Users/yangguang/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sci-read-paper
git diff --check
```

Expected: 25 tests pass, the skill validator reports `Skill is valid!`, and `git diff --check` is silent.

- [ ] **Step 5: Commit the verified showcase**

```bash
git add tests/sci-read-paper/outputs/siamprom-cyanobacteria-promoters.html
git commit -m "feat: update SiamProm report UI"
```
