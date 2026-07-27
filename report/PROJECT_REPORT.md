# Warehouse Intelligence Lab

## CSAI 301 Artificial Intelligence Project - Integrated Search and Learning System

**Made by:** Ammar Ahmed · Ahmed Sameh · Kareem Wael  
**Under the supervision of:** Dr Doaa

### Executive summary

This project builds a single warehouse pickup-and-delivery problem and studies it through classical search, heuristic search, local optimization, and reinforcement learning. The shared model makes every subsystem part of one coherent intelligent application: every method uses the same state semantics, actions, obstacles, pickup rule, delivery rule, and weighted movement costs.

The default 32 by 32 environment contains approximately 1,500 valid modeled states, satisfying the assignment target of 1,000-10,000 states. The search study implements every required algorithm and compares eleven configurations. The learning study trains a policy with tabular Q-learning and exports both midpoint and final Q-values. A React web laboratory visualizes search traces, local-search candidate evolution, controlled comparisons, learning curves, Q-value change, and the final policy.

Three-seed experiments show the intended trade-offs. UCS and both A* configurations returned the lowest mean weighted cost (59.0), while Manhattan A* reduced mean search work from 1,152.7 UCS expansions to 308. Q-learning achieved a 100% success rate over the final 100 episodes for all three seeds and generated a valid evaluation policy in every run.

## 1. Problem definition and assumptions

The environment is a rectangular warehouse grid. The robot starts at `S`, must reach package location `P`, and may complete the task only after carrying the package to delivery location `D`.

State: `s = (row, column, has_package)`. The Boolean package flag is essential because the same coordinate before and after pickup represents different future possibilities. The modeled state-space size is twice the number of traversable cells.

Actions: `A = {UP, DOWN, LEFT, RIGHT}`. An action changes position by one orthogonal cell when the destination is inside the grid and is not a wall. Search algorithms receive only legal successors. Reinforcement learning may attempt an illegal move and receives a collision penalty while remaining in place.

Transition cost: entering normal, medium, or heavy terrain costs 1, 2, or 4 units. All costs are positive. Weighted terrain creates a meaningful distinction between minimizing the number of moves and minimizing total cost.

Terminal condition: `has_package = true` and the robot is at `D`. Pickup is automatic when the robot enters `P`.

Environment generation uses a reproducible random seed and rejects maps unless both start-to-pickup and pickup-to-delivery paths exist. State-space size is calculated as `traversable cells x 2 package-status values`. For seed 7, `781 x 2 = 1,562` states; seeds 11 and 19 produce 1,606 and 1,582 states. All three satisfy the required 1,000-10,000 range.

## 2. Software architecture

The root-level architecture mirrors the algorithm list in the brief. `environment.py` owns the problem and MDP, `state.py` owns immutable shared types, and each algorithm has a dedicated module. `search_core.py` only centralizes trace recording, path reconstruction, and result creation. `local_search_core.py` centralizes the common candidate encoding and evaluation needed by three population/trajectory methods. `compare.py` is the reproducible experiment runner; `visualization.py` produces static report artifacts; and `api.py` exposes the same implementations to the web interface.

This separation provides three benefits: each algorithm remains short enough to explain orally, tests can isolate one behavior at a time, and the web layer cannot silently use a different implementation from the submitted Python code.

## 3. Search algorithms

### 3.1 Uninformed search

Breadth-First Search uses a FIFO frontier and a discovered set. It is complete on this finite graph and optimal in number of moves, but weighted terrain means it is not guaranteed to minimize total cost. Its worst-case time and space are exponential in solution depth under the standard tree-search notation.

Depth-First Search uses a LIFO frontier. The finite closed set makes this implementation complete for the finite warehouse graph, but it returns the first encountered solution and has no move or cost optimality guarantee. Its principal advantage is a relatively small frontier.

Uniform-Cost Search uses a priority queue ordered by cumulative path cost `g(n)`. Because every movement cost is strictly positive, it is complete and returns a minimum-cost solution.

Iterative Deepening Search repeatedly runs depth-limited search with limits 0, 1, 2, and so on. It combines the depth optimality of BFS for unit-depth goals with the memory profile of DFS. It repeats substantial work and, like BFS, is not cost-optimal under weighted terrain.

### 3.2 Informed search and two heuristics

Greedy Best-First Search orders the frontier by `h(n)` alone. It is fast in these finite maps because it aggressively approaches the current subgoal, but it ignores cost already incurred and therefore is not optimal.

A* orders by `f(n) = g(n) + h(n)`. With a consistent admissible heuristic and positive movement costs, the graph-search implementation is complete and cost-optimal.

Both heuristics account for the mission stage. Before pickup, they estimate distance from the current position to `P` plus `P` to `D`; after pickup, they estimate the distance to `D` only.

- Manhattan distance: `|r1-r2| + |c1-c2|`. It is admissible because each action changes one coordinate by one and the minimum step cost is 1. It is consistent because an orthogonal transition can reduce Manhattan distance by at most one.
- Euclidean distance: `sqrt((r1-r2)^2 + (c1-c2)^2)`. Straight-line distance never exceeds an obstacle-constrained orthogonal route, so it is also admissible and consistent.

Manhattan is usually more informed on a four-neighbor grid. The experiment supports this: Manhattan A* averaged 308 expansions, whereas Euclidean A* averaged 516.3, with identical mean solution cost.

### 3.3 Local search

All local methods optimize fixed-length action sequences rather than individual grid states. A candidate is simulated from `S`; its score includes progress toward the active subgoal, movement cost, collisions, and a large feasibility tier. That tier is critical: every valid complete delivery outranks any unfinished route, preventing a near-goal invalid sequence from appearing better than a real solution.

Hill Climbing mutates one candidate at a time and accepts improvements. Random restarts reduce, but do not remove, sensitivity to local optima and plateaus.

Simulated Annealing may accept a worse candidate with probability `exp(delta / temperature)`. A high initial temperature supports exploration; geometric cooling gradually emphasizes exploitation.

The Genetic Algorithm maintains a population with tournament selection, elitism, one-point crossover, mutation, and random immigrants. Diversity helps explore multiple route regions, at the cost of the largest evaluation and runtime budget.

No finite run of these three methods is complete or optimal. Their stochastic nature is why fixed seeds and multiple runs are required for fair analysis.

## 4. Search experimental evaluation

The controlled experiment used 32 by 32 weighted warehouses, obstacle ratio 0.22, and seeds 7, 11, and 19. Each configuration solved the environment generated from the same seed. Reported work is nodes expanded for graph search and candidate evaluations for local search. Memory is an implementation-level proxy: graph methods report peak frontier states, while local methods report encoded action slots retained by the active trajectory or population. Times are machine-dependent; work, memory, and solution quality provide reproducible structural evidence.

| Configuration | Success | Mean cost | Mean runtime (ms) | Mean work | Mean memory | Complete | Cost-optimal |
|---|---:|---:|---:|---:|---:|:---:|:---:|
| BFS | 100% | 68.3 | 7.8 | 1,223.7 | 51.0 | Yes | No |
| DFS | 100% | 340.3 | 7.0 | 1,019.0 | 287.0 | Yes* | No |
| UCS | 100% | 59.0 | 8.5 | 1,152.7 | 57.3 | Yes | Yes |
| IDS | 100% | 68.3 | 790.3 | 132,846.3 | 55.0 | Yes | No |
| Greedy - Manhattan | 100% | 76.0 | 0.5 | 57.0 | 57.7 | Yes* | No |
| Greedy - Euclidean | 100% | 68.7 | 0.4 | 49.3 | 54.7 | Yes* | No |
| A* - Manhattan | 100% | 59.0 | 2.4 | 308.0 | 71.3 | Yes | Yes |
| A* - Euclidean | 100% | 59.0 | 4.1 | 516.3 | 77.3 | Yes | Yes |
| Hill Climbing | 100% | 82.7 | 1,789.4 | 2,406.0 | 381.3 | No | No |
| Simulated Annealing | 100% | 82.7 | 2,785.2 | 3,204.0 | 381.3 | No | No |
| Genetic Algorithm | 100% | 84.0 | 4,146.2 | 8,884.0 | 12,202.7 | No | No |

`Yes*` refers to this finite graph implementation with a closed set, not the unrestricted infinite-depth tree-search form.

The strongest overall classical method is Manhattan A*. It matches UCS's optimum while using about 73% fewer expansions on average. BFS has the smallest mean memory proxy at 51 units; UCS remains close at 57.3. The Genetic Algorithm's 12,202.7 units expose the storage cost of maintaining a population. Greedy is fastest and uses the least work but sacrifices solution quality. IDS repeats substantial work while retaining a small frontier. The local methods find feasible routes but require more runtime and memory and provide no proof of optimality.

## 5. Visualization

Search events are recorded independently from rendering. The trace contains expansion/candidate events, the current state, frontier size, and available `g`, `h`, and `f` values. Trace storage is capped and reports truncation explicitly, keeping IDS and long local runs safe.

The web laboratory displays explored cells, the current state, and the final route. Local-search playback displays the best candidate path as it evolves. The comparison page charts selectable cost, runtime, work, and memory metrics and provides a theoretical decision matrix. Static report figures are exported from the same results. This satisfies the visualization requirement without changing algorithm behavior.

## 6. Q-learning formulation

The Q-learning agent uses the same state representation and four actions as the search solvers. Unlike explicit search, the agent learns action values from reward and experience.

The update is:

`Q(s,a) <- Q(s,a) + alpha [r + gamma max_a' Q(s',a') - Q(s,a)]`

The default learning rate is `alpha = 0.24`, allowing useful adaptation without replacing old estimates in one step. The discount factor is `gamma = 0.96`, valuing the delayed delivery reward while slightly preferring shorter/cheaper behavior. Epsilon-greedy exploration decays from 1.00 to 0.04, moving from broad exploration to stable exploitation while retaining a small chance of discovering alternatives.

Reward shaping preserves the actual objective:

- delivery bonus: large positive terminal reward;
- pickup bonus: positive reward for completing the first mission stage;
- legal movement: negative terrain cost;
- collision: additional negative penalty;
- progress shaping: small potential-based signal toward `P` before pickup and `D` afterward;
- timeout: negative reward when an episode exceeds its step budget.

The Q-table is initialized with a weak heuristic preference to reduce wasted early motion without hard-coding the final policy. The training output retains a complete midpoint snapshot at episode 700, a complete final snapshot at episode 1,400, a state lookup, the greedy policy, a learning curve, and a no-exploration evaluation trajectory.

## 7. Learning results and policy analysis

| Seed | Training successes | Final 100 success | Evaluation | Policy cost | Runtime (ms) |
|---:|---:|---:|:---:|---:|---:|
| 7 | 1,298 / 1,400 | 100% | Valid | 72.0 | 1,655.1 |
| 11 | 1,336 / 1,400 | 100% | Valid | 38.0 | 1,202.2 |
| 19 | 1,300 / 1,400 | 100% | Valid | 73.0 | 1,684.5 |

All three final policies completed the task without exploratory actions. The last-100 success rate reached 100% in every seed, demonstrating convergence to reliable behavior. Policy cost varies because each seed generates a different warehouse and Q-learning optimizes expected discounted reward, not an exact shortest-path proof. The learned policy should therefore be described as successful and stable, not guaranteed optimal.

The midpoint and final CSV files contain every state-action value, not a selected screenshot. The learning curve reports averaged reward, steps, success rate, and epsilon, allowing the improvement claim to be checked quantitatively. The policy map overlays the evaluated route on the warehouse and the web lab exposes initial-state midpoint/final values directly.

## 8. Testing, reliability, and limitations

The automated suite covers environment invariants, state-space sizing, successor and reward semantics, classical optimality relationships, both heuristics, all local methods, Q-learning snapshots/evaluation, API validation, and experiment export. Static checking uses Ruff for Python and Oxlint plus TypeScript compilation for the frontend. The production Vite build verifies asset generation.

Reproducibility is explicit: all stochastic algorithms receive local seeded random generators. Search trace limits avoid memory blowups. API input models reject malformed grids and out-of-range parameters. The UI clears stale results when its algorithm, heuristic, or environment changes and surfaces backend errors.

Limitations remain honest. Three seeds demonstrate the required comparison but do not establish performance over all warehouse distributions. Runtime depends on hardware. Tabular Q-learning scales poorly beyond the assignment-sized state space. Local-search quality depends on finite budgets. The reward-shaped policy is not guaranteed to match the true minimum-cost path. These limitations are analysis points rather than hidden defects.

## 9. Reflection and future improvements

The shared model was the most important design decision: it made every result directly comparable and exposed the practical difference between move depth, weighted cost, search work, and retained memory. The experiments show that stronger guidance does not automatically mean higher memory use, and that population-based optimization pays a visible storage cost for diversity. The deterministic memory proxy is appropriate for explaining implementation structure, while a future extension should add process-level peak-byte profiling, more environment seeds, confidence intervals, and larger maps. A second extension would replace the tabular Q-function with function approximation while preserving the same evaluation contract.

## 10. Conclusion

The project integrates planning, stochastic optimization, and learning on one coherent model. It demonstrates why guarantees matter: UCS and A* prove minimum weighted cost, BFS and IDS target depth, Greedy trades quality for speed, and local methods trade guarantees for stochastic exploration. Q-learning then replaces explicit planning with learned action values and produces a reliable final policy. The generated source, raw data, figures, Q-tables, tests, report, and interactive visualization form a reproducible evidence trail aligned with every technical requirement in the assignment brief.

## Appendix A - reproducibility commands

Install packages from `requirements.txt`, start the API and web interface with `scripts/start.ps1`, run all checks with `scripts/verify.ps1`, and regenerate experiment data with:

`python compare.py --output results --seeds 7 11 19 --rows 32 --cols 32 --obstacles 0.22 --q-episodes 1400`

## Appendix B - evidence files

- `results/search_runs.csv`: one row per algorithm/seed run.
- `results/search_summary.csv`: submission-ready comparison table including memory.
- `results/search_summary.json`: means, standard deviations, success, and guarantees.
- `results/search_comparison.png`: static comparison figure.
- `results/learning_summary.json`: training and policy metrics by seed.
- `results/q_values_midpoint.csv` and `q_values_final.csv`: complete Q-table snapshots.
- `results/learning_curve.png`: learning evidence.
- `results/learned_policy.png`: evaluated final policy.
