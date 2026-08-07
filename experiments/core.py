"""Core data structures for persistent distinctions experiments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional

import numpy as np

DistinctionEvaluator = Callable[["SystemState", "Distinction"], float]
DistinctionPredicate = Callable[[float], bool]


def _default_evaluator(state: "SystemState", distinction: "Distinction") -> float:
    """Default evaluator for value-target distinctions."""
    feature_index = int(distinction.parameters.get("feature_index", -1))
    target_value = float(distinction.parameters.get("target_value", 0.0))
    tolerance = float(distinction.parameters.get("tolerance", 0.1))
    min_fraction = float(distinction.parameters.get("min_fraction", 0.5))

    if feature_index < 0 or feature_index >= state.agent_features.shape[1]:
        return 0.0

    values = state.agent_features[:, feature_index]
    satisfied = np.abs(values - target_value) <= tolerance
    fraction = float(np.mean(satisfied))
    return 1.0 if fraction >= min_fraction else fraction


def _default_predicate(score: float) -> bool:
    """Default persistence predicate."""
    return score >= 1.0


@dataclass
class SystemState:
    """Represent a full system state at a simulation step.

    Parameters
    ----------
    step : int
        Simulation step index.
    agent_features : numpy.ndarray
        Array of shape ``(n_agents, n_features)``.
    global_state : numpy.ndarray, optional
        Optional global variables for the system.
    metadata : dict, optional
        Additional structured metadata.
    """

    step: int
    agent_features: np.ndarray
    global_state: np.ndarray = field(default_factory=lambda: np.array([], dtype=float))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.agent_features = np.asarray(self.agent_features, dtype=float)
        self.global_state = np.asarray(self.global_state, dtype=float)
        validate_state(self)


@dataclass
class Distinction:
    """General mathematical distinction object.

    A distinction is represented as a named evaluable object over system states.
    The evaluator and predicate are pluggable so multiple persistence criteria can
    be tested without changing this data structure.

    Parameters
    ----------
    name : str
        Distinction identifier.
    kind : str, default="invariant"
        Distinction category (e.g., invariant, observable, constraint).
    parameters : dict, optional
        Parameterization for the evaluator.
    evaluator : callable, optional
        Returns a numeric score for ``(state, distinction)``.
    predicate : callable, optional
        Maps score to a boolean persistence decision.
    relationships : dict, optional
        Free-form relationship metadata.
    """

    name: str
    kind: str = "invariant"
    parameters: Dict[str, Any] = field(default_factory=dict)
    evaluator: DistinctionEvaluator = _default_evaluator
    predicate: DistinctionPredicate = _default_predicate
    relationships: Dict[str, Any] = field(default_factory=dict)

    def evaluate(self, system_state: SystemState) -> float:
        """Return distinction score in the provided state."""
        check_distinction_integrity(self, system_state)
        return float(self.evaluator(system_state, self))

    def is_satisfied(self, system_state: SystemState) -> bool:
        """Return whether persistence criterion is satisfied."""
        return bool(self.predicate(self.evaluate(system_state)))


class DistinctionSet:
    """Mutable collection of :class:`Distinction` objects."""

    def __init__(self, distinctions: Optional[Iterable[Distinction]] = None) -> None:
        self._items: Dict[str, Distinction] = {}
        if distinctions is not None:
            for distinction in distinctions:
                self.add(distinction)

    def __len__(self) -> int:
        return len(self._items)

    def add(self, distinction: Distinction) -> None:
        """Add a distinction, replacing any existing distinction by name."""
        check_distinction_integrity(distinction)
        self._items[distinction.name] = distinction

    def get(self, name: str) -> Distinction:
        """Get distinction by name."""
        return self._items[name]

    def remove(self, name: str) -> None:
        """Remove distinction by name."""
        self._items.pop(name)

    def names(self) -> List[str]:
        """Return distinction names."""
        return list(self._items.keys())

    def update(self, name: str, **kwargs: Any) -> Distinction:
        """Update an existing distinction and return the updated object."""
        current = self._items[name]
        updated = Distinction(
            name=current.name,
            kind=kwargs.get("kind", current.kind),
            parameters=kwargs.get("parameters", dict(current.parameters)),
            evaluator=kwargs.get("evaluator", current.evaluator),
            predicate=kwargs.get("predicate", current.predicate),
            relationships=kwargs.get("relationships", dict(current.relationships)),
        )
        check_distinction_integrity(updated)
        self._items[name] = updated
        return updated

    def query_satisfied(
        self,
        state: SystemState,
        criterion: Optional[Callable[[Distinction, SystemState], bool]] = None,
    ) -> List[Distinction]:
        """Return distinctions satisfying criterion in ``state``."""
        validate_state(state)
        rule = criterion if criterion is not None else lambda d, s: d.is_satisfied(s)
        return [distinction for distinction in self._items.values() if rule(distinction, state)]

    def all(self) -> List[Distinction]:
        """Return all distinctions."""
        return list(self._items.values())


def validate_state(state: SystemState) -> None:
    """Validate a :class:`SystemState`.

    Raises
    ------
    ValueError
        If shape or value constraints are violated.
    """
    if state.step < 0:
        raise ValueError("step must be non-negative")
    if state.agent_features.ndim != 2:
        raise ValueError("agent_features must be a 2D array")
    if state.agent_features.shape[0] == 0 or state.agent_features.shape[1] == 0:
        raise ValueError("agent_features must have positive dimensions")
    if np.isnan(state.agent_features).any():
        raise ValueError("agent_features cannot contain NaN")


def check_distinction_integrity(
    distinction: Distinction, state: Optional[SystemState] = None
) -> bool:
    """Check distinction integrity and optional compatibility with a state."""
    if not distinction.name:
        raise ValueError("distinction name must be non-empty")
    if not callable(distinction.evaluator):
        raise ValueError("distinction evaluator must be callable")
    if not callable(distinction.predicate):
        raise ValueError("distinction predicate must be callable")
    if state is not None:
        validate_state(state)
    return True


def validate_distinction_set(
    distinction_set: DistinctionSet, state: Optional[SystemState] = None
) -> None:
    """Validate all distinctions in a set, optionally against a state."""
    for distinction in distinction_set.all():
        check_distinction_integrity(distinction, state)
