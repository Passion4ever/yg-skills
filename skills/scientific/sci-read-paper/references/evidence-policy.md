# Evidence Policy

## Source Order

Use sources in this order:

1. Paper and supplementary material.
2. Author-maintained official code, configuration, releases, and issue clarifications.
3. Official dataset documentation and version records.
4. First-party literature needed to test a conclusion-critical domain claim.
5. Secondary sources only when first-party evidence is unavailable; label them as secondary.

Record URL or local path, version or commit, access date, and supported claims. Search actively, but do not bypass authentication, payment, or access controls.

Acquire code with raw-file requests or sparse or blob-filtered repository retrieval. Inspect the remote tree first and exclude weight and checkpoint paths before checkout; never download weights. Repositories in this field routinely track multi-gigabyte checkpoints, and a plain clone spends the whole budget before the paper has been read. `ai-ml-reading-guide.md` sets the code-reading path once you have the files.

## Standard-Mode Evidence Boundary

In `standard` mode, externally verify at most three conclusion-critical claim families. Resolve the selected checks, then mark additional checks unresolved and offer `audit` mode instead of extending retrieval indefinitely. This limit applies to claim families, not to the number of source pages needed to resolve one family.

Stop broad collection once the central paper, relevant supplement, shortest official-code path, dataset provenance, and selected external checks are resolved or explicitly unavailable. Build the primary reading and embedded ledger before optional corroboration. `audit` mode may expand the evidence inventory when the user explicitly requests it.

## Evidence Labels

- `[论文]`: the paper or supplement states it explicitly.
- `[代码]`: official code, configuration, or processing demonstrates it.
- `[外部核验]`: a first-party external source supports or challenges it.
- `[推断]`: a reasoned reconstruction from cited evidence.
- `[缺失]`: the available sources do not report it.
- `[冲突]`: paper, supplement, code, dataset, or versions disagree.

These labels define epistemic status and remain mandatory in the embedded evidence ledger.

## Evidence IDs in the Main Report

Assign stable dossier-local IDs such as `E01`, `E02`, and `E03`. Cite a natural paragraph at its end, not sentence by sentence; do not append clusters of source labels to every clause. `../assets/fragments.html` holds the citation and ledger-row markup — one anchor per ID, never a range, because a range renders as one link for several records and leaves the rest unresolvable.

Each ID maps to one ledger row, and every citation links to it. Reuse an ID only for the statement it actually supports.

Lightweight IDs never hide inference, missing information, or conflict. When epistemic status changes the interpretation, write it directly in Chinese: “论文报告……”, “公开代码实际执行……”, “我们据此推断……”, or “当前材料无法确定……”.

## Conflict Rules

- Report paper-code conflicts without choosing the convenient version or inventing author intent.
- Code-only behavior can explain implementation; it is not automatically a claimed contribution.
- Paper-only behavior absent from released code is a reproducibility limitation.
- Identify conflicting versions and whether the difference changes a conclusion. Pause only when the choice changes the analysis materially.
- Put conclusion-changing conflicts in the primary eight-section reading; move secondary implementation differences to the relevant embedded audit panel.
- Never hide a critical fact merely to preserve narrative separation. `output-contract.md` defines how a conclusion-changing fact becomes a labelled boundary and how Section 7 discharges it; the verdict most likely to be wrong is the one a dropped boundary was about.

## Calibration

Rewrite author language when the design does not support it:

- `demonstrates` requires credible alternatives to be excluded.
- `improves` requires matched data, tuning, and evaluation.
- `generalizes` requires an appropriate family, scaffold, temporal, distribution, or external test.
- `novel` requires a declared comparison scope and defensible similarity criterion.

For a conclusion-critical novelty claim about a specific motif or sequence, search the literal sequence and recognized aliases in first-party literature. If no match is found, mark the comparison scope unresolved rather than treating search absence as evidence of novelty.

Never reconstruct missing splits, hyperparameters, seeds, preprocessing, or training stages from convention.

## Completion Status

Judge completion against the selected `standard|audit` mode. Use `complete` only when the paper, essential supplement, conclusion-changing implementation evidence, and required checks for that mode were accessible or explicitly resolved. Otherwise use `partial` and state once in the HTML header/status area:

- unavailable artifacts;
- affected conclusions;
- confidence reduction;
- the smallest resolving action.

Repeat a gap later only when it changes the current judgment.
