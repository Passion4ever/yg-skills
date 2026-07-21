# Evidence Policy

## Source Order

Use sources in this order:

1. Paper and supplementary material.
2. Author-maintained official code, configuration, releases, and issue clarifications.
3. Official dataset documentation and version records.
4. First-party literature needed to test a conclusion-critical domain claim.
5. Secondary sources only when first-party evidence is unavailable; label them as secondary.

Record the URL or local path, version or commit when available, access date, and which claims each source supports. Search actively, but do not bypass authentication, payment, or access controls.

## Evidence Labels

- `[论文]`: the paper or supplement states it explicitly.
- `[代码]`: official code, configuration, or processing demonstrates it.
- `[外部核验]`: a first-party external source supports or challenges it.
- `[推断]`: a reasoned reconstruction from cited evidence.
- `[缺失]`: the available sources do not report it.
- `[冲突]`: paper, supplement, code, dataset, or versions disagree.

Attach a label to every conclusion-changing statement. Nearby sentences may share one label only when their source and epistemic status are identical.

## Conflict Rules

- Report paper-code conflicts without choosing the more convenient version or inventing author intent.
- Code-only behavior can explain implementation; it is not automatically a claimed contribution.
- Paper-only behavior absent from released code is a reproducibility limitation.
- For version conflicts, identify the versions and determine whether the difference changes a conclusion. Pause only when the choice changes the analysis materially.

## Calibration

Rewrite author language into evidence-calibrated language when needed:

- `demonstrates` requires a design that excludes credible alternatives.
- `improves` requires a fair comparison under matched data, tuning, and evaluation.
- `generalizes` requires an appropriate distribution, family, scaffold, temporal, or external test.
- `novel` requires a declared comparison scope and defensible similarity criterion.

Missing splits, hyperparameters, seeds, preprocessing, or training stages remain `[缺失]`; never reconstruct them from convention alone.

## Completion Status

Use `complete` only when the paper, essential supplement, and conclusion-changing implementation evidence were accessible and the required audits were performed. Otherwise use `partial` and list:

- unavailable artifacts;
- affected sections;
- conclusions whose confidence is reduced;
- the smallest action that would resolve each gap.
