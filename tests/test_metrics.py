"""Tests for metrics utilities."""

import numpy as np

from experiments.core import Distinction, SystemState
from experiments.metrics import (
    default_metric_registry,
    confidence_interval,
    distinctiveness_score,
    divergence_metric,
    persistence_metric,
    recovery_cost_metric,
)


def _state(value: float) -> SystemState:
    return SystemState(step=0, agent_features=np.array([[value], [value], [value]]))


def _default_distinction() -> Distinction:
    return Distinction(
        name="p",
        parameters={"feature_index": 0, "target_value": 0.5, "tolerance": 0.05, "min_fraction": 1.0},
    )


def test_persistence_metric_synthetic_data():
    distinction = _default_distinction()
    states = [_state(0.5), _state(0.6), _state(0.49), _state(0.9)]
    result = persistence_metric(states, distinction)
    assert np.isclose(result, 0.5)


def test_divergence_metric_known_trajectories():
    baseline = [_state(0.0), _state(0.2)]
    altered = [_state(0.0), _state(0.3)]
    result = divergence_metric(baseline, altered)
    assert result > 0.0


def test_recovery_cost_metric_controlled_perturbation():
    trajectory = [_state(0.5), _state(0.8), _state(0.6), _state(0.51), _state(0.5)]
    result = recovery_cost_metric(trajectory, disruption_point=1)
    assert result == 2.0


def test_distinctiveness_score_in_range():
    state = _state(0.5)
    distinction = _default_distinction()
    score = distinctiveness_score(state, distinction)
    assert 0.0 <= score <= 1.0


def test_confidence_interval_returns_tuple():
    low, high = confidence_interval([1.0, 2.0, 3.0, 4.0])
    assert low < high


def test_metric_registry_extensible():
    registry = default_metric_registry()
    value = registry.compute("distinctiveness", _state(0.5), _default_distinction())
    assert value >= 0.0
