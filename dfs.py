"""Depth-first graph search (DFS)."""

from time import perf_counter

from environment import WarehouseEnvironment
from search_core import EventRecorder, build_result, reconstruct_path
from state import Guarantees, SearchResult

GUARANTEES = Guarantees(
    complete=True,
    optimal=False,
    optimality_scope="Returns the first solution encountered",
    time_complexity="O(V + E) with a visited set",
    space_complexity="O(V) worst case; typically much smaller than BFS",
)


def dfs(environment: WarehouseEnvironment, max_events: int = 18_000) -> SearchResult:
    started = perf_counter()
    recorder = EventRecorder(max_events)
    start = environment.initial_state
    stack = [start]
    visited = {start}
    came_from = {}
    expanded, generated, peak = 0, 1, 1

    while stack:
        state = stack.pop()
        expanded += 1
        recorder.add("expand", state, len(stack))
        if environment.is_goal(state):
            path, actions = reconstruct_path(came_from, state, start)
            return build_result(
                algorithm="dfs",
                display_name="Depth-First Search",
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
        # Reverse preserves the intuitive UP, DOWN, LEFT, RIGHT expansion order.
        for action in reversed(environment.legal_actions(state)):
            next_state = environment.transition(state, action)
            if next_state in visited:
                continue
            visited.add(next_state)
            came_from[next_state] = (state, action)
            stack.append(next_state)
            generated += 1
        peak = max(peak, len(stack))

    return build_result(
        algorithm="dfs",
        display_name="Depth-First Search",
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
