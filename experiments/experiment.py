#!/usr/bin/env python3

"""Run a deterministic baseline vs intervention comparison."""

from dataclasses import dataclass

from experiments.core import Distinction, DistinctionSet
from experiments.framework import PerturbationSpec, run_comparative_experiment
from experiments.models.baseline import BaselineComplexSystemModel
from experiments.models.distinctions import DistinctionAwareSystemModel


@dataclass(frozen=True)
class Result:
    name: str
    persistence: float
    recovery_cost: float
    violations: int


def _build_experiment() -> tuple[Result, Result, float]:
    steps = 60
    distinction = Distinction(
        name="feature-0-invariant",
        parameters={
            "feature_index": 0,
            "target_value": 0.5,
            "tolerance": 0.08,
            "min_fraction": 0.6,
        },
    )
    distinctions = DistinctionSet([distinction])

    baseline_model = BaselineComplexSystemModel(
        n_agents=40,
        n_features=3,
        interaction_strength=0.25,
        seed=7,
    )
    intervention_model = DistinctionAwareSystemModel(
        n_agents=40,
        n_features=3,
        interaction_strength=0.25,
        distinctions=distinctions.all(),
        seed=7,
    )

    comparative = run_comparative_experiment(
        baseline_model=baseline_model,
        intervention_model=intervention_model,
        steps=steps,
        distinctions=distinctions,
        perturbations=[PerturbationSpec(step=20, perturbation_type="gaussian_noise", magnitude=0.15, seed=11)],
    )

    key = f"persistence:{distinction.name}"
    violation_key = f"constraint_violation:{distinction.name}"
    state_count = len(comparative.baseline_trajectory)

    baseline = Result(
        name="baseline",
        persistence=comparative.baseline_metrics[key],
        recovery_cost=comparative.baseline_metrics["recovery_cost"],
        violations=round(comparative.baseline_metrics[violation_key] * state_count),
    )
    intervention = Result(
        name="intervention",
        persistence=comparative.intervention_metrics[key],
        recovery_cost=comparative.intervention_metrics["recovery_cost"],
        violations=round(comparative.intervention_metrics[violation_key] * state_count),
    )

    return baseline, intervention, comparative.comparative_metrics["divergence"]


def _print_summary(a: Result, b: Result, divergence: float) -> None:
    print("persistent distinctions comparative run")
    print(f"{'measurement':<22} {a.name:>14} {b.name:>14}")
    print("-" * 54)
    print(f"{'persistence':<22}{a.persistence:>14.4f}{b.persistence:>14.4f}")
    print(f"{'recovery cost (steps)':<22}{a.recovery_cost:>14.2f}{b.recovery_cost:>14.2f}")
    print(f"{'constraint violations':<22}{a.violations:>14}{b.violations:>14}")
    print(f"{'trajectory divergence':<22}{'—':>14}{divergence:>14.4f}")
    print()
    print("Higher persistence and fewer violations indicate stronger distinction retention.")


def main() -> None:
    baseline, intervention, divergence = _build_experiment()
    _print_summary(baseline, intervention, divergence)


if __name__ == "__main__":
    main()
