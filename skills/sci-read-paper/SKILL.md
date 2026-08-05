---
name: sci-read-paper
description: Use when deeply analyzing one AI/ML paper beyond summary, including its research logic, datasets, training, model data flow, experiments, reproducibility, code, or scientific validity, especially in protein, small-molecule, or drug-discovery research. Also use for 深度精读、复现性审查、论文与代码是否一致、模型内部数据流、实验能证明什么. Do not use for direct single-fact extraction, and do not use for full-text translation or 中英对照 bilingual reading.
---

# Deep Read Paper

Help the reader understand one paper as an expert does: reconstruct reasoning and data flow before judging evidence; never reduce it to a summary or field inventory.

## Workflow

1. Default to `standard`. Select `audit` only on explicit request for exhaustive audit, reproduction preparation, a full experiment matrix, or file-by-file code comparison.
2. Resolve the paper from a PDF/path, title, DOI, arXiv ID, journal page, or official repository. Collect only conclusion-relevant supplement, official code/configuration, dataset, and external evidence. Read [evidence-policy.md](references/evidence-policy.md). Ask only about authentication/payment, ambiguous identity, conclusion-changing version conflicts, or a material choice.
3. Orient the reader on the real task, significance, difficulty, mainstream framing, and gap; build limitation → hypothesis → design → evidence → bounded contribution.
4. Trace one concrete sample through provenance, construction, labels, splits, training, model transformations, output, and paper-code differences. Read [ai-ml-reading-guide.md](references/ai-ml-reading-guide.md).
5. Organize baseline, control, ablation, analysis, case-study, and external-validation evidence by the question each answers.
6. Audit internal validity and only conclusion-critical scientific claims. For protein, small-molecule, or drug-discovery work, read [bio-chem-validity.md](references/bio-chem-validity.md).
7. Write the output as [output-contract.md](references/output-contract.md) defines: copy `assets/report-template.html` to `<outdir>/<paper-slug>.html`, replace `{{REPORT_BODY}}` with eight empty section shells, then fill one section per edit. Never retype the template CSS.
8. Run `python3 <skill-dir>/scripts/validate_report.py --figure <mode> <delivered file>`. Fix every violation and re-run until it exits `0`. Do not call the report finished before it does.

`audit` mode adds embedded panels in `<paper-slug>-audit.html`. Continue as `partial` when non-critical artifacts are unavailable; never guess a gap shut or ship notes.

## Communication

- Use Chinese-first prose; pair an English term on first use only when it helps paper/code mapping. Preserve proper names, metrics, identifiers, paths, and author-defined modules.
- Develop Sections 1–6 as question → author rationale → technical detail → role in the argument.
- Keep a paragraph to one explanatory purpose and usually 3–5 sentences. Aim for a 15–20 minutes main-report reading path, independent of audit depth.
- Cite paragraphs with evidence IDs; say explicitly when the paper reports, code implements, evidence conflicts, information is missing, or you infer.

## Final Gates

- Background states the literal input and prediction target, separate from sampling/annotation proxies and biological mechanism.
- The three-minute map gives task, thought chain, minimal flow, reported outcome, and one review preview.
- Data and model explanations follow a concrete sample; module inventories fail.
- Section 6 states experiment questions, controls, results, and neutral boundaries; Section 7 judges them.
- Every boundary in Sections 1–6 carries a `B01`-style ID that Section 7 discharges in a review card or its no-material-effect list. No verdict endorses what a boundary called confounded.
- Computational proxies never become experimental biological or chemical facts.
- Mark `mode` and completion status; list unresolved gaps once, repeating only where they change a judgment.
- `scripts/validate_report.py` exits `0` on the delivered file — its output, not your reading of these gates, is the evidence.

`figure=off` is the default and emits no figure UI. Select `figure=brief` or `figure=generate` only on request; [output-contract.md](references/output-contract.md) defines both.
