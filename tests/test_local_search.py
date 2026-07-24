import pytest
from test_search import validate_result

from genetic import genetic_algorithm
from hill_climbing import hill_climbing
from simulated_annealing import simulated_annealing


@pytest.mark.parametrize(
    "solver",
    [
        lambda environment: hill_climbing(environment, iterations=700, restarts=4, seed=3),
        lambda environment: simulated_annealing(environment, iterations=900, restarts=3, seed=3),
        lambda environment: genetic_algorithm(
            environment, population_size=36, generations=55, seed=3
        ),
    ],
)
def test_local_search_returns_valid_solution(small_environment, solver):
    result = solver(small_environment)
    validate_result(small_environment, result)
    assert result.metrics.evaluations > 0
    assert result.metrics.memory_units > 0
    assert any(event.extra.get("best") for event in result.events)
