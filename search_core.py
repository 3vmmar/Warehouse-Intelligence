"""Small helpers shared by the individually named search modules."""

from __future__ import annotations

from time import perf_counter
from typing import Any

from environment import WarehouseEnvironment
from state import Action, Guarantees, SearchEvent, SearchMetrics, SearchResult, State


class EventRecorder:
    """Bounded recorder: the UI remains animated without multi-million-event payloads."""

    def __init__(self, max_events: int = 18_000) -> None:
        self.max_events = max_events
        self.events: list[SearchEvent] = []
        self.truncated = False
        self._seen = 0

    def add(
        self,
        kind: str,
        state: State | None = None,
        frontier_size: int | None = None,
        g: float | None = None,
        h: float | None = None,
        f: float | None = None,
        **extra: Any,
    ) -> None:
        self._seen += 1
        if len(self.events) >= self.max_events:
            self.truncated = True
            return
        self.events.append(
            SearchEvent(
                step=len(self.events),
                kind=kind,
                state=state.to_tuple() if state else None,
                frontier_size=frontier_size,
                g=g,
                h=h,
                f=f,
                extra=extra,
            )
        )


def reconstruct_path(
    came_from: dict[State, tuple[State, Action]], goal: State, start: State
) -> tuple[list[State], list[Action]]:
    states = [goal]
    actions: list[Action] = []
    current = goal
    while current != start:
        parent, action = came_from[current]
        states.append(parent)
        actions.append(action)
        current = parent
    states.reverse()
    actions.reverse()
    return states, actions


def build_result(
    *,
    algorithm: str,
    display_name: str,
    family: str,
    guarantees: Guarantees,
    environment: WarehouseEnvironment,
    started_at: float,
    recorder: EventRecorder,
    nodes_expanded: int,
    nodes_generated: int,
    max_frontier_size: int,
    path: list[State] | None,
    actions: list[Action] | None,
    evaluations: int = 0,
    iterations: int = 0,
    memory_units: int = 0,
    notes: list[str] | None = None,
) -> SearchResult:
    path_cost = environment.path_cost(path, actions) if path and actions is not None else None
    metrics = SearchMetrics(
        nodes_expanded=nodes_expanded,
        nodes_generated=nodes_generated,
        max_frontier_size=max_frontier_size,
        evaluations=evaluations,
        iterations=iterations,
        memory_units=max(memory_units, max_frontier_size),
        path_cost=path_cost,
        path_length=len(actions) if actions is not None else None,
        runtime_ms=(perf_counter() - started_at) * 1000.0,
        solution_found=path is not None,
    )
    return SearchResult(
        algorithm=algorithm,
        display_name=display_name,
        family=family,
        guarantees=guarantees,
        metrics=metrics,
        path=path,
        actions=actions,
        events=recorder.events,
        events_truncated=recorder.truncated,
        notes=notes or [],
    )
