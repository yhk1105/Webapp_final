import uuid
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import timedelta

# Import local modules
from Manager import Manager
import database
import auth

app = FastAPI()

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                   "http://127.0.0.1:5173"],  # Vite 開發伺服器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # 允許所有 headers，包括 Authorization
    expose_headers=["*"],  # 暴露所有 headers
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


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str

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
        if gm.result > 0:
            result_str = "player"
        elif gm.result < 0:
            result_str = "dealer"
        else:
            result_str = "push"

    # --- 計算ロジック ---
    remaining = gm.shoe.remaining()
    initial = gm.initial_shoe_size
    shoe_ratio = remaining / initial if initial > 0 else 0

    # セッション終了判定（残り枚数が閾値以下 かつ ラウンド終了時）
    session_completed = (remaining <= gm.stop_threshold) and gm.finish

    message = "Game in progress"
    if gm.finish:
        message = "Round finished"
    if session_completed:
        message = "Session Completed! Please start a new game."

    # Shoe Composition (始終更新以確保前端能正確顯示)
    shoe_comp = gm.get_shoe_composition()

    # 決定返回的錯誤記錄
    # mistakes: 用於訓練摘要（所有錯誤）
    # round_mistakes: 用於本局檢討（當前局的錯誤）
    if session_completed:
        # 訓練結束時，mistakes 包含所有錯誤，round_mistakes 包含當前局的錯誤
        final_mistakes = gm.all_mistakes
        round_mistakes = gm.current_round_mistakes
    elif gm.finish:
        # 單局結束時，mistakes 和 round_mistakes 都是當前局的錯誤
        final_mistakes = gm.current_round_mistakes
        round_mistakes = gm.current_round_mistakes
    else:
        # 遊戲進行中，顯示當前動作的錯誤（如果有）
        final_mistakes = mistakes or []
        round_mistakes = mistakes or []

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
        "actions_taken": gm.actions_taken,  # アクション履歴
        "shoe_composition": shoe_comp,     # カードカウンティング情報
        "mistakes": final_mistakes,        # 用於訓練摘要（所有錯誤）
        "round_mistakes": round_mistakes   # 用於本局檢討（當前局的錯誤）
    }

# --- 4. API Endpoints ---

# --- 認證相關 API ---


@app.post("/api/auth/register")
def register(request: RegisterRequest):
    """用戶註冊"""
    try:
        user = auth.create_user(request.username, request.password)
        return {"message": "註冊成功", "user_id": user["id"], "username": user["username"]}
    except ValueError as e:
        # ValueError 通常是驗證錯誤，返回 400
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 捕獲所有其他異常，記錄詳細信息
        import traceback
        error_msg = str(e)
        error_trace = traceback.format_exc()
        print(f"註冊錯誤: {error_msg}")
        print(f"錯誤堆疊: {error_trace}")
        # 返回用戶友好的錯誤訊息
        raise HTTPException(
            status_code=500,
            detail=f"註冊失敗，請稍後再試。錯誤: {error_msg}"
        )


@app.post("/api/auth/login")
def login(request: LoginRequest):
    """用戶登入"""
    user = auth.get_user_by_username(request.username)
    if not user or not auth.verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用戶名或密碼錯誤"
        )

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        # sub 必須是字符串
        data={"sub": str(user["id"])}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user["id"],
        "username": user["username"]
    }


@app.get("/api/auth/me")
def get_current_user_info(current_user: dict = Depends(auth.get_current_user)):
    """獲取當前用戶資訊"""
    return {
        "user_id": current_user["user_id"],
        "authenticated": True
    }


# --- 遊戲相關 API ---


@app.post("/api/games")
def start_game(
    request: CreateGameRequest,
    current_user: Optional[dict] = Depends(auth.get_optional_user)
):
    """Start a new game"""
    game_id = str(uuid.uuid4())
    gm = Manager(num_decks=request.num_decks)
    gm.start_round()
    gm.deal_initial()
    games[game_id] = gm

    # 如果用戶已登入，創建遊戲會話記錄
    if current_user:
        user_id = current_user.get("user_id")
        if user_id:
            database.create_game_session(user_id, game_id, request.num_decks)

    return format_game_state(game_id, gm)


@app.get("/api/games/{game_id}")
def get_game_state(game_id: str):
    """Get current game state"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    gm = games[game_id]
    return format_game_state(game_id, gm)


@app.post("/api/games/{game_id}/action")
def perform_action(
    game_id: str,
    request: ActionRequest,
    current_user: Optional[dict] = Depends(auth.get_optional_user)
):
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
    current_d_upcard = str(
        gm.dealer_hand.cards[0]) if gm.dealer_hand.cards else None

    if is_mistake:
        # decision_index 是當前回合中的第幾步決策（從 1 開始）
        # 在執行動作前，actions_taken 的長度就是已執行的動作數
        decision_index = len(gm.actions_taken) + 1
        mistake_record = {
            "chosen_action": user_action.lower(),
            "recommended_action": best_action.lower(),
            "player_hand": current_p_hand,
            "dealer_upcard": current_d_upcard,
            "round_index": gm.rounds_played,
            "decision_index": decision_index
        }
        mistakes.append(mistake_record)
        # 同時添加到當前回合和累積的錯誤列表中
        gm.current_round_mistakes.append(mistake_record)
        gm.all_mistakes.append(mistake_record)

    # 獲取用戶 ID（如果已登入）
    user_id = current_user.get("user_id") if current_user else None

    # <--- NEW: Save to Database --->
    database.log_action(
        game_id=game_id,
        p_hand=current_p_hand,
        d_upcard=current_d_upcard,
        taken=user_action,
        recommended=best_action,
        is_mistake=is_mistake,
        user_id=user_id,
        round_index=gm.rounds_played,
        decision_index=len(gm.actions_taken) + 1
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
        # 更新遊戲會話為已結束
        database.update_game_session(game_id, gm.rounds_played, ended=True)
        raise HTTPException(
            status_code=400, detail="Session completed. Please start a new game.")
    gm.start_round()
    gm.deal_initial()
    # 更新遊戲會話的回合數
    database.update_game_session(game_id, gm.rounds_played, ended=False)
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


# --- 歷史記錄相關 API ---


@app.get("/api/history/mistakes")
def get_my_mistakes(current_user: dict = Depends(auth.get_current_user)):
    """獲取當前用戶的所有錯誤記錄"""
    mistakes = database.get_user_mistakes(current_user["user_id"])
    return {"mistakes": mistakes}


@app.get("/api/history/sessions")
def get_my_sessions(current_user: dict = Depends(auth.get_current_user)):
    """獲取當前用戶的遊戲會話列表"""
    sessions = database.get_user_game_sessions(current_user["user_id"])
    return {"sessions": sessions}


@app.get("/api/history/sessions/{game_id}/mistakes")
def get_session_mistakes(
    game_id: str,
    current_user: dict = Depends(auth.get_current_user)
):
    """獲取特定遊戲會話的所有錯誤記錄"""
    mistakes = database.get_game_mistakes(current_user["user_id"], game_id)
    return {"mistakes": mistakes}
