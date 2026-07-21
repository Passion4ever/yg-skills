# Output Contract

Create one directory named from a stable paper slug:

```text
<paper-slug>/
├── deep-reading.md
├── appendices/
│   ├── evidence-ledger.md
│   ├── data-training.md
│   ├── model-dataflow.md
│   ├── experiment-matrix.md
│   └── critical-review.md
└── assets/
```

`deep-reading.md` is self-contained and is the only file a normal reader must open. Appendices preserve detail and traceability without duplicating the main narrative.

## Primary Report

Use exactly these top-level sections:

```markdown
# <Paper Title>

## 阅读状态
## 一页理解整篇论文
## 1. 作者为什么做这项研究
## 2. 数据与训练到底怎样完成
## 3. 模型内部的数据怎样流动
## 4. 每项实验究竟想证明什么
## 5. 作者的结论是否成立
## 6. 我们最终应该怎样理解这篇论文
## 可选科研绘图 Briefs
```

`阅读状态` records `complete|partial`, source availability, paper/code versions, and unresolved gaps. `一页理解整篇论文` gives orientation, not a substitute abstract.

The model section contains at least one reconstructed data-flow diagram when evidence supports it. Prefer Mermaid for explicit entities and edges. Mark inferred edges or shapes in the prose; do not make uncertain content look authoritative through visual polish.

## Appendices

### `appendices/evidence-ledger.md`

Use columns: evidence ID, label, source, version/commit, locator, supported statement, and access status.

### `appendices/data-training.md`

Record provenance, construction, counts, splits, preprocessing, leakage checks, objectives, stages, hyperparameters, compute, checkpoint selection, and paper-code differences.

### `appendices/model-dataflow.md`

Record a concrete sample trace plus a table with stage, semantic object, shape, operation, output, code anchor, and evidence label.

### `appendices/experiment-matrix.md`

Use columns: experiment ID, type, question/claim, changed variable, controls, data/split, metric, result, supported conclusion, unsupported conclusion, evidence IDs.

### `appendices/critical-review.md`

Separate internal validity, reproducibility, domain validity, external claim checks, alternative explanations, applicability, and unresolved questions. Rank issues by effect on the central conclusion rather than by writing style.

## Optional Figure Handoff

Include at most three briefs, and only when a visual materially improves understanding. Each brief contains:

- purpose and target reader;
- figure type;
- required entities and relationships;
- evidence IDs;
- visual hierarchy;
- content that must not be inferred or invented.

Do not generate images automatically. If `sci-ai-figure` is installed and the user explicitly asks for a figure, pass the brief as the handoff contract.
