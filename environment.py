"""Weighted warehouse environment shared by search and Q-learning.

State = (row, column, has_package). The robot must visit the pickup location
before delivery. Static walls and deterministic four-direction movement keep
the model explainable, while weighted terrain makes BFS and UCS meaningfully
different and gives A* a real cost-optimization task.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterator
from random import Random

from state import ACTIONS, Action, State


class WarehouseEnvironment:
    def __init__(
        self,
        grid: list[list[int]],
        terrain_costs: list[list[float]],
        start: tuple[int, int],
        pickup: tuple[int, int],
        delivery: tuple[int, int],
    ) -> None:
        self._validate_grid(grid, terrain_costs)
        self.grid = [list(row) for row in grid]
        self.terrain_costs = [[float(value) for value in row] for row in terrain_costs]
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.start = tuple(start)
        self.pickup = tuple(pickup)
        self.delivery = tuple(delivery)

        landmarks = {"start": self.start, "pickup": self.pickup, "delivery": self.delivery}
        if len(set(landmarks.values())) != 3:
            raise ValueError("start, pickup, and delivery must be distinct cells")
        for name, (row, col) in landmarks.items():
            if not self.in_bounds(row, col):
                raise ValueError(f"{name} {(row, col)} is outside the grid")
            if self.is_wall(row, col):
                raise ValueError(f"{name} {(row, col)} cannot be placed on a wall")

        self._states = [
            State(row, col, carrying)
            for row, col in self.free_cells()
            for carrying in (False, True)
        ]
        self._state_index = {state: index for index, state in enumerate(self._states)}
        self.minimum_step_cost = min(self.terrain_costs[row][col] for row, col in self.free_cells())

    @staticmethod
    def _validate_grid(grid: list[list[int]], terrain: list[list[float]]) -> None:
        if not grid or not grid[0]:
            raise ValueError("grid must be a non-empty rectangular matrix")
        width = len(grid[0])
        if any(len(row) != width for row in grid):
            raise ValueError("grid rows must have equal length")
        if any(cell not in (0, 1) for row in grid for cell in row):
            raise ValueError("grid cells must be 0 (free) or 1 (wall)")
        if len(terrain) != len(grid) or any(len(row) != width for row in terrain):
            raise ValueError("terrain_costs must match the grid dimensions")
        if any(value <= 0 for row in terrain for value in row):
            raise ValueError("terrain costs must be positive")

    @property
    def initial_state(self) -> State:
        return State(*self.start, False)

    @property
    def state_space_size(self) -> int:
        return len(self._states)

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def is_wall(self, row: int, col: int) -> bool:
        return self.grid[row][col] == 1

    def is_free(self, row: int, col: int) -> bool:
        return self.in_bounds(row, col) and not self.is_wall(row, col)

    def free_cells(self) -> list[tuple[int, int]]:
        return [
            (row, col)
            for row in range(self.rows)
            for col in range(self.cols)
            if self.grid[row][col] == 0
        ]

    def all_states(self) -> Iterator[State]:
        yield from self._states

    def state_index(self, state: State) -> int:
        return self._state_index[state]

    def index_state(self, index: int) -> State:
        return self._states[index]

    def legal_actions(self, state: State) -> list[Action]:
        actions: list[Action] = []
        for action in ACTIONS:
            dr, dc = action.delta
            if self.is_free(state.row + dr, state.col + dc):
                actions.append(action)
        return actions

    def transition(self, state: State, action: Action) -> State:
        dr, dc = action.delta
        row, col = state.row + dr, state.col + dc
        if not self.is_free(row, col):
            raise ValueError(f"{action.value} is illegal from {state.to_tuple()}")
        carrying = state.has_package or (row, col) == self.pickup
        return State(row, col, carrying)

    def step_cost(self, _state: State, _action: Action, next_state: State) -> float:
        return self.terrain_costs[next_state.row][next_state.col]

    def is_goal(self, state: State) -> bool:
        return state.has_package and state.position == self.delivery

    def remaining_distance(self, state: State, metric: str = "manhattan") -> float:
        def distance(a: tuple[int, int], b: tuple[int, int]) -> float:
            dr, dc = abs(a[0] - b[0]), abs(a[1] - b[1])
            if metric == "euclidean":
                return (dr * dr + dc * dc) ** 0.5
            if metric != "manhattan":
                raise ValueError("metric must be 'manhattan' or 'euclidean'")
            return float(dr + dc)

        if state.has_package:
            raw = distance(state.position, self.delivery)
        else:
            raw = distance(state.position, self.pickup) + distance(self.pickup, self.delivery)
        return raw * self.minimum_step_cost

    def path_cost(self, states: list[State], actions: list[Action]) -> float:
        return sum(
            self.step_cost(states[index], action, states[index + 1])
            for index, action in enumerate(actions)
        )

    def rl_step(
        self, state: State, action: Action, gamma: float = 0.96
    ) -> tuple[State, float, bool, dict]:
        """Transition used by Q-learning with dense progress shaping."""
        if action not in self.legal_actions(state):
            return state, -12.0, False, {"collision": True, "picked_up": False}

        before = self.remaining_distance(state)
        next_state = self.transition(state, action)
        after = self.remaining_distance(next_state)
        picked_up = not state.has_package and next_state.has_package
        done = self.is_goal(next_state)

        reward = -self.step_cost(state, action, next_state)
        # A distance *difference* gives no reward for cycling in place, rewards
        # genuine progress, and penalizes detours. Future Q-values still teach
        # the agent when a temporary detour is required around an obstacle.
        reward += 2.0 * (before - after)
        if picked_up:
            reward += 24.0
        if done:
            reward += 120.0
        return next_state, reward, done, {"collision": False, "picked_up": picked_up}

    def to_dict(self) -> dict:
        return {
            "grid": self.grid,
            "terrain_costs": self.terrain_costs,
            "start": self.start,
            "pickup": self.pickup,
            "delivery": self.delivery,
            "rows": self.rows,
            "cols": self.cols,
            "state_space_size": self.state_space_size,
            "minimum_step_cost": self.minimum_step_cost,
        }


def generate_environment(
    rows: int = 32,
    cols: int = 32,
    obstacle_ratio: float = 0.22,
    seed: int = 7,
    weighted_terrain: bool = True,
    require_assignment_size: bool = True,
    max_attempts: int = 400,
) -> WarehouseEnvironment:
    if not 5 <= rows <= 70 or not 5 <= cols <= 70:
        raise ValueError("rows and cols must each be between 5 and 70")
    if not 0.0 <= obstacle_ratio <= 0.55:
        raise ValueError("obstacle_ratio must be between 0 and 0.55")

    rng = Random(seed)
    minimum_landmark_distance = max(6, (rows + cols) // 5)

    for _ in range(max_attempts):
        grid = [
            [1 if rng.random() < obstacle_ratio else 0 for _ in range(cols)] for _ in range(rows)
        ]
        free = [(row, col) for row in range(rows) for col in range(cols) if grid[row][col] == 0]
        size = len(free) * 2
        if len(free) < 3 or (require_assignment_size and not 1_000 <= size <= 10_000):
            continue

        start, pickup, delivery = rng.sample(free, 3)
        if _manhattan(start, pickup) < minimum_landmark_distance:
            continue
        if _manhattan(pickup, delivery) < minimum_landmark_distance:
            continue
        if not _reachable(grid, start, pickup) or not _reachable(grid, pickup, delivery):
            continue

        terrain = [[1.0 for _ in range(cols)] for _ in range(rows)]
        if weighted_terrain:
            for row, col in free:
                roll = rng.random()
                terrain[row][col] = 1.0 if roll < 0.72 else 2.0 if roll < 0.92 else 4.0
        for row, col in (start, pickup, delivery):
            terrain[row][col] = 1.0
        return WarehouseEnvironment(grid, terrain, start, pickup, delivery)

    raise RuntimeError(
        f"Unable to generate a solvable {rows}x{cols} warehouse after {max_attempts} attempts"
    )


def environment_from_dict(data: dict) -> WarehouseEnvironment:
    terrain = data.get("terrain_costs")
    if terrain is None:
        terrain = [[1.0 for _ in row] for row in data["grid"]]
    return WarehouseEnvironment(
        data["grid"], terrain, tuple(data["start"]), tuple(data["pickup"]), tuple(data["delivery"])
    )


def _manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _reachable(grid: list[list[int]], source: tuple[int, int], target: tuple[int, int]) -> bool:
    rows, cols = len(grid), len(grid[0])
    queue = deque([source])
    visited = {source}
    while queue:
        row, col = queue.popleft()
        if (row, col) == target:
            return True
        for action in ACTIONS:
            dr, dc = action.delta
            nr, nc = row + dr, col + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0 and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append((nr, nc))
    return False
