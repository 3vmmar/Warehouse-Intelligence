import pytest

from environment import WarehouseEnvironment, generate_environment


@pytest.fixture(scope="session")
def small_environment() -> WarehouseEnvironment:
    return generate_environment(12, 12, obstacle_ratio=0.16, seed=17, require_assignment_size=False)


@pytest.fixture(scope="session")
def target_environment() -> WarehouseEnvironment:
    return generate_environment(32, 32, obstacle_ratio=0.22, seed=7)
