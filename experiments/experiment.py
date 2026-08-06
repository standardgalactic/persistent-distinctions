#!/usr/bin/env python3

"""
Minimal experiment scaffold.

Replace the baseline() and intervention() implementations with a concrete
operationalization of the repository's theoretical proposition.
"""

from dataclasses import dataclass


@dataclass
class Result:
    name: str
    persistence: float
    recovery_cost: float
    violations: int


def baseline() -> Result:
    return Result(
        name="baseline",
        persistence=0.0,
        recovery_cost=0.0,
        violations=0,
    )


def intervention() -> Result:
    return Result(
        name="intervention",
        persistence=0.0,
        recovery_cost=0.0,
        violations=0,
    )


def compare(a: Result, b: Result) -> None:
    print(f"{'measurement':<20} {a.name:>14} {b.name:>14}")
    print("-" * 50)

    print(
        f"{'persistence':<20}"
        f"{a.persistence:>14.4f}"
        f"{b.persistence:>14.4f}"
    )

    print(
        f"{'recovery cost':<20}"
        f"{a.recovery_cost:>14.4f}"
        f"{b.recovery_cost:>14.4f}"
    )

    print(
        f"{'violations':<20}"
        f"{a.violations:>14}"
        f"{b.violations:>14}"
    )


def main() -> None:
    control = baseline()
    experiment = intervention()

    compare(control, experiment)


if __name__ == "__main__":
    main()
