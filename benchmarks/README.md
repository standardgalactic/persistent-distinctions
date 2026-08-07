# Benchmarks

Performance and accuracy benchmarking suite.

## Structure

- **runtime.py** – Measure execution time across system sizes
- **memory.py** – Profile memory usage
- **scaling.py** – Analyze algorithmic scaling behavior
- **accuracy.py** – Verify numerical accuracy against reference values
- **generate_report.py** – Aggregate results into Markdown reports

## Running Benchmarks

```bash
python benchmarks/runtime.py
python benchmarks/memory.py
python benchmarks/generate_report.py
```

Output: `results/benchmarks/report.md`

## Success Criteria

- Linear or better scaling with system size
- Memory usage within expected bounds
- Numerical outputs within floating-point tolerance
- Consistent results across runs (deterministic seeding)
