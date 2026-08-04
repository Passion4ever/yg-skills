# FrameFlow-Inspired Paper Report Design

## Goal

Rework the desktop `sci-read-paper` report into a compact technical monograph inspired by `frameflow_guide_2.html`. Transfer its information architecture—fixed dark navigation, restrained typography, continuous article flow, and semantic callouts—without copying its external dependencies, interactive widgets, unfinished content, or mobile overflow.

The report remains one offline HTML file with the existing eight-section scientific argument and embedded evidence ledger.

## Alternatives Considered

1. **Surface-only restyle:** recolor the current TOC and cards. Rejected because the large section containers would preserve the current dashboard-like reading experience.
2. **Structural visual migration:** fixed sidebar, continuous article, compact hero, and semantic cards only. Selected because it captures the reference's reading quality while preserving the report contract.
3. **Near-reproduction:** copy web fonts, interactive viewers, scripts, and component styling. Rejected because it conflicts with offline delivery, adds unnecessary dependencies, and carries over the reference's mobile overflow.

## Desktop Information Architecture

Place a fixed `280px` dark sidebar at the left edge. Place a bounded content shell to its right, approximately `900–980px` including internal padding, leaving unused viewport width on the far right. Header, primary report, figure brief, provenance, and evidence ledger share the same article axis.

Group sidebar links by reading purpose:

- `论文概览`: Sections 1–2;
- `问题与方法`: Sections 3–5;
- `实验与审查`: Sections 6–7;
- `最终结论`: Section 8;
- `报告附录`: provenance and evidence ledger.

The sidebar header uses the report's short identity and a one-line domain description. Navigation remains numbered, keyboard accessible, internally linked, fixed, and independently scrollable.

## Hero

Use a compact in-article hero rather than a full-width cover:

1. eyebrow `SCI · DEEP READING`;
2. short Chinese display title, for example `SiamProm 深度精读`;
3. the complete original English paper title as a smaller serif subtitle;
4. mode/status, journal, DOI or stable identifier, and access date;
5. one compact `论文速览` block.

`论文速览` replaces the three summary cards. It contains three labeled rows—`作者主线`, `证据状态`, and `审查入口`—without repeating detailed judgments or provenance.

## Continuous Chapter System

Remove background, border, radius, and shadow from every primary `section.report-section`. Separate chapters through approximately `64–72px` vertical rhythm. Each chapter begins with:

```html
<p class="chapter-label">CHAPTER 01</p>
<h2>为什么要做这项研究：背景、现状与本文切入点</h2>
<p class="chapter-intro">...</p>
```

The chapter label is blue, uppercase, tracked, and small. The Chinese heading uses the local serif stack. The intro is muted and uses a subtle left rule. The body uses approximately `15.5–16px` type, `1.8` line height, and an effective reading width of `820–860px`.

Scope selectors so a heading carrying a copied `report-section` class cannot inherit the chapter container's layout. This removes the current nested-card heading defect.

## Visual Language

Use the reference's restrained family of tokens with local fonts only:

- page background `#fafaf8`;
- article/card background `#ffffff`;
- sidebar `#1a1a2e`;
- primary text near `#2c2c2c`;
- muted text near `#6b6b6b`;
- primary blue near `#4a6fa5`;
- subtle warm borders near `#e2e0d8`;
- small radii around `8–12px` only where a component needs containment.

Use the system sans stack for body copy, the local Chinese/Latin serif stack for display and chapter headings, and the system mono stack for code and tensor shapes. Do not load Google Fonts.

## Semantic Components

Cards are reserved for information that benefits from containment:

- experiment cards: blue accent;
- evidence boundaries: amber accent and light amber surface;
- critical-review cards: red accent and light red surface;
- supported/qualified/rejected takeaways: green, amber, and red;
- model flow, tables, code, and formulas: neutral technical containers.

Avoid wrapping whole chapters in cards. Keep provenance and the evidence ledger as collapsed footer disclosures aligned with the article.

## Offline and Content Constraints

- Keep all CSS inline and use no external font, stylesheet, script, iframe, or network image.
- Preserve Sections 1–8, scientific wording, E01–E24, evidence targets, print rules, and standard/audit naming.
- Do not copy Three.js, Molstar, interactive protein viewers, or reference-page JavaScript.
- Do not add unfinished navigation items.
- Desktop is the acceptance target for this revision. Preserve a basic narrow-screen fallback, but do not design or test a mobile navigation drawer in this scope.

## Verification

Automated checks must prove:

- the sidebar is fixed, `280px`, dark, grouped, and links to every section plus both footer disclosures;
- the hero uses a short display title, full original title, compact metadata, and one `论文速览` block;
- three summary cards are absent;
- every primary section contains a sequential `CHAPTER 01`–`CHAPTER 08` label and has no container border, background, radius, or shadow;
- semantic experiment, evidence, review, and takeaway components remain present;
- all internal links resolve and the single HTML remains self-contained;
- HTML Tidy passes and a `1440x1200` Chromium screenshot matches the intended desktop hierarchy.

The committed SiamProm showcase is updated together with the reusable template so the example remains the visual acceptance fixture.
