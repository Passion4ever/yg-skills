# CProMG Deep-Reading Showcase Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a complete Chinese-first standard-mode CProMG deep-reading HTML that demonstrates the current `sci-read-paper` contract on a protein-conditioned molecular-generation paper.

**Architecture:** Reuse the existing offline report template and eight-section narrative without changing the general skill. Treat the paper, official repository at commit `1c9fc00`, released split, Zenodo record, and three conclusion-critical external checks as an embedded Evidence Ledger; expose conclusion-changing conflicts neutrally before judging them in Section 7.

**Tech Stack:** Static HTML/CSS, Python `unittest` and `HTMLParser`, HTML Tidy.

## Global Constraints

- Output exactly `tests/sci-read-paper/outputs/cpromg-protein-oriented-molecule-generation.html`.
- Use `mode=standard`, `complete`, and default `figure=off`; emit no figure UI.
- Preserve the existing template's desktop layout, eight exact section IDs/titles, provenance disclosure, and embedded ledger.
- State the literal task as prepared 3D pocket plus requested property vector to autoregressive SMILES, separate from experimental binding or drug discovery.
- Keep Sections 1–6 explanatory and Section 7 explicitly critical.
- Every main-report Evidence ID must be visible in its own anchor and resolve to a unique ledger row.
- Do not download the 7.1 GB Zenodo bundle or pretrained weights.

---

### Task 1: Add the CProMG standard-mode acceptance report

**Files:**
- Create: `tests/sci-read-paper/outputs/cpromg-protein-oriented-molecule-generation.html`
- Modify: `tests/test_sci_read_paper.py`
- Reference: `skills/sci-read-paper/assets/report-template.html`

**Interfaces:**
- Consumes: `DocumentIndex`, `EXPECTED_SECTION_TITLES`, and `assert_frameflow_inspired_layout` from the existing test module.
- Produces: one self-contained HTML with eight primary sections, no figure output, individually resolvable Evidence links, and CProMG-specific scientific facts.

- [ ] **Step 1: Write the failing acceptance test**

Add `CPROMG_HTML` beside `SIAMPROM_HTML`, then add:

```python
def test_cpromg_showcase_is_complete_traceable_and_scientifically_grounded(self):
    self.assertTrue(CPROMG_HTML.is_file(), "complete CProMG HTML showcase is missing")
    text = CPROMG_HTML.read_text(encoding="utf-8")
    parser = DocumentIndex()
    parser.feed(text)

    self.assertEqual(parser.section_ids, [f"section-{i}" for i in range(1, 9)])
    self.assertEqual(len(parser.ids), len(set(parser.ids)))
    self.assertLessEqual(set(parser.internal_targets), set(parser.ids))
    self.assertNotIn('id="figure-briefs"', text)
    for fact in (
        "CrossDocked2020",
        "prepared 3D binding pocket",
        "1c9fc00",
        "AutoDock Vina",
        "QED",
        "SA score",
        "AddLaplacianEigenvectorPE",
        "50 iterations",
    ):
        self.assertIn(fact, text)
    for href, visible in parser.main_report_evidence_links:
        self.assertEqual(re.findall(r"E\\d{2}", visible), [href.removeprefix("#")])
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
python -m unittest tests.test_sci_read_paper.SkillContractTests.test_cpromg_showcase_is_complete_traceable_and_scientifically_grounded -v
```

Expected: FAIL because the CProMG HTML file does not exist.

- [ ] **Step 3: Write the report from verified evidence**

Build the HTML from `report-template.html`. Cover literal task and field gap; reconstructed design chain; one CrossDocked pocket–ligand example through split, preprocessing, teacher forcing, and checkpoint selection; atom/residue graph shapes and cross-fusion; baseline/control/ablation/case-study questions; and a separate review of docking-oracle validity, property proxies, split/generalization, and released-code reproducibility. Include a ledger row for every cited paper/code/data/external/conflict/inference claim.

- [ ] **Step 4: Run focused GREEN verification**

Run the focused test from Step 2. Expected: PASS.

- [ ] **Step 5: Run complete verification**

Run:

```bash
python -m unittest -v
tidy -qe tests/sci-read-paper/outputs/cpromg-protein-oriented-molecule-generation.html
git diff --check
```

Expected: all tests pass, Tidy emits no diagnostics, and the diff check exits 0.

- [ ] **Step 6: Review the rendered desktop report**

Open the HTML at 1440×900. Confirm the sidebar remains visible and close to the viewport edge, all navigation targets work, Section 8 flows directly to provenance with no figure placeholder, tables remain readable, and visited links remain legible.

- [ ] **Step 7: Commit**

```bash
git add docs/superpowers/plans/2026-08-05-cpromg-showcase.md tests/test_sci_read_paper.py tests/sci-read-paper/outputs/cpromg-protein-oriented-molecule-generation.html
git commit -m "feat: add CProMG deep-reading showcase"
```
