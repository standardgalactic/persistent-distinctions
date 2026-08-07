"""Tests for distinction-aware model behavior."""

import numpy as np

from experiments.core import Distinction
from experiments.models.distinctions import DistinctionAwareSystemModel


def test_distinction_constraints_enforced_after_step():
    distinction = Distinction(
        name="lock-feature-0",
        parameters={"feature_index": 0, "target_value": 0.7, "tolerance": 0.05, "min_fraction": 1.0},
    )
    model = DistinctionAwareSystemModel(
        n_agents=6,
        n_features=2,
        interaction_strength=0.2,
        distinctions=[distinction],
        seed=5,
    )

    model.step()
    state = model.get_state()
    values = state.agent_features[:, 0]
    assert np.all(np.abs(values - 0.7) <= 0.05 + 1e-12)
