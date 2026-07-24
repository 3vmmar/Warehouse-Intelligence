import type {
  ComparisonRequest,
  ComparisonResponse,
  EnvironmentData,
  GenerateRequest,
  QLearningResult,
  SearchResult,
  SolveRequest,
  TrainRequest,
} from "./types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function post<TResponse>(path: string, body: unknown): Promise<TResponse> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${path} failed (${res.status}): ${detail}`);
  }
  return res.json() as Promise<TResponse>;
}

export function generateEnvironment(req: GenerateRequest): Promise<EnvironmentData> {
  return post<EnvironmentData>("/generate-environment", req);
}

export function solve(req: SolveRequest): Promise<SearchResult> {
  return post<SearchResult>("/solve", req);
}

export function compareAlgorithms(req: ComparisonRequest): Promise<ComparisonResponse> {
  return post<ComparisonResponse>("/compare", req);
}

export function trainQLearning(req: TrainRequest): Promise<QLearningResult> {
  return post<QLearningResult>("/train-q-learning", req);
}
