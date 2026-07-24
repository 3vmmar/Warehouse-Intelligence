"""Tabular Q-learning for Phase 2 of the CSAI 301 project."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from random import Random
from time import perf_counter

import numpy as np

from environment import WarehouseEnvironment
from state import ACTIONS, Action, State


@dataclass(frozen=True, slots=True)
class QLearningConfig:
    episodes: int = 1_400
    max_steps_per_episode: int = 420
    learning_rate: float = 0.24
    discount_factor: float = 0.96
    epsilon_start: float = 1.0
    epsilon_end: float = 0.04
    seed: int = 7
    curve_interval: int = 10

    def validate(self) -> None:
        if self.episodes < 10 or self.max_steps_per_episode < 10:
            raise ValueError("episodes and max_steps_per_episode must each be at least 10")
        if not 0 < self.learning_rate <= 1 or not 0 < self.discount_factor <= 1:
            raise ValueError("learning_rate and discount_factor must be in (0,1]")
        if not 0 <= self.epsilon_end <= self.epsilon_start <= 1:
            raise ValueError("epsilon values must satisfy 0 <= end <= start <= 1")


@dataclass(slots=True)
class QLearningResult:
    config: QLearningConfig
    q_values_midpoint: list[list[float]]
    q_values_final: list[list[float]]
    state_lookup: list[tuple[int, int, bool]]
    policy: list[str | None]
    policy_path: list[tuple[int, int, bool]] | None
    policy_actions: list[str] | None
    policy_cost: float | None
    training_curve: list[dict]
    midpoint_episode: int
    training_successes: int
    final_100_success_rate: float
    best_episode_reward: float
    evaluation_success: bool
    training_runtime_ms: float
    reward_design: dict[str, str]

    def to_dict(self) -> dict:
        return {
            "config": asdict(self.config),
            "q_values_midpoint": self.q_values_midpoint,
            "q_values_final": self.q_values_final,
            "state_lookup": self.state_lookup,
            "policy": self.policy,
            "policy_path": self.policy_path,
            "policy_actions": self.policy_actions,
            "policy_cost": self.policy_cost,
            "training_curve": self.training_curve,
            "midpoint_episode": self.midpoint_episode,
            "training_successes": self.training_successes,
            "final_100_success_rate": self.final_100_success_rate,
            "best_episode_reward": self.best_episode_reward,
            "evaluation_success": self.evaluation_success,
            "training_runtime_ms": self.training_runtime_ms,
            "reward_design": self.reward_design,
        }


def train_q_learning(
    environment: WarehouseEnvironment,
    config: QLearningConfig | None = None,
) -> QLearningResult:
    config = config or QLearningConfig()
    config.validate()
    started = perf_counter()
    rng = Random(config.seed)
    q_values = np.zeros((environment.state_space_size, len(ACTIONS)), dtype=np.float64)
    # Mild heuristic initialization is explicit and defensible: it breaks the
    # all-zero action tie toward progress while exploration and Bellman updates
    # remain responsible for learning obstacle-aware long-term values.
    for state in environment.all_states():
        state_index = environment.state_index(state)
        for action in environment.legal_actions(state):
            next_state = environment.transition(state, action)
            q_values[state_index, ACTIONS.index(action)] = -0.05 * environment.remaining_distance(
                next_state
            )
    midpoint_values = None
    midpoint_episode = config.episodes // 2
    epsilon_decay = (
        (config.epsilon_end / config.epsilon_start) ** (1 / max(1, config.episodes - 1))
        if config.epsilon_start > 0 and config.epsilon_end > 0
        else 1.0
    )
    epsilon = config.epsilon_start

    rewards: list[float] = []
    steps_history: list[int] = []
    successes: list[int] = []
    curve: list[dict] = []

    for episode in range(1, config.episodes + 1):
        state = environment.initial_state
        episode_reward = 0.0
        success = False
        steps_taken = 0

        for step in range(1, config.max_steps_per_episode + 1):
            steps_taken = step
            legal = environment.legal_actions(state)
            action = _epsilon_greedy(rng, environment, q_values, state, legal, epsilon)
            next_state, reward, done, _ = environment.rl_step(
                state, action, gamma=config.discount_factor
            )
            state_index = environment.state_index(state)
            action_index = ACTIONS.index(action)
            next_legal = environment.legal_actions(next_state)
            next_best = (
                0.0
                if done
                else max(
                    q_values[environment.state_index(next_state), ACTIONS.index(candidate)]
                    for candidate in next_legal
                )
            )
            target = reward + config.discount_factor * next_best
            q_values[state_index, action_index] += config.learning_rate * (
                target - q_values[state_index, action_index]
            )
            episode_reward += reward
            state = next_state
            if done:
                success = True
                break

        rewards.append(episode_reward)
        steps_history.append(steps_taken)
        successes.append(int(success))
        if episode == midpoint_episode:
            midpoint_values = q_values.copy()
        if episode % config.curve_interval == 0 or episode == 1:
            window = min(config.curve_interval, len(rewards))
            curve.append(
                {
                    "episode": episode,
                    "average_reward": float(sum(rewards[-window:]) / window),
                    "average_steps": float(sum(steps_history[-window:]) / window),
                    "success_rate": float(sum(successes[-window:]) / window),
                    "epsilon": float(epsilon),
                }
            )
        epsilon = max(config.epsilon_end, epsilon * epsilon_decay)

    if midpoint_values is None:
        midpoint_values = q_values.copy()

    policy = _extract_policy(environment, q_values)
    path, actions, cost = rollout_policy(
        environment, policy, max_steps=config.max_steps_per_episode
    )
    final_window = successes[-min(100, len(successes)) :]
    return QLearningResult(
        config=config,
        q_values_midpoint=_rounded_matrix(midpoint_values),
        q_values_final=_rounded_matrix(q_values),
        state_lookup=[state.to_tuple() for state in environment.all_states()],
        policy=[action.value if action else None for action in policy],
        policy_path=[state.to_tuple() for state in path] if path else None,
        policy_actions=[action.value for action in actions] if actions else None,
        policy_cost=cost,
        training_curve=curve,
        midpoint_episode=midpoint_episode,
        training_successes=sum(successes),
        final_100_success_rate=sum(final_window) / len(final_window),
        best_episode_reward=max(rewards),
        evaluation_success=path is not None,
        training_runtime_ms=(perf_counter() - started) * 1000.0,
        reward_design={
            "movement": "negative weighted terrain cost",
            "progress": "dense reward from the decrease in remaining pickup/delivery distance",
            "pickup": "+24 bonus on first package pickup",
            "delivery": "+120 terminal bonus",
            "collision": "-12 penalty; training selects from legal actions",
        },
    )


def rollout_policy(
    environment: WarehouseEnvironment,
    policy: list[Action | None],
    max_steps: int = 500,
) -> tuple[list[State] | None, list[Action] | None, float | None]:
    state = environment.initial_state
    states = [state]
    actions: list[Action] = []
    total_cost = 0.0
    visit_counts: dict[State, int] = {state: 1}

    for _ in range(max_steps):
        if environment.is_goal(state):
            return states, actions, total_cost
        action = policy[environment.state_index(state)]
        if action is None or action not in environment.legal_actions(state):
            return None, None, None
        next_state = environment.transition(state, action)
        total_cost += environment.step_cost(state, action, next_state)
        actions.append(action)
        states.append(next_state)
        state = next_state
        visit_counts[state] = visit_counts.get(state, 0) + 1
        if visit_counts[state] > 4:
            return None, None, None
    return None, None, None


def _epsilon_greedy(
    rng: Random,
    environment: WarehouseEnvironment,
    q_values: np.ndarray,
    state: State,
    legal: list[Action],
    epsilon: float,
) -> Action:
    if rng.random() < epsilon:
        return rng.choice(legal)
    row = q_values[environment.state_index(state)]
    best_value = max(row[ACTIONS.index(action)] for action in legal)
    best_actions = [action for action in legal if row[ACTIONS.index(action)] == best_value]
    return rng.choice(best_actions)


def _extract_policy(environment: WarehouseEnvironment, q_values: np.ndarray) -> list[Action | None]:
    policy: list[Action | None] = []
    for state in environment.all_states():
        if environment.is_goal(state):
            policy.append(None)
            continue
        legal = environment.legal_actions(state)
        if not legal:
            # Random generation can leave isolated free cells outside the
            # connected task component; they are valid defined states but have
            # no action and are unreachable from the start.
            policy.append(None)
            continue
        row = q_values[environment.state_index(state)]
        policy.append(max(legal, key=lambda action: row[ACTIONS.index(action)]))
    return policy


def _rounded_matrix(values: np.ndarray) -> list[list[float]]:
    return np.round(values, 5).tolist()
