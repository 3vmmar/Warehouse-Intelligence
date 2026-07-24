"""Greedy best-first search."""

import heapq
import itertools
from time import perf_counter

from astar import Heuristic, _resolve_heuristic
from environment import WarehouseEnvironment
from search_core import EventRecorder, build_result, reconstruct_path
from state import Guarantees, SearchResult

GUARANTEES = Guarantees(
    complete=True,
    optimal=False,
    optimality_scope="Complete on this finite graph with a closed set, but not cost-optimal",
    time_complexity="O(E) worst case",
    space_complexity="O(V)",
)


def greedy(
    environment: WarehouseEnvironment,
    heuristic: str | Heuristic = "manhattan",
    max_events: int = 18_000,
) -> SearchResult:
    heuristic_name, heuristic_fn = _resolve_heuristic(heuristic)
    started = perf_counter()
    recorder = EventRecorder(max_events)
    start = environment.initial_state
    counter = itertools.count()
    frontier = [(heuristic_fn(start, environment), next(counter), start)]
    visited = {start}
    came_from = {}
    expanded, generated, peak = 0, 1, 1

    while frontier:
        h_value, _, state = heapq.heappop(frontier)
        expanded += 1
        recorder.add("expand", state, len(frontier), h=h_value, f=h_value)
        if environment.is_goal(state):
            path, actions = reconstruct_path(came_from, state, start)
            return build_result(
                algorithm=f"greedy_{heuristic_name}",
                display_name=f"Greedy Best-First ({heuristic_name.title()})",
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
            if next_state in visited:
                continue
            visited.add(next_state)
            came_from[next_state] = (state, action)
            heapq.heappush(
                frontier, (heuristic_fn(next_state, environment), next(counter), next_state)
            )
            generated += 1
        peak = max(peak, len(frontier))

    return build_result(
        algorithm=f"greedy_{heuristic_name}",
        display_name=f"Greedy Best-First ({heuristic_name.title()})",
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
