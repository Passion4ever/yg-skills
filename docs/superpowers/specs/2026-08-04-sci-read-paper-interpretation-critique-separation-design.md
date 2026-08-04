# `sci-read-paper` Interpretation/Critique Separation Design

## Purpose

The main report should first help the reader reconstruct the paper on its own terms, then switch explicitly into reviewer mode. Critical depth is preserved, but strong evaluative judgments stop interrupting the explanation before the reader has a stable model of the work.

This is a narrative-boundary change only. It does not add files, reduce evidence checks, weaken paper-code conflict reporting, or change standard/audit mode.

## Core Reading Sequence

```text
理解作者（Sections 1–6）
→ 集中审查作者（Section 7）
→ 形成自己的结论（Section 8）
```

Sections 1–6 answer: “What did the authors think, build, run, and observe?”

Section 7 answers: “Do those observations justify the claims, and what else could explain them?”

Section 8 answers: “What should the reader retain after combining both views?”

## Soft Separation

Use soft rather than absolute separation. A conclusion-changing fact must not be hidden until Section 7, but its early form is a neutral evidence boundary rather than a developed verdict.

Early boundary format:

```text
证据边界：论文报告……；公开代码/数据实际显示……。这一差异对结论的影响在第 7 节集中评估。〔E…〕
```

The boundary may state paper behavior, code behavior, missing material, or direct conflict. It must not rank severity, propose alternative explanations, declare a claim invalid, or repeat the full critique.

## Section Responsibilities

### Reading guide

Record mode/status, versions, missing artifacts, generated files, and reading path. Replace the opening credibility verdict with two navigation lines:

- `作者主线：` one sentence describing the paper's intended contribution.
- `审查入口：` one sentence naming the issue evaluated in Section 7 without giving the final verdict.

### Section 1 — Field background

Explain the real task, stakes, difficulty, mainstream framing, and entry gap. Separate field consensus from author framing. Do not assess this paper's success here.

### Section 2 — Three-minute map

Give the author's task, central tension, causal design, minimal data flow, and reported experimental outcome. End with one `审查预告` sentence that names the largest evidence question and points to Section 7. Do not develop the answer.

### Section 3 — Author thought chain

Reconstruct limitation → hypothesis → design choice → intended evidence → claimed contribution. Explain why each choice is reasonable from the authors' perspective. Use a neutral evidence boundary only where paper and implementation facts differ materially.

### Sections 4–5 — Data/training and model flow

Explain what the sample is, how it is constructed, how it moves, and what the implementation does. Paper-code differences remain visible as factual boundaries. Move severity, leakage implications, alternative mechanisms, and credibility judgments to Section 7.

### Section 6 — Experiments

Organize by research question and use:

```text
作者要回答：...
实验怎么做：...
观察到什么：...
证据边界：...
```

`证据边界` records missing controls, uncertainty, unavailable artifacts, or an immediate design limitation in neutral language. Remove `我们的判断` from Section 6. The cumulative judgment belongs to Section 7.

### Section 7 — Critical review

Concentrate all reviewer-mode reasoning here. Start with a short transition making the mode switch explicit. Rank issues by effect on the central conclusion and use compact review cards:

```text
审查议题：...
作者主张：...
支持证据：...
反证或替代解释：...
对中心结论的影响：...
最小解决实验：...
```

Reference earlier evidence IDs and explanation sections instead of re-copying data flow or experiment details. End with: can believe, provisionally believe, cannot conclude.

### Section 8 — Final takeaways

Separate two subsections:

- `方法上值得带走什么`: the genuine idea, design lesson, and transferable method.
- `最终可以相信到哪里`: the calibrated conclusion after Section 7.

This prevents a useful methodological idea from being buried by criticism while preventing the contribution summary from silently restoring rejected claims.

## Language Boundary

Before Section 7, prefer descriptive language: “论文报告”, “代码执行”, “当前材料缺少”, “两者存在差异”, and “留待第 7 节评估”.

Concentrate evaluative language in Section 7: “核心威胁”, “替代解释”, “证据不足”, “不支持”, “不能推出”, and “结论需要降级”.

Direct logical facts remain direct facts. For example, a sequence documented decades earlier is not new; the early section may state the prior identity, while Section 7 evaluates what that does to novelty and biological-function claims.

## Output and Evidence Behavior

- Keep `deep-reading.md` plus `evidence-ledger.md` in standard mode.
- Keep all six Markdown files in explicit audit mode.
- Keep lightweight evidence IDs and all six evidence labels.
- Keep conclusion-changing conflicts in the main report.
- Keep Chinese-first prose and the concrete-sample requirement.
- Keep optional `sci-ai-figure` handoff explicit-user-only.

## Validation

Add structural tests that fail until the contract:

- declares the three-phase reading sequence;
- defines the neutral `证据边界` handoff;
- removes `我们的判断` from the Section 6 template;
- defines Section 7 review cards;
- defines both Section 8 subsections;
- preserves the existing modes, headings, evidence rules, and scientific gates.

Create a visible before/after excerpt using the existing SiamProm report as source material. Do not rerun paper retrieval. Rewrite only representative excerpts for the three-minute map, one experiment, and the Section 7 transition, so the user can judge the narrative separation directly.

## Success Criteria

- A reader can understand the author's logic through Section 6 without repeatedly switching into reviewer mode.
- Conclusion-changing conflicts are still visible before Section 7 as neutral facts.
- Strong criticism is easier to find because it is concentrated and ranked.
- Section 7 does not duplicate the earlier technical explanation.
- Section 8 clearly separates transferable method value from final evidential confidence.

## Non-Goals

- Making the report less critical.
- Hiding paper-code conflicts until the end.
- Adding a default `critical-review.md` file.
- Shortening every report regardless of paper complexity.
- Re-running the completed SiamProm research trial.
