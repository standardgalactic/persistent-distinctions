"""Baseline complex-systems model without explicit distinction constraints."""

from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np

from experiments.core import Distinction, SystemState, validate_state
from experiments.metrics import MetricRegistry
from experiments.models import BaseComplexSystemModel, perturb_system


class BaselineComplexSystemModel(BaseComplexSystemModel):
    """Generic agent-based baseline model."""

    def __init__(
        self,
        n_agents: int,
        n_features: int,
        interaction_strength: float,
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
        self.initialize()

    def initialize(self) -> None:
        self._step = 0
        self._features = self._rng.random((self.n_agents, self.n_features))

    def step(self) -> None:
        influence = np.mean(self._features, axis=0, keepdims=True)
        deterministic_delta = self.interaction_strength * (influence - self._features)
        noise = self._rng.normal(loc=0.0, scale=0.01, size=self._features.shape)
        self._features = np.clip(self._features + deterministic_delta + noise, 0.0, 1.0)
        self._step += 1

    def get_state(self) -> SystemState:
        return SystemState(
            step=self._step,
            agent_features=np.array(self._features, copy=True),
            global_state=np.mean(self._features, axis=0),
            metadata={"model": "baseline"},
        )

    def observe(self) -> Dict[str, Any]:
        state = self.get_state()
        return {
            "step": state.step,
            "mean_feature": np.mean(state.agent_features, axis=0),
            "std_feature": np.std(state.agent_features, axis=0),
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

    def validate_state(self) -> bool:
        validate_state(self.get_state())
        return True
