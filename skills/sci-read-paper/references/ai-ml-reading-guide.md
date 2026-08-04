# AI/ML Reading Guide

## Field Orientation

Before discussing the paper, explain only the domain context needed later:

1. What real scientific or engineering task is being solved?
2. Why does it matter, and what makes it difficult?
3. How do mainstream approaches usually frame it?
4. Which precise limitation creates the opening for this paper?

Distinguish field consensus from the authors' framing and from claims that still require verification. Do not turn this section into a broad literature review.

## Research Logic

Build one causal chain:

```text
task and stakes
→ prior approach
→ decisive limitation
→ unresolved gap
→ author hypothesis
→ design choice intended to address it
→ evidence
→ bounded contribution
```

Explain how each major design choice answers a named limitation. Separate a new capability from a new combination, dataset construction, engineering improvement, or evaluation change.

## Concrete Sample First

Start data, training, and model explanations from one concrete sample. Follow its semantic identity before listing aggregate statistics:

```text
raw sample
→ inclusion and label construction
→ preprocessing and representation
→ split membership and batch
→ model path
→ loss or decoding
→ prediction, generated object, or metric
```

After the sample is clear, add dataset origin/version, counts, deduplication, augmentation, split unit, leakage checks, objectives, optimization, schedules, seeds, hardware, precision, and checkpoint selection. Put exhaustive configuration and secondary paper-code differences in `appendices/data-training.md`.

Do not infer a library default without proving the released version used it and labeling the inference in the evidence ledger.

## Model Data Flow

Give one simplified Mermaid diagram when evidence supports explicit edges. Then record each main-path stage:

| Question | Record |
|---|---|
| What is it now? | semantic object and raw/encoded type |
| What is its shape? | tensor, sequence, graph, or batch shape |
| What happens? | operation and information gained or lost |
| Why is it needed? | connection to the author's hypothesis |
| Where does it go? | next module, fusion, decoder, or output |
| Can we verify it? | paper/code agreement, inference, missing detail, or conflict |

Explain intuition before equations. Define symbols and connect them to real objects immediately. Keep the main report on the primary path; place exhaustive interfaces, shapes, and code anchors in `appendices/model-dataflow.md`.

## Code Audit

In `standard` mode, follow the shortest conclusion-relevant path through the dataset constructor or loader, split logic, model entry point and primary `forward`, loss/training loop, evaluation entry point, and active configuration. Stop when the primary data flow and conclusion-changing paper-code conflicts are resolved. Cite paths and commits in the evidence ledger; distinguish executable paths from dead code, examples, or unused options.

Do not download weights, inspect every utility, enumerate every configuration field, or reconstruct secondary experiments unless that artifact can change a central interpretation. In `audit` mode, expand to the complete executable-path inventory and audit appendix schemas.

## Experiment Reasoning

Organize experiments by research question rather than paper table order. Group baseline, control, ablation, robustness/generalization, case study, and external validation evidence around the claim being tested.

For each core question explain:

```text
what the authors want to prove
→ changed and controlled variables
→ data, split, metric, and result
→ what the evidence supports
→ what it does not establish
```

End a core experiment section with a compact judgment card:

```text
作者想证明：...
当前证据：...
我们的判断：...
```

Check baseline fairness, isolated ablations, uncertainty, seeds, confidence intervals, and whether analysis plots provide evidence or illustration. Store the exhaustive experiment inventory in `appendices/experiment-matrix.md`.
