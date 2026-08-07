"""Tests for baseline and shared model utilities."""

import numpy as np

from experiments.core import Distinction, DistinctionSet, SystemState
from experiments.metrics import default_metric_registry
from experiments.models import perturb_system, run_simulation
from experiments.models.baseline import BaselineComplexSystemModel


def test_initialization_and_state_consistency():
    model = BaselineComplexSystemModel(n_agents=5, n_features=3, interaction_strength=0.2, seed=7)
    state = model.get_state()
    assert state.agent_features.shape == (5, 3)
    assert state.step == 0


def test_reproducibility_same_seed_same_trajectory():
    model_a = BaselineComplexSystemModel(n_agents=4, n_features=2, interaction_strength=0.15, seed=11)
    model_b = BaselineComplexSystemModel(n_agents=4, n_features=2, interaction_strength=0.15, seed=11)

    traj_a = run_simulation(model_a, steps=5)
    traj_b = run_simulation(model_b, steps=5)

    for state_a, state_b in zip(traj_a.trajectory, traj_b.trajectory):
        assert np.allclose(state_a.agent_features, state_b.agent_features)


def test_perturbation_handling_and_zero_magnitude_invariant():
    model = BaselineComplexSystemModel(n_agents=3, n_features=2, interaction_strength=0.1, seed=3)
    state = model.get_state()

    zero = perturb_system(state, perturbation_type="gaussian_noise", magnitude=0.0, seed=99)
    assert np.allclose(zero.agent_features, state.agent_features)

    perturbed = perturb_system(state, perturbation_type="gaussian_noise", magnitude=0.1, seed=99)
    assert isinstance(perturbed, SystemState)
    assert perturbed.agent_features.shape == state.agent_features.shape
    assert not np.allclose(perturbed.agent_features, state.agent_features)


def test_simulation_result_tracks_histories():
    model = BaselineComplexSystemModel(n_agents=4, n_features=2, interaction_strength=0.1, seed=1)
    distinctions = DistinctionSet(
        [
            Distinction(
                name="d",
                parameters={
                    "feature_index": 0,
                    "target_value": 0.5,
                    "tolerance": 0.5,
                    "min_fraction": 0.5,
                },
            )
        ]
    )
    result = run_simulation(model, steps=3, distinctions=distinctions, registry=default_metric_registry())

    assert len(result.trajectory) == 4
    assert len(result.distinction_history) == 3
    assert len(result.metric_history) == 3
