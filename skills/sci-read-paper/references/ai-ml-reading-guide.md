# AI/ML Reading Guide

Use the eight report sections as one reading argument: orient the field in Section 1, compress the whole paper in Section 2, reconstruct design logic in Section 3, trace data and training in Section 4, trace internal model flow in Section 5, explain experiment logic in Section 6, switch explicitly to reviewer mode in Section 7, and synthesize in Section 8. Do not mix cumulative criticism into Sections 1–6.

## Field Orientation

Before discussing the paper, explain only the domain context needed later:

1. What real scientific or engineering task is being solved?
2. Why does it matter, and what makes it difficult?
3. How do mainstream approaches usually frame it?
4. Which precise limitation creates the opening for this paper?

State the literal model input and prediction target before explaining the broader science. Keep the prediction target separate from any sampling or annotation proxy and from the biological mechanism. For example, promoter/non-promoter sequence classification is the target; a TSS-aligned window may be how a positive sample is collected; transcription initiation is the underlying biological process. Do not redefine one as another.

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

First reconstruct how each major design choice answers a named limitation from the authors' perspective. Preserve factual evidence boundaries, but defer severity, alternatives, and final claim calibration to the critical-review section. Separate a new capability from a new combination, dataset construction, engineering improvement, or evaluation change.

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

After the sample is clear, add dataset origin/version, counts, deduplication, augmentation, split unit, leakage checks, objectives, optimization, schedules, seeds, hardware, precision, and checkpoint selection. In `audit` mode, put exhaustive configuration and secondary paper-code differences in the embedded `data-training` panel.

Do not infer a library default without proving the released version used it and labeling the inference in the evidence ledger.

## Model Data Flow

Give one simplified inline SVG or semantic HTML flow when evidence supports explicit edges. Then record each main-path stage:

| Question | Record |
|---|---|
| What is it now? | semantic object and raw/encoded type |
| What is its shape? | tensor, sequence, graph, or batch shape |
| What happens? | operation and information gained or lost |
| Why is it needed? | connection to the author's hypothesis |
| Where does it go? | next module, fusion, decoder, or output |
| Can we verify it? | paper/code agreement, inference, missing detail, or conflict |

Explain intuition before equations. Define symbols and connect them to real objects immediately. Keep the main report on the primary path; in `audit` mode, place exhaustive interfaces, shapes, and code anchors in the embedded `model-dataflow` panel.

## Code Audit

In `standard` mode, follow the shortest conclusion-relevant path through the dataset constructor or loader, split logic, model entry point and primary `forward`, loss/training loop, evaluation entry point, and active configuration. Stop when the primary data flow and conclusion-changing paper-code conflicts are resolved. Cite paths and commits in the evidence ledger; distinguish executable paths from dead code, examples, or unused options.

Acquire code with raw-file requests or sparse or blob-filtered repository retrieval. Inspect the remote tree first and exclude weight/checkpoint paths before checkout; a normal clone that fetches tracked weights does not satisfy the standard-mode boundary.

Do not download weights, inspect every utility, enumerate every configuration field, or reconstruct secondary experiments unless that artifact can change a central interpretation. In `audit` mode, expand the embedded panels to the complete executable-path inventory.

## Experiment Reasoning

Organize experiments by research question rather than paper table order. Group baseline, control, ablation, robustness/generalization, case study, and external validation evidence around the claim being tested. `output-contract.md` defines the experiment card fields and the experiment-type vocabulary; use them verbatim rather than a local variant.

The evidence boundary records missing controls, uncertainty, unavailable artifacts, or direct design limits in neutral language, carries its own `B01`-style ID, and is discharged in Section 7. Concentrate the cumulative judgment there; in `audit` mode, store the exhaustive inventory in the embedded `experiment-matrix` panel.

Check seeds, confidence intervals, isolated ablations, and whether analysis plots are evidence or illustration. Three checks are easy to skip and decide what the main table means:

**Baseline parity.** Do the baselines have the same interface as the proposed model — same inputs, same conditioning signals, same tuning budget, same evaluation protocol? A model conditioned on the very quantities the table scores will beat an unconditioned baseline on those quantities without being a better model. When the comparison mixes architecture with capability, say so and note whether an equally-conditioned variant or an unconditioned ablation restores the comparison.

**Input ablation.** Name the single input whose removal would falsify the paper's mechanistic claim, and check whether that ablation was run. A model claiming to capture an interaction must lose accuracy when one side of the interaction is withheld; a ligand-only or sequence-only variant that matches the full model shows the claimed mechanism is not what carries the performance. Unrun means the claim tops out at association.

**Metric validity.** Check that the reported metric can express the failure that matters: class balance and prevalence against AUROC versus AUPRC, threshold choice, whether enrichment is computed over a matched decoy set, and whether the aggregate hides per-target or per-scaffold variance. A metric chosen after seeing results, or reported without the spread across seeds and targets, bounds the claim rather than supporting it.
