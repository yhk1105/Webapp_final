export type GameAction = "hit" | "stand" | "double";

export interface AnalysisEvaluation {
  win_rate: number;
  push_rate: number;
  loss_rate: number;
}

export interface DecisionMistake {
  round_index: number;
  decision_index: number;
  chosen_action: GameAction;
  recommended_action: GameAction;
  player_hand: string[];
  dealer_upcard: string | null;
  evaluations: Record<GameAction, AnalysisEvaluation>;
}

export interface GameState {
  game_id: string;
  player_hand: string[];
  dealer_hand: string[];
  dealer_upcard: string | null;
  player_score: number;
  dealer_score?: number | null;
  is_over: boolean;
  result: "player" | "dealer" | "push" | null;
  message: string;
  available_actions: GameAction[];
  actions_taken: string[];
  shoe_remaining: number;
  shoe_ratio: number;
  initial_shoe_size: number;
  stop_threshold: number;
  rounds_played: number;
  session_completed: boolean;
  can_start_next_round: boolean;

  mistakes: DecisionMistake[];
  round_mistakes: DecisionMistake[];
  respect_shoe_state: boolean;
  shoe_composition: Record<string, number>;
}

export interface AnalysisResult {
  best_action: GameAction | "";

  evaluations: Partial<Record<GameAction, AnalysisEvaluation>>;
}

