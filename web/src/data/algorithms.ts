import type { Algorithm } from "../lib/types";

export interface AlgorithmInfo {
  id: Algorithm;
  short: string;
  name: string;
  family: "uninformed" | "informed" | "local";
  description: string;
  badge: string;
}

export const ALGORITHMS: AlgorithmInfo[] = [
  { id: "bfs", short: "BFS", name: "Breadth-First Search", family: "uninformed", description: "Layer-by-layer exploration that guarantees the fewest moves.", badge: "Complete" },
  { id: "dfs", short: "DFS", name: "Depth-First Search", family: "uninformed", description: "Commits deeply before backtracking; lean, fast, and intentionally non-optimal.", badge: "Low memory" },
  { id: "ucs", short: "UCS", name: "Uniform-Cost Search", family: "uninformed", description: "Dijkstra-style expansion that finds the cheapest weighted route.", badge: "Cost optimal" },
  { id: "ids", short: "IDS", name: "Iterative Deepening", family: "uninformed", description: "DFS memory behavior with progressively deeper limits and bounded traces.", badge: "Depth optimal" },
  { id: "greedy", short: "GBFS", name: "Greedy Best-First", family: "informed", description: "Chases the heuristic directly for aggressive, usually fast solutions.", badge: "Heuristic" },
  { id: "astar", short: "A*", name: "A-Star Search", family: "informed", description: "Balances known cost and admissible estimates for provably optimal routes.", badge: "Best balance" },
  { id: "hill_climbing", short: "HC", name: "Hill Climbing", family: "local", description: "Improves candidate routes with random restarts and visible local minima.", badge: "Stochastic" },
  { id: "simulated_annealing", short: "SA", name: "Simulated Annealing", family: "local", description: "Accepts calculated setbacks early, then cools into focused exploitation.", badge: "Escapes minima" },
  { id: "genetic_algorithm", short: "GA", name: "Genetic Algorithm", family: "local", description: "Evolves a diverse population with elitism, crossover, mutation, and immigrants.", badge: "Population" },
];

export const FAMILY_LABELS = {
  uninformed: "Uninformed search",
  informed: "Heuristic search",
  local: "Local search",
} as const;

