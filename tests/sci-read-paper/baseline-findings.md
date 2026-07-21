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

## Partial-source and trigger results

Run date: 2026-07-22. The unchanged DOI-only prompt used
`10.1093/bioinformatics/btad222`. A fresh skill-assisted run resolved the PMC
paper, official `lijianing0902/CProMG` repository at
`main@1c9fc00da88af9a279eb15b19fd031617d92bba7`, its two configurations and
public split, and Zenodo v1 (`10.5281/zenodo.7737709`). The downloaded
`CProMG-VQS.pt` matched the published MD5
`aee806f6587d74867ddf0f9cae912ac7`.

The dossier honestly reports **partial** and scores **20/20** with no critical
zero or fabrication found. It continues the reliable paper-and-code analysis
while naming the unresolved material gaps: no located independent supplement,
complete evaluation/baseline/ablation pipeline, MMseqs2/split-construction
commands, or reproducible Tables 1–3 workflow; the full training/runtime stack
was not executed. It does not call the official code missing. Source attempts
and versions are recorded in the evidence ledger, and the main report separates
reported, implemented, inferred, missing, conflicting, and externally checked
claims.

Fresh prompt-only metadata selection results were:

- `trigger-deep-model-question`: `sci-read-paper` **5/5**.
- `nontrigger-quick-summary`: `summarize-paper` **5/5**.
- `nontrigger-translation`: `translate-academic-text` **5/5**.
- `nontrigger-literature-review`: `review-literature` **5/5**.

All 20 responses used the same exact four-skill catalog. No selection failed,
so the `sci-read-paper` metadata did not change.

## Post-audit boundary correction

Run date: 2026-07-22. Final review identified two uncovered design boundaries:
the six accepted starting forms were not explicit in `SKILL.md`, and direct
single-fact extraction had neither a stored non-trigger fixture nor routing
evidence. The new supported-input structural test failed before the workflow
sentence changed because `PDF` was absent, then passed after the source resolver
explicitly accepted a PDF/path, title, DOI, arXiv ID, journal page, or official
repository.

The first five fresh `nontrigger-simple-fact` metadata samples used the prior
description and all selected `sci-read-paper` (**0/5 pass**). The prior exact
description was:

```text
Use when deeply analyzing one AI/ML paper beyond summary, including its research logic, datasets, training, model data flow, experiments, reproducibility, code, or scientific validity, especially in protein, small-molecule, or drug-discovery research.
```

Following the metadata-only correction rule, one sentence was appended to the
frontmatter description. The final exact description is:

```text
Use when deeply analyzing one AI/ML paper beyond summary, including its research logic, datasets, training, model data flow, experiments, reproducibility, code, or scientific validity, especially in protein, small-molecule, or drug-discovery research. Do not use for direct single-fact extraction.
```

Five fresh samples for the failed case plus all four existing boundary cases
then produced:

- `nontrigger-simple-fact`: `none` **5/5**;
- `nontrigger-quick-summary`: `summarize-paper` **5/5**;
- `nontrigger-translation`: `translate-academic-text` **5/5**;
- `nontrigger-literature-review`: `review-literature` **5/5**;
- `trigger-deep-model-question`: `sci-read-paper` **5/5**.

Thus the post-fix simple-fact boundary passes **5/5**, all three earlier
non-trigger controls remain **5/5**, and the positive deep-model trigger remains
**5/5**. Each sample saw only its stored prompt, the exact four-skill catalog,
and the exact routing question; no kind, assertion, expected choice, prior
output, rubric, design, plan, or skill body was exposed.

All 30 raw prompt/catalog/question/response transcripts are preserved at
`/private/tmp/sci-read-paper-task5-fix.SValkA/`: five pre-fix records under
`pre-fix/` and 25 fresh post-fix records under `post-fix/`. SHA-256 values are:

- pre-fix `m21`–`m25`: `f0be8627c25f65b84e1889726e76fa17339f1c5161b89f8cb08f4c5b28b24776` each;
- post-fix `m26`–`m30`: `808f63898feaaefa496847910973d48461363ffcaa050fac088fb6db677f7b13` each;
- post-fix `m31`–`m35`: `82f1367ec88f891d596ae794471ab83c43461cce2094adbec4ab0e44b9c6fd6f` each;
- post-fix `m36`–`m40`: `17fbf674c4acea5c1796bef569ab94a5f29d2a0443623035b32f55136c54645a` each;
- post-fix `m41`–`m45`: `91a2847d39fe00ca854cc775e48909dde0745f42e23633dcbc40aeeb3613445d` each;
- post-fix `m46`–`m50`: `5c2065a20ed7e1878e4d90b96d335408c5dc82810b6e1893994ec80304976117` each.
