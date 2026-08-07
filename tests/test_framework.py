"""Tests for comparative research framework."""

from experiments.core import Distinction, DistinctionSet
from experiments.framework import PerturbationSpec, run_comparative_experiment
from experiments.models.baseline import BaselineComplexSystemModel
from experiments.models.distinctions import DistinctionAwareSystemModel


def test_run_comparative_experiment_with_perturbation():
    distinction = Distinction(
        name="feature-0-persistent",
        parameters={"feature_index": 0, "target_value": 0.6, "tolerance": 0.1, "min_fraction": 0.7},
    )
    distinctions = DistinctionSet([distinction])

    baseline = BaselineComplexSystemModel(n_agents=8, n_features=2, interaction_strength=0.2, seed=11)
    intervention = DistinctionAwareSystemModel(
        n_agents=8,
        n_features=2,
        interaction_strength=0.2,
        distinctions=[distinction],
        seed=11,
    )

    result = run_comparative_experiment(
        baseline_model=baseline,
        intervention_model=intervention,
        steps=5,
        distinctions=distinctions,
        perturbations=[PerturbationSpec(step=2, perturbation_type="gaussian_noise", magnitude=0.1, seed=9)],
    )

    assert len(result.baseline_trajectory) == 6
    assert len(result.intervention_trajectory) == 6
    assert "divergence" in result.comparative_metrics
    assert "state_reachability" in result.baseline_metrics
    assert "state_reachability" in result.intervention_metrics
    assert "recovery_cost" in result.baseline_metrics
    assert "sensitivity" in result.intervention_metrics
