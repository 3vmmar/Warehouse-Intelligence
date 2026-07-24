"""Breadth-first search (BFS)."""

from collections import deque
from time import perf_counter

from environment import WarehouseEnvironment
from search_core import EventRecorder, build_result, reconstruct_path
from state import Guarantees, SearchResult

GUARANTEES = Guarantees(
    complete=True,
    optimal=False,
    optimality_scope="Optimal in number of moves; not guaranteed minimum weighted terrain cost",
    time_complexity="O(V + E) for this finite graph",
    space_complexity="O(V)",
)


def bfs(environment: WarehouseEnvironment, max_events: int = 18_000) -> SearchResult:
    started = perf_counter()
    recorder = EventRecorder(max_events)
    start = environment.initial_state
    frontier = deque([start])
    visited = {start}
    came_from = {}
    expanded, generated, peak = 0, 1, 1

    while frontier:
        state = frontier.popleft()
        expanded += 1
        recorder.add("expand", state, len(frontier), g=float(expanded - 1))
        if environment.is_goal(state):
            path, actions = reconstruct_path(came_from, state, start)
            return build_result(
                algorithm="bfs",
                display_name="Breadth-First Search",
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
                notes=[
                    "BFS minimizes moves, while weighted terrain can make a longer path cheaper."
                ],
            )
        for action in environment.legal_actions(state):
            next_state = environment.transition(state, action)
            if next_state in visited:
                continue
            visited.add(next_state)
            came_from[next_state] = (state, action)
            frontier.append(next_state)
            generated += 1
        peak = max(peak, len(frontier))

    return build_result(
        algorithm="bfs",
        display_name="Breadth-First Search",
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
