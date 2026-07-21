# Protein and Small-Molecule Validity

Load only for protein, small-molecule, molecular-generation, binding, or drug-discovery work.

## Protein and Sequence Tasks

Check:

- split unit: sequence, chain, complex, protein, family, species, structure, or time;
- sequence identity and homology thresholds, clustering order, and cross-split relatives;
- redundancy among chains, complexes, structures, and augmented samples;
- whether pretrained representations may include benchmark proteins or close homologs;
- label provenance, assay conditions, organism context, and negative-label validity;
- whether motif or mechanism claims have experimental, comparative-genomic, or only model-attribution support.

Random sequence splits rarely establish family- or species-level generalization. A discovered motif is a computational candidate until independent biological evidence supports function.

## Small Molecules and Binding

Check:

- molecule, scaffold, target, protein-family, complex, and temporal separation;
- duplicate structures, stereochemistry, tautomers, protonation, salts, conformers, and assay units;
- pocket definition and whether ligand or test-complex information leaks into input construction;
- affinity-label provenance and comparability across assays;
- docking engine, receptor preparation, search box, protonation, seeds, pose selection, and rescoring;
- whether train/test targets or chemotypes are genuinely novel.

Docking scores are model-dependent ranking proxies, not measured affinity. QED is a heuristic desirability score. SA scores are computational proxies, not proof that a compound can be synthesized. Predicted ADMET is not experimental safety or efficacy.

## Molecular Generation

Separate:

- syntactic validity;
- uniqueness within generated samples;
- novelty relative to the declared reference set;
- structural and scaffold diversity;
- property-distribution matching or conditional control;
- target relevance and binding proxies;
- retrosynthetic or experimental synthesizability;
- wet-lab validation.

Check whether selection and reporting use the same predictor that supplied the conditioning signal. Improvement under a reused oracle can reflect oracle exploitation. Case studies chosen from top docking scores demonstrate examples, not population-level efficacy.

## Scientific Claim Calibration

For every biological or chemical conclusion, state the strongest justified level:

1. observed experimental fact;
2. supported computational association;
3. model-based prediction;
4. plausible hypothesis;
5. unsupported speculation.

Use external first-party literature only for claims that change the paper's credibility or interpretation. Record disagreement and evidence limits instead of forcing consensus.
