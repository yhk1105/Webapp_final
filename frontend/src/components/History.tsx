import { useEffect, useState } from "react";
import { getMyMistakes, getMySessions, getSessionMistakes, MistakeRecord, GameSession } from "../api";

// 格式化牌值
function formatCard(card: string): string {
  if (card === "11") return "J";
  if (card === "12") return "Q";
  if (card === "13") return "K";
  return card;
}

export function History() {
  const [mistakes, setMistakes] = useState<MistakeRecord[]>([]);
  const [sessions, setSessions] = useState<GameSession[]>([]);
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const [sessionMistakes, setSessionMistakes] = useState<MistakeRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"all" | "sessions">("all");

  useEffect(() => {
    // 確保 token 存在後再載入數據
    const token = localStorage.getItem("auth_token");
    if (!token) {
      console.error("History: 沒有 token，無法載入數據");
      return;
    }
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [mistakesData, sessionsData] = await Promise.all([
        getMyMistakes(),
        getMySessions()
      ]);
      setMistakes(mistakesData.mistakes);
      setSessions(sessionsData.sessions);
    } catch (err) {
      console.error("載入歷史記錄失敗:", err);
      const errorMessage = err instanceof Error ? err.message : "載入失敗";
      
      // 如果是 401 錯誤，可能是 token 過期，需要重新登入
      if (errorMessage.includes("401") || errorMessage.includes("未授權") || errorMessage.includes("未登入")) {
        setError("登入已過期，請重新登入");
        // 清除 token
        localStorage.removeItem("auth_token");
        // 3 秒後重新載入頁面
        setTimeout(() => {
          window.location.reload();
        }, 3000);
      } else {
        setError(`載入失敗: ${errorMessage}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSessionClick = async (gameId: string) => {
    setSelectedSession(gameId);
    try {
      const data = await getSessionMistakes(gameId);
      setSessionMistakes(data.mistakes);
    } catch (err) {
      console.error("載入會話錯誤失敗:", err);
      // 如果是 401 錯誤，清除 token 並重新載入
      if (err instanceof Error && (err.message.includes("401") || err.message.includes("未授權"))) {
        localStorage.removeItem("auth_token");
        alert("登入已過期，請重新登入");
        window.location.reload();
      }
    }
  };

  if (loading) {
    return <div className="history-container">載入中...</div>;
  }

  if (error) {
    return (
      <div className="history-container">
        <h2>歷史檢討</h2>
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="history-container">
      <h2>歷史檢討</h2>
      
      <div className="history-tabs">
        <button
          className={activeTab === "all" ? "active" : ""}
          onClick={() => setActiveTab("all")}
        >
          所有錯誤 ({mistakes.length})
        </button>
        <button
          className={activeTab === "sessions" ? "active" : ""}
          onClick={() => setActiveTab("sessions")}
        >
          遊戲歷史 ({sessions.length})
        </button>
      </div>

      {activeTab === "all" && (
        <div className="mistakes-list">
          {mistakes.length === 0 ? (
            <p>目前沒有錯誤記錄</p>
          ) : (
            <ol>
              {mistakes.map((mistake, index) => (
                <li key={index}>
                  <div className="mistake-item">
                    <div className="mistake-header">
                      <span className="mistake-time">
                        {new Date(mistake.timestamp).toLocaleString("zh-TW")}
                      </span>
                      {mistake.game_id && (
                        <span className="mistake-game-id">遊戲: {mistake.game_id.slice(0, 8)}...</span>
                      )}
                    </div>
                    <div className="mistake-content">
                      第 {mistake.round_index} 局第 {mistake.decision_index} 步：
                      建議 <strong>{mistake.recommended_action}</strong>，
                      但你選擇了 {mistake.chosen_action}
                    </div>
                    <div className="mistake-hand">
                      手牌：{mistake.player_hand.map(formatCard).join(", ")}，
                      莊家明牌：{formatCard(mistake.dealer_upcard ?? "?")}
                    </div>
                  </div>
                </li>
              ))}
            </ol>
          )}
        </div>
      )}

      {activeTab === "sessions" && (
        <div className="sessions-list">
          {sessions.length === 0 ? (
            <p>目前沒有遊戲歷史記錄</p>
          ) : (
            <>
              <ul className="sessions">
                {sessions.map((session) => (
                  <li
                    key={session.game_id}
                    className={selectedSession === session.game_id ? "active" : ""}
                    onClick={() => handleSessionClick(session.game_id)}
                  >
                    <div className="session-item">
                      <div className="session-header">
                        <span>遊戲 ID: {session.game_id.slice(0, 8)}...</span>
                        <span>{session.num_decks} 副牌</span>
                      </div>
                      <div className="session-info">
                        <span>回合數: {session.rounds_played}</span>
                        <span>
                          {new Date(session.started_at).toLocaleString("zh-TW")}
                        </span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>

              {selectedSession && sessionMistakes.length > 0 && (
                <div className="session-mistakes">
                  <h3>此會話的錯誤記錄</h3>
                  <ol>
                    {sessionMistakes.map((mistake, index) => (
                      <li key={index}>
                        第 {mistake.round_index} 局第 {mistake.decision_index} 步：
                        建議 <strong>{mistake.recommended_action}</strong>，
                        但你選擇了 {mistake.chosen_action}。
                        手牌：{mistake.player_hand.map(formatCard).join(", ")}，
                        莊家明牌：{formatCard(mistake.dealer_upcard ?? "?")}
                      </li>
                    ))}
                  </ol>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}

