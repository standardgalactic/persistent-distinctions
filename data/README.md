# Data directory

This directory contains:

- **raw/** – Original, unprocessed datasets (if applicable)
- **processed/** – Cleaned, structured datasets ready for analysis
- **external/** – Reference datasets from other sources

## Guidelines

- **Do not commit large files** – Use git-lfs for datasets > 100 MB
- **Document sources** – Include metadata about data origin, collection method, dates
- **Version tracking** – Record data version in experiments metadata
- **License compliance** – Ensure proper attribution and license compliance
- **Reproducibility** – Pin exact dataset versions used for published results

## Reference Outputs

See `reproducibility/reference_outputs/` for expected outputs that can be compared against to verify correctness of simulations.
