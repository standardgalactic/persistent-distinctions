"""Tests for core data structures."""

import numpy as np
import pytest

from experiments.core import Distinction, DistinctionSet, SystemState, validate_state


class TestSystemState:
    """SystemState tests."""

    def test_validation_rejects_bad_shape(self):
        with pytest.raises(ValueError):
            SystemState(step=0, agent_features=np.array([1.0, 2.0]))

    def test_validation_accepts_2d_features(self):
        state = SystemState(step=0, agent_features=np.ones((3, 2)))
        validate_state(state)
        assert state.agent_features.shape == (3, 2)


class TestDistinction:
    """Distinction tests."""

    def test_evaluate_and_satisfy_default(self):
        state = SystemState(step=0, agent_features=np.array([[0.5], [0.48], [0.52], [0.2]]))
        distinction = Distinction(
            name="identity",
            parameters={
                "feature_index": 0,
                "target_value": 0.5,
                "tolerance": 0.05,
                "min_fraction": 0.75,
            },
        )
        assert np.isclose(distinction.evaluate(state), 1.0)
        assert distinction.is_satisfied(state)


class TestDistinctionSet:
    """DistinctionSet tests."""

    def test_add_query_update(self):
        state = SystemState(step=0, agent_features=np.array([[0.5, 0.1], [0.51, 0.2], [0.49, 0.3]]))
        ds = DistinctionSet()
        ds.add(
            Distinction(
                name="d1",
                parameters={
                    "feature_index": 0,
                    "target_value": 0.5,
                    "tolerance": 0.02,
                    "min_fraction": 1.0,
                },
            )
        )

        satisfied = ds.query_satisfied(state)
        assert len(satisfied) == 1
        assert satisfied[0].name == "d1"

        updated = ds.update("d1", kind="observable")
        assert updated.kind == "observable"
        assert ds.get("d1").kind == "observable"
