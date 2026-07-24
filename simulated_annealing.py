"""Simulated annealing with geometric cooling and independent restarts."""

import math
from random import Random
from time import perf_counter

from environment import WarehouseEnvironment
from local_search_core import (
    default_sequence_length,
    evaluate,
    event_payload,
    mutate_tail,
    random_candidate,
)
from search_core import EventRecorder, build_result
from state import Guarantees, SearchResult

GUARANTEES = Guarantees(
    complete=False,
    optimal=False,
    optimality_scope=(
        "Probabilistically escapes local optima; finite cooling has no optimality guarantee"
    ),
    time_complexity="O(restarts × iterations × candidate_length)",
    space_complexity="O(candidate_length)",
)


def simulated_annealing(
    environment: WarehouseEnvironment,
    max_steps: int | None = None,
    iterations: int = 3_200,
    restarts: int = 4,
    initial_temperature: float = 2_500.0,
    final_temperature: float = 0.5,
    seed: int = 7,
    max_events: int = 1_000,
) -> SearchResult:
    if iterations < 1 or restarts < 1:
        raise ValueError("iterations and restarts must be positive")
    if initial_temperature <= final_temperature or final_temperature <= 0:
        raise ValueError("temperatures must satisfy initial > final > 0")
    started = perf_counter()
    recorder = EventRecorder(max_events)
    rng = Random(seed)
    length = max_steps or default_sequence_length(environment)
    per_restart = max(1, iterations // restarts)
    cooling = (final_temperature / initial_temperature) ** (1.0 / per_restart)
    evaluations = 0
    best = None

    for restart in range(restarts):
        current = random_candidate(rng, environment, length)
        evaluations += 1
        if best is None or current.score < best.score:
            best = current
        temperature = initial_temperature
        for local_iteration in range(per_restart):
            neighbor = evaluate(environment, mutate_tail(rng, environment, current.sequence))
            evaluations += 1
            delta = neighbor.score - current.score
            if delta < 0 or rng.random() < math.exp(-delta / max(temperature, 1e-9)):
                current = neighbor
                if current.score < best.score:
                    best = current
            temperature *= cooling
            if local_iteration % 20 == 0 or current.success:
                recorder.add(
                    "candidate",
                    current.states[-1],
                    iteration=restart * per_restart + local_iteration,
                    restart=restart,
                    temperature=temperature,
                    best=event_payload(best),
                    current_score=current.score,
                )

    path = best.states if best and best.success else None
    actions = best.actions_used if best and best.success else None
    return build_result(
        algorithm="simulated_annealing",
        display_name="Simulated Annealing",
        family="local",
        guarantees=GUARANTEES,
        environment=environment,
        started_at=started,
        recorder=recorder,
        nodes_expanded=0,
        nodes_generated=0,
        max_frontier_size=2,
        path=path,
        actions=actions,
        evaluations=evaluations,
        iterations=iterations,
        memory_units=length * 2,
        notes=[
            "Early high-temperature moves accept worse candidates; "
            "cooling gradually becomes greedy."
        ],
    )
