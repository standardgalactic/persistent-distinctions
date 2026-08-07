"""Model interfaces and simulation utilities."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from experiments.core import Distinction, DistinctionSet, SystemState
from experiments.metrics import MetricRegistry


@dataclass
class SimulationResult:
    """Structured simulation output for downstream analysis."""

    metadata: Dict[str, Any]
    parameters: Dict[str, Any]
    trajectory: List[SystemState]
    distinction_history: List[Dict[str, float]]
    metric_history: List[Dict[str, float]]
    random_seed: Optional[int]
    execution_time: float


class BaseComplexSystemModel(ABC):
    """Abstract simulation model interface."""

    @abstractmethod
    def initialize(self) -> None:
        """Initialize model state."""

    @abstractmethod
    def step(self) -> None:
        """Advance the model by one step."""

    @abstractmethod
    def get_state(self) -> SystemState:
        """Return current system state."""

    @abstractmethod
    def reset(self, seed: Optional[int] = None) -> None:
        """Reset model to a reproducible initial condition."""

    @abstractmethod
    def observe(self) -> Dict[str, Any]:
        """Return observable state summary."""

    @abstractmethod
    def apply_perturbation(self, perturbation_type: str, magnitude: float, seed: int = 0) -> None:
        """Apply in-place perturbation."""

    def compute_metrics(
        self,
        distinctions: Optional[Sequence[Distinction]] = None,
        registry: Optional[MetricRegistry] = None,
    ) -> Dict[str, float]:
        """Compute model metrics using a pluggable registry."""
        if registry is None or distinctions is None:
            return {}
        state = self.get_state()
        scores: Dict[str, float] = {}
        for distinction in distinctions:
            scores[f"distinctiveness:{distinction.name}"] = registry.compute(
                "distinctiveness", state, distinction
            )
        return scores

    def snapshot(self) -> Dict[str, Any]:
        """Return serializable model snapshot."""
        state = self.get_state()
        return {
            "step": state.step,
            "agent_features": np.array(state.agent_features, copy=True),
            "global_state": np.array(state.global_state, copy=True),
            "metadata": dict(state.metadata),
        }

    def restore_snapshot(self, snapshot_data: Dict[str, Any]) -> None:
        """Restore from snapshot."""
        self.set_state(
            SystemState(
                step=int(snapshot_data["step"]),
                agent_features=np.array(snapshot_data["agent_features"], copy=True),
                global_state=np.array(snapshot_data.get("global_state", []), copy=True),
                metadata=dict(snapshot_data.get("metadata", {})),
            )
        )

    def validate_state(self) -> bool:
        """Validate current state."""
        _ = self.get_state()
        return True

    @abstractmethod
    def set_seed(self, seed: int) -> None:
        """Set model random seed."""

    def set_state(self, state: SystemState) -> None:
        """Set current model state."""
        raise NotImplementedError("This model does not support setting state")


def run_simulation(
    model: BaseComplexSystemModel,
    steps: int,
    initial_state: Optional[SystemState] = None,
    distinctions: Optional[DistinctionSet] = None,
    registry: Optional[MetricRegistry] = None,
) -> SimulationResult:
    """Run simulation for a fixed number of steps."""
    if steps < 0:
        raise ValueError("steps must be non-negative")

    if initial_state is not None:
        model.set_state(initial_state)

    start = time.perf_counter()
    trajectory = [model.get_state()]
    distinction_history: List[Dict[str, float]] = []
    metric_history: List[Dict[str, float]] = []

    active_distinctions = distinctions.all() if distinctions is not None else []

    for _ in range(steps):
        model.step()
        state = model.get_state()
        trajectory.append(state)

        distinction_scores = {d.name: d.evaluate(state) for d in active_distinctions}
        distinction_history.append(distinction_scores)

        metrics = model.compute_metrics(active_distinctions, registry)
        metric_history.append(metrics)

    elapsed = time.perf_counter() - start

    return SimulationResult(
        metadata={"model": type(model).__name__},
        parameters={"steps": steps},
        trajectory=trajectory,
        distinction_history=distinction_history,
        metric_history=metric_history,
        random_seed=getattr(model, "_seed", None),
        execution_time=elapsed,
    )


def perturb_system(
    state: SystemState,
    perturbation_type: str,
    magnitude: float,
    seed: int = 0,
) -> SystemState:
    """Create a deterministically perturbed copy of a state."""
    if magnitude < 0:
        raise ValueError("magnitude must be non-negative")

    rng = np.random.default_rng(seed)
    perturbed = np.array(state.agent_features, copy=True)

    if perturbation_type == "gaussian_noise":
        perturbed += rng.normal(loc=0.0, scale=magnitude, size=perturbed.shape)
    elif perturbation_type == "feature_flip":
        count = int(np.ceil(magnitude * perturbed.size))
        count = min(max(count, 0), perturbed.size)
        if count > 0:
            flat = perturbed.reshape(-1)
            indices = rng.choice(flat.size, size=count, replace=False)
            flat[indices] = 1.0 - flat[indices]
            perturbed = flat.reshape(perturbed.shape)
    elif perturbation_type == "uniform_shift":
        perturbed += magnitude
    else:
        raise ValueError(f"Unsupported perturbation_type: {perturbation_type}")

    return SystemState(
        step=state.step,
        agent_features=np.clip(perturbed, 0.0, 1.0),
        global_state=np.array(state.global_state, copy=True),
        metadata=dict(state.metadata),
    )
