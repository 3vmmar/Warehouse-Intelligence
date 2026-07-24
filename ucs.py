"""Uniform-cost search (Dijkstra's algorithm)."""

import heapq
import itertools
from time import perf_counter

from environment import WarehouseEnvironment
from search_core import EventRecorder, build_result, reconstruct_path
from state import Guarantees, SearchResult

GUARANTEES = Guarantees(
    complete=True,
    optimal=True,
    optimality_scope="Minimum total terrain cost because every edge cost is positive",
    time_complexity="O((V + E) log V)",
    space_complexity="O(V)",
)


def ucs(environment: WarehouseEnvironment, max_events: int = 18_000) -> SearchResult:
    started = perf_counter()
    recorder = EventRecorder(max_events)
    start = environment.initial_state
    counter = itertools.count()
    frontier = [(0.0, next(counter), start)]
    best_cost = {start: 0.0}
    came_from = {}
    expanded, generated, peak = 0, 1, 1

    while frontier:
        cost, _, state = heapq.heappop(frontier)
        if cost != best_cost.get(state):
            continue
        expanded += 1
        recorder.add("expand", state, len(frontier), g=cost, f=cost)
        if environment.is_goal(state):
            path, actions = reconstruct_path(came_from, state, start)
            return build_result(
                algorithm="ucs",
                display_name="Uniform-Cost Search",
                family="uninformed",
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
            heapq.heappush(frontier, (new_cost, next(counter), next_state))
            generated += 1
        peak = max(peak, len(frontier))

    return build_result(
        algorithm="ucs",
        display_name="Uniform-Cost Search",
        family="uninformed",
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
