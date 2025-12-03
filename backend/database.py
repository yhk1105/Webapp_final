import sqlite3
import json
from datetime import datetime

DB_NAME = "blackjack.db"

def init_db():
    """データベースとテーブルを初期化する"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # アクション記録用テーブルの作成
    # game_id: ゲームID
    # timestamp: 日時
    # player_hand: プレイヤーの手札
    # dealer_upcard: ディーラーの表カード
    # action_taken: プレイヤーが選んだアクション
    # action_recommended: AIが推奨したアクション
    # is_mistake: ミスだったかどうか (True/False)
    c.execute('''
        CREATE TABLE IF NOT EXISTS action_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT,
            timestamp DATETIME,
            player_hand TEXT,
            dealer_upcard TEXT,
            action_taken TEXT,
            action_recommended TEXT,
            is_mistake BOOLEAN
        )
    ''')
    
    conn.commit()
    conn.close()

def log_action(game_id, p_hand, d_upcard, taken, recommended, is_mistake):
    """プレイヤーの1手をデータベースに保存する"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # リスト型の手札などはJSON文字列に変換して保存
    c.execute('''
        INSERT INTO action_logs (game_id, timestamp, player_hand, dealer_upcard, action_taken, action_recommended, is_mistake)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (game_id, datetime.now(), json.dumps(p_hand), d_upcard, taken, recommended, is_mistake))
    
    conn.commit()
    conn.close()

def get_all_mistakes(game_id):
    """指定されたgame_idのすべてのミスを取得する"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''
        SELECT player_hand, dealer_upcard, action_taken, action_recommended, timestamp
        FROM action_logs
        WHERE game_id = ? AND is_mistake = 1
        ORDER BY timestamp
    ''', (game_id,))
    
    results = c.fetchall()
    conn.close()
    
    mistakes = []
    for row in results:
        p_hand_json, d_upcard, taken, recommended, timestamp = row
        p_hand = json.loads(p_hand_json) if p_hand_json else []
        mistakes.append({
            "player_hand": p_hand,
            "dealer_upcard": d_upcard,
            "chosen_action": taken.lower(),
            "recommended_action": recommended.lower(),
            "timestamp": timestamp
        })
    
    return mistakes