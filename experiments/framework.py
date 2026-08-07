"""Comparative research framework for persistent distinctions experiments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from .core import Distinction, DistinctionSet, SystemState
from .metrics import MetricRegistry, default_metric_registry
from .models import BaseComplexSystemModel, run_simulation


@dataclass(frozen=True)
class PerturbationSpec:
    """Specification for scheduled perturbations during simulation."""

    step: int
    perturbation_type: str
    magnitude: float
    seed: int = 0


@dataclass
class ComparativeExperimentResult:
    """Structured baseline-vs-intervention experiment output."""

    baseline_trajectory: List[SystemState]
    intervention_trajectory: List[SystemState]
    baseline_metrics: Dict[str, float]
    intervention_metrics: Dict[str, float]
    comparative_metrics: Dict[str, float]
    perturbations_applied: List[PerturbationSpec] = field(default_factory=list)


def _active_distinctions(distinctions: Optional[DistinctionSet]) -> List[Distinction]:
    return distinctions.all() if distinctions is not None else []


def _compute_model_metrics(
    trajectory: Sequence[SystemState],
    active_distinctions: Sequence[Distinction],
    registry: MetricRegistry,
    disruption_point: Optional[int],
    sensitivity_reference: Optional[Sequence[SystemState]],
) -> Dict[str, float]:
    metrics: Dict[str, float] = {
        "state_reachability": registry.compute("state_reachability", trajectory),
    }

    for distinction in active_distinctions:
        metrics[f"persistence:{distinction.name}"] = registry.compute(
            "persistence", trajectory, distinction
        )
        metrics[f"constraint_violation:{distinction.name}"] = registry.compute(
            "constraint_violation", trajectory, distinction
        )

    if disruption_point is not None:
        metrics["recovery_cost"] = registry.compute("recovery_cost", trajectory, disruption_point)
    if sensitivity_reference is not None:
        metrics["sensitivity"] = registry.compute("sensitivity", sensitivity_reference, trajectory)
    return metrics


def run_comparative_experiment(
    baseline_model: BaseComplexSystemModel,
    intervention_model: BaseComplexSystemModel,
    steps: int,
    distinctions: Optional[DistinctionSet] = None,
    registry: Optional[MetricRegistry] = None,
    perturbations: Optional[Sequence[PerturbationSpec]] = None,
) -> ComparativeExperimentResult:
    """Run comparable baseline and intervention simulations with shared perturbations."""
    if steps < 0:
        raise ValueError("steps must be non-negative")

    metric_registry = registry if registry is not None else default_metric_registry()
    active_distinctions = _active_distinctions(distinctions)
    perturbation_schedule = sorted((perturbations or []), key=lambda spec: spec.step)

    start_snapshot_baseline = baseline_model.snapshot()
    start_snapshot_intervention = intervention_model.snapshot()

    baseline_result = run_simulation(
        baseline_model,
        steps=steps,
        distinctions=distinctions,
        registry=metric_registry,
    )
    intervention_result = run_simulation(
        intervention_model,
        steps=steps,
        distinctions=distinctions,
        registry=metric_registry,
    )

    baseline_trajectory = baseline_result.trajectory
    intervention_trajectory = intervention_result.trajectory

    if perturbation_schedule:
        baseline_model.restore_snapshot(start_snapshot_baseline)
        intervention_model.restore_snapshot(start_snapshot_intervention)

        perturbations_by_step: Dict[int, List[PerturbationSpec]] = {}
        for spec in perturbation_schedule:
            perturbations_by_step.setdefault(spec.step, []).append(spec)

        baseline_trajectory = [baseline_model.get_state()]
        intervention_trajectory = [intervention_model.get_state()]

        for step in range(1, steps + 1):
            for spec in perturbations_by_step.get(step, []):
                baseline_model.apply_perturbation(spec.perturbation_type, spec.magnitude, seed=spec.seed)
                intervention_model.apply_perturbation(
                    spec.perturbation_type, spec.magnitude, seed=spec.seed
                )
            baseline_model.step()
            intervention_model.step()
            baseline_trajectory.append(baseline_model.get_state())
            intervention_trajectory.append(intervention_model.get_state())

    disruption_point: Optional[int] = None
    if perturbation_schedule:
        first_step = perturbation_schedule[0].step
        if 1 <= first_step < len(baseline_trajectory):
            disruption_point = first_step

    baseline_metrics = _compute_model_metrics(
        baseline_trajectory,
        active_distinctions,
        metric_registry,
        disruption_point=disruption_point,
        sensitivity_reference=baseline_result.trajectory if perturbation_schedule else None,
    )
    intervention_metrics = _compute_model_metrics(
        intervention_trajectory,
        active_distinctions,
        metric_registry,
        disruption_point=disruption_point,
        sensitivity_reference=intervention_result.trajectory if perturbation_schedule else None,
    )

    comparative_metrics: Dict[str, float] = {
        "divergence": metric_registry.compute(
            "divergence", baseline_trajectory, intervention_trajectory
        )
    }
    for distinction in active_distinctions:
        baseline_key = f"persistence:{distinction.name}"
        intervention_key = f"persistence:{distinction.name}"
        comparative_metrics[f"delta_persistence:{distinction.name}"] = (
            intervention_metrics[intervention_key] - baseline_metrics[baseline_key]
        )

    return ComparativeExperimentResult(
        baseline_trajectory=baseline_trajectory,
        intervention_trajectory=intervention_trajectory,
        baseline_metrics=baseline_metrics,
        intervention_metrics=intervention_metrics,
        comparative_metrics=comparative_metrics,
        perturbations_applied=list(perturbation_schedule),
    )
