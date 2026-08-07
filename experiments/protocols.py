"""Typing protocols for extensible experimentation interfaces."""

from __future__ import annotations

from typing import Any, Dict, Optional, Protocol, Sequence

from experiments.core import Distinction, SystemState


class ModelProtocol(Protocol):
    """Protocol for simulation models."""

    def initialize(self) -> None:
        """Initialize model state."""

    def step(self) -> None:
        """Advance model by one step."""

    def reset(self, seed: Optional[int] = None) -> None:
        """Reset model state."""

    def get_state(self) -> SystemState:
        """Return current state."""

    def observe(self) -> Dict[str, Any]:
        """Return observable summary."""


class MetricProtocol(Protocol):
    """Protocol for metric callables."""

    def __call__(self, *args: Any, **kwargs: Any) -> float:
        """Compute metric value."""


class PerturbationProtocol(Protocol):
    """Protocol for perturbation operators."""

    def __call__(self, state: SystemState, magnitude: float) -> SystemState:
        """Apply perturbation."""


class ObserverProtocol(Protocol):
    """Protocol for observers over trajectories."""

    def __call__(
        self, trajectory: Sequence[SystemState], distinctions: Sequence[Distinction]
    ) -> Dict[str, Any]:
        """Observe trajectory and return structured outputs."""
