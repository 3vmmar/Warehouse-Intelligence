"""Iterative deepening search (IDS) with bounded trace recording.

Each depth-limited iteration stores the shallowest depth seen for a state. This
retains iterative deepening's shallowest-solution guarantee while avoiding the
explosive duplicate paths that made the original browser payload unsafe.
"""

from time import perf_counter

from environment import WarehouseEnvironment
from search_core import EventRecorder, build_result, reconstruct_path
from state import Guarantees, SearchResult

GUARANTEES = Guarantees(
    complete=True,
    optimal=False,
    optimality_scope="Optimal in depth (moves), not weighted terrain cost",
    time_complexity="O(d(V + E)) with per-iteration duplicate suppression",
    space_complexity="O(V)",
)


def ids(
    environment: WarehouseEnvironment,
    max_depth: int | None = None,
    max_expansions: int = 500_000,
    max_events: int = 18_000,
) -> SearchResult:
    started = perf_counter()
    recorder = EventRecorder(max_events)
    start = environment.initial_state
    depth_ceiling = max_depth if max_depth is not None else environment.state_space_size
    expanded = generated = 0
    peak = 1

    for depth_limit in range(depth_ceiling + 1):
        stack = [(start, 0)]
        best_depth = {start: 0}
        came_from = {}
        recorder.add("iteration", start, 1, depth_limit=depth_limit)

        while stack:
            state, depth = stack.pop()
            expanded += 1
            recorder.add("expand", state, len(stack), g=float(depth), depth_limit=depth_limit)
            if environment.is_goal(state):
                path, actions = reconstruct_path(came_from, state, start)
                return build_result(
                    algorithm="ids",
                    display_name="Iterative Deepening Search",
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
                    iterations=depth_limit + 1,
                    notes=[
                        "Duplicate suppression makes target-size runs practical "
                        "and keeps traces bounded."
                    ],
                )
            if expanded >= max_expansions:
                return build_result(
                    algorithm="ids",
                    display_name="Iterative Deepening Search",
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
                    iterations=depth_limit + 1,
                    notes=[
                        f"Stopped safely at the configured {max_expansions:,}-expansion budget."
                    ],
                )
            if depth >= depth_limit:
                continue
            for action in reversed(environment.legal_actions(state)):
                next_state = environment.transition(state, action)
                next_depth = depth + 1
                if next_depth >= best_depth.get(next_state, float("inf")):
                    continue
                best_depth[next_state] = next_depth
                came_from[next_state] = (state, action)
                stack.append((next_state, next_depth))
                generated += 1
            peak = max(peak, len(stack))

    return build_result(
        algorithm="ids",
        display_name="Iterative Deepening Search",
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
        iterations=depth_ceiling + 1,
    )
