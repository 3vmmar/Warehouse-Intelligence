export type Cell = [number, number];
export type StateTuple = [row: number, col: number, hasPackage: boolean];
export type View = "overview" | "search" | "compare" | "learning";
export type Heuristic = "manhattan" | "euclidean";
export type Algorithm =
  | "bfs"
  | "dfs"
  | "ucs"
  | "ids"
  | "greedy"
  | "astar"
  | "hill_climbing"
  | "simulated_annealing"
  | "genetic_algorithm";

export interface EnvironmentData {
  grid: number[][];
  terrain_costs: number[][];
  start: Cell;
  pickup: Cell;
  delivery: Cell;
  rows: number;
  cols: number;
  state_space_size: number;
  minimum_step_cost: number;
}

export interface Guarantees {
  complete: boolean;
  optimal: boolean;
  optimality_scope: string;
  time_complexity: string;
  space_complexity: string;
}

export interface SearchEvent {
  step: number;
  kind: string;
  state: StateTuple | null;
  frontier_size: number | null;
  g: number | null;
  h: number | null;
  f: number | null;
  extra: {
    best?: {
      score: number;
      path_cost: number;
      success: boolean;
      collisions: number;
      path: StateTuple[];
    };
    [key: string]: unknown;
  };
}

export interface SearchMetrics {
  nodes_expanded: number;
  nodes_generated: number;
  max_frontier_size: number;
  evaluations: number;
  iterations: number;
  memory_units: number;
  path_cost: number | null;
  path_length: number | null;
  runtime_ms: number;
  solution_found: boolean;
}

export interface SearchResult {
  algorithm: string;
  display_name: string;
  family: "uninformed" | "informed" | "local";
  guarantees: Guarantees;
  metrics: SearchMetrics;
  path: StateTuple[] | null;
  actions: string[] | null;
  events: SearchEvent[];
  events_truncated: boolean;
  notes: string[];
}

export interface ComparisonRow {
  algorithm: string;
  display_name: string;
  family: string;
  runs: number;
  success_rate: number;
  mean_path_cost: number | null;
  std_path_cost: number | null;
  mean_runtime_ms: number;
  std_runtime_ms: number;
  mean_work_units: number;
  mean_memory_units: number;
  std_memory_units: number;
  theoretically_complete: boolean;
  theoretically_optimal: boolean;
  optimality_scope: string;
}

export interface ComparisonResponse {
  summary: ComparisonRow[];
  runs: Record<string, string | number | boolean | null>[];
  state_space_size: number;
}

export interface LearningPoint {
  episode: number;
  average_reward: number;
  average_steps: number;
  success_rate: number;
  epsilon: number;
}

export interface QLearningResult {
  config: {
    episodes: number;
    max_steps_per_episode: number;
    learning_rate: number;
    discount_factor: number;
    epsilon_start: number;
    epsilon_end: number;
    seed: number;
    curve_interval: number;
  };
  q_values_midpoint: number[][];
  q_values_final: number[][];
  state_lookup: StateTuple[];
  policy: Array<string | null>;
  policy_path: StateTuple[] | null;
  policy_actions: string[] | null;
  policy_cost: number | null;
  training_curve: LearningPoint[];
  midpoint_episode: number;
  training_successes: number;
  final_100_success_rate: number;
  best_episode_reward: number;
  evaluation_success: boolean;
  training_runtime_ms: number;
  reward_design: Record<string, string>;
}

interface EnvironmentRequestBody {
  grid: number[][];
  terrain_costs: number[][];
  start: Cell;
  pickup: Cell;
  delivery: Cell;
}

export interface GenerateRequest {
  rows: number;
  cols: number;
  obstacle_ratio: number;
  seed: number;
  weighted_terrain: boolean;
}

export interface SolveRequest extends EnvironmentRequestBody {
  algorithm: Algorithm;
  heuristic: Heuristic;
  seed: number;
}

export interface ComparisonRequest extends EnvironmentRequestBody {
  seed: number;
  quick: boolean;
}

export interface TrainRequest extends EnvironmentRequestBody {
  episodes: number;
  max_steps_per_episode: number;
  learning_rate: number;
  discount_factor: number;
  epsilon_start: number;
  epsilon_end: number;
  seed: number;
}
