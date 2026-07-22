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
