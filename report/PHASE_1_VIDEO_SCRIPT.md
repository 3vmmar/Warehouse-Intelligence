# Phase 1 Video Script

Target length: 5-7 minutes.

## 0:00-0:35 - Problem and architecture

"This is the Warehouse Intelligence Lab. The robot starts at S, must visit pickup P, and then deliver at D. The state combines row, column, and whether the robot carries the package. The same environment feeds every algorithm. Weighted terrain costs 1, 2, or 4, which makes path cost different from path length."

Show: Overview hero, phase card, and clean root file structure.

## 0:35-1:20 - Environment model

"The default world is 32 by 32 with a reproducible seed. Obstacles are generated only if both mission stages remain reachable. The modeled state count stays inside the assignment's 1,000-10,000 target."

Show: Search Lab environment controls and state counter.

## 1:20-2:30 - Uninformed search

"BFS explores by depth and is optimal in moves, not weighted cost. DFS commits deeply and may return an expensive route. UCS expands by cumulative cost and is optimal because all movement costs are positive. IDS repeats depth-limited search, preserving low memory but doing repeated work."

Show: run BFS, scrub playback, then run UCS and compare costs. Briefly select DFS/IDS cards.

## 2:30-3:35 - Informed search

"Greedy uses only the remaining-distance estimate. A* combines known cost and heuristic. Both Manhattan and Euclidean estimates are admissible; before pickup they estimate current-to-pickup plus pickup-to-delivery. Manhattan is usually more informed on this four-direction grid."

Show: run A* Manhattan and Euclidean; point to guarantees, expansions, and path cost.

## 3:35-4:25 - Local search

"Hill Climbing, Simulated Annealing, and the Genetic Algorithm optimize complete action sequences. A feasibility tier means a valid delivery always outranks an unfinished route. Playback shows the best candidate changing. These methods can find useful routes but have no finite completeness or optimality guarantee."

Show: run one local algorithm and replay candidate evolution; select the other cards.

## 4:25-5:40 - Controlled comparison

"The comparison runs eleven required configurations on the same warehouse: four uninformed, Greedy and A* with both heuristics, and three local methods. It records success, cost, runtime, work, memory, completeness, and optimality. Across three seeds, UCS and both A* variants achieved the lowest mean cost of 59. Manhattan A* averaged 308 expansions versus 1,152.7 for UCS."

Show: Compare page chart and decision matrix; switch cost/work tabs.

## 5:40-6:10 - Evidence and close

"The results folder contains raw CSV rows, JSON summaries, and a static comparison chart. Automated tests verify environment rules, optimality relationships, algorithms, APIs, and exports. This completes Phase 1 with implementation, analysis, and visualization tied to one reproducible model."

Show: results directory, report figure, and verification command output.
