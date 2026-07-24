import pytest

from environment import WarehouseEnvironment, generate_environment
from state import Action


def test_generated_environment_hits_assignment_target(target_environment):
    assert 1_000 <= target_environment.state_space_size <= 10_000
    assert {1.0, 2.0, 4.0}.issuperset(
        value for row in target_environment.terrain_costs for value in row if value > 0
    )
    assert any(value > 1 for row in target_environment.terrain_costs for value in row)


def test_generation_is_reproducible():
    first = generate_environment(seed=23)
    second = generate_environment(seed=23)
    assert first.to_dict() == second.to_dict()


def test_pickup_changes_the_state_and_delivery_finishes():
    grid = [[0] * 5 for _ in range(5)]
    terrain = [[1.0] * 5 for _ in range(5)]
    environment = WarehouseEnvironment(grid, terrain, (0, 0), (0, 1), (0, 2))
    carrying = environment.transition(environment.initial_state, Action.RIGHT)
    assert carrying.has_package
    delivered = environment.transition(carrying, Action.RIGHT)
    assert environment.is_goal(delivered)


def test_environment_rejects_bad_landmarks_and_costs():
    with pytest.raises(ValueError):
        WarehouseEnvironment(
            [[0] * 5 for _ in range(5)], [[1.0] * 5 for _ in range(5)], (0, 0), (0, 0), (0, 2)
        )
    with pytest.raises(ValueError):
        WarehouseEnvironment(
            [[0] * 5 for _ in range(5)], [[0.0] * 5 for _ in range(5)], (0, 0), (0, 1), (0, 2)
        )
