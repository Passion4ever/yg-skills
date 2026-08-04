# Output Contract

Deliver one offline, self-contained HTML file from a stable paper slug. Start from `../assets/report-template.html`; preserve its semantic structure and component classes while replacing all template placeholders with escaped report content.

## Standard Mode — Default

Required output:

```text
<paper-slug>.html
```

The file contains the complete eight-section reading, an embedded evidence ledger, report/version information, and optional collapsed figure briefs. Do not leave working notes or intermediate artifacts in the final output directory.

## Audit Mode — Explicit

Required output:

```text
<paper-slug>-audit.html
```

Keep the same primary report and embedded evidence ledger, then add four collapsed audit panels after Section 8: `data-training`, `model-dataflow`, `experiment-matrix`, and `critical-review`. Audit mode adds traceability, not a second narrative or extra files.

## Primary Report

Use exactly these section IDs, titles, and order inside `<main>`:

```html
<section id="section-1">为什么要做这项研究：背景、现状与本文切入点</section>
<section id="section-2">三分钟建立论文全局地图</section>
<section id="section-3">从问题到方法：作者为什么这样设计</section>
<section id="section-4">数据从哪里来，又怎样进入训练</section>
<section id="section-5">模型内部：数据怎样一步步变成输出</section>
<section id="section-6">实验逻辑：每项实验在回答什么问题</section>
<section id="section-7">批判性审查：证据究竟支持到哪里</section>
<section id="section-8">读完这篇论文，真正应该带走什么</section>
```

Follow this narrative sequence: 理解作者（Sections 1–6） → 集中审查作者（Section 7） → 形成自己的结论（Section 8）.

## Header and Navigation

Do not create a `阅读导航` report section. Keep the header metadata compact: record `mode: standard|audit`, `complete|partial`, paper identity, DOI/stable ID, and access date. Fill three summary cards:

- `作者主线`: intended contribution, without a verdict;
- `证据状态`: conclusion-changing gaps and the smallest resolving material;
- `审查入口`: the issue assessed in Section 7, without developing the answer.

Keep the template's eight-link table of contents and quick link to Section 2. Do not include a generated-file inventory.

## Footer Provenance

Immediately before the embedded evidence ledger, use a collapsed disclosure named `来源、版本与未解决问题`. Record the paper version, code commit, conclusion-changing unavailable artifacts, affected claims, and smallest resolving material there. Do not duplicate this full provenance block in the hero.

## Section Responsibilities

### Section 1 — Background → Progress → Gap → Entry

Begin with literal model input and prediction target. Keep the target separate from dataset sampling/annotation proxies and the underlying biological mechanism. Then explain significance, field progress, the decisive remaining limitation, and how the paper enters that gap. Do not list literature or assess whether the paper succeeds.

### Section 2 — Three-Minute Map

Give the prediction task and central tension, author's overall solution, minimal data flow, two or three central reported results, and one `审查预告` pointing to Section 7. It must stand alone without replacing the deep read.

### Section 3 — Reconstructed Design Logic

State that the sequence is an evidence-based reconstruction, not the authors' private chronology. For each major choice explain problem → author hypothesis → design → intended effect → reason the next choice is needed. Leave detailed data, shapes, and judgments to later sections.

### Section 4 — Data and Training

Track one concrete sample through source/version, inclusion and label construction, deduplication/preprocessing, dataset composition, split unit, batch/pair/conditioning, objectives, stages, key hyperparameters, and checkpoint selection. Stop at model input and training signal.

### Section 5 — Model Data Flow

Continue the same sample inside the model. Include one supported inline SVG or semantic flow, then explain semantic object, shape/structure, operation, information gained or lost, design purpose, next destination, and paper/code status at each main stage. Explain intuition before equations. A computational output is not automatically a biological, chemical, or clinical fact.

### Section 6 — Experiment Logic

Start with an experiment map distinguishing main/baseline comparison, control, ablation, robustness/generalization, analysis, case study, and external validation. Organize experiments by question, not table number. Use:

```text
作者要回答什么：...
实验类型：...
实验怎样设计：...
改变了什么，控制了什么：...
数据与指标：...
实际观察到什么：...
作者据此主张什么：...
证据边界：...
```

Separate observation from author interpretation. Do not add `我们的判断`; cumulative evaluation belongs in Section 7.

### Section 7 — Critical Review

Open with an explicit switch into reviewer mode. Separate data/method, computational performance, generalization, mechanism/domain-fact, and novelty claims. Rank central-conclusion threats first, generalization/domain validity second, reproducibility third, and secondary issues last. Use review cards:

```text
审查议题：...
作者主张：...
支持证据：...
反证或替代解释：...
证据缺少什么：...
对中心结论的影响：...
最小解决实验：...
```

Calibrate impact as no material effect, reduced confidence, narrowed scope, weaker supported claim, or rejected claim. End with `可以相信`, `可以暂时相信`, `当前不能推出`, and `被现有证据否定` as applicable.

### Section 8 — Final Synthesis

Use `论文真正贡献了什么`, `最终可以相信到哪里`, and `如果继续这项研究，下一步最该做什么`. Separate transferable method value from evidential confidence; recommend only one to three decisive next experiments or changes.

## Interpretation/Critique Boundary

Develop Sections 1–6 as:

```text
本节要理解什么
→ 作者为什么这样设计
→ 必要的技术展开
→ 这一部分在作者论证中的作用
```

Keep one explanatory purpose per paragraph and usually 3–5 sentences. Use Chinese-first prose. Retain English only for precise names, metrics, code mapping, identifiers, and author-defined modules.

When any conclusion-changing fact appears—including a paper-code/data conflict, missing material, external correction, or direct logical fact—use a compact neutral handoff. For a conflict, state both the paper's report and what released evidence shows.

```text
证据边界：相关材料显示……。这是理解论文必须知道的事实；其对结论的影响在第 7 节集中评估。〔E…〕
```

The boundary states facts. Severity, alternatives, claim downgrades, and verdicts belong in Section 7.

## Embedded Evidence Ledger

Place the complete ledger in `<details id="evidence-ledger">` in the footer. Each record keeps evidence ID, one of `[论文] [代码] [外部核验] [推断] [缺失] [冲突]`, source, version/commit, locator, supported statement, and access status.

Every main-report citation is an internal link such as `<a class="evidence-link" href="#E03">〔E03〕</a>`, and every ledger record has a unique matching ID such as `<tr class="ledger-row" id="E03">`. A range or cluster must link each cited claim to a resolvable record; never use evidence styling without a target.

## UI and Offline Contract

- Preserve the template's publication-style hero, three summary cards, sticky numbered TOC, readable 820–900 px text column, evidence boundaries, experiment cards, review cards, graded takeaways, responsive tables, and print CSS.
- Keep CSS inline. Do not use external stylesheets, fonts, scripts, Mermaid, MathJax, iframes, or non-data-URI images.
- Escape all paper/code/data text before inserting it as HTML. Do not copy source event handlers or executable markup.
- Use semantic HTML, visible focus states, labels in addition to color, `prefers-reduced-motion`, a single-column layout below 900 px, and print rules that expose collapsed evidence.
- External evidence URLs may require network access, but reading and navigating the report must work offline.

## Main/Audit Boundary

The primary report keeps background, causal reasoning, one sample, primary model flow, core experiment logic, conclusion-changing facts, calibrated review, and final synthesis. Audit panels own exhaustive configurations, complete interfaces/shapes, every experiment row, and expanded reproducibility inventories. Reference earlier sections and evidence IDs rather than duplicating prose.

## Optional Figure Handoff

Keep at most three collapsed briefs only when a visual materially improves understanding. Each brief contains purpose/reader, figure type, entities/relationships, evidence IDs, visual hierarchy, and content that must not be invented.

Do not generate images automatically. If `sci-ai-figure` is installed and the user explicitly asks, pass the brief as the handoff contract. Embed an explicitly requested final image as a data URI when the report must remain one file.
