# Contributing

This research project welcomes contributions, corrections, and critiques.

## Setting up development environment

```bash
./scripts/manage.sh dev-install
```

## Running tests

```bash
./scripts/manage.sh test
```

## Code quality

Format and check code before committing:

```bash
./scripts/manage.sh format
./scripts/manage.sh lint
./scripts/manage.sh type-check
```

## Workflow

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request with a clear description of changes

## Experimental additions

When adding new experiments:

1. Place Python scripts in `experiments/`
2. Document methodology and hypotheses in `experiment.md`
3. Store raw data in `data/`
4. Place analysis results in `results/`
5. Update `project.json` metadata as needed

## Version management

Version bumping:

```bash
./scripts/manage.sh version-bump    # patch: 0.1.0 → 0.1.1
./scripts/manage.sh version-minor   # minor: 0.1.0 → 0.2.0
./scripts/manage.sh version-major   # major: 0.1.0 → 1.0.0
```

## Reporting issues

When reporting issues, include:

- Environment (Python version, OS)
- Steps to reproduce
- Expected vs. actual results
- Relevant experiment parameters or configuration
