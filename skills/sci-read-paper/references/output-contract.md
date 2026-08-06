# Output Contract

Deliver one offline, self-contained HTML file from a stable paper slug. Start from `../assets/report-template.html`; preserve its semantic structure and component classes while replacing all template placeholders with escaped report content.

## Build Procedure

Never type the report from scratch and never retype the template CSS; the stylesheet must survive byte-for-byte.

1. Write to `<outdir>/<paper-slug>.html`, or `<outdir>/<paper-slug>-audit.html` in `audit` mode. Use the user's working directory as `<outdir>` unless they name one, and report the absolute path when you finish.
2. Copy `../assets/report-template.html` to that path.
3. Replace `{{REPORT_BODY}}` with eight empty section shells first — `id`, `class="report-section"`, chapter label, `<h2>` title, and reading cue — so the skeleton exists before any prose does.
4. Fill one section per edit, then the remaining placeholders. Editing in place keeps a truncated write visible as a leftover `{{TOKEN}}` instead of a silently short report.
5. Run the validator. Fix every reported violation and re-run until it exits `0`. Do not describe the report as finished before that.

   ```bash
   python3 <skill-dir>/scripts/validate_report.py --figure <off|brief|generate> <delivered file>
   ```

   `<skill-dir>` is the directory holding `SKILL.md`; the report path is relative to the user's working directory, not the skill.

The template has ten placeholders and every one must be resolved — two by deletion:

| Placeholder | Where | Replace with |
|---|---|---|
| `{{DISPLAY_TITLE}}` ×3 | `<title>`, sidebar header, hero `<h1>` | short Chinese display title, e.g. `SiamProm 深度精读` |
| `{{PAPER_SUBTITLE}}` ×2 | `<title>`, hero | the complete original paper title |
| `{{SIDEBAR_SUBTITLE}}` | sidebar header | one compressed line identifying the paper |
| `{{REPORT_META}}` | hero | status badges and journal/DOI/access-date spans |
| `{{SUMMARY_ROWS}}` | hero `论文速览` | the three labeled rows |
| `{{REPORT_BODY}}` | `<main>` | the eight sections |
| `{{FIGURE_OUTPUT}}` | `<main>` | `<section id="figure-output">…</section>`, or **delete the whole line** when `figure=off` |
| `{{AUDIT_PANELS}}` | `<main>` | the four audit panels, or **delete the whole line** in `standard` mode |
| `{{REPORT_DETAILS}}` | footer disclosure | provenance, versions, unresolved gaps |
| `{{EVIDENCE_LEDGER}}` | footer disclosure | the complete ledger table |

## Standard Mode — Default

Required output:

```text
<paper-slug>.html
```

The file contains the complete eight-section reading, an embedded evidence ledger, and report/version information. With the default `figure=off`, it contains no figure material. Do not leave working notes or intermediate artifacts in the final output directory.

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

Open every section with a sequential label, its exact title, and a one-sentence neutral reading cue:

```html
<p class="chapter-label">CHAPTER 01</p>
<h2>为什么要做这项研究：背景、现状与本文切入点</h2>
<p class="chapter-intro">本章要建立……</p>
```

Continue through `CHAPTER 08`. Primary sections are continuous article chapters, not cards: do not give the section container a background, border, radius, or shadow.

## Header and Navigation

Do not create a `阅读导航` report section. Use a short Chinese display title such as `SiamProm 深度精读`, then preserve the complete original paper title as the subtitle. Keep the metadata compact: record `mode: standard|audit`, `complete|partial`, journal identity, DOI/stable ID, and access date.

Record the mode and status as separate badges, `<span class="status-badge">mode: standard</span><span class="status-badge">partial</span>`. Do not add a `figure:` badge; the figure mode is not report metadata.

Use one compact `论文速览` block with three labeled rows, not three cards. Each row is `<div class="quick-view-row"><strong>标签</strong><p>……</p></div>` — the template styles `p` inside a row and does not style `span`:

- `作者主线`: intended contribution, without a verdict;
- `证据状态`: conclusion-changing gaps and the smallest resolving material;
- `审查入口`: the issue assessed in Section 7, without developing the answer.

Use the fixed dark sidebar and group links as `论文概览` (Sections 1–2), `问题与方法` (3–5), `实验与审查` (6–7), `最终结论` (8), and `报告附录` (provenance and ledger). Do not add unfinished links or a generated-file inventory.

## Footer Provenance

Immediately before the embedded evidence ledger, use the disclosure named `来源、版本与未解决问题`. Record the paper version, code commit, conclusion-changing unavailable artifacts, affected claims, and smallest resolving material there. Do not duplicate this full provenance block in the hero.

Keep both footer disclosures marked `open`, as the template ships them. A closed `<details>` is hidden in print and PDF, which would strand every `〔E…〕` in the report body.

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

All eight fields appear in every card, in this order, each as one `<strong>` label. `validate_report.py` enforces the set and the order, so a card that drops `数据与指标` or renames `实际观察到什么` fails rather than drifting.

The `证据边界` field **is** a boundary, not a pointer to one: it carries its own `B01`-style id on the element holding it, exactly like a standalone boundary. When an experiment raises no conclusion-changing fact, write `证据边界：无` — that needs no id. A card whose boundary needs more than one fact gets one boundary per fact, the extras as `<aside>` blocks after the card.

Separate observation from author interpretation. Do not add `我们的判断`; cumulative evaluation belongs in Section 7.

### Section 7 — Critical Review

Open with an explicit switch into reviewer mode. Separate data/method, computational performance, generalization, mechanism/domain-fact, and novelty claims. Rank central-conclusion threats first, generalization/domain validity second, reproducibility third, and secondary issues last. Use review cards:

```text
处理的证据边界：B02、B05
审查议题：...
作者主张：...
支持证据：...
反证或替代解释：...
证据缺少什么：...
对中心结论的影响：...
最小解决实验：...
```

Every boundary raised in Sections 1–6 must be discharged here. A card claims the boundaries it assesses by linking each one, `<a class="boundary-link" href="#B02">B02</a>`; write `无` when a card answers a question no boundary raised. Close the section with `<section id="no-effect-boundaries">无实质影响的证据边界</section>`, linking every remaining boundary once with a one-clause reason. The link only counts from inside a review card or that closing block — a passing mention elsewhere is not a discharge, and `validate_report.py` fails on both an unlinked and a merely-mentioned boundary.

Keep one boundary to one fact. A boundary bundling four unreported items can be linked by a card that addresses one of them, and the validator cannot tell the difference; a card discharges a boundary only by naming what that boundary asserts, in its own `反证或替代解释` or `证据缺少什么`.

Calibrate impact as no material effect, reduced confidence, narrowed scope, weaker supported claim, or rejected claim. End with `可以相信`, `可以暂时相信`, `当前不能推出`, and `被现有证据否定` as applicable. Each verdict must survive every boundary that touches it: do not endorse a comparison a boundary flagged as confounded.

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

## Readability

A reader who has to re-read a sentence to parse it has been failed, however correct the content is. `validate_report.py` measures paragraph and list prose only — tables, code and flow diagrams are exempt — and fails a report whose sentences run long:

- no sentence past **120 characters**; that length is a run-on, not a dense sentence;
- 90th-percentile sentence at or under **80 characters**; the long tail is what makes a report feel impenetrable, so trimming only the worst offender does not pass;
- median near **45 characters**, and a warning above it.

Split a long sentence at its seams rather than compressing it: one clause that states the fact, one that states what follows from it. Semicolon chains carrying three independent claims are three sentences.

**Gloss the load-bearing terms.** The first time an English concept word appears, say in plain Chinese what it means, then use the term freely:

```text
✗ 第一是 motif amortization，第二是 motif guidance。
✓ 第一条路线是"把条件训进模型"（motif amortization）：训练时就把 motif 作为输入喂进去。
```

Expand an acronym once at first use. A term a domain reader knows still needs its gloss — the report is read by someone entering the field, not by the paper's authors. The validator warns when Latin script exceeds 35% of the prose, which usually means terms are being repeated instead of explained.

When any conclusion-changing fact appears—including a paper-code/data conflict, missing material, external correction, or direct logical fact—use a compact neutral handoff. For a conflict, state both the paper's report and what released evidence shows.

Give every boundary a sequential ID on the element that holds its text, so Section 7 can be checked against it. There are exactly two shapes:

```html
<aside class="evidence-boundary" id="B02">…</aside>          <!-- standalone, anywhere in Sections 1–6 -->
<li id="B06"><strong>证据边界：</strong>…</li>                <!-- the experiment card's own field -->
```

The `evidence-boundary` class carries the styling and the `:target` highlight that Section 7's links jump to; use it for every standalone boundary. A `证据边界` with no B-id fails validation unless its whole value is `无`.

```text
证据边界：相关材料显示……。这是理解论文必须知道的事实；其对结论的影响在第 7 节集中评估。〔E…〕
```

The boundary states facts. Severity, alternatives, claim downgrades, and verdicts belong in Section 7. Raising a boundary is a promise; Section 7 keeps it.

## Embedded Evidence Ledger

Place the complete ledger in `<details id="evidence-ledger">` in the footer. Each record keeps evidence ID, one of `[论文] [代码] [外部核验] [推断] [缺失] [冲突]`, source, version/commit, locator, supported statement, and access status.

Every ledger record is a row with a unique matching ID, `<tr class="ledger-row" id="E03">`. Cite it with one anchor per ID, and keep `〔`, `、`, and `〕` outside the anchors so every link's visible text is exactly one resolvable evidence ID:

```html
〔<a class="evidence-link" href="#E01">E01</a>、<a class="evidence-link" href="#E02">E02</a>〕
```

Never write a range, never wrap punctuation in an anchor, and never use evidence styling without a target.

## UI and Offline Contract

- Preserve the template's technical-monograph hero, fixed `280px` dark grouped sidebar, compact `论文速览`, continuous chapters, readable 820–860 px text column, evidence boundaries, experiment cards, review cards, graded takeaways, responsive tables, and print CSS.
- Keep the template's single `<style>` element byte-for-byte. Express every report-specific need with the classes it already defines; a second stylesheet or an edited rule means the report was not built from the template.
- Keep CSS inline. Do not use external stylesheets, fonts, scripts, Mermaid, MathJax, iframes, or non-data-URI images.
- Escape all paper/code/data text before inserting it as HTML. Do not copy source event handlers or executable markup.
- Use semantic HTML, visible focus states, labels in addition to color, `prefers-reduced-motion`, a basic single-column fallback below 900 px, and print rules that hide the sidebar and expose collapsed evidence. Do not add a mobile navigation drawer in the desktop-first report.
- External evidence URLs may require network access, but reading and navigating the report must work offline.

## Main/Audit Boundary

The primary report keeps background, causal reasoning, one sample, primary model flow, core experiment logic, conclusion-changing facts, calibrated review, and final synthesis. Audit panels own exhaustive configurations, complete interfaces/shapes, every experiment row, and expanded reproducibility inventories. Reference earlier sections and evidence IDs rather than duplicating prose.

## Figure Mode

Select `mode` and `figure` independently:

```text
mode=standard|audit, figure=off|brief|generate
```

All figure output lives in one `<section id="figure-output">` replacing the `{{FIGURE_OUTPUT}}` placeholder after Section 8. Pass the selected mode to the validator with `--figure`; it checks both directions, so a `figure=brief` report validated as `off` fails, and so does an `off` report that emitted figure UI.

- `figure=off` is the default. Delete the `{{FIGURE_OUTPUT}}` line and emit no figure heading, brief, image, empty disclosure, or other figure UI.
- Select `figure=brief` when the user asks for a figure plan, visual brief, or drawing proposal. Render at most three collapsed briefs inside `#figure-output`. Do not invoke a figure-generation skill.
- Select `figure=generate` when the user asks to create, draw, or generate a scientific figure. When `sci-diagram` is available, invoke it from the brief as a handoff contract and embed at most three usable generated images inside `#figure-output` as data URIs with concise captions, alt text, and evidence IDs. Do not expose the internal handoff brief by default.

Each brief contains purpose/reader, figure type, entities and relationships, evidence IDs, visual hierarchy, and content that must not be invented.

If generation is unavailable or fails before producing a usable image, finish the reading, fall back to `figure=brief`, and state the reason once. This fallback does not change the paper-reading completion status.
