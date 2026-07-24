"""Reproducible experiments and exports for both phases.

Run `python compare.py` to regenerate every CSV, JSON, and PNG used by the
report. The same functions power the web comparison dashboard.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

from astar import astar
from bfs import bfs
from dfs import dfs
from environment import WarehouseEnvironment, generate_environment
from genetic import genetic_algorithm
from greedy import greedy
from hill_climbing import hill_climbing
from ids import ids
from q_learning import QLearningConfig, QLearningResult, train_q_learning
from simulated_annealing import simulated_annealing
from state import SearchResult
from ucs import ucs
from visualization import save_phase1_comparison, save_policy_map, save_q_learning_curve


def run_phase1_suite(
    environment: WarehouseEnvironment,
    seed: int = 7,
    quick: bool = False,
) -> list[SearchResult]:
    local_kwargs = (
        {
            "hill": {"iterations": 600, "restarts": 3},
            "anneal": {"iterations": 800, "restarts": 2},
            "genetic": {"population_size": 32, "generations": 45},
        }
        if quick
        else {
            "hill": {},
            "anneal": {},
            "genetic": {},
        }
    )
    return [
        bfs(environment),
        dfs(environment),
        ucs(environment),
        ids(environment),
        greedy(environment, "manhattan"),
        greedy(environment, "euclidean"),
        astar(environment, "manhattan"),
        astar(environment, "euclidean"),
        hill_climbing(environment, seed=seed, **local_kwargs["hill"]),
        simulated_annealing(environment, seed=seed, **local_kwargs["anneal"]),
        genetic_algorithm(environment, seed=seed, **local_kwargs["genetic"]),
    ]


def results_to_rows(results: list[SearchResult], environment_seed: int) -> list[dict]:
    rows = []
    for result in results:
        metrics = result.metrics
        rows.append(
            {
                "environment_seed": environment_seed,
                "algorithm": result.algorithm,
                "display_name": result.display_name,
                "family": result.family,
                "solution_found": metrics.solution_found,
                "path_cost": metrics.path_cost,
                "path_length": metrics.path_length,
                "runtime_ms": metrics.runtime_ms,
                "nodes_expanded": metrics.nodes_expanded,
                "evaluations": metrics.evaluations,
                "work_units": metrics.nodes_expanded or metrics.evaluations,
                "memory_units": metrics.memory_units,
                "theoretically_complete": result.guarantees.complete,
                "theoretically_optimal": result.guarantees.optimal,
                "optimality_scope": result.guarantees.optimality_scope,
            }
        )
    return rows


def summarize_rows(rows: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["algorithm"]].append(row)

    summary = []
    for algorithm, group in grouped.items():
        successful = [row for row in group if row["solution_found"]]
        base = group[0]
        costs = [float(row["path_cost"]) for row in successful]
        runtimes = [float(row["runtime_ms"]) for row in group]
        work = [float(row["work_units"]) for row in group]
        summary.append(
            {
                "algorithm": algorithm,
                "display_name": base["display_name"],
                "family": base["family"],
                "runs": len(group),
                "success_rate": len(successful) / len(group),
                "mean_path_cost": mean(costs) if costs else None,
                "std_path_cost": stdev(costs) if len(costs) > 1 else 0.0 if costs else None,
                "mean_runtime_ms": mean(runtimes),
                "std_runtime_ms": stdev(runtimes) if len(runtimes) > 1 else 0.0,
                "mean_work_units": mean(work),
                "theoretically_complete": base["theoretically_complete"],
                "theoretically_optimal": base["theoretically_optimal"],
                "optimality_scope": base["optimality_scope"],
            }
        )
    return summary


def run_full_experiment(
    output_dir: str | Path = "results",
    seeds: tuple[int, ...] = (7, 11, 19),
    rows: int = 32,
    cols: int = 32,
    obstacle_ratio: float = 0.22,
    q_episodes: int = 1_400,
    quick: bool = False,
) -> dict:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    raw_rows: list[dict] = []
    q_results: list[QLearningResult] = []
    environments: list[WarehouseEnvironment] = []

    for seed in seeds:
        environment = generate_environment(rows, cols, obstacle_ratio, seed)
        environments.append(environment)
        raw_rows.extend(results_to_rows(run_phase1_suite(environment, seed, quick), seed))
        q_config = QLearningConfig(
            episodes=350 if quick else q_episodes,
            max_steps_per_episode=260 if quick else 420,
            seed=seed,
        )
        q_results.append(train_q_learning(environment, q_config))

    summary = summarize_rows(raw_rows)
    _write_csv(output / "phase1_raw.csv", raw_rows)
    _write_json(output / "phase1_summary.json", summary)
    _write_json(
        output / "phase2_summary.json",
        [_compact_q_result(result, seed) for result, seed in zip(q_results, seeds, strict=True)],
    )
    _write_q_values(output / "q_values_midpoint.csv", environments[0], q_results[0], midpoint=True)
    _write_q_values(output / "q_values_final.csv", environments[0], q_results[0], midpoint=False)
    save_phase1_comparison(summary, output / "phase1_comparison.png")
    save_q_learning_curve(q_results[0], output / "phase2_learning_curve.png")
    save_policy_map(environments[0], q_results[0], output / "phase2_policy.png")
    manifest = {
        "environment_seeds": list(seeds),
        "rows": rows,
        "cols": cols,
        "obstacle_ratio": obstacle_ratio,
        "state_space_sizes": [environment.state_space_size for environment in environments],
        "phase1_algorithms": len(summary),
        "phase2_success_rate": mean(result.final_100_success_rate for result in q_results),
        "files": sorted(path.name for path in output.iterdir() if path.is_file()),
    }
    _write_json(output / "experiment_manifest.json", manifest)
    return {"raw": raw_rows, "summary": summary, "q_results": q_results, "manifest": manifest}


def _compact_q_result(result: QLearningResult, seed: int) -> dict:
    return {
        "seed": seed,
        "episodes": result.config.episodes,
        "training_successes": result.training_successes,
        "final_100_success_rate": result.final_100_success_rate,
        "evaluation_success": result.evaluation_success,
        "policy_cost": result.policy_cost,
        "training_runtime_ms": result.training_runtime_ms,
        "best_episode_reward": result.best_episode_reward,
    }


def _write_q_values(
    path: Path,
    environment: WarehouseEnvironment,
    result: QLearningResult,
    midpoint: bool,
) -> None:
    values = result.q_values_midpoint if midpoint else result.q_values_final
    rows = []
    for state_tuple, row in zip(result.state_lookup, values, strict=True):
        rows.append(
            {
                "row": state_tuple[0],
                "col": state_tuple[1],
                "has_package": state_tuple[2],
                "UP": row[0],
                "DOWN": row[1],
                "LEFT": row[2],
                "RIGHT": row[3],
            }
        )
    _write_csv(path, rows)


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run every CSAI 301 experiment")
    parser.add_argument("--output", default="results")
    parser.add_argument("--seeds", nargs="+", type=int, default=[7, 11, 19])
    parser.add_argument("--rows", type=int, default=32)
    parser.add_argument("--cols", type=int, default=32)
    parser.add_argument("--obstacles", type=float, default=0.22)
    parser.add_argument("--q-episodes", type=int, default=1_400)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    result = run_full_experiment(
        args.output,
        tuple(args.seeds),
        args.rows,
        args.cols,
        args.obstacles,
        args.q_episodes,
        args.quick,
    )
    print(json.dumps(result["manifest"], indent=2))


if __name__ == "__main__":
    main()
