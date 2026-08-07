# Reproducibility Manifest

This directory contains infrastructure for ensuring reproducibility of published results.

## Contents

- **environment.yml** – Conda environment specification
- **requirements-lock.txt** – Exact pinned Python dependencies
- **reference_outputs/** – Expected outputs for key experiments
- **expected_hashes.json** – SHA256 hashes for verification
- **seed_values.json** – Random seeds for stochastic experiments
- **experiment_parameters.json** – Exact parameters used for published results

## Workflow

1. Run experiment with fixed random seed
2. Generate outputs (figures, data, tables)
3. Compute SHA256 hash of outputs
4. Compare against expected_hashes.json
5. If all pass, results are reproducible

## Example

```bash
# Regenerate a published result
python experiments/baseline_model.py \
  --seed 42 \
  --config reproducibility/experiment_parameters.json \
  --output results/figures/baseline_v1.png

# Verify against reference
sha256sum results/figures/baseline_v1.png | \
  grep -f reproducibility/expected_hashes.json
```

## Usage

See ROADMAP.md for reproducibility success criteria.
