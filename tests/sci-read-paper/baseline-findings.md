# Baseline Findings

Run date: 2026-07-21.

Each prompt was run without the skill in a fresh, prompt-only context. Scores use
`rubric.md` in criterion order; each output was scored separately. Raw outputs
are retained outside the repository in
`/private/tmp/sci-read-paper-baseline.0YIyae/`.

## `siamprom-deep-read`

Score: **20/20**.

| Criterion | Score |
|---|---:|
| Research problem chain | 2 |
| Source completion | 2 |
| Data and training | 2 |
| Model data flow | 2 |
| Experiment-to-claim mapping | 2 |
| Paper-code comparison | 2 |
| Evidence calibration | 2 |
| Bio/chemical validity | 2 |
| Main-report usability | 2 |
| Reproducibility and boundaries | 2 |

Critical failures: none observed.

Minimal evidence:

- Source and provenance resolution: “论文全文见 PMC 正文与补充材料，作者代码和数据见 SiamProm GitHub。”
- Training/code trace: “编码器只从 contrastive loss 获得梯度；分类器只从 cross-entropy 获得梯度。”
- Calibration of the independent set: “这个结果只能叫 specificity，不能叫完整独立测试 accuracy。”
- Motif boundary: “注意力高也不等于功能重要。”

## `cpromg-deep-read`

Score: **15/20**.

| Criterion | Score |
|---|---:|
| Research problem chain | 2 |
| Source completion | 1 |
| Data and training | 1 |
| Model data flow | 2 |
| Experiment-to-claim mapping | 2 |
| Paper-code comparison | 0 |
| Evidence calibration | 2 |
| Bio/chemical validity | 2 |
| Main-report usability | 2 |
| Reproducibility and boundaries | 1 |

Critical failures: **Data and training = 1**. The output gives the source,
split, tokenization, objective, and inference outline, but does not trace
preprocessing/configuration or label those implementation details as missing.

Minimal evidence:

- The training account stops at: “训练目标只是 teacher-forcing 下的 next-token negative log-likelihood。”
- A paper ambiguity is left unresolved as: “需要以代码为准。”
- No supplement, official code/configuration, or dataset availability record
  appears in the complete output.
- The boundary statement is strong but not a reproduction account: “应把
  CProMG 定位为一个有启发性的候选分子提议器与多属性计算筛选器。”

## `partial-source-doi-only`

Score: **18/20**.

| Criterion | Score |
|---|---:|
| Research problem chain | 1 |
| Source completion | 2 |
| Data and training | 1 |
| Model data flow | 2 |
| Experiment-to-claim mapping | 2 |
| Paper-code comparison | 2 |
| Evidence calibration | 2 |
| Bio/chemical validity | 2 |
| Main-report usability | 2 |
| Reproducibility and boundaries | 2 |

Critical shortfalls: **Research problem chain = 1** and **Data and training =
1**. The answer states the contribution and method but does not reconstruct the
prior-limitation → gap → hypothesis chain; it records the data source, split,
and objective but not a complete preprocessing path.

Minimal evidence:

- The opening starts from the contribution: “CProMG 的真实贡献是一个‘蛋白口袋
  → 条件化 SMILES’的生成模型。”
- The data account records: “数据源为 CrossDocked/Pocket10” and
  “训练/验证为 99,000/1,000 对。”
- Missing supplement status is explicit: “截至检索时未发现独立补充材料。”
- Paper/code conflicts are concrete: “论文原子类型为 H/C/N/O/S/P，代码却使用
  H/C/N/O/S/Se。”

## Stop condition

The stop condition is **not met**. Of the two positive controls,
`siamprom-deep-read` scores 20/20, while `cpromg-deep-read` scores 15/20
and has a critical criterion below 2. No fabrication flag was assigned from the
three complete outputs.

## Observed cross-case patterns

- Source completion varied sharply: two outputs resolved code/data or
  supplement status; one stopped at paper-level sources.
- Detailed model and experiment narratives did not guarantee a complete
  data/training or paper-code trace.
- One positive baseline and the partial-source baseline already met the numeric
  GREEN threshold without the skill.
- All three outputs explicitly narrowed at least one biological or chemical
  claim to the evidence actually reported.

## GREEN results

Run date: 2026-07-21. Skill commit: `5e93f46`.

Each unchanged positive-control prompt was run with the skill in a fresh,
isolated context. Complete raw dossiers are retained outside the repository in
`/tmp/sci-read-paper-green.uaO99b/siamprom-raw-created/` and
`/tmp/sci-read-paper-green.uaO99b/cpromg-raw-created/`.

### Score changes

| Criterion | SiamProm RED → GREEN | CProMG RED → GREEN |
|---|---:|---:|
| Research problem chain | 2 → 2 | 2 → 2 |
| Source completion | 2 → 2 | 1 → 2 |
| Data and training | 2 → 2 | 1 → 2 |
| Model data flow | 2 → 2 | 2 → 2 |
| Experiment-to-claim mapping | 2 → 2 | 2 → 2 |
| Paper-code comparison | 2 → 2 | 0 → 2 |
| Evidence calibration | 2 → 2 | 2 → 2 |
| Bio/chemical validity | 2 → 2 | 2 → 2 |
| Main-report usability | 2 → 2 | 2 → 2 |
| Reproducibility and boundaries | 2 → 2 | 1 → 2 |
| **Total** | **20 → 20** | **15 → 20** |

Both runs meet the numeric GREEN gate, have no critical criterion at `0`,
contain every case assertion, and have no fabrication flag. Each standalone
`deep-reading.md` contains the full problem chain, data/training trace, model
flow, experiment interpretation, validity audit, and reproducibility boundary;
the appendices are traceability aids rather than required reading.

### Resolved baseline failures

- CProMG now records the paper, official repository and commit, configuration,
  released split/data, Zenodo artifacts, unavailable supplement, incomplete
  checkpoint access, and missing evaluation pipeline.
- CProMG now traces pocket and ligand preprocessing, the 99,000/1,000/100
  released split, property-label construction, teacher-forced objective,
  optimizer/scheduler, coordinate noise, checkpoint behavior, and missing
  table-generation details.
- CProMG now separates paper claims, executable code, implementation conflicts,
  and missing artifacts. It identifies one-way residue-to-atom fusion, reversed
  token-type IDs, the `max_iters: 50` conflict, hard-coded paths, silent missing
  Vina-label fallback, and the absent evaluation entry point.
- CProMG now gives an actionable reproduction boundary: checkpoint generation
  is plausible after path/environment repair, while training and Tables 1–3 are
  not independently reproducible from the release.
- SiamProm preserved its prior full score while making the phantom-sampling,
  gradient-path, independent-set, and motif-evidence boundaries explicit.

### Short evidence

- SiamProm: “训练负样本制造了捷径”; “encoder 只从 contrastive loss 收梯度”;
  “`GCGATCGC` 就是已知 HIP1”.
- CProMG: “训练信号只有 teacher-forced next-token cross-entropy”;
  “残基查询原子”; “Vina 是 docking scoring proxy”.

### Remaining limitations

Both dossiers honestly use `partial`. SiamProm lacks the released generation,
10-fold CV, baseline, significance-test, and motif-analysis workflows. CProMG
lacks the complete Table 1–3 evaluation/docking pipeline, baseline artifacts,
validity/failure handling, and chemical split/novelty audit. Its checkpoints
are publicly listed, but this evaluation did not complete their download and
verification. The missing release artifacts are limitations of the paper
releases; incomplete checkpoint verification is an evaluation limitation.
Neither can be repaired by adding speculative skill instructions. No skill file
changed during GREEN.
