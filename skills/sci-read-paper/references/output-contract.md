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

`deep-reading.md` contains the complete research story and is the only file a normal reader must open. Appendices preserve exhaustive audit detail without copying it into the main narrative.

## Primary Report

Use exactly these top-level sections:

```markdown
# <论文标题>

## 阅读导航
## 1. 先把论文放回领域里
## 2. 三分钟看懂这篇论文
## 3. 作者是怎样一步步想到这个方法的
## 4. 数据与训练：跟踪一条样本
## 5. 模型：数据怎样一步步变成输出
## 6. 实验：每项实验究竟回答什么问题
## 7. 批判性审查：哪些结论可以相信
## 8. 最终带走什么
## 可选科研绘图 Briefs
```

### `阅读导航`

Keep this compact. Record `complete|partial`, recommended reading path, conclusion-changing source gaps, paper/code versions, and a one-sentence credibility judgment. Do not begin with an exhaustive source inventory.

### `1. 先把论文放回领域里`

In roughly 600–1000 Chinese characters, explain the real task, significance, difficulty, mainstream framing, and the paper's entry gap. Separate field consensus from author framing. Include only concepts used later.

### `2. 三分钟看懂这篇论文`

In roughly 900 Chinese characters, give the task, central tension, thought chain, minimal data flow, overall experimental verdict, and largest credibility risk. This section must stand alone but cannot replace the deep reading.

### Guided deep-reading sections

Develop every core section as:

```text
本节结论
→ 直观解释
→ 必要的技术展开
→ 这对论文结论意味着什么
```

Keep paragraphs to one main judgment and usually 3–5 sentences. Use Chinese-first prose. At first mention, add an English term only when needed for paper/code mapping; preserve proper names, metrics, identifiers, paths, and author-defined modules.

The data and model sections start from one concrete sample. The model section includes one simplified Mermaid data-flow diagram when supported. Mark inferred edges or shapes explicitly in prose.

Organize experiments by question, not table number. A core experiment may end with:

```text
作者想证明：...
当前证据：...
我们的判断：...
```

Rank critical-review issues as: core-conclusion threats, generalization/reproducibility limits, then secondary reporting issues. End by separating what can be believed, provisionally believed, not concluded, and the smallest decisive next experiment.

The final section answers only: the real contribution, the transferable idea, and the most important next experiment.

Use paragraph-level evidence IDs such as `〔E03〕` and `〔E12–E15〕`. Explicitly name paper report, code behavior, inference, missing information, or conflict when that status changes interpretation.

## Appendices

### `appendices/evidence-ledger.md`

Use columns: evidence ID, label, source, version/commit, locator, supported statement, and access status. This file owns the six evidence labels and complete locators.

### `appendices/data-training.md`

Record full provenance, construction, counts, splits, preprocessing, leakage checks, objectives, stages, hyperparameters, compute, checkpoint selection, and paper-code differences.

### `appendices/model-dataflow.md`

Record the concrete sample trace plus a table with stage, semantic object, shape, operation, output, code anchor, and evidence ID.

### `appendices/experiment-matrix.md`

Use columns: experiment ID, type, question/claim, changed variable, controls, data/split, metric, result, supported conclusion, unsupported conclusion, and evidence IDs.

### `appendices/critical-review.md`

Separate internal validity, reproducibility, domain validity, external checks, alternative explanations, applicability, and unresolved questions. Rank issues by effect on the central conclusion.

## Main/Appendix Boundary

The main report keeps background, causal reasoning, primary data flow, core experiment judgments, and conclusion-changing conflicts. Move exhaustive configurations, complete shape/interface inventories, secondary conflicts, all experiment rows, and full source locators to appendices.

Self-contained means the reader can understand the research story and judgments without opening appendices; it does not mean duplicating every audit entry.

## Optional Figure Handoff

Include at most three briefs, only when a visual materially improves understanding. Each brief contains purpose/reader, figure type, entities/relationships, evidence IDs, visual hierarchy, and content that must not be invented.

Do not generate images automatically. If `sci-ai-figure` is installed and the user explicitly asks for a figure, pass the brief as the handoff contract.
