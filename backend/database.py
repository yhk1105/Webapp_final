import sqlite3
import json
from datetime import datetime
from typing import List, Dict

DB_NAME = "blackjack.db"


def init_db():
    """初始化資料庫和所有表格"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # 用戶表
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 遊戲會話表（記錄每場遊戲的基本資訊）
    c.execute('''
        CREATE TABLE IF NOT EXISTS game_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            game_id TEXT UNIQUE NOT NULL,
            num_decks INTEGER,
            rounds_played INTEGER DEFAULT 0,
            started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            ended_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 動作記錄表（添加 user_id 和 game_session_id）
    c.execute('''
        CREATE TABLE IF NOT EXISTS action_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            game_id TEXT,
            round_index INTEGER,
            decision_index INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            player_hand TEXT,
            dealer_upcard TEXT,
            action_taken TEXT,
            action_recommended TEXT,
            is_mistake BOOLEAN,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 為現有表格添加 user_id 欄位（如果不存在）
    try:
        c.execute('ALTER TABLE action_logs ADD COLUMN user_id INTEGER')
    except sqlite3.OperationalError:
        pass  # 欄位已存在

    try:
        c.execute('ALTER TABLE action_logs ADD COLUMN round_index INTEGER')
    except sqlite3.OperationalError:
        pass

    try:
        c.execute('ALTER TABLE action_logs ADD COLUMN decision_index INTEGER')
    except sqlite3.OperationalError:
        pass

    # 創建索引以提高查詢效率
    c.execute(
        'CREATE INDEX IF NOT EXISTS idx_action_logs_user_id ON action_logs(user_id)')
    c.execute(
        'CREATE INDEX IF NOT EXISTS idx_action_logs_game_id ON action_logs(game_id)')
    c.execute(
        'CREATE INDEX IF NOT EXISTS idx_game_sessions_user_id ON game_sessions(user_id)')

    conn.commit()
    conn.close()


def log_action(game_id, p_hand, d_upcard, taken, recommended, is_mistake,
               user_id=None, round_index=None, decision_index=None):
    """記錄玩家的動作到資料庫"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        INSERT INTO action_logs 
        (user_id, game_id, round_index, decision_index, timestamp, player_hand, dealer_upcard, action_taken, action_recommended, is_mistake)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, game_id, round_index, decision_index, datetime.now(),
          json.dumps(p_hand), d_upcard, taken, recommended, is_mistake))

    conn.commit()
    conn.close()


def create_game_session(user_id: int, game_id: str, num_decks: int):
    """創建新的遊戲會話"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        INSERT INTO game_sessions (user_id, game_id, num_decks)
        VALUES (?, ?, ?)
    ''', (user_id, game_id, num_decks))

    conn.commit()
    conn.close()


def update_game_session(game_id: str, rounds_played: int, ended: bool = False):
    """更新遊戲會話資訊"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if ended:
        c.execute('''
            UPDATE game_sessions 
            SET rounds_played = ?, ended_at = CURRENT_TIMESTAMP
            WHERE game_id = ?
        ''', (rounds_played, game_id))
    else:
        c.execute('''
            UPDATE game_sessions 
            SET rounds_played = ?
            WHERE game_id = ?
        ''', (rounds_played, game_id))

    conn.commit()
    conn.close()


def get_user_mistakes(user_id: int, limit: int = 100) -> List[Dict]:
    """獲取用戶的所有錯誤記錄"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        SELECT game_id, round_index, decision_index, timestamp, player_hand, 
               dealer_upcard, action_taken, action_recommended
        FROM action_logs
        WHERE user_id = ? AND is_mistake = 1
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (user_id, limit))

    results = c.fetchall()
    conn.close()

    mistakes = []
    for row in results:
        game_id, round_index, decision_index, timestamp, p_hand_json, d_upcard, taken, recommended = row
        p_hand = json.loads(p_hand_json) if p_hand_json else []
        mistakes.append({
            "game_id": game_id,
            "round_index": round_index,
            "decision_index": decision_index,
            "timestamp": timestamp,
            "player_hand": p_hand,
            "dealer_upcard": d_upcard,
            "chosen_action": taken.lower() if taken else None,
            "recommended_action": recommended.lower() if recommended else None
        })

    return mistakes


def get_user_game_sessions(user_id: int, limit: int = 50) -> List[Dict]:
    """獲取用戶的遊戲會話列表"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        SELECT game_id, num_decks, rounds_played, started_at, ended_at
        FROM game_sessions
        WHERE user_id = ?
        ORDER BY started_at DESC
        LIMIT ?
    ''', (user_id, limit))

    results = c.fetchall()
    conn.close()

    sessions = []
    for row in results:
        game_id, num_decks, rounds_played, started_at, ended_at = row
        sessions.append({
            "game_id": game_id,
            "num_decks": num_decks,
            "rounds_played": rounds_played,
            "started_at": started_at,
            "ended_at": ended_at
        })

    return sessions


def get_game_mistakes(user_id: int, game_id: str) -> List[Dict]:
    """獲取特定遊戲的所有錯誤記錄"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        SELECT round_index, decision_index, timestamp, player_hand, 
               dealer_upcard, action_taken, action_recommended
        FROM action_logs
        WHERE user_id = ? AND game_id = ? AND is_mistake = 1
        ORDER BY timestamp ASC
    ''', (user_id, game_id))

    results = c.fetchall()
    conn.close()

    mistakes = []
    for row in results:
        round_index, decision_index, timestamp, p_hand_json, d_upcard, taken, recommended = row
        p_hand = json.loads(p_hand_json) if p_hand_json else []
        mistakes.append({
            "round_index": round_index,
            "decision_index": decision_index,
            "timestamp": timestamp,
            "player_hand": p_hand,
            "dealer_upcard": d_upcard,
            "chosen_action": taken.lower() if taken else None,
            "recommended_action": recommended.lower() if recommended else None
        })

    return mistakes
