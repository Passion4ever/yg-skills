---
name: sci-read-paper
description: Use when deeply analyzing one AI/ML paper beyond summary, including its research logic, datasets, training, model data flow, experiments, reproducibility, code, or scientific validity, especially in protein, small-molecule, or drug-discovery research. Do not use for direct single-fact extraction.
---

# Deep Read Paper

Reconstruct the research argument and implementation from evidence. Detail-shaped prose is not understanding: explain why each choice exists, how it works, and what supports it.

## Workflow

1. Resolve the paper from a PDF/path, title, DOI, arXiv ID, journal page, or official repository; then collect its supplement, official code/configuration, and dataset sources. Read [evidence-policy.md](references/evidence-policy.md). Ask only for authentication/payment, ambiguous source identity, conclusion-changing version conflicts, or a material user choice.
2. Map the task, prior limitation, gap, hypothesis, contributions, evidence, and conclusion.
3. Reconstruct why prior limitations lead to each design choice and whether the claimed innovation addresses the gap.
4. Trace data provenance, sample construction, splits, leakage, preprocessing, objectives, training stages, hyperparameters, and paper-code differences. Read [ai-ml-reading-guide.md](references/ai-ml-reading-guide.md).
5. Trace input through representations, tensor transformations, interactions or conditioning, fusion, and output. Explain design motivation first; then give formulas, shapes, module interfaces, and code anchors.
6. Classify baseline, ablation, analysis, case-study, and external-validation experiments. Map each to its question, controls, result, and supported claim.
7. Audit internal validity, then verify only conclusion-critical scientific claims with first-party literature. For protein, small-molecule, or drug-discovery work, read [bio-chem-validity.md](references/bio-chem-validity.md).
8. Write the dossier exactly as [output-contract.md](references/output-contract.md) defines.

Run stages continuously. Continue with a `partial` dossier when non-critical artifacts are unavailable; never fill evidence gaps by guessing.

## Communication

For every core point, provide:

1. Chinese intuitive reasoning: why the authors made the choice.
2. Technical reconstruction: formulas, tensors, configuration, and data flow.
3. Traceable support using the evidence labels.

Preserve precise English terms, names, metrics, formulas, and short source excerpts.

## Final Gates

- The problem chain is causal, not a background list.
- Data and training details distinguish reported, implemented, inferred, missing, and conflicting information.
- Model explanation follows data; a module inventory does not pass.
- Every experiment maps to a claim and an honest evidence strength.
- Computational proxies never become experimental biological or chemical facts.
- `deep-reading.md` stands alone; appendices provide traceability.
- Mark the dossier `complete` or `partial` and list unresolved gaps.

Generate figure briefs only when a visual materially improves understanding. Do not invoke `sci-ai-figure` unless it is available and the user asks for a figure.
