# Expert-default behavioral findings

## Trial

- Date: 2026-08-04
- Skill commit: `f829eaf`
- Prompt: unchanged `siamprom-deep-read` from `tests/sci-read-paper/evals.json`
- Output root: `/tmp/sci-read-paper-expert-default-siamprom.0uQFso`
- Elapsed: `857 seconds` (`14m 17s`)
- Status and mode: `partial`, `standard`
- Generated Markdown files: `2`
  - `/tmp/sci-read-paper-expert-default-siamprom.0uQFso/siamprom-cyanobacteria-promoters/deep-reading.md` — 210 lines, SHA-256 `277b18c0fd65467b459ab4684a602921d37e3657e7d66dc905474e2d04bf757c`
  - `/tmp/sci-read-paper-expert-default-siamprom.0uQFso/siamprom-cyanobacteria-promoters/evidence-ledger.md` — 39 lines, SHA-256 `3b5f403d2f3ba5591a5a386b5558c01a826c2b0acfcedc0fd621572c89792039`
- Retry count: `0`; the trial was not regenerated or edited.

## Expert-understanding checks

| Check | Result | Exact report evidence |
|---|---|---|
| Field background and real task | PASS | `deep-reading.md:15–21` explains the TSS-aligned promoter task, why negative labels are scientifically difficult, the shortcut problem, the multi-view response, and the distinction between computational association and biological function. |
| Author limitation-to-design chain | PASS | `deep-reading.md:37–45` reconstructs easy negative sets → hard phantom negatives → contrastive geometry → multi-view encoder → motif interpretation, including each step's evidential limit. |
| Concrete sample through data and model | FAIL | `deep-reading.md:49–71` traces the first released positive and paired phantom through provenance, construction, split, pairing, loss, and gradient flow; `deep-reading.md:75–103` then returns to generic `[B,79,1024]` tensors and does not explicitly carry that same named sample to its output. |
| Experiments organized by questions | PASS | `deep-reading.md:107–167` uses five research questions and ends each with “作者想证明 / 当前证据 / 我们的判断”. |
| Critical claims and boundaries | PASS | `deep-reading.md:169–198` ranks central threats and reproducibility limits, then separates believable, provisional, unsupported conclusions and the smallest decisive next experiment. |

Overall: `4/5` expert-understanding checks passed. The report is a substantive expert reading rather than a summary or field extraction, but concrete-sample continuity remains incomplete.

## Preserved scientific checks

- **Negative-sample construction remains central:** `deep-reading.md:15–19`, `:25–33`, and `:37–45` make the absence of trustworthy negatives the methodological problem rather than a side detail.
- **Phantom sampling and contrastive learning remain causal:** `deep-reading.md:27` and `:37–43` explain sampling as removal of easy cues and contrastive geometry as the response to the harder task.
- **Promoter, non-promoter, pair, classifier, and gradient flow remain traceable:** `deep-reading.md:49–71` follows positive/phantom construction, random pairing, XOR pair labels, two cross-entropies, and the `no_grad()`-induced gradient separation.
- **Motif identity is externally calibrated:** `deep-reading.md:33`, `:155–167`, and `:175–179` identify `GCGATCGC` as the previously known HIP1 sequence, distinguish genome signature from promoter function, and quantify the sampling-induced shortcut.
- **Conclusion-changing paper-code conflicts remain visible:** `deep-reading.md:31`, `:65–69`, `:97–101`, and `:175–191` retain TSS/GC construction conflicts, 10-fold versus 90/10 split behavior, label encoding, attention masking, and missing executable experiment paths.
- **External-check boundary was obeyed:** `evidence-ledger.md:32–39` records two conclusion-critical external claim families rather than a broad literature review.

## Observed limitations

- First visible dossier output appeared after about 13 minutes; the complete agent turn took 14m 17s. Source scope was bounded, but first-result latency is still not interactive.
- The 210-line, 12,773-character main report is readable and strongly structured, but still closer to a long expert note than a short everyday reading aid.
- The concrete first sample is not explicitly carried through the generic model tensor path to a named prediction.
- Status is `partial` because the official release lacks negative-generation scripts, a 10-fold driver, baseline reproduction, and motif-analysis code; this cannot be fixed by report wording.
- The trial establishes one successful cross-domain behavior sample, not a stable runtime distribution.
