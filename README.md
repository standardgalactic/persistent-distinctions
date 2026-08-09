# Persistent Distinctions

**Version:** 0.1.0  
**Domain:** Complex systems  
**Theory seed:** `persistent distinctions`

This repository turns a theoretical proposition into an inspectable experiment.
It does not assume the proposition is true. Instead, it makes the idea concrete
enough to simulate, measure, critique, and potentially reject.

## Research framing

### Research question

What observable consequences follow when **persistent distinctions** are treated
as an organizing principle in complex systems?

### Working hypothesis

If persistent distinctions are structurally relevant, then systems organized
around them should show measurable differences in persistence, failure,
recovery, or robustness compared with equivalent baseline systems.

### Null hypothesis

Operationalizing persistent distinctions yields no systematic difference from
the baseline in the selected measurements.

### Operationalization

Apply an explicit constraint or transformation representing persistent
distinctions, then compare resulting trajectories against an otherwise
equivalent baseline.

### Measurements

Track persistence, divergence, recovery cost, state reachability, constraint
violations, and perturbation sensitivity.

## Repository structure

The repository separates conceptual framing from executable investigation:

- `theory.md` — theoretical foundation
- `experiment.md` — experiment specification
- `project.json` — machine-readable project metadata
- `experiments/` — executable investigations and simulation framework
- `data/` — raw and generated observations
- `results/` — interpreted outputs

Treat this project as an executable conjecture, not a finished research result.

## Quick start

### Prerequisites

- Python 3.9+
- `pip` and `venv`

### Setup

```bash
git clone https://github.com/standardgalactic/persistent-distinctions.git
cd persistent-distinctions

# Recommended
./scripts/manage.sh dev-install

# Manual alternative
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Common commands

Use `scripts/manage.sh` for day-to-day tasks:

```bash
./scripts/manage.sh help          # Show all commands
./scripts/manage.sh install       # Install dependencies
./scripts/manage.sh test          # Run tests with coverage
./scripts/manage.sh lint          # Run black/flake8/isort checks
./scripts/manage.sh format        # Auto-format code
./scripts/manage.sh type-check    # Run mypy
./scripts/manage.sh run           # Run experiments
./scripts/manage.sh clean         # Remove build/cache artifacts
./scripts/manage.sh version       # Show current version
./scripts/manage.sh version-bump  # Patch bump
./scripts/manage.sh version-minor # Minor bump
./scripts/manage.sh version-major # Major bump
./scripts/manage.sh release       # Create release tag
```

## Dependencies

Core: `numpy`, `pandas`, `matplotlib`, `scipy`  
Development: `pytest`, `pytest-cov`, `black`, `flake8`, `isort`, `mypy`,
`sphinx`

See `pyproject.toml` and `requirements.txt` for pinned versions.

## Core research framework

The `experiments` package provides an extensible simulation stack:

- `experiments.core` — `SystemState`, `Distinction`, `DistinctionSet`
- `experiments.framework` — baseline/intervention comparative runner with perturbation scheduling
- `experiments.metrics` — built-in metrics and pluggable `MetricRegistry`
- `experiments.models` — `BaseComplexSystemModel`, `SimulationResult`, and runners
- `experiments.protocols` — typing protocols for models, metrics, perturbations, observers

### Example usage

```python
from experiments.core import Distinction, DistinctionSet
from experiments.metrics import default_metric_registry
from experiments.models import run_simulation
from experiments.models.baseline import BaselineComplexSystemModel

model = BaselineComplexSystemModel(n_agents=10, n_features=3, interaction_strength=0.2, seed=42)
distinctions = DistinctionSet(
    [
        Distinction(
            name="feature-0-invariant",
            parameters={"feature_index": 0, "target_value": 0.5, "tolerance": 0.1, "min_fraction": 0.6},
        )
    ]
)

result = run_simulation(
    model,
    steps=50,
    distinctions=distinctions,
    registry=default_metric_registry(),
)

print(len(result.trajectory), result.metric_history[-1] if result.metric_history else {})
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT License. See [LICENSE](LICENSE).

## Project origin

This repository was scaffolded by `genrepo`.

Scaffolding is not evidence for the theory; it reduces the cost of converting
an abstract proposition into an inspectable experimental object.
