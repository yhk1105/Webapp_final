import uuid
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import local modules
from Manager import Manager
import database  # <--- NEW: データベース機能を読み込み

app = FastAPI()

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite 開發伺服器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Initialization ---
@app.on_event("startup")
def startup_event():
    """サーバー起動時にデータベースを準備する"""
    database.init_db()

# --- 1. In-memory Game Storage ---
games: Dict[str, Manager] = {}

# --- 2. Data Models (Pydantic) ---
class CreateGameRequest(BaseModel):
    num_decks: int

class ActionRequest(BaseModel):
    action: str

# --- 3. Helper Function ---
def format_game_state(game_id: str, gm: Manager, mistakes: list = None):
    # 手札変換
    p_cards = [str(c) if c != 1 else "A" for c in gm.player_hand.cards]
    d_cards = [str(c) if c != 1 else "A" for c in gm.dealer_hand.cards]
    
    dealer_display = []
    if not gm.finish and len(d_cards) > 0:
        dealer_display = [d_cards[0], "??"]
    else:
        dealer_display = d_cards

    result_str = None
    if gm.finish:
        if gm.result > 0: result_str = "player"
        elif gm.result < 0: result_str = "dealer"
        else: result_str = "push"

    # --- 計算ロジック ---
    remaining = gm.shoe.remaining()
    initial = gm.initial_shoe_size
    shoe_ratio = remaining / initial if initial > 0 else 0
    
    # セッション終了判定（残り枚数が閾値以下 かつ ラウンド終了時）
    session_completed = (remaining <= gm.stop_threshold) and gm.finish

    message = "Game in progress"
    if gm.finish: message = "Round finished"
    if session_completed: message = "Session Completed! Please start a new game."

    # Shoe Composition (ラウンド開始前か終了後のみ更新)
    shoe_comp = {}
    if gm.finish or len(gm.actions_taken) == 0: 
         shoe_comp = gm.get_shoe_composition()

    return {
        "game_id": game_id,
        "player_hand": p_cards,
        "dealer_hand": dealer_display,
        "dealer_upcard": d_cards[0] if d_cards else None,
        "player_score": gm.player_hand.best_value(),
        "dealer_score": gm.final_dealer_value if gm.finish else None,
        "is_over": gm.finish,
        "result": result_str,
        "message": message,
        "available_actions": ["hit", "stand", "double"] if (not gm.finish and not session_completed) else [],
        
        # --- 不足していたデータを追加 ---
        "shoe_remaining": remaining,
        "shoe_ratio": round(shoe_ratio, 2),
        "initial_shoe_size": initial,
        "stop_threshold": gm.stop_threshold,
        "rounds_played": gm.rounds_played,
        "session_completed": session_completed,
        "can_start_next_round": gm.finish and not session_completed,
        "actions_taken": gm.actions_taken, # アクション履歴
        "shoe_composition": shoe_comp,     # カードカウンティング情報
        "mistakes": mistakes or []
    }

# --- 4. API Endpoints ---

@app.post("/api/games")
def start_game(request: CreateGameRequest):
    """Start a new game"""
    game_id = str(uuid.uuid4())
    gm = Manager(num_decks=request.num_decks)
    gm.start_round()
    gm.deal_initial()
    games[game_id] = gm
    return format_game_state(game_id, gm)

@app.get("/api/games/{game_id}")
def get_game_state(game_id: str):
    """Get current game state"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    gm = games[game_id]
    return format_game_state(game_id, gm)

@app.post("/api/games/{game_id}/action")
def perform_action(game_id: str, request: ActionRequest):
    """Perform action and SAVE to database"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    gm = games[game_id]
    
    if gm.finish:
        raise HTTPException(status_code=400, detail="Round is already over")

    # 1. Logic & Calculation
    rec = gm.get_recommendation()
    best_action = rec["best_action"]
    user_action = request.action.upper()
    
    # Mistake check
    is_mistake = (user_action != best_action)
    mistakes = []
    
    # Current Hand Info for logging
    current_p_hand = [str(c) if c != 1 else "A" for c in gm.player_hand.cards]
    current_d_upcard = str(gm.dealer_hand.cards[0]) if gm.dealer_hand.cards else None

    if is_mistake:
        mistake_record = {
            "chosen_action": user_action.lower(),
            "recommended_action": best_action.lower(),
            "player_hand": current_p_hand,
            "dealer_upcard": current_d_upcard
        }
        mistakes.append(mistake_record)

    # <--- NEW: Save to Database --->
    database.log_action(
        game_id=game_id,
        p_hand=current_p_hand,
        d_upcard=current_d_upcard,
        taken=user_action,
        recommended=best_action,
        is_mistake=is_mistake
    )

    # 2. Update Game
    if user_action == "HIT":
        gm.player_hit()
    elif user_action == "STAND":
        gm.player_stand()
    elif user_action == "DOUBLE":
        gm.player_double()
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    return format_game_state(game_id, gm, mistakes=mistakes)

@app.post("/api/games/{game_id}/next-round")
def next_round(game_id: str):
    """Proceed to the next round"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    gm = games[game_id]
    if not gm.finish:
        raise HTTPException(status_code=400, detail="Round is not over yet")
    remaining = gm.shoe.remaining()
    if remaining <= gm.stop_threshold:
        raise HTTPException(status_code=400, detail="Session completed. Please start a new game.")
    gm.start_round()
    gm.deal_initial()
    return format_game_state(game_id, gm)

@app.get("/api/games/{game_id}/analysis")
def get_analysis(game_id: str):
    """Get analysis"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    gm = games[game_id]
    rec = gm.get_recommendation()
    evaluations = {}
    for action, stats in rec["results"].items():
        evaluations[action.lower()] = stats
    return {
        "best_action": rec["best_action"].lower(),
        "evaluations": evaluations
    }