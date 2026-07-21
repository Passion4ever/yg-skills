# AI/ML Reading Guide

## Research Logic

Build one causal chain:

```text
task and stakes
→ limitation of prior data, assumptions, representation, optimization, or evaluation
→ unresolved gap
→ author hypothesis
→ design choice intended to test it
→ evidence
→ bounded conclusion
```

Separate a genuinely new capability from a new combination, new dataset construction, engineering improvement, or evaluation change. Test whether the proposed method addresses the stated gap rather than a nearby easier problem.

## Data and Training

Recover and cross-check:

- dataset origin, version, license, inclusion/exclusion, labels, units, and sample counts;
- sample construction, negatives or decoys, augmentation, deduplication, and preprocessing order;
- train/validation/test split unit and strategy; group, identity, scaffold, temporal, and external separation;
- leakage through duplicates, related entities, preprocessing fit, target knowledge, pretrained data, or test-guided selection;
- objective terms, weighting, optimization, schedules, freezing, early stopping, seeds, precision, hardware, and checkpoint selection;
- differences among paper prose, supplement, default config, training command, and released checkpoint.

Do not infer an unreported value from a library default without labeling it `[推断]` and proving that the released version used that default.

## Model Data Flow

Start from one concrete sample. Track:

| Stage | Record |
|---|---|
| Input | semantic meaning, raw type, shape, and preprocessing |
| Representation | tokenizer/featurizer, embedding, positional or geometric information |
| Transformation | operation, input/output shape, parameters, and information gained or lost |
| Interaction | attention, message passing, pairing, cross-view exchange, or conditioning |
| Fusion | concatenation, sum, pooling, gating, or decoder context |
| Output | prediction/generation target, decoding, calibration, and postprocessing |
| Training signal | loss path and which modules receive gradients |

Explain motivation before equations. Define symbols and shapes before manipulating them. When shapes are not reported, derive only those forced by code or equations and label them `[推断]`.

## Code Audit

Locate the actual data loader, split generator, model entry point, loss computation, training loop, evaluation command, and default configuration. Cite file paths and commit IDs. Distinguish executable paths from dead code, examples, or unused options.

## Experiment Reasoning

Classify each result as baseline, ablation, analysis, robustness/generalization, case study, or external validation. For each experiment record:

1. Question or claim under test.
2. Changed and controlled variables.
3. Data split and metric.
4. Fairness of baselines and tuning.
5. Result with uncertainty or statistical support.
6. What the result supports.
7. What it does not establish.

Check whether ablations isolate one factor, whether baseline implementations and compute budgets are comparable, whether multiple seeds or confidence intervals matter, and whether analysis plots are explanatory evidence or illustrations.
