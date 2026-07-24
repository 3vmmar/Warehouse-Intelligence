"""A* search and the project's two admissible heuristic functions."""

import heapq
import itertools
from collections.abc import Callable
from time import perf_counter

from environment import WarehouseEnvironment
from search_core import EventRecorder, build_result, reconstruct_path
from state import Guarantees, SearchResult, State

Heuristic = Callable[[State, WarehouseEnvironment], float]


def manhattan_heuristic(state: State, environment: WarehouseEnvironment) -> float:
    return environment.remaining_distance(state, "manhattan")


def euclidean_heuristic(state: State, environment: WarehouseEnvironment) -> float:
    return environment.remaining_distance(state, "euclidean")


HEURISTICS: dict[str, Heuristic] = {
    "manhattan": manhattan_heuristic,
    "euclidean": euclidean_heuristic,
}

GUARANTEES = Guarantees(
    complete=True,
    optimal=True,
    optimality_scope=(
        "Minimum total terrain cost with either provided admissible, consistent heuristic"
    ),
    time_complexity="O(E) worst case; substantially less with an informative heuristic",
    space_complexity="O(V)",
)


def astar(
    environment: WarehouseEnvironment,
    heuristic: str | Heuristic = "manhattan",
    max_events: int = 18_000,
) -> SearchResult:
    heuristic_name, heuristic_fn = _resolve_heuristic(heuristic)
    started = perf_counter()
    recorder = EventRecorder(max_events)
    start = environment.initial_state
    counter = itertools.count()
    start_h = heuristic_fn(start, environment)
    frontier = [(start_h, 0.0, next(counter), start)]
    best_cost = {start: 0.0}
    came_from = {}
    expanded, generated, peak = 0, 1, 1

    while frontier:
        score, cost, _, state = heapq.heappop(frontier)
        if cost != best_cost.get(state):
            continue
        expanded += 1
        recorder.add("expand", state, len(frontier), g=cost, h=score - cost, f=score)
        if environment.is_goal(state):
            path, actions = reconstruct_path(came_from, state, start)
            return build_result(
                algorithm=f"astar_{heuristic_name}",
                display_name=f"A* ({heuristic_name.title()})",
                family="informed",
                guarantees=GUARANTEES,
                environment=environment,
                started_at=started,
                recorder=recorder,
                nodes_expanded=expanded,
                nodes_generated=generated,
                max_frontier_size=peak,
                path=path,
                actions=actions,
            )
        for action in environment.legal_actions(state):
            next_state = environment.transition(state, action)
            new_cost = cost + environment.step_cost(state, action, next_state)
            if new_cost >= best_cost.get(next_state, float("inf")):
                continue
            best_cost[next_state] = new_cost
            came_from[next_state] = (state, action)
            h_value = heuristic_fn(next_state, environment)
            heapq.heappush(frontier, (new_cost + h_value, new_cost, next(counter), next_state))
            generated += 1
        peak = max(peak, len(frontier))

    return build_result(
        algorithm=f"astar_{heuristic_name}",
        display_name=f"A* ({heuristic_name.title()})",
        family="informed",
        guarantees=GUARANTEES,
        environment=environment,
        started_at=started,
        recorder=recorder,
        nodes_expanded=expanded,
        nodes_generated=generated,
        max_frontier_size=peak,
        path=None,
        actions=None,
    )


def _resolve_heuristic(heuristic: str | Heuristic) -> tuple[str, Heuristic]:
    if callable(heuristic):
        return getattr(heuristic, "__name__", "custom"), heuristic
    if heuristic not in HEURISTICS:
        raise ValueError(f"Unknown heuristic {heuristic!r}; choose {', '.join(HEURISTICS)}")
    return heuristic, HEURISTICS[heuristic]
