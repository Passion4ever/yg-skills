# `sci-read-paper` Behavioral Rubric

Score each positive or partial-source output from 0 to 2 on every criterion.

- `0`: absent, invented, or materially wrong.
- `1`: present but incomplete, weakly traced, or insufficiently calibrated.
- `2`: explicit, technically useful, and traceable to identified evidence.

## Criteria

| Criterion | Critical | A score of 2 requires |
|---|---:|---|
| Research problem chain | Yes | Background, prior limitation, gap, hypothesis, design choice, and contribution form a causal chain. |
| Source completion | No | Paper, supplement, official code/configuration, and dataset sources are sought and their availability recorded. |
| Data and training | Yes | Provenance, sample construction, split, preprocessing, objectives, stages, and missing details are distinguished. |
| Model data flow | Yes | Inputs are traced through representations, transformations, interactions or conditioning, and outputs; module lists alone do not pass. |
| Experiment-to-claim mapping | Yes | Baseline, ablation, analysis, case study, and external validation are tied to questions, controls, results, and claims. |
| Paper-code comparison | No | Code-only behavior, paper-only claims, and conflicts are separated without invented reconciliation. |
| Evidence calibration | Yes | Paper facts, code facts, external evidence, inference, missing information, and conflicts are distinguishable. |
| Bio/chemical validity | Yes | Relevant leakage, split, proxy-metric, assay, docking, synthesis, or wet-lab limitations are examined. |
| Main-report usability | No | One Chinese primary report tells the complete research story while preserving precise English technical terms. |
| Reproducibility and boundaries | No | The output states what can be reproduced, what cannot, the real contribution, applicability, and unresolved questions. |

GREEN requires at least 16/20 and no `0` on a critical criterion. A run with fabricated evidence fails regardless of total score.

For trigger cases, show the case prompt and the metadata descriptions available to the agent, but do not show the expected selection. A trigger run passes only when the agent selects `sci-read-paper`; a non-trigger run passes only when it rejects it.
