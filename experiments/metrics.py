"""Quantitative metrics for persistent distinctions experiments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, Protocol, Sequence, Tuple

import numpy as np
from scipy.stats import norm

from .core import Distinction, SystemState


class MetricProtocol(Protocol):
    """Protocol for metric callables."""

    def __call__(self, *args: Any, **kwargs: Any) -> float:
        """Return computed metric value."""


@dataclass
class MetricRegistry:
    """Registry for pluggable metric implementations."""

    metrics: Dict[str, MetricProtocol] = field(default_factory=dict)

    def register(self, name: str, metric: MetricProtocol) -> None:
        """Register a metric callable by name."""
        if not name:
            raise ValueError("name must be non-empty")
        if not callable(metric):
            raise ValueError("metric must be callable")
        self.metrics[name] = metric

    def compute(self, name: str, *args: Any, **kwargs: Any) -> float:
        """Compute registered metric by name."""
        return float(self.metrics[name](*args, **kwargs))

    def available(self) -> Tuple[str, ...]:
        """Return available metric names."""
        return tuple(sorted(self.metrics.keys()))


def persistence_metric(states: Sequence[SystemState], distinction: Distinction) -> float:
    """Measure the fraction of states where a distinction is satisfied."""
    if len(states) == 0:
        raise ValueError("states cannot be empty")
    satisfied = [distinction.is_satisfied(state) for state in states]
    return float(np.mean(satisfied))


def divergence_metric(
    baseline_states: Sequence[SystemState], distinction_states: Sequence[SystemState]
) -> float:
    """Compute average L2 divergence between aligned trajectories."""
    if len(baseline_states) == 0 or len(distinction_states) == 0:
        raise ValueError("trajectories cannot be empty")
    n_steps = min(len(baseline_states), len(distinction_states))
    distances = []
    for idx in range(n_steps):
        a = baseline_states[idx].agent_features
        b = distinction_states[idx].agent_features
        if a.shape != b.shape:
            raise ValueError("trajectory states must have matching shapes")
        distances.append(np.linalg.norm(a - b))
    return float(np.mean(distances))


def state_reachability_metric(states: Sequence[SystemState], bins: int = 10) -> float:
    """Estimate normalized reachability from discretized unique states."""
    if len(states) == 0:
        raise ValueError("states cannot be empty")
    if bins <= 1:
        raise ValueError("bins must be greater than 1")

    visited = set()
    for state in states:
        clipped = np.clip(state.agent_features, 0.0, 1.0)
        discretized = np.floor(clipped * bins).astype(int)
        discretized = np.clip(discretized, 0, bins - 1)
        visited.add(tuple(discretized.reshape(-1).tolist()))
    return float(len(visited) / len(states))


def recovery_cost_metric(
    baseline_trajectory: Sequence[SystemState], disruption_point: int
) -> float:
    """Estimate recovery cost as steps until near pre-disruption state."""
    if len(baseline_trajectory) < 2:
        raise ValueError("baseline_trajectory must contain at least 2 states")
    if disruption_point <= 0 or disruption_point >= len(baseline_trajectory):
        raise ValueError("disruption_point must be in [1, len(trajectory)-1]")

    reference = baseline_trajectory[disruption_point - 1].agent_features
    disrupted = baseline_trajectory[disruption_point].agent_features
    initial_distance = float(np.linalg.norm(disrupted - reference))

    if initial_distance == 0.0:
        return 0.0

    threshold = max(1e-12, 0.1 * initial_distance)
    for idx in range(disruption_point, len(baseline_trajectory)):
        distance = np.linalg.norm(baseline_trajectory[idx].agent_features - reference)
        if distance <= threshold:
            return float(idx - disruption_point)

    return float(len(baseline_trajectory) - disruption_point)


def distinctiveness_score(system_state: SystemState, distinction: Distinction) -> float:
    """Quantify distinction clarity as normalized score in ``[0, 1]``."""
    score = float(distinction.evaluate(system_state))
    return float(np.clip(score, 0.0, 1.0))


def constraint_violation_metric(states: Sequence[SystemState], distinction: Distinction) -> float:
    """Return fraction of states where distinction persistence is violated."""
    if len(states) == 0:
        raise ValueError("states cannot be empty")
    violations = [not distinction.is_satisfied(state) for state in states]
    return float(np.mean(violations))


def perturbation_sensitivity_metric(
    reference_states: Sequence[SystemState], perturbed_states: Sequence[SystemState]
) -> float:
    """Measure sensitivity as average divergence between aligned trajectories."""
    return divergence_metric(reference_states, perturbed_states)


def mean(values: Iterable[float]) -> float:
    """Return arithmetic mean."""
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        raise ValueError("values cannot be empty")
    return float(np.mean(arr))


def std(values: Iterable[float], ddof: int = 0) -> float:
    """Return standard deviation."""
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        raise ValueError("values cannot be empty")
    return float(np.std(arr, ddof=ddof))


def confidence_interval(values: Iterable[float], confidence: float = 0.95) -> Tuple[float, float]:
    """Return a two-sided normal-approximation confidence interval."""
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        raise ValueError("values cannot be empty")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be within (0, 1)")

    mu = float(np.mean(arr))
    if arr.size == 1:
        return mu, mu

    sigma = float(np.std(arr, ddof=1))
    z_value = float(norm.ppf(0.5 + confidence / 2.0))
    half_width = z_value * sigma / np.sqrt(arr.size)
    return mu - half_width, mu + half_width


def default_metric_registry() -> MetricRegistry:
    """Create a registry populated with built-in metrics."""
    registry = MetricRegistry()
    registry.register("persistence", persistence_metric)
    registry.register("divergence", divergence_metric)
    registry.register("state_reachability", state_reachability_metric)
    registry.register("recovery_cost", recovery_cost_metric)
    registry.register("distinctiveness", distinctiveness_score)
    registry.register("constraint_violation", constraint_violation_metric)
    registry.register("sensitivity", perturbation_sensitivity_metric)
    return registry
