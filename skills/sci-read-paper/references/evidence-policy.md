# Evidence Policy

## Source Order

Use sources in this order:

1. Paper and supplementary material.
2. Author-maintained official code, configuration, releases, and issue clarifications.
3. Official dataset documentation and version records.
4. First-party literature needed to test a conclusion-critical domain claim.
5. Secondary sources only when first-party evidence is unavailable; label them as secondary.

Record URL or local path, version or commit, access date, and supported claims. Search actively, but do not bypass authentication, payment, or access controls.

## Evidence Labels

- `[论文]`: the paper or supplement states it explicitly.
- `[代码]`: official code, configuration, or processing demonstrates it.
- `[外部核验]`: a first-party external source supports or challenges it.
- `[推断]`: a reasoned reconstruction from cited evidence.
- `[缺失]`: the available sources do not report it.
- `[冲突]`: paper, supplement, code, dataset, or versions disagree.

These labels define epistemic status and remain mandatory in the evidence ledger.

## Evidence IDs in the Main Report

Assign stable dossier-local IDs such as `E01`, `E02`, and `E03`. Cite a natural paragraph with compact forms such as `〔E03〕` or `〔E12–E15〕`; do not append clusters of source labels to every sentence.

Each ID maps to one ledger row containing label, source, version/commit, locator, supported statement, and access status. Reuse an ID only for the statement it actually supports.

Lightweight IDs never hide inference, missing information, or conflict. When epistemic status changes the interpretation, write it directly in Chinese: “论文报告……”, “公开代码实际执行……”, “我们据此推断……”, or “当前材料无法确定……”.

## Conflict Rules

- Report paper-code conflicts without choosing the convenient version or inventing author intent.
- Code-only behavior can explain implementation; it is not automatically a claimed contribution.
- Paper-only behavior absent from released code is a reproducibility limitation.
- Identify conflicting versions and whether the difference changes a conclusion. Pause only when the choice changes the analysis materially.
- Put conclusion-changing conflicts in `deep-reading.md`; move secondary implementation differences to the relevant appendix.

## Calibration

Rewrite author language when the design does not support it:

- `demonstrates` requires credible alternatives to be excluded.
- `improves` requires matched data, tuning, and evaluation.
- `generalizes` requires an appropriate family, scaffold, temporal, distribution, or external test.
- `novel` requires a declared comparison scope and defensible similarity criterion.

Never reconstruct missing splits, hyperparameters, seeds, preprocessing, or training stages from convention.

## Completion Status

Use `complete` only when the paper, essential supplement, and conclusion-changing implementation evidence were accessible and the required audits were performed. Otherwise use `partial` and state once in the reading guide:

- unavailable artifacts;
- affected conclusions;
- confidence reduction;
- the smallest resolving action.

Repeat a gap later only when it changes the current judgment.
