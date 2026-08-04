# Output Contract

Create one directory from a stable paper slug. `deep-reading.md` is always the primary reading path.

## Standard Mode — Default

Required output:

```text
<paper-slug>/
├── deep-reading.md
└── evidence-ledger.md
```

Standard mode does not require the four audit appendices. It may add at most one targeted appendix from the audit schemas below only when a conclusion-changing conflict cannot be explained and audited succinctly in the two required files. State the reason in `阅读导航`; otherwise record unresolved audit detail once and offer audit mode as the next step.

## Audit Mode — Explicit

Use only for explicit exhaustive audit, reproduction preparation, a full experiment matrix, or file-by-file code comparison:

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

Audit mode adds traceability, not a second copy of the narrative. The complete dossier contains six Markdown files.

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

Follow this narrative sequence: 理解作者（Sections 1–6） → 集中审查作者（Section 7） → 形成自己的结论（Section 8）.

### `阅读导航`

Keep it compact. Record `mode: standard|audit`, `complete|partial`, recommended reading path, conclusion-changing gaps, paper/code versions, and generated files. Add `作者主线：` with the intended contribution and `审查入口：` with the issue evaluated in Section 7, without giving the verdict. Do not begin with a source inventory.

### `1. 先把论文放回领域里`

In roughly 600–1000 Chinese characters, explain the real task, significance, difficulty, mainstream framing, and the paper's precise entry gap. Separate field consensus from author framing and include only concepts used later.

### `2. 三分钟看懂这篇论文`

In roughly 900 Chinese characters, give the task, central tension, thought chain, minimal data flow, and reported experimental outcome. End with one `审查预告：` sentence naming the largest evidence question and pointing to Section 7; do not develop the answer. It must stand alone without replacing the deep reading.

### Guided deep-reading sections

Develop Sections 1–6 as:

```text
本节要理解什么
→ 作者为什么这样设计
→ 必要的技术展开
→ 这一部分在作者论证中的作用
```

Keep one explanatory purpose per paragraph and usually 3–5 sentences. Use Chinese-first prose. Retain English only for precise names, metrics, code mapping, identifiers, and author-defined modules.

Keep one concrete sample identifiable across data construction, training, model flow, and output. Include one simplified Mermaid data-flow diagram when supported; mark inferred edges or shapes in prose.

Sections 1–6 explain the authors' problem, choices, implementation, and observations. When any conclusion-changing fact appears—including a paper-code/data conflict, missing material, external correction, or direct logical fact—use a compact neutral handoff. For a conflict, state both the paper's report and what released evidence shows.

```text
证据边界：相关材料显示……。这是理解论文必须知道的事实；其对结论的影响在第 7 节集中评估。〔E…〕
```

The boundary states facts. Severity ranking, alternative explanations, claim downgrades, and final verdicts belong in Section 7.

Organize experiments by question, not table number. End a core question with:

```text
作者要回答：...
实验怎么做：...
观察到什么：...
证据边界：...
```

Open Section 7 with an explicit transition into reviewer mode. Rank criticism as central-conclusion threats, generalization/reproducibility limits, then secondary issues. Use compact review cards:

```text
审查议题：...
作者主张：...
支持证据：...
反证或替代解释：...
对中心结论的影响：...
最小解决实验：...
```

Reference earlier explanations and evidence IDs instead of repeating data flow or result tables. End Section 7 by separating what can be believed, provisionally believed, and not concluded.

Section 8 contains `### 方法上值得带走什么` for the genuine contribution and transferable design lesson, followed by `### 最终可以相信到哪里` for the calibrated conclusion after review.

Use paragraph-level evidence IDs such as `〔E03〕` and `〔E12–E15〕`. Explicitly name paper report, code behavior, inference, missing information, external check, or conflict when that status changes interpretation.

## Evidence Ledger

`evidence-ledger.md` is required in both modes. Use columns: evidence ID, label, source, version/commit, locator, supported statement, and access status. It owns the six evidence labels and full locators.

## Audit Appendix Schemas

### `appendices/data-training.md`

Record full provenance, construction, counts, splits, preprocessing, leakage checks, objectives, stages, hyperparameters, compute, checkpoint selection, and paper-code differences.

### `appendices/model-dataflow.md`

Record the concrete-sample trace plus stage, semantic object, shape, operation, output, code anchor, and evidence ID.

### `appendices/experiment-matrix.md`

Record experiment type, question, changed variable, controls, data/split, metric, result, supported conclusion, unsupported conclusion, and evidence IDs.

### `appendices/critical-review.md`

Separate internal validity, reproducibility, domain validity, external checks, alternatives, applicability, and unresolved questions. Rank issues by effect on the central conclusion.

## Main/Audit Boundary

The main report keeps background, causal reasoning, primary sample and model flow, core experiment judgments, and conclusion-changing conflicts. The ledger owns source locators. Audit appendices own exhaustive configurations, full shapes/interfaces, secondary conflicts, every experiment row, and extended reproducibility inventories.

Self-contained means the reader understands the research story and judgments without an appendix; it does not mean duplicating audit entries.

## Optional Figure Handoff

Include at most three briefs only when a visual materially improves understanding. Each brief contains purpose/reader, figure type, entities/relationships, evidence IDs, visual hierarchy, and content that must not be invented.

Do not generate images automatically. If `sci-ai-figure` is installed and the user explicitly asks for a figure, pass the brief as the handoff contract.
