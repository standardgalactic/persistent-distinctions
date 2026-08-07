"""Experiments package exports."""

from .core import (
    Distinction,
    DistinctionSet,
    SystemState,
    check_distinction_integrity,
    validate_distinction_set,
    validate_state,
)
from .framework import ComparativeExperimentResult, PerturbationSpec, run_comparative_experiment
from .metrics import (
    MetricRegistry,
    constraint_violation_metric,
    confidence_interval,
    default_metric_registry,
    distinctiveness_score,
    divergence_metric,
    mean,
    perturbation_sensitivity_metric,
    persistence_metric,
    recovery_cost_metric,
    state_reachability_metric,
    std,
)
from .models import BaseComplexSystemModel, SimulationResult, perturb_system, run_simulation
from .models.baseline import BaselineComplexSystemModel
from .models.distinctions import DistinctionAwareSystemModel

__all__ = [
    "BaseComplexSystemModel",
    "BaselineComplexSystemModel",
    "ComparativeExperimentResult",
    "Distinction",
    "DistinctionAwareSystemModel",
    "DistinctionSet",
    "MetricRegistry",
    "PerturbationSpec",
    "SimulationResult",
    "SystemState",
    "check_distinction_integrity",
    "constraint_violation_metric",
    "confidence_interval",
    "default_metric_registry",
    "distinctiveness_score",
    "divergence_metric",
    "mean",
    "perturbation_sensitivity_metric",
    "persistence_metric",
    "perturb_system",
    "run_comparative_experiment",
    "recovery_cost_metric",
    "run_simulation",
    "state_reachability_metric",
    "std",
    "validate_distinction_set",
    "validate_state",
]
