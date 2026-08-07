"""Distinction-aware complex-systems model."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

import numpy as np

from experiments.core import Distinction, DistinctionSet, SystemState, validate_state
from experiments.metrics import MetricRegistry
from experiments.models import BaseComplexSystemModel, perturb_system


class DistinctionAwareSystemModel(BaseComplexSystemModel):
    """Agent-based model with distinction-persistence constraints."""

    def __init__(
        self,
        n_agents: int,
        n_features: int,
        interaction_strength: float,
        distinctions: Optional[Iterable[Distinction]] = None,
        seed: int = 0,
    ) -> None:
        if n_agents <= 0 or n_features <= 0:
            raise ValueError("n_agents and n_features must be positive")
        self.n_agents = n_agents
        self.n_features = n_features
        self.interaction_strength = float(interaction_strength)
        self._seed = seed
        self._rng = np.random.default_rng(seed)
        self._step = 0
        self._features = np.zeros((n_agents, n_features), dtype=float)
        self.distinctions = DistinctionSet(distinctions)
        self.initialize()

    def initialize(self) -> None:
        self._step = 0
        self._features = self._rng.random((self.n_agents, self.n_features))
        self._apply_distinction_constraints()

    def _apply_distinction_constraints(self) -> None:
        for distinction in self.distinctions.all():
            params = distinction.parameters
            idx = int(params.get("feature_index", -1))
            if idx < 0 or idx >= self.n_features:
                continue
            target = float(params.get("target_value", 0.0))
            tol = float(params.get("tolerance", 0.1))
            values = self._features[:, idx]
            lower = target - tol
            upper = target + tol
            constrained = np.clip(values, lower, upper)
            min_fraction = float(params.get("min_fraction", 0.5))
            if min_fraction > 0:
                required = int(np.ceil(min_fraction * self.n_agents))
                required = min(max(required, 0), self.n_agents)
                ordering = np.argsort(np.abs(constrained - target))
                chosen = ordering[:required]
                constrained[chosen] = target
            self._features[:, idx] = np.clip(constrained, 0.0, 1.0)

    def step(self) -> None:
        influence = np.mean(self._features, axis=0, keepdims=True)
        deterministic_delta = self.interaction_strength * (influence - self._features)
        noise = self._rng.normal(loc=0.0, scale=0.01, size=self._features.shape)
        self._features = np.clip(self._features + deterministic_delta + noise, 0.0, 1.0)
        self._apply_distinction_constraints()
        self._step += 1

    def get_state(self) -> SystemState:
        return SystemState(
            step=self._step,
            agent_features=np.array(self._features, copy=True),
            global_state=np.mean(self._features, axis=0),
            metadata={"model": "distinction-aware", "n_distinctions": len(self.distinctions)},
        )

    def observe(self) -> Dict[str, Any]:
        state = self.get_state()
        return {
            "step": state.step,
            "mean_feature": np.mean(state.agent_features, axis=0),
            "n_distinctions": len(self.distinctions),
        }

    def apply_perturbation(self, perturbation_type: str, magnitude: float, seed: int = 0) -> None:
        state = perturb_system(self.get_state(), perturbation_type, magnitude, seed=seed)
        self.set_state(state)

    def compute_metrics(
        self,
        distinctions: Optional[list[Distinction]] = None,
        registry: Optional[MetricRegistry] = None,
    ) -> Dict[str, float]:
        return super().compute_metrics(distinctions, registry)

    def reset(self, seed: Optional[int] = None) -> None:
        if seed is not None:
            self.set_seed(seed)
        self.initialize()

    def set_seed(self, seed: int) -> None:
        self._seed = seed
        self._rng = np.random.default_rng(seed)

    def set_state(self, state: SystemState) -> None:
        validate_state(state)
        if state.agent_features.shape != (self.n_agents, self.n_features):
            raise ValueError("state shape does not match model dimensions")
        self._step = state.step
        self._features = np.array(state.agent_features, copy=True)
        self._apply_distinction_constraints()

    def validate_state(self) -> bool:
        validate_state(self.get_state())
        return True
