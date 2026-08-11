---
name: sci-read-paper
description: Use when deeply analyzing one AI/ML paper beyond summary, including its research logic, datasets, training, model data flow, experiments, reproducibility, code, or scientific validity, especially in protein, small-molecule, or drug-discovery research. Also use for 深度精读、复现性审查、论文与代码是否一致、模型内部数据流、实验能证明什么. Do not use for direct single-fact extraction, and do not use for full-text translation or 中英对照 bilingual reading.
---

# Deep Read Paper

Help the reader understand one paper as an expert does: reconstruct reasoning and data flow before judging evidence; never reduce it to a summary.

## Workflow

1. Default to `standard`. Select `audit` only on explicit request for exhaustive audit, reproduction preparation, a full experiment matrix, or file-by-file code comparison.
2. Resolve the paper from a PDF/path, title, DOI, arXiv ID, journal page, or official repository. Collect only conclusion-relevant supplement, code/configuration, dataset, and external evidence. Read [evidence-policy.md](references/evidence-policy.md). Ask only about access, ambiguous identity, or a conclusion-changing conflict.
3. Orient the reader on the real task, significance, difficulty, mainstream framing, and gap; build limitation → hypothesis → design → evidence → contribution.
4. Trace one concrete sample through provenance, construction, labels, splits, training, model transformations, output, and paper-code differences. Read [ai-ml-reading-guide.md](references/ai-ml-reading-guide.md).
5. Organize baseline, control, ablation, analysis, case-study, and external-validation evidence by the question each answers.
6. Audit internal validity and conclusion-critical scientific claims. For protein, small-molecule, or drug-discovery work, read [bio-chem-validity.md](references/bio-chem-validity.md).
7. Scaffold with `python3 <skill-dir>/scripts/new_report.py --slug <paper-slug> --outdir <outdir>`, then fill one placeholder per edit. Copy every repeated structure — cards, boundaries, ledger rows, citations, verdicts — from `assets/fragments.html` instead of writing markup. [output-contract.md](references/output-contract.md) defines the rest.
8. Run `python3 <skill-dir>/scripts/validate_report.py <delivered file>`. Fix every violation and re-run until it exits `0`. Do not call the report finished before it does.

Continue as `partial` when non-critical artifacts are unavailable; never guess a gap shut.

## Communication

- Use Chinese-first prose. Say in plain Chinese what an English term means at first use, then use the term. Preserve proper names, metrics, identifiers, paths, and author-defined modules.
- Develop Sections 1–6 as question → author rationale → technical detail → role in the argument.
- Keep a paragraph to one explanatory purpose and usually 3–5 sentences. A sentence the reader has to re-read has failed. Aim for a 15–20 minute main reading path.
- Cite paragraphs with evidence IDs; name the source kind: paper, code, conflict, missing, or inference.

## Final Gates

`scripts/validate_report.py` decides every mechanical question, and its output — not your reading of it — is the evidence. Check the delivered file yourself against what it cannot see:

- Background states the literal input and prediction target, separate from sampling proxies and biological mechanism.
- The three-minute map gives task, thought chain, minimal flow, reported outcome, and one review preview.
- Data and model explanations follow a concrete sample; module inventories fail.
- Section 6 states experiment questions, controls, results, and neutral boundaries; Section 7 judges them.
- Each discharge names what its boundary actually asserts. Linking the id satisfies the validator without answering anything.
- No verdict endorses what a boundary called confounded.
- Computational proxies never become experimental biological or chemical facts.
- Unresolved gaps appear once, only where they change a judgment.

`figure=off` is the default and emits no figure UI. Select `figure=brief` or `figure=generate` only on request; `output-contract.md` defines both. `sci-diagram` is invoked only under `figure=generate`.
