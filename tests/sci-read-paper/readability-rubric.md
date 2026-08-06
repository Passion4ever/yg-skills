# `sci-read-paper` Readability Rubric

Score the single primary HTML report from 0 to 2 on every criterion. Judge both the long-form reading experience and whether embedded evidence remains reachable without interrupting the narrative.

- `0`: absent, misleading, or seriously obstructs understanding.
- `1`: present but dense, fragmented, inconsistently applied, or dependent on appendices.
- `2`: clear, progressive, concise enough to follow, and scientifically faithful.

| Criterion | A score of 2 requires |
|---|---|
| Background orientation | Explains the real task, importance, difficulty, mainstream approach, and the paper's entry gap without turning into a broad literature review. |
| Three-minute map | Independently gives the task, central tension, author thought chain, minimal data flow, overall experimental verdict, and largest credibility risk. |
| Causal narrative | Prior limitations lead naturally to hypotheses and design choices; the report is not a section-by-section inventory. |
| Concrete sample | Data, training, and model flow begin from one traceable sample before aggregate counts and exhaustive configuration. |
| Progressive technical depth | Gives conclusion and intuition before equations, tensor shapes, configuration, and code; technical detail does not interrupt the main line. |
| Chinese-first prose | Uses natural Chinese by default and retains English only for precise mapping, proper names, code identifiers, metrics, or author-defined modules. |
| Plain language | Sentences are short enough to parse once — most near 45 characters, none past 120, no semicolon chains carrying three claims. Every load-bearing English term is glossed in plain Chinese at first use and every acronym expanded once, so a reader entering the field can follow without looking anything up. |
| Readable evidence | Uses light paragraph-level evidence IDs and explicit epistemic language without dense repeated source-label clusters. |
| Main/audit separation | The eight-section report contains the complete research story; the embedded ledger and optional audit panels remain available without duplicating inventories in the narrative. |
| HTML reading experience | The page has a clear publication-style hierarchy, useful sticky contents, readable line length, responsive tables/cards, working internal links, and no external UI dependency. |

Score only reports for which `validate_report.py` already exits `0` — it enforces the mechanical half of Plain language (sentence length) and the rubric judges the half it cannot measure (whether the words were actually explained).

Readability GREEN requires at least 18/20 and no criterion at `0`.

Joint GREEN additionally requires the existing scientific-depth score to remain at least 16/20 with no critical criterion at `0`, all case-specific assertions present, and no fabricated evidence.
