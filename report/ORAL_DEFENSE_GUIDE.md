# Oral Defense Guide

## The 30-second explanation

The project models a warehouse robot that must pick up a package before delivery. A state is position plus a package flag, so the same location can represent two different situations. Weighted terrain makes BFS move-optimal but not cost-optimal. UCS is cost-optimal, and A* preserves that guarantee while using admissible Manhattan or Euclidean estimates. The local methods optimize complete action sequences without guarantees. Phase 2 uses the identical problem as an MDP and learns a reliable policy through Q-learning.

## Questions you should answer confidently

### Why include `has_package` in the state?

Without it, the process is not Markov: the legal meaning of reaching delivery depends on whether pickup happened earlier. Position alone loses information needed to predict reward and termination.

### Why is BFS not cost-optimal here?

BFS minimizes the number of actions when every edge counts as one level. Terrain costs are 1, 2, and 4, so a longer route through cheap cells may cost less than a shorter route through heavy cells.

### Why is UCS optimal?

It always expands the open state with the smallest cumulative cost. All edge costs are positive, so when a goal is popped its cost cannot later be improved.

### Why are both heuristics admissible?

They ignore walls and multiply distance by the minimum step cost. Ignoring constraints can only underestimate or equal the real remaining cost. Before pickup, each estimate includes current-to-pickup plus pickup-to-delivery.

### Why did Manhattan A* expand fewer nodes than Euclidean A*?

On a four-neighbor grid Manhattan usually gives a larger admissible estimate than Euclidean. A larger still-admissible estimate is more informed and narrows the search more strongly.

### Is Greedy complete?

This implementation is complete on the finite warehouse graph because it maintains a closed set and eventually can exhaust the finite frontier. Greedy is still not cost-optimal. In unrestricted infinite search spaces, that completeness statement would need different conditions.

### Why is IDS slow?

It repeats shallow expansions at every increasing depth limit. The memory advantage remains, but this warehouse's goal depth makes the repeated work visible.

### What exactly do the local methods optimize?

A fixed-length sequence of actions. Simulation measures whether it completes the mission, movement cost, collisions, and progress. A feasibility tier ensures any valid delivery beats every unfinished candidate.

### Why can local search not promise an optimum?

It samples a limited candidate neighborhood or population and may stop at local optima, cool too quickly, or miss useful genetic combinations. Finite stochastic budgets provide no exhaustive proof.

### Explain the Q-learning update in plain language.

The chosen action value moves toward the immediate reward plus the discounted value of the best next action. Alpha controls how much the new experience changes the estimate; gamma controls how strongly future reward matters.

### Why use epsilon decay?

High early epsilon explores many actions. Lower later epsilon exploits learned values. A final floor of 0.04 retains limited exploration during training; evaluation uses no exploration.

### Is the learned policy optimal?

No proof is claimed. It is empirically successful and stable. Reward shaping, finite training, stochastic exploration, and function choice mean Q-learning's evaluation path can differ from the exact UCS/A* optimum.

### What proves learning happened?

The learning curve shows reward and success over episodes, epsilon decreases, full Q-values are saved at the midpoint and final episode, and the greedy policy is evaluated separately. Across three seeds the last 100 episodes were 100% successful.

### How is the comparison fair?

Every algorithm for one seed gets the same environment. Deterministic search has identical inputs; stochastic methods receive controlled local seeds. The report separates empirical metrics from theoretical guarantees.

## Numbers worth remembering

- Modeled states: 1,562, 1,606, and 1,582.
- Eleven Phase 1 configurations; all succeeded on the three selected seeds.
- Best mean cost: 59.0 for UCS and both A* configurations.
- Mean work: UCS 1,152.7 expansions; Manhattan A* 308.
- Q-learning: 1,400 episodes; alpha 0.24; gamma 0.96; epsilon 1.00 to 0.04.
- Final-100 success: 100% for all three Q-learning seeds.

## Safe live demonstration order

1. Open Overview and state the shared problem.
2. Open Search Lab; show the state count is within 1K-10K.
3. Run BFS and point out move optimality versus weighted cost.
4. Run UCS and A* Manhattan; compare cost and expanded nodes.
5. Run one local method and replay evolving candidate paths.
6. Open Compare and run all eleven configurations.
7. Open Q-Learning, train, show the curve, midpoint/final Q-values, and policy map.
8. End with the generated raw results and tests.

## Traps to avoid

- Do not call BFS cost-optimal on weighted terrain.
- Do not call Greedy or a local method optimal.
- Do not claim Q-learning proves the shortest path.
- Do not compare raw runtimes as universal facts; they depend on the machine.
- Do not say the heuristic sees obstacles; it deliberately underestimates by ignoring them.
- Do not confuse search `visited` logic with RL exploration.
