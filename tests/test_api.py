from api import (
    CompareRequest,
    GenerateRequest,
    SolveRequest,
    TrainRequest,
    compare,
    generate,
    health,
    solve,
    train,
)


def test_health_and_generation_contract():
    assert health()["phases"] == 2
    world = generate(GenerateRequest(rows=32, cols=32, seed=7))
    assert 1_000 <= world["state_space_size"] <= 10_000


def test_solve_compare_and_train_endpoints():
    world = generate(GenerateRequest(rows=32, cols=32, seed=9))
    common = {
        "grid": world["grid"],
        "terrain_costs": world["terrain_costs"],
        "start": world["start"],
        "pickup": world["pickup"],
        "delivery": world["delivery"],
    }
    result = solve(SolveRequest(**common, algorithm="astar", heuristic="manhattan"))
    assert result["metrics"]["solution_found"]
    comparison = compare(CompareRequest(**common, seed=9, quick=True))
    assert len(comparison["summary"]) == 11
    learning = train(
        TrainRequest(
            **common,
            episodes=350,
            max_steps_per_episode=300,
            seed=9,
        )
    )
    assert learning["evaluation_success"]
