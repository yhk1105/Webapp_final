import { AnalysisResult, GameAction, GameState } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

// Token 管理
function getToken(): string | null {
  return localStorage.getItem("auth_token");
}

function setToken(token: string): void {
  localStorage.setItem("auth_token", token);
}

function removeToken(): void {
  localStorage.removeItem("auth_token");
}

export function isAuthenticated(): boolean {
  return getToken() !== null;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    // 先複製 response 以便可以多次讀取（如果需要）
    const contentType = response.headers.get("content-type");
    let message: string;
    
    if (contentType && contentType.includes("application/json")) {
      // 如果是 JSON，直接讀取 JSON
      const errorData = await response.json();
      message = errorData.detail || errorData.message || JSON.stringify(errorData);
    } else {
      // 如果不是 JSON，讀取文本
      message = await response.text();
    }
    
    // 如果是 401 錯誤，在錯誤訊息中包含狀態碼
    if (response.status === 401) {
      throw new Error(`401: ${message || "未授權，請重新登入"}`);
    }
    
    throw new Error(message || "請求失敗");
  }
  return response.json() as Promise<T>;
}

async function fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
  const token = getToken();
  if (!token) {
    throw new Error("401: 未登入，請先登入");
  }
  
  // 創建新的 headers 對象，確保不覆蓋現有的
  const headers = new Headers(options.headers || {});
  
  // 確保密碼正確設置 Authorization header
  headers.set("Authorization", `Bearer ${token}`);
  
  // 確保 Content-Type 被正確設置（如果沒有設置且需要）
  if (!headers.has("Content-Type") && options.body && typeof options.body === 'string') {
    headers.set("Content-Type", "application/json");
  }
  
  // 創建新的 options，確保 headers 被正確傳遞
  const fetchOptions: RequestInit = {
    ...options,
    headers: headers
  };
  
  return fetch(url, fetchOptions);
}

// 認證相關 API
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  username: string;
}

export async function register(request: RegisterRequest): Promise<{ message: string; user_id: number; username: string }> {
  const response = await fetch(`${API_BASE}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request)
  });
  return handleResponse(response);
}

export async function login(request: LoginRequest): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request)
  });
  const data = await handleResponse<AuthResponse>(response);
  
  // 確保密碼正確保存 token
  if (data && data.access_token) {
    setToken(data.access_token);
    // 驗證 token 是否正確保存
    const savedToken = getToken();
    if (!savedToken || savedToken !== data.access_token) {
      console.error("Token 保存失敗", { saved: savedToken, received: data.access_token });
      throw new Error("Token 保存失敗，請重試");
    }
    console.log("Token 已成功保存，長度:", savedToken.length);
  } else {
    console.error("登入響應中沒有 access_token", data);
    throw new Error("登入響應格式錯誤");
  }
  return data;
}

export function logout(): void {
  removeToken();
}

export async function getCurrentUser(): Promise<{ user_id: number; authenticated: boolean }> {
  const response = await fetchWithAuth(`${API_BASE}/api/auth/me`);
  return handleResponse(response);
}

// 遊戲相關 API
export async function startGame(numDecks: number): Promise<GameState> {
  const body: Record<string, unknown> = { num_decks: numDecks };
  const response = await fetchWithAuth(`${API_BASE}/api/games`, {
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
  const response = await fetchWithAuth(`${API_BASE}/api/games/${gameId}/action`, {
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

// 歷史記錄相關 API
export interface MistakeRecord {
  game_id?: string;
  round_index: number;
  decision_index: number;
  timestamp: string;
  player_hand: string[];
  dealer_upcard: string | null;
  chosen_action: string;
  recommended_action: string;
}

export interface GameSession {
  game_id: string;
  num_decks: number;
  rounds_played: number;
  started_at: string;
  ended_at: string | null;
}

export async function getMyMistakes(): Promise<{ mistakes: MistakeRecord[] }> {
  const response = await fetchWithAuth(`${API_BASE}/api/history/mistakes`);
  return handleResponse(response);
}

export async function getMySessions(): Promise<{ sessions: GameSession[] }> {
  const response = await fetchWithAuth(`${API_BASE}/api/history/sessions`);
  return handleResponse(response);
}

export async function getSessionMistakes(gameId: string): Promise<{ mistakes: MistakeRecord[] }> {
  const response = await fetchWithAuth(`${API_BASE}/api/history/sessions/${gameId}/mistakes`);
  return handleResponse(response);
}

