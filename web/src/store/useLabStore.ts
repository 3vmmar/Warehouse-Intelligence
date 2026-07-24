import { create } from "zustand";
import { compareAlgorithms, generateEnvironment, solve, trainQLearning } from "../lib/api";
import type {
  Algorithm,
  ComparisonResponse,
  EnvironmentData,
  Heuristic,
  QLearningResult,
  SearchResult,
  View,
} from "../lib/types";

interface LabState {
  view: View;
  setView: (view: View) => void;

  rows: number;
  cols: number;
  obstacleRatio: number;
  seed: number;
  setEnvironmentParams: (params: Partial<Pick<LabState, "rows" | "cols" | "obstacleRatio" | "seed">>) => void;
  environment: EnvironmentData | null;
  environmentLoading: boolean;
  environmentError: string | null;
  regenerate: () => Promise<void>;

  algorithm: Algorithm;
  heuristic: Heuristic;
  setAlgorithm: (algorithm: Algorithm) => void;
  setHeuristic: (heuristic: Heuristic) => void;
  searchResult: SearchResult | null;
  searchLoading: boolean;
  searchError: string | null;
  runSearch: () => Promise<void>;

  playbackStep: number;
  playbackSpeed: number;
  isPlaying: boolean;
  setPlaybackStep: (step: number) => void;
  setPlaybackSpeed: (speed: number) => void;
  play: () => void;
  pause: () => void;
  tick: () => void;

  comparison: ComparisonResponse | null;
  comparisonLoading: boolean;
  comparisonError: string | null;
  runComparison: () => Promise<void>;

  episodes: number;
  learningRate: number;
  discountFactor: number;
  setLearningParams: (params: Partial<Pick<LabState, "episodes" | "learningRate" | "discountFactor">>) => void;
  qLearning: QLearningResult | null;
  qLoading: boolean;
  qError: string | null;
  trainAgent: () => Promise<void>;
}

const environmentBody = (environment: EnvironmentData) => ({
  grid: environment.grid,
  terrain_costs: environment.terrain_costs,
  start: environment.start,
  pickup: environment.pickup,
  delivery: environment.delivery,
});

export const useLabStore = create<LabState>((set, get) => ({
  view: "overview",
  setView: (view) => set({ view }),

  rows: 32,
  cols: 32,
  obstacleRatio: 0.22,
  seed: 7,
  setEnvironmentParams: (params) => set(params),
  environment: null,
  environmentLoading: false,
  environmentError: null,
  regenerate: async () => {
    const { rows, cols, obstacleRatio, seed } = get();
    set({ environmentLoading: true, environmentError: null, isPlaying: false });
    try {
      const environment = await generateEnvironment({
        rows,
        cols,
        obstacle_ratio: obstacleRatio,
        seed,
        weighted_terrain: true,
      });
      set({
        environment,
        environmentLoading: false,
        searchResult: null,
        comparison: null,
        qLearning: null,
        playbackStep: 0,
      });
    } catch (error) {
      set({ environmentLoading: false, environmentError: (error as Error).message });
    }
  },

  algorithm: "astar",
  heuristic: "manhattan",
  setAlgorithm: (algorithm) =>
    set({ algorithm, searchResult: null, searchError: null, playbackStep: 0, isPlaying: false }),
  setHeuristic: (heuristic) =>
    set({ heuristic, searchResult: null, searchError: null, playbackStep: 0, isPlaying: false }),
  searchResult: null,
  searchLoading: false,
  searchError: null,
  runSearch: async () => {
    const { environment, algorithm, heuristic, seed } = get();
    if (!environment) return;
    set({ searchLoading: true, searchError: null, searchResult: null, isPlaying: false, playbackStep: 0 });
    try {
      const searchResult = await solve({
        ...environmentBody(environment),
        algorithm,
        heuristic,
        seed,
      });
      set({
        searchResult,
        searchLoading: false,
        // Show the verified final path and totals immediately. Pressing Play
        // resets the trace to step zero for a full reasoning replay.
        playbackStep: searchResult.events.length,
      });
    } catch (error) {
      set({ searchLoading: false, searchError: (error as Error).message });
    }
  },

  playbackStep: 0,
  playbackSpeed: 90,
  isPlaying: false,
  setPlaybackStep: (playbackStep) => set({ playbackStep, isPlaying: false }),
  setPlaybackSpeed: (playbackSpeed) => set({ playbackSpeed }),
  play: () => {
    const { searchResult, playbackStep } = get();
    if (!searchResult) return;
    set({
      playbackStep: playbackStep >= searchResult.events.length ? 0 : playbackStep,
      isPlaying: true,
    });
  },
  pause: () => set({ isPlaying: false }),
  tick: () => {
    const { searchResult, playbackStep, isPlaying } = get();
    if (!searchResult || !isPlaying) return;
    const next = Math.min(searchResult.events.length, playbackStep + 1);
    set({ playbackStep: next, isPlaying: next < searchResult.events.length });
  },

  comparison: null,
  comparisonLoading: false,
  comparisonError: null,
  runComparison: async () => {
    const { environment, seed } = get();
    if (!environment) return;
    set({ comparisonLoading: true, comparisonError: null });
    try {
      const comparison = await compareAlgorithms({
        ...environmentBody(environment),
        seed,
        quick: true,
      });
      set({ comparison, comparisonLoading: false });
    } catch (error) {
      set({ comparisonLoading: false, comparisonError: (error as Error).message });
    }
  },

  episodes: 1400,
  learningRate: 0.24,
  discountFactor: 0.96,
  setLearningParams: (params) => set(params),
  qLearning: null,
  qLoading: false,
  qError: null,
  trainAgent: async () => {
    const { environment, episodes, learningRate, discountFactor, seed } = get();
    if (!environment) return;
    set({ qLoading: true, qError: null, qLearning: null });
    try {
      const qLearning = await trainQLearning({
        ...environmentBody(environment),
        episodes,
        max_steps_per_episode: 420,
        learning_rate: learningRate,
        discount_factor: discountFactor,
        epsilon_start: 1,
        epsilon_end: 0.04,
        seed,
      });
      set({ qLearning, qLoading: false });
    } catch (error) {
      set({ qLoading: false, qError: (error as Error).message });
    }
  },
}));
