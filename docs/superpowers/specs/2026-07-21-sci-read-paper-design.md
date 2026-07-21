# `sci-read-paper` Design

**Date:** 2026-07-21
**Status:** Approved design
**Repository:** `sci-skills`

## Purpose

`sci-read-paper` helps a researcher deeply understand one AI/ML paper rather
than receive a section-by-section summary. It reconstructs why the authors made
their research choices, how the work was implemented, how information flows
through the model, what each experiment was intended to establish, and whether
the evidence supports the scientific claims.

The first version targets AI/ML papers, especially work at the intersection of
deep learning with proteins, small molecules, and drug discovery.

## Goals

- Reconstruct the chain from background and prior limitations to the authors'
  hypothesis, design decisions, contributions, and conclusions.
- Recover implementation details from the paper, supplementary material,
  official code, configuration, and dataset sources.
- Explain model behavior at two levels: intuitive design reasoning first, then
  formulas, tensors, module interfaces, hyperparameters, and code evidence.
- Map every experiment to its intended claim, controls, result, and actual
  evidential strength.
- Audit both internal validity and the most important scientific claims against
  first-party domain evidence.
- Produce one self-contained primary report, with detailed evidence in
  supporting appendices.

## Non-Goals

- Quick paper summaries.
- Translation-only work.
- Broad multi-paper literature reviews.
- Pure wet-lab or non-AI/ML theoretical papers in the first version.
- Treating author claims, docking scores, or computational proxies as verified
  biological or chemical facts.

## Skill Shape

The skill uses one compact entry point plus a small number of directly linked,
on-demand references. It does not use a manifest or a general-purpose router.

```text
sci-read-paper/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── references/
    ├── evidence-policy.md
    ├── ai-ml-reading-guide.md
    ├── bio-chem-validity.md
    └── output-contract.md
```

`SKILL.md` owns triggering, the staged method, pause conditions, and final
quality gates. References contain details that are loaded only when their stage
or domain requires them.

## Trigger Boundary

The skill name is `sci-read-paper`.

It should trigger when a user asks to deeply analyze one AI/ML paper beyond a
summary, including its research logic, implementation, experiments, code, model
data flow, reproducibility, or scientific validity. Protein, small-molecule, and
drug-discovery terminology should be included in discovery metadata.

It should not trigger for a quick summary, abstract translation, broad
literature review, or simple fact extraction.

Accepted starting inputs include a PDF, title, DOI, arXiv identifier, journal
page, or official repository.

## Source and Retrieval Policy

The skill proactively completes the evidence base in this order:

1. Paper and supplementary material.
2. Author-maintained official code and configuration.
3. Official dataset documentation and releases.
4. Other first-party sources needed to resolve implementation or scientific
   claims.
5. Secondary sources only when first-party evidence is unavailable and their
   status is made explicit.

The workflow pauses only when access requires authentication or payment, source
identity is ambiguous, versions conflict in a conclusion-changing way, or a
missing user decision would materially alter the analysis.

## Reading Workflow

The default run is staged but continuous:

1. **Build the source ledger.** Resolve the paper and collect accessible
   supplementary material, official code, configurations, and dataset sources.
2. **Map the paper.** Identify the task, central tension, research gap,
   hypothesis, claimed contributions, evidence, and conclusion.
3. **Reconstruct the problem chain.** Explain why prior limitations lead to the
   proposed design and whether the innovation addresses the stated gap.
4. **Reconstruct data and training.** Trace data provenance, sample generation,
   splits, leakage risks, preprocessing, objectives, training stages,
   hyperparameters, and paper-code differences.
5. **Reconstruct model data flow.** Follow the input through representations,
   transformations, interactions, fusion or conditioning, and outputs. Explain
   the motivation first, then provide formulas, tensor shapes, module
   interfaces, and code/configuration anchors.
6. **Reconstruct experimental reasoning.** Classify baseline, ablation,
   analysis, case-study, and external-validation experiments. For each, record
   the question, controlled variables, comparison, result, and supported claim.
7. **Audit validity.** Check internal consistency, isolate the claims that
   determine trustworthiness, and verify those claims against first-party domain
   literature. Separate field consensus, active dispute, insufficient evidence,
   and over-extrapolation.
8. **Synthesize the reading dossier.** Produce the main report, appendices,
   completion status, unresolved gaps, and optional visualization briefs.

Every stage uses three layers of communication:

1. Intuitive explanation of why the authors made the choice.
2. Technical reconstruction of how it works.
3. Traceable evidence supporting the reconstruction.

## Output Contract

Each paper receives one directory:

```text
<paper-slug>/
├── deep-reading.md
├── appendices/
│   ├── evidence-ledger.md
│   ├── data-training.md
│   ├── model-dataflow.md
│   ├── experiment-matrix.md
│   └── critical-review.md
└── assets/
```

`deep-reading.md` is the default and sufficient reading surface. Appendices
provide traceability and expanded technical material without forcing the reader
to navigate between files for the core explanation.

The main report uses this order:

1. Paper identity and source-completeness status.
2. One-page orientation to the task, tension, approach, evidence, and verdict.
3. The authors' problem and innovation chain.
4. Data, sample construction, splits, training, and code reality.
5. Model design motivation and full data-flow reconstruction.
6. Experiment-by-experiment reasoning.
7. Claim-evidence and external-validity audit.
8. Final understanding: real contribution, scope, reproducibility, remaining
   questions, and reusable ideas.
9. Optional scientific-figure briefs.

The report is written primarily in Chinese. Important original terms, module
names, datasets, metrics, claims, formulas, and short evidence excerpts retain
their English wording where precision benefits.

## Evidence Discipline

Key statements use these labels:

- `[论文]`: explicitly supported by the paper or supplementary material.
- `[代码]`: supported by official code, configuration, or data processing.
- `[外部核验]`: supported by first-party external literature or dataset records.
- `[推断]`: a reasoned reconstruction from identified evidence.
- `[缺失]`: not reported or not recoverable from available material.
- `[冲突]`: inconsistent across paper, supplement, code, or source versions.

Rules:

- Do not explain away paper-code conflicts on the authors' behalf.
- Code-only behavior may clarify implementation but is not automatically a
  paper contribution.
- Missing splits, hyperparameters, or training steps are reproducibility gaps,
  not invitations to guess.
- Strong author language must be checked against design, metrics, statistics,
  and controls.
- Computational proxies such as docking, QED, or SA must not be upgraded into
  experimentally verified binding, synthesis, efficacy, or safety claims.
- Mark the dossier `complete` or `partial` and state why.

## Optional `sci-ai-figure` Integration

`sci-read-paper` has no hard dependency on a figure-generation skill. At the end
of a reading, it identifies up to three visuals that would materially improve
understanding, such as a model data-flow diagram, dataset-construction diagram,
or claim-to-experiment map.

For each useful visual, the main report records a brief containing:

- purpose and target reader;
- figure type;
- required entities and relationships;
- evidence anchors;
- content that must not be inferred or invented.

Images are not generated automatically. If the user requests them and
`sci-ai-figure` is available, the brief becomes the handoff contract. The exact
name and scope of `sci-ai-figure` remain provisional until that skill is
designed.

## Failure and Pause Behavior

- Continue autonomously across stages by default.
- Pause for authentication, payment, ambiguous official sources,
  conclusion-changing source conflicts, or a material user choice.
- Continue with a `partial` dossier when non-critical artifacts are unavailable.
- Never hide missing evidence to make the report appear complete.
- Record retrieval failures and their effect on confidence.

## Evaluation Design

Skill evaluation follows a baseline-then-skill comparison. A successful run
must produce the required primary report, appendices, evidence labels, data-flow
reconstruction, experiment-claim mapping, and calibrated critique.

### Positive Fixture 1: SiamProm

Paper: *Recognition of cyanobacteria promoters via Siamese network-based
contrastive learning under novel non-promoter generation*.

The evaluation must verify that the reader:

- recognizes negative-sample construction as a central methodological problem,
  rather than reducing the paper to a Siamese-network summary;
- traces promoter, non-promoter, contrastive-pair, and classifier-label
  construction;
- explains the relationship between representation learning and the final
  predictor;
- maps phantom sampling, architecture, ablations, and motif discovery to their
  intended claims;
- audits whether the newly reported motif receives adequate biological
  validation.

Primary paper: <https://doi.org/10.1093/bib/bbae193>

### Positive Fixture 2: CProMG

Paper: *CProMG: controllable protein-oriented molecule generation with desired
binding affinity and drug-like properties*.

The evaluation must verify that the reader:

- reconstructs the residue-graph, atom-graph, dual-view encoder, property
  conditioning, and molecular decoder data flow;
- explains how binding affinity, QED, SA, LogP, and TPSA enter conditioning or
  evaluation;
- distinguishes baseline, property-control, ablation, and case-study evidence;
- treats docking, QED, and SA as computational proxies rather than direct proof
  of experimental binding, synthesizability, or drug efficacy.

Primary paper: <https://doi.org/10.1093/bioinformatics/btad222>

### Failure Scenarios

- Invented code paths, configurations, splits, or hyperparameters.
- Author claims repeated as objective facts.
- Section-by-section paraphrase without reconstructed reasoning.
- Module lists without data-flow explanation.
- Result lists without experiment-to-claim mapping.
- Missing or conflicting evidence hidden for apparent completeness.

### Non-Trigger Scenarios

- "Summarize this paper."
- "Translate this abstract."
- "Compare these twenty papers and write a literature review."

## Deferred Work

- Design and implement `sci-ai-figure`.
- Add other scientific domains only after the AI/ML protein and small-molecule
  workflow is stable.
- Add deterministic extraction or visualization scripts only when repeated real
  runs demonstrate a need.
