# Optional Figure Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make scientific-figure output explicitly controlled by `figure=off|brief|generate`, with no figure UI in default paper-reading reports.

**Architecture:** Keep paper-reading mode and figure mode independent. `SKILL.md` selects the mode, `references/output-contract.md` defines state behavior and fallback, `assets/report-template.html` exposes one conditional output slot, and the SiamProm fixture represents the default `off` path.

**Tech Stack:** Markdown skill instructions, self-contained HTML/CSS, Python `unittest`, Skill Creator validation, HTML Tidy, Helium visual inspection.

## Global Constraints

- `figure=off` is the default and produces no heading, disclosure, image, or empty placeholder in rendered HTML.
- `figure=brief` produces at most three collapsed briefs and never invokes a figure skill.
- `figure=generate` embeds at most three generated data-URI images with captions, alt text, and evidence IDs.
- If generation is unavailable or fails before producing a usable image, finish the reading and fall back to `brief` with one reason statement.
- Do not make `sci-ai-figure` a hard dependency or change the eight primary sections, evidence policy, standard/audit behavior, or report visual design.

---

### Task 1: Define Figure Mode Selection and Fallback

**Files:**
- Modify: `tests/test_sci_read_paper.py`
- Modify: `skills/sci-read-paper/SKILL.md`
- Modify: `skills/sci-read-paper/references/output-contract.md`

**Interfaces:**
- Consumes: user parameters or natural-language requests.
- Produces: selected state `figure=off|brief|generate` and a documented `generate → brief` fallback.

- [ ] **Step 1: Write the failing contract test**

Add to `SkillContractTests`:

```python
def test_figure_mode_is_explicit_and_defaults_off(self):
    skill = SKILL_MD.read_text(encoding="utf-8")
    contract = (SKILL_DIR / "references" / "output-contract.md").read_text(
        encoding="utf-8"
    )
    for state in ("figure=off", "figure=brief", "figure=generate"):
        self.assertIn(state, skill)
        self.assertIn(state, contract)
    self.assertIn("default", skill)
    self.assertIn("fall back to `figure=brief`", contract)
    self.assertIn("does not change the paper-reading completion status", contract)
```

- [ ] **Step 2: Run the test and verify RED**

```bash
.venv/bin/python -m unittest \
  tests.test_sci_read_paper.SkillContractTests.test_figure_mode_is_explicit_and_defaults_off -v
```

Expected: FAIL because the three explicit states and fallback contract are absent.

- [ ] **Step 3: Implement minimal selection guidance in `SKILL.md`**

Replace the current final figure paragraph with:

```markdown
Select `figure=off` by default and emit no figure UI. Select `figure=brief` only when the user asks for a drawing plan or visual brief. Select `figure=generate` only when the user asks to create the figure; invoke `sci-ai-figure` when available, otherwise fall back to `figure=brief` without interrupting the paper reading.
```

- [ ] **Step 4: Update the output contract**

Change the Standard Mode description so the required default file contains no figure material unless requested. Replace `## Optional Figure Handoff` with `## Figure Mode` defining the three exact states, natural-language mapping, independent `mode`/`figure` selection, the existing brief fields, and this fallback text:

```markdown
If generation is unavailable or fails before producing a usable image, finish the reading, fall back to `figure=brief`, and state the reason once. This fallback does not change the paper-reading completion status.
```

- [ ] **Step 5: Run the focused contract tests**

```bash
.venv/bin/python -m unittest \
  tests.test_sci_read_paper.SkillContractTests.test_figure_mode_is_explicit_and_defaults_off \
  tests.test_sci_read_paper.SkillContractTests.test_output_contract_has_one_primary_report \
  tests.test_sci_read_paper.SkillContractTests.test_standard_mode_has_one_html_output \
  tests.test_sci_read_paper.SkillContractTests.test_audit_mode_has_one_html_output -v
```

Expected: four tests PASS.

- [ ] **Step 6: Commit the parameter contract**

```bash
git add tests/test_sci_read_paper.py \
  skills/sci-read-paper/SKILL.md \
  skills/sci-read-paper/references/output-contract.md
git commit -m "feat: make figure output explicitly selectable"
```

### Task 2: Make Figure HTML Conditional

**Files:**
- Modify: `tests/test_sci_read_paper.py`
- Modify: `skills/sci-read-paper/assets/report-template.html`
- Modify: `tests/sci-read-paper/outputs/siamprom-cyanobacteria-promoters.html`

**Interfaces:**
- Consumes: selected figure state and pre-rendered `{{FIGURE_OUTPUT}}`.
- Produces: an empty slot for `off`, a collapsed disclosure for `brief`, or semantic figures for `generate`.

- [ ] **Step 1: Write failing template and fixture tests**

Add to `SkillContractTests`:

```python
def test_template_uses_conditional_figure_output(self):
    text = HTML_TEMPLATE.read_text(encoding="utf-8")
    self.assertIn("{{FIGURE_OUTPUT}}", text)
    self.assertNotIn("{{FIGURE_BRIEFS}}", text)
    self.assertNotIn("可选科研绘图 Briefs", text)

def test_siamprom_default_report_omits_figure_output(self):
    text = SIAMPROM_HTML.read_text(encoding="utf-8")
    self.assertNotIn('id="figure-briefs"', text)
    self.assertNotIn("可选科研绘图 Brief", text)
    self.assertNotIn("sci-ai-figure 的交接契约", text)
```

- [ ] **Step 2: Run the tests and verify RED**

```bash
.venv/bin/python -m unittest \
  tests.test_sci_read_paper.SkillContractTests.test_template_uses_conditional_figure_output \
  tests.test_sci_read_paper.SkillContractTests.test_siamprom_default_report_omits_figure_output -v
```

Expected: both tests FAIL on the current always-present figure Brief.

- [ ] **Step 3: Replace the fixed template disclosure**

Replace the fixed `<details id="figure-briefs">` block in `assets/report-template.html` with:

```html
{{FIGURE_OUTPUT}}
```

Keep the slot after `{{REPORT_BODY}}` and before `{{AUDIT_PANELS}}`.

- [ ] **Step 4: Remove the Brief from the SiamProm default fixture**

Delete the complete `<section id="figure-briefs" ...>` block, including the Brief 1 fields and handoff sentence. Do not change Section 8 content, footer provenance, evidence ledger, or scientific claims.

- [ ] **Step 5: Run focused HTML tests and validation**

```bash
.venv/bin/python -m unittest \
  tests.test_sci_read_paper.SkillContractTests.test_template_uses_conditional_figure_output \
  tests.test_sci_read_paper.SkillContractTests.test_siamprom_default_report_omits_figure_output \
  tests.test_sci_read_paper.SkillContractTests.test_siamprom_showcase_has_complete_internal_links \
  tests.test_sci_read_paper.SkillContractTests.test_siamprom_showcase_preserves_scientific_depth -v
/opt/homebrew/bin/tidy -quiet -errors \
  skills/sci-read-paper/assets/report-template.html \
  tests/sci-read-paper/outputs/siamprom-cyanobacteria-promoters.html
```

Expected: four tests PASS and Tidy exits 0.

- [ ] **Step 6: Commit conditional report output**

```bash
git add tests/test_sci_read_paper.py \
  skills/sci-read-paper/assets/report-template.html \
  tests/sci-read-paper/outputs/siamprom-cyanobacteria-promoters.html
git commit -m "feat: hide figure output by default"
```

### Task 3: Full Verification and Desktop Review

**Files:**
- Verify only: all Task 1–2 files

**Interfaces:**
- Consumes: committed figure-mode contract and HTML output.
- Produces: evidence that the default report remains valid, readable, and scientifically intact.

- [ ] **Step 1: Run the complete test suite**

```bash
.venv/bin/python -m unittest tests.test_sci_read_paper -v
```

Expected: all tests PASS with zero failures.

- [ ] **Step 2: Validate the skill and HTML artifacts**

```bash
.venv/bin/python /Users/yangguang/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/sci-read-paper
/opt/homebrew/bin/tidy -quiet -errors \
  skills/sci-read-paper/assets/report-template.html \
  tests/sci-read-paper/outputs/siamprom-cyanobacteria-promoters.html
git diff --check
```

Expected: `Skill is valid!`, both HTML files have zero Tidy errors, and Git reports no whitespace errors.

- [ ] **Step 3: Review the default report in Helium**

Open the SiamProm report in Helium at desktop width and verify:

- Section 8 flows directly into report provenance with no figure Brief heading or empty gap.
- The sidebar still exposes only the eight chapters and report appendices.
- Clicking TOC links keeps visited links legible.
- Evidence ledger and footer disclosures still open and navigate correctly.

- [ ] **Step 4: Confirm repository state**

```bash
git status --short
git log -4 --oneline
```

Expected: clean worktree with the Task 1 and Task 2 commits at the branch tip.
