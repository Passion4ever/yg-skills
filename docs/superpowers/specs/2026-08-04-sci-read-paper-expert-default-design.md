# `sci-read-paper` Expert-Default Design

## Purpose

`sci-read-paper` should help a researcher understand one paper as if a careful human expert were guiding the reading. Its job is not to extract every reported field. It should identify the paper's real problem, reconstruct why the authors made each consequential choice, trace how evidence flows through the method and experiments, and explain what the paper does and does not establish.

The current skill preserves scientific depth but defaults to a six-file forensic audit. That makes ordinary reading slower and less stable than necessary. This revision separates expert reading from exhaustive audit while keeping the same critical-thinking standard.

## Core Principle

Optimize for **understanding per unit of evidence**, not evidence volume.

A successful default report lets the reader answer:

1. What problem is the paper actually solving, and why does it matter?
2. What limitation led the authors to this design?
3. How does one real sample move through data construction, training, and the model?
4. What question does each important experiment answer?
5. Which conclusions are credible, provisional, unsupported, or contradicted by released evidence?

Reducing output files must never turn the report into an abstract summary, section inventory, or metadata table.

## Two Reading Modes

### Standard expert reading — default

Use unless the user explicitly requests exhaustive audit, reproduction preparation, or a full paper-code inventory.

Required outputs:

```text
<paper-slug>/
├── deep-reading.md
└── evidence-ledger.md
```

`deep-reading.md` remains self-contained and keeps the existing guided structure:

- field background;
- three-minute map;
- author thought chain;
- concrete-sample data and training trace;
- primary model data flow;
- experiments organized by research question;
- ranked critical review;
- final transferable takeaways.

`evidence-ledger.md` keeps source provenance, versions, exact locators, evidence labels, missing material, and paper-code conflicts.

Standard mode may add one targeted appendix only when a conclusion-changing conflict cannot be explained and audited succinctly in the two required files. The reading guide must say why that appendix exists. Otherwise, unresolved audit detail is recorded once and offered as a next step.

### Full audit — explicit

Enter this mode when the user asks for phrases such as “完整审计”, “准备复现”, “逐文件核对代码”, “完整实验矩阵”, or equivalent intent.

Produce the full six-file dossier:

```text
<paper-slug>/
├── deep-reading.md
├── evidence-ledger.md
└── appendices/
    ├── data-training.md
    ├── model-dataflow.md
    ├── experiment-matrix.md
    └── critical-review.md
```

The main report remains primary. Audit mode increases traceability, not narrative duplication.

## Evidence Scope in Standard Mode

Resolve the paper and supplement status first. Inspect official code only along the shortest path needed to understand the paper:

- dataset construction or loader;
- split logic;
- model entry point and primary `forward` path;
- loss and training loop;
- evaluation entry point and active configuration.

Do not download weights, inspect every utility, enumerate all configuration fields, or reconstruct secondary experiments unless one of those artifacts can change a central interpretation.

Externally verify at most three conclusion-critical claim families in standard mode. Suitable targets include biological identity or novelty, data leakage, evaluation-proxy validity, and a claimed generalization boundary. If further checks are needed, label them unresolved and recommend full audit instead of extending retrieval indefinitely.

For a conclusion-critical motif or sequence novelty claim, search the literal sequence and recognized aliases in first-party literature. Search absence is unresolved comparison scope, not evidence of novelty.

Once the central paper, relevant supplement, shortest official-code path, and selected external checks are resolved or explicitly unavailable, write the two required files before optional corroboration.

## Expert Narrative Contract

Every core section follows:

```text
本节判断 → 直观解释 → 必要技术细节 → 对论文结论的意义
```

The report must:

- start with the scientific background needed to understand this paper;
- reconstruct limitation → hypothesis → design → evidence → bounded contribution;
- keep one concrete sample identifiable across data construction, training, model flow, and output;
- explain modules as answers to named problems, not as a component list;
- organize experiments by the claim being tested, not by table order;
- distinguish paper claims, executable code, inference, missing evidence, external checks, and conflicts;
- keep computational proxies separate from biological or chemical facts;
- use Chinese-first prose and retain English only where it improves precision or paper-code mapping;
- keep detailed inventories out of the main reading path.

The report may be `complete` or `partial`. It must also record `mode: standard|audit`; completion is judged against the selected mode rather than the six-file maximum.

## Failure and Escalation Behavior

- Missing non-critical material produces a `partial` report, not an indefinite search.
- Authentication, payment, ambiguous source identity, conclusion-changing version conflict, or a material user choice may pause execution.
- A critical unresolved issue is explained in the main report and ledger. Standard mode does not silently expand into full audit.
- Optional `sci-ai-figure` handoff remains explicit-user-only.

## Validation Strategy

### Structural RED/GREEN

Add tests that fail against the current six-file-default contract and pass only when:

- standard mode requires the primary report and ledger without requiring the four audit appendices;
- audit mode preserves all six files;
- standard-mode source and external-check boundaries are explicit;
- output status includes the selected mode;
- expert narrative requirements remain intact.

Existing trigger, Chinese-first, evidence-calibration, `partial`, biological-validity, and optional-figure behavior must not regress.

### One normal behavioral trial

Run the unchanged SiamProm request once in a fresh context using standard mode. Do not add independent scoring agents or repeat the run to improve a score.

Record:

- elapsed wall time;
- generated file count and paths;
- whether the main report explains background, author reasoning, sample/data flow, experiment logic, and critical conclusions;
- whether negative-sample construction, phantom sampling plus contrastive learning, label/gradient flow, the known identity check for the reported motif, and paper-code conflicts remain visible;
- observed limitations.

The trial is successful when it produces a comprehensible expert reading with the two required files in one run. It need not be exhaustive. Any failure is reported rather than hidden behind repeated regeneration.

## Non-Goals

- Guaranteeing a fixed wall-clock runtime across papers or network conditions.
- Replacing a reproduction study, systematic review, or wet-lab validation.
- Automatically generating scientific figures.
- Maximizing file count, citation count, or configuration coverage.
