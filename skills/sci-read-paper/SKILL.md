---
name: sci-read-paper
description: Use when deeply analyzing one AI/ML paper beyond summary, including its research logic, datasets, training, model data flow, experiments, reproducibility, code, or scientific validity, especially in protein, small-molecule, or drug-discovery research. Do not use for direct single-fact extraction.
---

# Deep Read Paper

Reconstruct the authors' reasoning and implementation from evidence. The main report should feel like a research mentor guiding the reader, not an audit log with prose between entries.

## Workflow

1. Resolve the paper from a PDF/path, title, DOI, arXiv ID, journal page, or official repository; then collect its supplement, official code/configuration, and dataset sources. Read [evidence-policy.md](references/evidence-policy.md). Ask only for authentication/payment, ambiguous source identity, conclusion-changing version conflicts, or a material user choice.
2. Orient the reader: explain the real scientific task, why it matters, why it is difficult, the mainstream approach, and the precise gap this paper enters.
3. Build the causal thought chain from prior limitation to hypothesis, design choice, evidence, and bounded contribution.
4. Trace one concrete sample through provenance, construction, preprocessing, labels, splits, training stages, objectives, and paper-code differences. Read [ai-ml-reading-guide.md](references/ai-ml-reading-guide.md).
5. Follow that sample through representations, tensor or graph transformations, interactions, fusion or conditioning, and output. Give motivation before formulas, shapes, interfaces, and code anchors.
6. Organize baseline, control, ablation, analysis, case-study, and external-validation evidence by the research question each experiment answers.
7. Audit internal validity, then verify only conclusion-critical scientific claims with first-party literature. For protein, small-molecule, or drug-discovery work, read [bio-chem-validity.md](references/bio-chem-validity.md).
8. Write the dossier exactly as [output-contract.md](references/output-contract.md) defines.

Run continuously. Continue with a `partial` dossier when non-critical artifacts are unavailable; never fill gaps by guessing.

## Communication

- Use Chinese-first prose. At first use, give Chinese with the English term only when it helps paper/code mapping; then prefer Chinese. Preserve proper names, metrics, code identifiers, file paths, and author-defined modules.
- Develop each core section as conclusion → intuition → technical detail → meaning. Start from a concrete object before aggregate inventories.
- Keep a paragraph to one main judgment and usually 3–5 sentences. Aim for a 15–20 minutes main-report reading path; move exhaustive audit detail to appendices.
- Cite paragraphs with lightweight evidence IDs. Explicitly say when the paper reports, code implements, evidence conflicts, information is missing, or the analysis infers.

## Final Gates

- Background makes the paper's problem understandable without becoming a broad review.
- The three-minute map stands alone and includes the task, tension, thought chain, minimal data flow, experimental verdict, and largest risk.
- Data and model explanations follow a concrete sample; module inventories do not pass.
- Every experiment maps to a question, controls, result, supported claim, and unsupported claim.
- Computational proxies never become experimental biological or chemical facts.
- `deep-reading.md` contains the complete research story without copying appendix inventories.
- Mark `complete|partial`, list unresolved gaps once, and repeat them only where they change a judgment.

Generate figure briefs only when a visual materially improves understanding. Do not invoke `sci-ai-figure` unless it is available and the user explicitly asks for a figure.
