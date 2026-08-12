# Output Contract

One offline, self-contained HTML file per paper. Three artifacts own the parts of
it that never vary, so this document only has to explain the parts that do:

| Artifact | Owns |
|---|---|
| `../assets/report-template.html` | page shell, stylesheet, sidebar, the eight section headings, Section 8's three subheadings |
| `../assets/fragments.html` | every repeated structure — cards, boundaries, ledger rows, citations, verdicts — and the closed vocabularies they draw on |
| `../scripts/validate_report.py` | the mechanical rules, checked against the delivered file |

Copy from the first two rather than typing markup; whatever you invent instead
is what makes two readings of two papers look like two different skills.

## Build

```bash
python3 <skill-dir>/scripts/new_report.py --slug <paper-slug> --outdir <outdir> \
        [--mode standard|audit] [--figure off|brief|generate]
```

It writes the skeleton, resolves everything the two flags already determine, and
prints the remaining `{{PLACEHOLDER}}` list. Use the user's working directory as
`<outdir>` unless they name one, and report the absolute path when you finish.

Fill one placeholder per edit. Editing in place keeps a truncated write visible
as a leftover `{{TOKEN}}` rather than a silently short report. Never retype the
stylesheet; it must survive byte-for-byte.

```bash
python3 <skill-dir>/scripts/validate_report.py <delivered file>
```

Fix every violation and re-run until it exits `0`. The report records its own
mode and figure setting, so the validator checks the modes it was actually built
in — do not describe the report as finished before it passes.

## What each section establishes

The eight titles are fixed in the template. Sections 1–6 explain the paper as its
authors would, Section 7 judges it, Section 8 concludes. Each opens with a
one-sentence neutral reading cue in `{{CUE_n}}`.

**1 — Background → progress → gap → entry.** Begin with the literal model input
and prediction target, kept separate from sampling or annotation proxies and from
the biological mechanism. Then significance, field progress, the decisive
remaining limitation, and how the paper enters it. Not a literature review, and
no verdict on whether the paper succeeds.

**2 — Three-minute map.** Prediction task and central tension, the author's
overall solution, minimal data flow, two or three central reported results, and
one `审查预告` pointing at Section 7. It stands alone without replacing the read.

**3 — Reconstructed design logic.** Say that the sequence is an evidence-based
reconstruction, not the authors' private chronology. Per major choice: problem →
author hypothesis → design → intended effect → why the next choice is needed.

**4 — Data and training.** Track one concrete sample through source/version,
inclusion and label construction, deduplication, dataset composition, split unit,
batching or conditioning, objectives, stages, key hyperparameters, and checkpoint
selection. Stop at model input and training signal.

**5 — Model data flow.** Continue the same sample inside the model. Include one
flow diagram, then per main stage: semantic object, shape, operation, information
gained or lost, design purpose, next destination, and paper/code status.
Intuition before equations. A computational output is not a biological,
chemical, or clinical fact.

**6 — Experiment logic.** Open with a map distinguishing the experiment types,
then one experiment card per research question — organised by question, not by
table number. Separate observation from author interpretation; cumulative
judgement belongs in Section 7, so do not add `我们的判断`.

**7 — Critical review.** Open by switching explicitly into reviewer mode. Rank
central-conclusion threats first, generalisation and domain validity second,
reproducibility third, secondary issues last. One review card per issue, then the
`无实质影响的证据边界` list, then the graded verdicts. Every verdict must survive
every boundary that touches it: do not endorse a comparison a boundary flagged as
confounded.

**8 — Final synthesis.** Under the three fixed subheadings, separate transferable
method value from evidential confidence, and recommend only one to three decisive
next experiments or changes.

## The interpretation/critique wall

Develop Sections 1–6 as 本节要理解什么 → 作者为什么这样设计 → 必要的技术展开 →
这一部分在作者论证中的作用. The four verdict terms may not appear before Section 7;
`validate_report.py` fails a report that leaks one, because a reading that judges
while it explains cannot be checked for having judged fairly.

## Evidence boundaries

Any conclusion-changing fact found in Sections 1–6 — a paper-code conflict,
missing material, an external correction, a direct logical fact — is stated there
as a neutral boundary carrying its own `Bnn` id, and discharged in Section 7. For
a conflict, state both what the paper reports and what released evidence shows.

The boundary states facts only. Severity, alternatives, claim downgrades, and
verdicts belong in Section 7. Raising a boundary is a promise; Section 7 keeps it.

Every boundary declares what kind of thing it is, in `data-kind`: `conflict` when
two statements disagree — including two places in the same paper, such as text
against a figure, a table, or the supplement, not only paper against code — `missing` when nothing reports it, `external` when a
first-party source outside the paper established it, `inference` when it was
reconstructed from cited evidence, `fact` when the paper itself states it and the
statement still narrows what its conclusion supports. The first four must cite a
ledger row carrying the matching label — `[冲突]`, `[缺失]`, `[外部核验]`,
`[推断]`. Recording only where the evidence sits leaves the ledger unable to say
that two rows disagree, and a reading that found four contradictions can log one.

Keep one boundary to one fact. A boundary bundling four unreported items can be
claimed by a card that addresses one of them, and the validator cannot tell the
difference; a card discharges a boundary only by naming what that boundary
asserts, in its own `反证或替代解释` or `证据缺少什么`.

A boundary is discharged from inside a review card or from
`#no-effect-boundaries`, and nowhere else — a passing mention is not a discharge.

## Header, navigation, footer

Use a short Chinese display title such as `SiamProm 深度精读` and keep the complete
original paper title as the subtitle. `{{META_EXTRA}}` holds journal identity,
DOI or stable id, and access date; the mode and completion badges are already in
the template, so do not restate them anywhere else. The three `论文速览` rows are
`作者主线` (intended contribution, no verdict), `证据状态` (conclusion-changing gaps
and the smallest resolving material), and `审查入口` (the Section 7 issue, without
developing the answer). Do not create a `阅读导航` section or add sidebar links.

`{{REPORT_DETAILS}}` records paper version, code commit, conclusion-changing
unavailable artifacts, affected claims, and the smallest resolving material.
`{{EVIDENCE_LEDGER}}` holds the complete ledger table. Both footer disclosures
stay `open`: a closed `<details>` is hidden in print, which would strand every
`〔E…〕` in the body.

## Readability

A reader who has to re-read a sentence to parse it has been failed, however
correct the content is. `validate_report.py` measures paragraph, list and card
prose — tables, code and diagrams are exempt — and fails a report whose sentences
run long: none past **120 characters**, 90th percentile at or under **80**, median
near **45**, and no sentence carrying more than **4** comma-separated clauses.
Split a long sentence at its seams rather than compressing it: one clause that
states the fact, one that states what follows.

The clause limit catches a different failure from the character limits. Every
over-long sentence observed so far was a list — a hyperparameter set, a symbol
legend, three conflicting numbers — written as prose. Put those in a table, which
is exempt from all of these limits precisely because a table is how a reader
scans a list.

Gloss the load-bearing terms. The first time an English concept word appears, say
in plain Chinese what it means, then use the term freely:

```text
✗ 第一是 motif amortization，第二是 motif guidance。
✓ 第一条路线是"把条件训进模型"（motif amortization）：训练时就把 motif 作为输入喂进去。
```

Expand an acronym once at first use. A term a domain reader knows still needs its
gloss — the report is read by someone entering the field, not by the paper's
authors.

Reusing a term you have glossed is not a problem — it is the point of glossing.
Introducing many terms once each is the problem, because every one of them is
vocabulary the reader has to carry and never sees again. The validator counts
distinct English terms per 1000 Chinese characters, naming the ones that appear
once as ordinary words: it warns above **28** and fails above **40**.

Domain proper nouns and acronyms stay in Latin script — `ProteinMPNN`, `QED`,
`AutoDock Vina`, `SMILES`. Ordinary English does not: `achieved` is 达到,
`available` is 可获取, `architecture` is 架构. Reusing a term costs the reader
nothing; introducing one costs them something every time.

## Modes

`mode` and `figure` are independent, and both are recorded in the file by
`new_report.py`.

`standard` delivers `<paper-slug>.html`: the complete eight-section reading, the
embedded ledger, and report information. `audit` delivers `<paper-slug>-audit.html`
and appends exactly four panels — `data-training`, `model-dataflow`,
`experiment-matrix`, `critical-review` — which own exhaustive configurations,
complete interfaces and shapes, every experiment row, and expanded reproducibility
inventories. All four are required, all four ship collapsed, and a standard report
carries none of them; `validate_report.py` checks all three directions.

Panels add traceability, not a second narrative. Reference sections and evidence
IDs instead of duplicating prose, and keep them on the same side of the wall as
Sections 1–6: the four verdict terms may not appear there either, because a
graded judgement in an appendix is one no boundary can be checked against. The
reading-length band is measured on the eight sections alone, so an exhaustive
panel does not push the report out of its own range.

`figure=off` is the default and emits no figure UI at all. `figure=brief` renders
at most three collapsed briefs in `#figure-output` — purpose and reader, figure
type, entities and relationships, evidence IDs, visual hierarchy, and content that
must not be invented — without invoking any figure-generation skill.
`figure=generate` invokes `sci-diagram` from those briefs and embeds at most three
usable images as data URIs with captions, alt text, and evidence IDs. If
generation is unavailable or fails, finish the reading, fall back to
`figure=brief`, and say why once; this does not change the completion status.

## UI and offline

- Express every report-specific need with a class the template stylesheet already
  defines. A class it does not define, a second stylesheet, or an edited rule all
  mean the report was not built from the template, and all three fail validation.
- Keep CSS inline. No external stylesheets, fonts, scripts, Mermaid, MathJax,
  iframes, or non-data-URI images.
- Escape all paper, code, and data text before inserting it as HTML. Never copy
  source event handlers or executable markup.
- External evidence URLs may need the network, but reading and navigating the
  report must work offline.
