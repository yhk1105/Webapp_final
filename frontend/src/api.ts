import { AnalysisResult, GameAction, GameState } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "請求失敗");
  }
  return response.json() as Promise<T>;
}

export async function startGame(numDecks: number): Promise<GameState> {
  const body: Record<string, unknown> = { num_decks: numDecks };
  const response = await fetch(`${API_BASE}/api/games`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  return handleResponse<GameState>(response);
}

export async function sendAction(
  gameId: string,
  action: GameAction
): Promise<GameState> {
  const body: Record<string, unknown> = { action };
  const response = await fetch(`${API_BASE}/api/games/${gameId}/action`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  return handleResponse<GameState>(response);
}

export async function fetchAnalysis(gameId: string): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE}/api/games/${gameId}/analysis`);
  return handleResponse<AnalysisResult>(response);
}

export async function startNextRound(gameId: string): Promise<GameState> {
  const response = await fetch(`${API_BASE}/api/games/${gameId}/next-round`, {
    method: "POST"
  });
  return handleResponse<GameState>(response);
}

