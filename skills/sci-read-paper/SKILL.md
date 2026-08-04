---
name: sci-read-paper
description: Use when deeply analyzing one AI/ML paper beyond summary, including its research logic, datasets, training, model data flow, experiments, reproducibility, code, or scientific validity, especially in protein, small-molecule, or drug-discovery research. Do not use for direct single-fact extraction.
---

# Deep Read Paper

Help the reader understand one paper as a human expert: reconstruct reasoning and data flow before judging evidence; never reduce it to a summary or field inventory.

## Workflow

1. Select `standard` mode by default. Select `audit` only when the user explicitly requests exhaustive audit, reproduction preparation, a full experiment matrix, or file-by-file code comparison.
2. Resolve the paper from a PDF/path, title, DOI, arXiv ID, journal page, or official repository. Collect only conclusion-relevant supplement, official code/configuration, dataset, and external evidence. Read [evidence-policy.md](references/evidence-policy.md). Ask only for authentication/payment, ambiguous identity, conclusion-changing version conflicts, or a material user choice.
3. Orient the reader: explain the real task, significance, difficulty, mainstream framing, and precise gap. Build limitation → hypothesis → design → evidence → bounded contribution.
4. Trace one concrete sample through provenance, construction, labels, splits, training, model transformations, output, and paper-code differences. Read [ai-ml-reading-guide.md](references/ai-ml-reading-guide.md).
5. Organize baseline, control, ablation, analysis, case-study, and external-validation evidence by the research question each answers.
6. Audit internal validity and only conclusion-critical scientific claims. For protein, small-molecule, or drug-discovery work, read [bio-chem-validity.md](references/bio-chem-validity.md).
7. Write the selected output exactly as [output-contract.md](references/output-contract.md) defines.

In `standard` mode, resolve conclusion-changing evidence, then write one self-contained `<paper-slug>.html`. In `audit` mode, write `<paper-slug>-audit.html` with embedded audit panels. Continue with `partial` when non-critical artifacts are unavailable; never fill gaps by guessing or leave working notes as deliverables.

## Communication

- Use Chinese-first prose. At first use, give Chinese with the English term only when it helps paper/code mapping; then prefer Chinese. Preserve proper names, metrics, code identifiers, file paths, and author-defined modules.
- Develop Sections 1–6 as question → author rationale → technical detail → role in the argument. Start from a concrete object before aggregate inventories.
- Follow understand authors (1–6) → review (7) → synthesize (8); use neutral early fact handoffs.
- Keep a paragraph to one explanatory purpose and usually 3–5 sentences. Aim for a 15–20 minutes main-report reading path, independent of audit depth.
- Cite paragraphs with lightweight evidence IDs. Explicitly say when the paper reports, code implements, evidence conflicts, information is missing, or the analysis infers.

## Final Gates

- Background states the literal input and prediction target, separating it from sampling/annotation proxies and biological mechanism.
- The three-minute map gives the task, thought chain, minimal flow, reported outcome, and one review preview.
- Data and model explanations follow a concrete sample; module inventories do not pass.
- Section 6 states experiment questions, controls, results, and neutral boundaries; Section 7 judges them.
- Computational proxies never become experimental biological or chemical facts.
- The HTML contains the complete research story and embedded evidence ledger without duplicated inventories.
- Mark `mode: standard|audit` and `complete|partial`; list unresolved gaps once and repeat them only where they change a judgment.

Generate figure briefs only when a visual materially improves understanding. Do not invoke `sci-ai-figure` unless it is available and the user explicitly asks for a figure.
