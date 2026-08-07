# Persistent Distinctions

**Version:** 0.1.0

**Domain:** Complex Systems

**Theory seed:** `persistent distinctions`

This repository is a small experimental investigation generated from a
theoretical proposition. Its purpose is not to assume that the proposition is
correct, but to turn it into something sufficiently explicit that consequences
can be inspected, simulated, measured, criticized, or rejected.

## Research question

What observable consequences follow if "persistent distinctions" is treated as an operative principle in complex-systems?

## Working hypothesis

If "persistent distinctions" is structurally relevant to complex-systems, then systems organized around that principle should exhibit measurable differences in persistence, failure, recovery, or robustness compared to equivalent systems without this organizational constraint.

## Null hypothesis

Operationalizing "persistent distinctions" produces no systematic difference from the baseline model in the selected measurements.

## Operationalization

Introduce an explicit constraint or transformation representing "persistent distinctions" and compare the resulting trajectories with an otherwise equivalent baseline.

## Measurements

Measure persistence, divergence, recovery cost, state reachability, constraint violations, and sensitivity to perturbation.

## Experimental structure

The repository separates the conceptual seed from its operationalization. The
theory is recorded in `theory.md`; the proposed experiment is specified in
`experiment.md`; machine-readable project metadata is stored in
`project.json`; executable investigations belong in `experiments/`; raw or
generated observations belong in `data/`; and interpreted outputs belong in
`results/`.

The initial repository should therefore be understood as a conjecture made
executable rather than as a finished research result.

## Quick Start

### Prerequisites

- Python 3.9 or higher
- `pip` and `venv`

### Installation

Clone the repository and set up the environment:

```bash
git clone https://github.com/standardgalactic/persistent-distinctions.git
cd persistent-distinctions

# Install with project management script
./scripts/manage.sh dev-install

# Or manually
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Project Management

Use `scripts/manage.sh` for common tasks:

```bash
# Show help
./scripts/manage.sh help

# Clean build artifacts
./scripts/manage.sh clean

# Install dependencies
./scripts/manage.sh install

# Run tests with coverage
./scripts/manage.sh test

# Format code
./scripts/manage.sh format

# Check code quality
./scripts/manage.sh lint

# Run experiments
./scripts/manage.sh run

# Version management
./scripts/manage.sh version              # Show current version
./scripts/manage.sh version-bump         # Patch bump (0.1.0 → 0.1.1)
./scripts/manage.sh version-minor        # Minor bump (0.1.0 → 0.2.0)
./scripts/manage.sh version-major        # Major bump (0.1.0 → 1.0.0)

# Create a release
./scripts/manage.sh release
```

## Dependencies

### Core

- **numpy** – Numerical computing
- **pandas** – Data manipulation and analysis
- **matplotlib** – Visualization
- **scipy** – Scientific computing

### Development

- **pytest** – Testing framework
- **pytest-cov** – Code coverage
- **black** – Code formatter
- **flake8** – Linter
- **isort** – Import sorter
- **mypy** – Type checker
- **sphinx** – Documentation generator

See `pyproject.toml` and `requirements.txt` for pinned versions.

## Project Layout

```
├── experiments/           # Executable investigations
├── data/                  # Raw and generated observations
├── results/               # Interpreted outputs and analysis
├── tests/                 # Test suite
├── theory.md              # Theoretical framework
├── experiment.md          # Experiment specification
├── project.json           # Project metadata
├── pyproject.toml         # Python project configuration
├── requirements.txt       # Dependency versions
├── scripts/
│   └── manage.sh          # Project management automation
├── README.md              # This file
├── LICENSE                # MIT License
└── CONTRIBUTING.md        # Contribution guidelines
```

## Core Research Framework

The `experiments` package now includes an extensible simulation framework:

- `experiments.core` — `SystemState`, general `Distinction`, and `DistinctionSet`
- `experiments.framework` — baseline/intervention comparative runner with perturbation scheduling
- `experiments.metrics` — built-in metrics plus a pluggable `MetricRegistry`
- `experiments.models` — `BaseComplexSystemModel`, `SimulationResult`, and runners
- `experiments.protocols` — typing protocols for models, metrics, perturbations, observers

### Example Usage

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

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to this research project.

## License

This project is licensed under the MIT License – see [LICENSE](LICENSE) for details.

## Generated project

This repository was scaffolded by `genrepo`.

Generation does not constitute evidence for the theory. The purpose of the
generator is to reduce the cost of moving from an abstract proposition to an
inspectable experimental object.
