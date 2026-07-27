import pytest

from astar import astar, euclidean_heuristic, manhattan_heuristic
from bfs import bfs
from dfs import dfs
from environment import WarehouseEnvironment
from greedy import greedy
from ids import ids
from ucs import ucs


def validate_result(environment, result):
    assert result.metrics.solution_found, f"{result.display_name} did not find a solution"
    assert result.path and result.actions is not None
    assert result.path[0] == environment.initial_state
    assert environment.is_goal(result.path[-1])
    assert len(result.path) == len(result.actions) + 1
    for index, action in enumerate(result.actions):
        assert environment.transition(result.path[index], action) == result.path[index + 1]
    assert result.metrics.path_cost == environment.path_cost(result.path, result.actions)


def weighted_fixture():
    grid = [[0] * 5 for _ in range(5)]
    terrain = [[1.0] * 5 for _ in range(5)]
    terrain[0][1] = 12.0
    terrain[0][2] = 12.0
    return WarehouseEnvironment(grid, terrain, (0, 0), (0, 3), (0, 4))


def test_weighted_costs_make_ucs_meaningfully_better_than_bfs():
    environment = weighted_fixture()
    breadth = bfs(environment)
    uniform = ucs(environment)
    validate_result(environment, breadth)
    validate_result(environment, uniform)
    assert breadth.metrics.path_length < uniform.metrics.path_length
    assert uniform.metrics.path_cost < breadth.metrics.path_cost


@pytest.mark.parametrize(
    "solver",
    [
        bfs,
        dfs,
        ucs,
        ids,
        lambda environment: greedy(environment, "manhattan"),
        lambda environment: greedy(environment, "euclidean"),
        lambda environment: astar(environment, "manhattan"),
        lambda environment: astar(environment, "euclidean"),
    ],
)
def test_every_graph_search_returns_a_legal_path(small_environment, solver):
    validate_result(small_environment, solver(small_environment))


def test_astar_matches_ucs_optimal_weighted_cost(small_environment):
    uniform = ucs(small_environment)
    assert astar(small_environment, "manhattan").metrics.path_cost == uniform.metrics.path_cost
    assert astar(small_environment, "euclidean").metrics.path_cost == uniform.metrics.path_cost


def test_heuristics_are_admissible_at_the_start(small_environment):
    optimal = ucs(small_environment).metrics.path_cost
    assert manhattan_heuristic(small_environment.initial_state, small_environment) <= optimal
    assert euclidean_heuristic(small_environment.initial_state, small_environment) <= optimal


@pytest.mark.parametrize("heuristic", [manhattan_heuristic, euclidean_heuristic])
def test_heuristics_are_consistent_across_legal_transitions(small_environment, heuristic):
    for state in small_environment.all_states():
        for action in small_environment.legal_actions(state):
            next_state = small_environment.transition(state, action)
            cost = small_environment.step_cost(state, action, next_state)
            assert heuristic(state, small_environment) <= (
                cost + heuristic(next_state, small_environment) + 1e-9
            )


def test_manhattan_astar_reduces_expansions_against_ucs(target_environment):
    uniform = ucs(target_environment)
    informed = astar(target_environment, "manhattan")
    assert informed.metrics.path_cost == uniform.metrics.path_cost
    assert informed.metrics.nodes_expanded < uniform.metrics.nodes_expanded


def test_ids_trace_is_bounded_on_target_environment(target_environment):
    result = ids(target_environment, max_events=2_000)
    validate_result(target_environment, result)
    assert len(result.events) <= 2_000
    assert result.events_truncated
