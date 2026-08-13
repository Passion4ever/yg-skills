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
| Boundary closure | Yes | Every `证据边界` deferred from Sections 1–6 is discharged in Section 7 — assessed in a review card or listed once as no material effect — and no graded verdict endorses a claim a boundary called confounded. |
| Bio/chemical validity | Yes | Relevant leakage, split, proxy-metric, assay, docking, synthesis, or wet-lab limitations are examined. |
| Main-report usability | No | One offline Chinese HTML report tells the complete eight-section story, preserves precise English terms, and embeds its evidence ledger. |
| Reproducibility and boundaries | No | The output states what can be reproduced, what cannot, the real contribution, applicability, and unresolved questions. |

An otherwise strong report does not pass if it emits multiple deliverable files, depends on external UI resources, breaks its internal evidence links, drops a deferred boundary, or mixes the Section 7 verdict into the explanatory Sections 1–6.

Score only reports for which `skills/scientific/sci-read-paper/scripts/validate_report.py` already exits `0`. The rubric judges what the validator cannot: whether the reasoning is right. A report that fails the validator is not eligible for scoring.

Do not spend scoring effort on anything the gate already decides — section order and headings, card fields, the experiment-type/impact/verdict/ledger vocabularies, boundary labelling and discharge, citation resolution, badges, figure mode, template-only classes, sentence length, or section length. Those are closed sets or fixed strings, and a report that reached the rubric has already satisfied all of them. Judge the open questions instead: is the causal chain real, does the concrete sample actually trace, does each discharge answer what its boundary asserts, and does any verdict outrun its evidence.

GREEN requires at least 18/22 and no `0` on a critical criterion. A run with fabricated evidence fails regardless of total score.

For trigger cases, show the case prompt and the metadata descriptions available to the agent, but do not show the expected selection. A trigger run passes only when the agent selects `sci-read-paper`; a non-trigger run passes only when it rejects it.
