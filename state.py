"""Core, shared data contracts for the CSAI 301 warehouse project.

The project deliberately keeps these objects small and explicit so every
algorithm module can be read and defended independently during the oral exam.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class Action(StrEnum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"

    @property
    def delta(self) -> tuple[int, int]:
        return {
            Action.UP: (-1, 0),
            Action.DOWN: (1, 0),
            Action.LEFT: (0, -1),
            Action.RIGHT: (0, 1),
        }[self]


ACTIONS: tuple[Action, ...] = tuple(Action)


@dataclass(frozen=True, slots=True)
class State:
    row: int
    col: int
    has_package: bool = False

    @property
    def position(self) -> tuple[int, int]:
        return self.row, self.col

    def to_tuple(self) -> tuple[int, int, bool]:
        return self.row, self.col, self.has_package


@dataclass(frozen=True, slots=True)
class Guarantees:
    complete: bool
    optimal: bool
    optimality_scope: str
    time_complexity: str
    space_complexity: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SearchEvent:
    step: int
    kind: str
    state: tuple[int, int, bool] | None = None
    frontier_size: int | None = None
    g: float | None = None
    h: float | None = None
    f: float | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SearchMetrics:
    nodes_expanded: int = 0
    nodes_generated: int = 0
    max_frontier_size: int = 0
    evaluations: int = 0
    iterations: int = 0
    memory_units: int = 0
    path_cost: float | None = None
    path_length: int | None = None
    runtime_ms: float = 0.0
    solution_found: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        # Compatibility aliases make result files easy to consume in notebooks
        # and preserve the original UI contract while the richer schema is used.
        data["complete"] = self.solution_found
        data["runtime_sec"] = self.runtime_ms / 1000.0
        return data


@dataclass(slots=True)
class SearchResult:
    algorithm: str
    display_name: str
    family: str
    guarantees: Guarantees
    metrics: SearchMetrics
    path: list[State] | None = None
    actions: list[Action] | None = None
    events: list[SearchEvent] = field(default_factory=list)
    events_truncated: bool = False
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "algorithm": self.algorithm,
            "display_name": self.display_name,
            "family": self.family,
            "guarantees": self.guarantees.to_dict(),
            "metrics": self.metrics.to_dict(),
            "path": [state.to_tuple() for state in self.path] if self.path else None,
            "actions": [action.value for action in self.actions] if self.actions else None,
            "events": [event.to_dict() for event in self.events],
            "events_truncated": self.events_truncated,
            "notes": self.notes,
        }
