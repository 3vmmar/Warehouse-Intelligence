"""Validated FastAPI surface for the premium web laboratory."""

from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from astar import GUARANTEES as ASTAR_GUARANTEES
from astar import astar
from bfs import GUARANTEES as BFS_GUARANTEES
from bfs import bfs
from compare import results_to_rows, run_search_suite, summarize_rows
from dfs import GUARANTEES as DFS_GUARANTEES
from dfs import dfs
from environment import WarehouseEnvironment, generate_environment
from genetic import GUARANTEES as GA_GUARANTEES
from genetic import genetic_algorithm
from greedy import GUARANTEES as GREEDY_GUARANTEES
from greedy import greedy
from hill_climbing import GUARANTEES as HC_GUARANTEES
from hill_climbing import hill_climbing
from ids import GUARANTEES as IDS_GUARANTEES
from ids import ids
from q_learning import QLearningConfig, train_q_learning
from simulated_annealing import GUARANTEES as SA_GUARANTEES
from simulated_annealing import simulated_annealing
from ucs import GUARANTEES as UCS_GUARANTEES
from ucs import ucs

app = FastAPI(
    title="Warehouse Intelligence Lab API",
    version="3.0.0",
    description="CSAI 301 search and reinforcement-learning laboratory",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    rows: int = Field(32, ge=5, le=70)
    cols: int = Field(32, ge=5, le=70)
    obstacle_ratio: float = Field(0.22, ge=0.0, le=0.55)
    seed: int = Field(7, ge=0, le=2_147_483_647)
    weighted_terrain: bool = True


class EnvironmentPayload(BaseModel):
    grid: list[list[int]]
    terrain_costs: list[list[float]]
    start: tuple[int, int]
    pickup: tuple[int, int]
    delivery: tuple[int, int]


AlgorithmName = Literal[
    "bfs",
    "dfs",
    "ucs",
    "ids",
    "greedy",
    "astar",
    "a_star",
    "hill_climbing",
    "simulated_annealing",
    "genetic_algorithm",
]


class SolveRequest(EnvironmentPayload):
    algorithm: AlgorithmName
    heuristic: Literal["manhattan", "euclidean"] = "manhattan"
    seed: int = Field(7, ge=0, le=2_147_483_647)
    max_steps: int | None = Field(None, ge=16, le=2_000)
    iterations: int | None = Field(None, ge=10, le=50_000)
    generations: int | None = Field(None, ge=1, le=2_000)
    population_size: int | None = Field(None, ge=8, le=500)
    max_expansions: int = Field(500_000, ge=1_000, le=1_000_000)


class CompareRequest(EnvironmentPayload):
    seed: int = Field(7, ge=0, le=2_147_483_647)
    quick: bool = True


class TrainRequest(EnvironmentPayload):
    episodes: int = Field(1_400, ge=50, le=20_000)
    max_steps_per_episode: int = Field(420, ge=20, le=5_000)
    learning_rate: float = Field(0.24, gt=0, le=1)
    discount_factor: float = Field(0.96, gt=0, le=1)
    epsilon_start: float = Field(1.0, ge=0, le=1)
    epsilon_end: float = Field(0.04, ge=0, le=1)
    seed: int = Field(7, ge=0, le=2_147_483_647)


CATALOG = [
    ("bfs", "BFS", "uninformed", BFS_GUARANTEES),
    ("dfs", "DFS", "uninformed", DFS_GUARANTEES),
    ("ucs", "UCS", "uninformed", UCS_GUARANTEES),
    ("ids", "IDS", "uninformed", IDS_GUARANTEES),
    ("greedy", "Greedy Best-First", "informed", GREEDY_GUARANTEES),
    ("astar", "A*", "informed", ASTAR_GUARANTEES),
    ("hill_climbing", "Hill Climbing", "local", HC_GUARANTEES),
    ("simulated_annealing", "Simulated Annealing", "local", SA_GUARANTEES),
    ("genetic_algorithm", "Genetic Algorithm", "local", GA_GUARANTEES),
]


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "version": "3.0.0",
        "architecture": "integrated",
        "modules": 2,
    }


@app.get("/algorithms")
def algorithms() -> list[dict]:
    return [
        {
            "id": identifier,
            "name": name,
            "family": family,
            "guarantees": guarantees.to_dict(),
        }
        for identifier, name, family, guarantees in CATALOG
    ]


@app.get("/project-status")
def project_status() -> dict:
    return {
        "project": {"status": "complete", "architecture": "integrated"},
        "search": {"status": "complete", "configurations": 11, "heuristics": 2},
        "learning": {"status": "complete", "algorithm": "Tabular Q-learning"},
        "state_space_target": "1K–10K",
        "deliverables": [
            "interactive laboratory",
            "reproducible results",
            "formal report",
            "recorded demonstration",
        ],
    }


@app.post("/generate-environment")
def generate(request: GenerateRequest) -> dict:
    try:
        environment = generate_environment(
            request.rows,
            request.cols,
            request.obstacle_ratio,
            request.seed,
            request.weighted_terrain,
            True,
        )
        return environment.to_dict()
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(400, str(exc)) from exc


@app.post("/solve")
def solve(request: SolveRequest) -> dict:
    environment = _build_environment(request)
    try:
        result = _solve(environment, request)
        return result.to_dict()
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.post("/compare")
def compare(request: CompareRequest) -> dict:
    environment = _build_environment(request)
    results = run_search_suite(environment, request.seed, request.quick)
    rows = results_to_rows(results, request.seed)
    return {
        "summary": summarize_rows(rows),
        "runs": rows,
        "state_space_size": environment.state_space_size,
    }


@app.post("/train-q-learning")
def train(request: TrainRequest) -> dict:
    if request.epsilon_end > request.epsilon_start:
        raise HTTPException(400, "epsilon_end cannot exceed epsilon_start")
    environment = _build_environment(request)
    config = QLearningConfig(
        episodes=request.episodes,
        max_steps_per_episode=request.max_steps_per_episode,
        learning_rate=request.learning_rate,
        discount_factor=request.discount_factor,
        epsilon_start=request.epsilon_start,
        epsilon_end=request.epsilon_end,
        seed=request.seed,
    )
    try:
        return train_q_learning(environment, config).to_dict()
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


def _build_environment(request: EnvironmentPayload) -> WarehouseEnvironment:
    if (
        not request.grid
        or not request.grid[0]
        or not 5 <= len(request.grid) <= 70
        or not 5 <= len(request.grid[0]) <= 70
    ):
        raise HTTPException(400, "environment dimensions must each be between 5 and 70")
    try:
        return WarehouseEnvironment(
            request.grid,
            request.terrain_costs,
            request.start,
            request.pickup,
            request.delivery,
        )
    except (ValueError, IndexError) as exc:
        raise HTTPException(400, str(exc)) from exc


def _solve(environment: WarehouseEnvironment, request: SolveRequest):
    if request.algorithm == "bfs":
        return bfs(environment)
    if request.algorithm == "dfs":
        return dfs(environment)
    if request.algorithm == "ucs":
        return ucs(environment)
    if request.algorithm == "ids":
        return ids(environment, max_expansions=request.max_expansions)
    if request.algorithm == "greedy":
        return greedy(environment, request.heuristic)
    if request.algorithm in ("astar", "a_star"):
        return astar(environment, request.heuristic)
    if request.algorithm == "hill_climbing":
        kwargs = {"seed": request.seed}
        if request.max_steps is not None:
            kwargs["max_steps"] = request.max_steps
        if request.iterations is not None:
            kwargs["iterations"] = request.iterations
        return hill_climbing(environment, **kwargs)
    if request.algorithm == "simulated_annealing":
        kwargs = {"seed": request.seed}
        if request.max_steps is not None:
            kwargs["max_steps"] = request.max_steps
        if request.iterations is not None:
            kwargs["iterations"] = request.iterations
        return simulated_annealing(environment, **kwargs)
    kwargs = {"seed": request.seed}
    if request.max_steps is not None:
        kwargs["max_steps"] = request.max_steps
    if request.generations is not None:
        kwargs["generations"] = request.generations
    if request.population_size is not None:
        kwargs["population_size"] = request.population_size
    return genetic_algorithm(environment, **kwargs)
