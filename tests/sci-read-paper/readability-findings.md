# Readability Findings

## Current-output baseline

Run date: 2026-07-22. Evaluated skill state: `52604ba` plus no readability changes.

### CProMG

Evidence path: `/tmp/sci-read-paper-green.uaO99b/cpromg-raw-created/deep-reading.md`

| Criterion | Score | Concrete evidence |
|---|---:|---|
| Background orientation | 2 | Lines 11–13 frame the task and the two prior routes: “给定一个已知蛋白口袋……写出 SMILES” and “两条各有缺陷的路线”; line 36 states the entry gap: “target-specific generation 需要 pocket 信息”. |
| Three-minute map | 2 | The opening gives the task (line 11), author logic (line 13), minimal conditional flow (lines 17–21), verdict (line 23), and main credibility risk: “Vina 是 docking scoring proxy” (line 25). |
| Causal narrative | 2 | Line 36 makes limitations cause the design: “因此把双尺度 pocket encoder 与 property-prefix autoregressive decoder 组合起来”; lines 40–54 connect each choice and hypothesis to evidence. |
| Concrete sample | 1 | A generic sample appears at line 68: “每条样本由……`*_pocket10.pdb` 和一个 ligand SDF 构成”, but aggregate counts precede it at lines 60–62, so the explanation is not one traceable sample first. |
| Progressive technical depth | 2 | The conclusion and intuition appear first: “模型学到的是条件分布” (line 15); equations follow at lines 17–21 and shapes/configuration later at lines 120‑25. |
| Chinese-first prose | 2 | Natural Chinese carries the explanation—“新增能力来自它们……的组合” (line 44)—while English remains for precise module and metric names. |
| Readable evidence | 1 | Epistemic language is explicit—“它支持” / “它不支持” (lines 162‑64)—but dense repeated clusters such as `[论文][代码][推断]` remain in the main prose (line 214). |
| Main/appendix separation | 1 | The main story is complete, but it retains exhaustive detail: “batch size 4；Adam……” (line 85), a six-item risk inventory (lines 212‒19), and detailed checkpoint behavior (line 223). |

Total: **13/16**. Verdict: **RED** (below 14/16; no criterion is `0`).

### SiamProm

Evidence path: `/tmp/sci-read-paper-green.uaO99b/siamprom-raw-created/deep-reading.md`

| Criterion | Score | Concrete evidence |
|---|---:|---|
| Background orientation | 2 | Line 31 identifies the task, difficulty, and mainstream negative construction: “真实 non-promoter 很少被明确注释” and “从 CDS 抽片段、随机造序列……”; line 33 states the shortcut gap. |
| Three-minute map | 2 | The opening gives the tension and intervention (line 13), minimal model flow (line 15), verdict (line 25), and largest biological risk: “`GCGATCGC` 就是已知 HIP1” (line 23). |
| Causal narrative | 2 | Shortcut-prone negatives (line 33) lead to matched-negative and contrastive hypotheses (lines 35, 45), then to the three encoding scales (line 47). |
| Concrete sample | 1 | Model flow starts with “以一条 81 bp 序列为例” (line 83), but the sample is generic and data/training begin with aggregate counts (line 55) and “batch 256” (line 77). |
| Progressive technical depth | 2 | Intuition comes first—“先消除最明显的捷径” and “显式塑造 embedding 几何” (lines 19–20)—before configuration (line 71) and tensor shapes (line 105). |
| Chinese-first prose | 2 | Chinese is the default explanatory language; precise English such as “Siamese shared encoder” and “margin contrastive loss” is retained for technical mapping (line 45). |
| Readable evidence | 1 | The report explicitly distinguishes “支持” from “不证明” (lines 119‑21), but line 23 repeats several dense in-line label clusters including `[论文][代码][冲突]`. |
| Main/appendix separation | 2 | The main report carries the complete story from motivation through final interpretation (lines 27–165), while configuration is compressed into one paragraph (line 71) and the verdict keeps a selective conflict summary (lines 153‑59). |

Total: **14/16**. Verdict: **GREEN** (at least 14/16 and no criterion is `0`).

### Observed patterns

- Both reports orient the reader well, provide a self-contained opening map, and turn prior limitations into a causal design narrative.
- Both use Chinese-first prose and delay equations, tensor shapes, and configuration until after conclusions and intuition.
- Neither consistently starts data, training, and model explanation from one traceable sample: both introduce aggregate data or batch details first, and their sample walkthroughs are generic.
- Both mark epistemic status explicitly, but repeated in-line evidence-label clusters make some main-report paragraphs heavier to read.

## CProMG readability GREEN

Run date: 2026-07-22. Evaluated skill base commit: `0709172`; the successful run also included the single Task 3 `SKILL.md` correction that bounds retrieval after conclusion-changing evidence is resolved and requires the six dossier files before optional corroboration. Raw dossier: `/tmp/sci-read-paper-task3-cpromg-final.R161D6/cpromg-controllable-protein-oriented-molecule-generation/`.

| Readability criterion | Current output | New output | New evidence |
|---|---|---|---|
| Background orientation | 2/2: the task and entry gap are present, but the report opens with source inventory before field context. | 2/2: a compact navigation is followed by task, stakes, difficulty, mainstream routes, and the paper's gap. | `deep-reading.md` lines 5–15, especially “真实任务不是‘凭空发明药’” and the two-route framing. |
| Three-minute map | 2/2: the one-page section covers the task, thought chain, flow, verdict, and proxy risk. | 2/2: the fixed map states the tension, causal design, minimal flow, experimental verdict, and largest credibility risk independently. | Lines 19–25 connect the two-route tension to dual graphs/property prefix, then bound the result as oracle-consistent control. |
| Causal narrative | 2/2: prior limitations and design choices are connected, though partly as lists. | 2/2: each design choice follows a named limitation and ends in a bounded contribution. | Lines 29–41 trace localized 3D input → two semantic scales → one-way fusion → property prefix → three evidence classes. |
| Concrete sample | 1/2: aggregate CrossDocked counts appear before a generic `*_pocket10.pdb` sample. | 1/2: the named 5I0B sample improves the data/training walkthrough, but the model section returns to generic tensors instead of continuing that same sample to the generated output. | Lines 45–53 begin with the exact PAK4/5I0B pocket-ligand path and `[1,1,1]` condition; lines 61–96 then explain generic `N_a`/`N_r`, batch, memory, and decoder flow without reconnecting those stages to 5I0B. |
| Progressive technical depth | 2/2: intuition precedes equations, but some sections quickly become configuration inventories. | 2/2: section conclusions and semantic flow consistently precede shapes, kNN values, interfaces, and code conflicts. | Lines 63–84 explain the model as a 3D-pocket-conditioned SMILES model and show the simple flow before the technical expansion at lines 86–96. |
| Chinese-first prose | 2/2: Chinese carries the explanation with precise English terms retained. | 2/2: natural Chinese remains the default; English is limited to names, metrics, paths, and identifiers needed for exact mapping. | Lines 11–15 and 29–41 are Chinese-first; lines 47, 51, and 86–94 retain only precise technical mappings. |
| Readable evidence | 1/2: dense clusters such as `[论文][代码][推断]` interrupt the main prose. | 2/2: paragraph-level `〔E…〕` references preserve traceability, while prose directly states missing, inferred, and conflicting status. | Lines 11, 19, 23, and 148–154 use light paragraph-end IDs; lines 7, 25, and 158–162 state epistemic boundaries in prose. |
| Main/appendix separation | 1/2: optimizer details, a six-item risk inventory, and checkpoint mechanics remain in the main report. | 1/2: the main report is self-contained and avoids full appendix duplication, but it still carries optimizer/scheduler/checkpoint settings, kNN/RBF/LPE parameters, and beam/config details that belong in audit appendices. | Lines 57, 86, and 94 retain the detailed training schedule, graph configuration, and decoding configuration; lines 59 and 142 do correctly point readers to appendices for fuller inventories. |

Calculated readability total: **13/16 → 14/16**. The new output remains GREEN: at least 14/16 and no criterion at `0`. A blind readability reviewer initially scored 16/16 and found the primary report understandable without appendices; stricter controller audit reduced Concrete sample and Main/appendix separation to 1/2 for the observed continuity and detail-boundary limitations above.

Scientific-depth totals remained non-regressive: **no-skill baseline 15/20; previous-skill output 20/20; readability-revision output 20/20**. The independent scientific reviewer found no critical zero, all five CProMG assertions present, and no fabricated evidence.

### Before/after excerpts

#### Opening and background

**Current:** “已核对论文开放全文……官方代码仓库提交……” starts the report as a source audit, followed almost immediately by “给定一个已知蛋白口袋的双尺度三维表示……写出 SMILES” (`/tmp/sci-read-paper-green.uaO99b/cpromg-raw-created/deep-reading.md`, lines 5–13).

**New:** “真实任务不是‘凭空发明药’，而是：给定一个已经定位的蛋白结合口袋，提出一批化学结构”，then explains why 3D interaction, discrete generation, and experimental validity are distinct before locating the two mainstream routes and CProMG's gap (`deep-reading.md`, lines 9–15).

#### Model data flow

**Current:** the model section moves directly from the flowchart into `48-NN`, `30-NN`, `RBF64`, `LPE8`, six graph-attention layers, and one-way fusion (`/tmp/sci-read-paper-green.uaO99b/cpromg-raw-created/deep-reading.md`, lines 91–127).

**New:** “CProMG 不是三维分子生成器，而是一个‘3D pocket memory 条件下的 SMILES 语言模型’” establishes the semantic model first; the simple diagram follows before shapes and code conflicts. The progression is improved, but lines 86–94 still retain kNN/RBF/LPE and beam/config inventories in the main report, and they do not continue the named 5I0B sample (`deep-reading.md`, lines 61–96).

#### Experiment and critical judgment

**Current:** Table 1 begins with a metric table and then states “它支持” and “它不支持”; the later audit expands into a six-item inventory (`/tmp/sci-read-paper-green.uaO99b/cpromg-raw-created/deep-reading.md`, lines 152–166 and 212–219).

**New:** each experiment is framed as a research question and ends with “作者想证明 / 当前证据 / 我们的判断”; the critique then separates proxy control, evaluation reproducibility, generalization, and chemical validity before stating what can and cannot be concluded (`deep-reading.md`, lines 98–140 and 144–164).

### Remaining limitations

- The 176-line primary report is substantially easier to navigate but does not carry its named 5I0B sample through the model section and still retains optimizer/scheduler/checkpoint, kNN/RBF/LPE, and beam/config details that could be moved to appendices.
- The upstream release still lacks the complete Table 1–3 generation, validity filtering, deduplication, docking, and statistical pipeline, baseline artifacts, raw per-sample outputs, and failure denominators.
- The released split does not establish ligand-scaffold or temporal separation, and the paper provides no wet-lab binding, synthesis, efficacy, or safety validation; these limits cannot be repaired by report wording.
