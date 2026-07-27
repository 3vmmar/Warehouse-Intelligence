
# Warehouse Intelligence Lab

A complete CSAI 301 project covering classical search, informed search, local search, reinforcement learning, visualization, controlled experiments, and a premium animated web laboratory.

## Project team

Made by:

- Ammar Ahmed
- Ahmed Sameh
- Kareem Wael

Under the supervision of **Dr Doaa**.

## System coverage

- Search and optimization: BFS, DFS, UCS, IDS, Greedy Best-First with Manhattan and Euclidean heuristics, A* with both heuristics, Hill Climbing, Simulated Annealing, and a Genetic Algorithm.
- Learning and policy: tabular Q-learning on the same pickup-and-delivery problem, including explicit state/action/reward definitions, epsilon-greedy exploration, learning curves, midpoint/final Q-value exports, and final-policy evaluation.
- Analysis: reproducible three-seed experiments, raw CSV data, JSON summaries, comparison charts, Q-learning charts, and policy maps.
- Presentation: animated search traces, evolving local-search candidates, comparison dashboards, and the learned policy.
- Submission support: formal report, oral-defense guide, and a recorded demonstration checklist.

## Clean project structure

```text
CSAI 301 Project/
|-- environment.py              # Warehouse problem and MDP
|-- state.py                    # Shared state, actions, metrics, results
|-- bfs.py
|-- dfs.py
|-- ucs.py
|-- ids.py
|-- astar.py                    # A* plus both admissible heuristics
|-- greedy.py
|-- hill_climbing.py
|-- simulated_annealing.py
|-- genetic.py
|-- q_learning.py
|-- visualization.py
|-- compare.py                  # Reproducible search + learning experiments
|-- api.py                      # FastAPI bridge for the web lab
|-- search_core.py
|-- local_search_core.py
|-- tests/
|-- web/                        # React, TypeScript, Tailwind, Framer Motion
|-- report/                     # Report and presentation support
|-- results/                    # Reproducible outputs
|-- scripts/
|-- requirements.txt
`-- pyproject.toml
```

The two small `*_core.py` files hold shared mechanics so algorithms remain readable without duplicating result construction, path reconstruction, or local-search candidate evaluation.

## Run the project

### One-command development start (Windows)

```powershell
.\scripts\start.ps1
```

The API starts on `http://127.0.0.1:8000` and Vite prints the web URL, normally `http://127.0.0.1:5173`.

### Manual start

Terminal 1:

```powershell
.\.venv\Scripts\python.exe -m uvicorn api:app --reload --port 8000
```

Terminal 2:

```powershell
cd web
npm run dev
```

## Verify everything

```powershell
.\scripts\verify.ps1
```

This runs the Python tests, Ruff static checks, frontend lint, and a production frontend build. To regenerate the complete evidence set:

```powershell
.\.venv\Scripts\python.exe compare.py --output results --seeds 7 11 19 --q-episodes 1400
```

## Problem model

The robot begins at `S`, must visit pickup `P`, and then deliver at `D`. A state is `(row, column, has_package)`. Actions are up, down, left, and right. Walls are invalid; normal, medium, and heavy terrain cost 1, 2, and 4. This makes the difference between move-optimal BFS and cost-optimal UCS/A* measurable. For seed 7, 781 traversable cells × two package-status values produce 1,562 modeled states, satisfying the required 1,000-10,000 range.

## Key results

Across seeds 7, 11, and 19, all eleven search and optimization configurations found valid solutions. UCS and both A* configurations achieved the lowest mean path cost (59.0). Manhattan A* averaged 308 expansions versus 1,152.7 for UCS. BFS used the leanest mean memory proxy (51 units), while the Genetic Algorithm's population required 12,202.7 units. All three Q-learning runs reached a 100% success rate over the final 100 episodes and produced a valid evaluation policy.

See `report/PROJECT_REPORT.md`, `report/ORAL_DEFENSE_GUIDE.md`, `results/search_summary.csv`, and `results/experiment_manifest.json` for the complete interpretation and evidence trail.
