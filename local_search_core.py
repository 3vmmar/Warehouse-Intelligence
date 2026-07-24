"""Candidate representation shared by the three local-search algorithms."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random

from environment import WarehouseEnvironment
from state import Action, State


@dataclass(slots=True)
class Candidate:
    sequence: list[Action]
    states: list[State]
    actions_used: list[Action]
    score: float
    path_cost: float
    success: bool
    collisions: int


def default_sequence_length(environment: WarehouseEnvironment) -> int:
    lower_bound = (
        environment.remaining_distance(environment.initial_state) / environment.minimum_step_cost
    )
    return max(32, int(lower_bound * 4) + 20)


def evaluate(environment: WarehouseEnvironment, sequence: list[Action]) -> Candidate:
    state = environment.initial_state
    states = [state]
    actions_used: list[Action] = []
    collisions = 0
    cost = 0.0

    for action in sequence:
        if environment.is_goal(state):
            break
        if action not in environment.legal_actions(state):
            collisions += 1
            continue
        next_state = environment.transition(state, action)
        cost += environment.step_cost(state, action, next_state)
        state = next_state
        states.append(state)
        actions_used.append(action)

    success = environment.is_goal(state) and collisions == 0
    if success:
        score = cost + len(actions_used) * 0.01
    else:
        # A hard feasibility tier ensures any legal complete solution always
        # outranks an attractive-looking but unfinished or colliding trajectory.
        score = (
            1_000_000.0
            + environment.remaining_distance(state) * 1_000.0
            + collisions * 150.0
            + cost
        )
    return Candidate(sequence, states, actions_used, score, cost, success, collisions)


def biased_random_walk(
    rng: Random,
    environment: WarehouseEnvironment,
    start: State,
    length: int,
    greedy_bias: float = 0.72,
) -> list[Action]:
    state = start
    sequence: list[Action] = []
    for _ in range(length):
        legal = environment.legal_actions(state)
        if not legal:
            break
        if rng.random() < greedy_bias:
            best_distance = min(
                environment.remaining_distance(environment.transition(state, action))
                for action in legal
            )
            best = [
                action
                for action in legal
                if environment.remaining_distance(environment.transition(state, action))
                == best_distance
            ]
            action = rng.choice(best)
        else:
            action = rng.choice(legal)
        sequence.append(action)
        state = environment.transition(state, action)
        if environment.is_goal(state):
            break
    # Fixed-length representation is useful for crossover; after reaching the
    # goal, padding is ignored by evaluate().
    while len(sequence) < length:
        sequence.append(rng.choice(list(Action)))
    return sequence


def random_candidate(rng: Random, environment: WarehouseEnvironment, length: int) -> Candidate:
    return evaluate(
        environment, biased_random_walk(rng, environment, environment.initial_state, length)
    )


def mutate_tail(
    rng: Random, environment: WarehouseEnvironment, sequence: list[Action]
) -> list[Action]:
    if not sequence:
        return sequence
    cut = rng.randrange(len(sequence))
    prefix = sequence[:cut]
    prefix_candidate = evaluate(environment, prefix)
    tail = biased_random_walk(rng, environment, prefix_candidate.states[-1], len(sequence) - cut)
    return prefix + tail


def event_payload(candidate: Candidate) -> dict:
    return {
        "score": candidate.score,
        "path_cost": candidate.path_cost,
        "success": candidate.success,
        "collisions": candidate.collisions,
        "path": [state.to_tuple() for state in candidate.states],
    }
