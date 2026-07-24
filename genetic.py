"""Genetic algorithm using tournament selection, crossover, mutation and elitism."""

from random import Random
from time import perf_counter

from environment import WarehouseEnvironment
from local_search_core import (
    Candidate,
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
        "Population search can discover high-quality paths but has no finite optimality guarantee"
    ),
    time_complexity="O(generations × population × candidate_length)",
    space_complexity="O(population × candidate_length)",
)


def genetic_algorithm(
    environment: WarehouseEnvironment,
    max_steps: int | None = None,
    population_size: int = 64,
    generations: int = 140,
    mutation_rate: float = 0.35,
    tournament_size: int = 4,
    immigrant_rate: float = 0.10,
    seed: int = 7,
    max_events: int = 1_000,
) -> SearchResult:
    if population_size < 8 or generations < 1:
        raise ValueError("population_size must be at least 8 and generations must be positive")
    if not 0 <= mutation_rate <= 1 or not 0 <= immigrant_rate < 0.5:
        raise ValueError("mutation_rate must be in [0,1] and immigrant_rate in [0,0.5)")
    if not 2 <= tournament_size <= population_size:
        raise ValueError("tournament_size must be between 2 and population_size")

    started = perf_counter()
    recorder = EventRecorder(max_events)
    rng = Random(seed)
    length = max_steps or default_sequence_length(environment)
    population = [random_candidate(rng, environment, length) for _ in range(population_size)]
    evaluations = population_size
    best = min(population, key=lambda candidate: candidate.score)
    immigrants = max(1, int(population_size * immigrant_rate))

    def select() -> Candidate:
        return min(rng.sample(population, tournament_size), key=lambda candidate: candidate.score)

    for generation in range(generations):
        generation_best = min(population, key=lambda candidate: candidate.score)
        if generation_best.score < best.score:
            best = generation_best
        recorder.add(
            "generation",
            generation_best.states[-1],
            generation=generation,
            average_score=sum(candidate.score for candidate in population) / population_size,
            best=event_payload(best),
        )

        next_population = [best]
        target_children = population_size - immigrants
        while len(next_population) < target_children:
            parent_a, parent_b = select(), select()
            cut = rng.randrange(1, length)
            child_sequence = parent_a.sequence[:cut] + parent_b.sequence[cut:]
            if rng.random() < mutation_rate:
                child_sequence = mutate_tail(rng, environment, child_sequence)
            next_population.append(evaluate(environment, child_sequence))
            evaluations += 1
        for _ in range(immigrants):
            next_population.append(random_candidate(rng, environment, length))
            evaluations += 1
        population = next_population[:population_size]

    final_best = min(population, key=lambda candidate: candidate.score)
    if final_best.score < best.score:
        best = final_best
    path = best.states if best.success else None
    actions = best.actions_used if best.success else None
    return build_result(
        algorithm="genetic_algorithm",
        display_name="Genetic Algorithm",
        family="local",
        guarantees=GUARANTEES,
        environment=environment,
        started_at=started,
        recorder=recorder,
        nodes_expanded=0,
        nodes_generated=0,
        max_frontier_size=population_size,
        path=path,
        actions=actions,
        evaluations=evaluations,
        iterations=generations,
        memory_units=population_size * length,
        notes=["Elitism preserves the best path; immigrants restore diversity after convergence."],
    )
