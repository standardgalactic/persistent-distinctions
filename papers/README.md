# Papers and Writing

This directory contains:

- **manuscripts/** – Research papers, preprints, publications
- **drafts/** – Working drafts and notes
- **figures/** – High-quality figures for publication
- **supplementary/** – Supplementary materials, extended derivations, proofs

## Publication Workflow

1. Develop theory and experiments
2. Generate figures using reproducibility manifest
3. Write manuscript in `drafts/`
4. Include generated figures and reference hashes
5. Prepare supplementary materials
6. Publish to `manuscripts/`

## Reproducibility

Every published figure must be:
- Exactly reproducible from code in `experiments/`
- Verified against hash in `reproducibility/expected_hashes.json`
- Generated with fixed random seeds from `reproducibility/seed_values.json`

See ROADMAP.md for publication success criteria.
