import { useEffect, useMemo, useState } from "react";
import { fetchAnalysis, sendAction, startGame, startNextRound } from "./api";
import { ShoeCompositionChart } from "./components/ShoeCompositionChart";
import { GameControls } from "./components/GameControls";
import { Hand } from "./components/Hand";
import { AnalysisResult, GameAction, GameState } from "./types";

// 格式化牌值：將 11、12、13 轉換為 J、Q、K
function formatCard(card: string): string {
  if (card === "11") return "J";
  if (card === "12") return "Q";
  if (card === "13") return "K";
  return card;
}

function App() {
  const [numDecks, setNumDecks] = useState(4);
  const [game, setGame] = useState<GameState | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAnalysis, setShowAnalysis] = useState(true);
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });

  const analysisKey = useMemo(() => {
    if (!game) {
      return "";
    }
    return `${game.game_id}-${game.actions_taken.join("-")}`;
  }, [game]);

  useEffect(() => {
    if (!game || game.is_over || game.session_completed || !showAnalysis) {
      setAnalysis(null);
      return;
    }
    setAnalysisLoading(true);
    fetchAnalysis(game.game_id)
      .then(setAnalysis)
      .catch((err) => setError(err.message))
      .finally(() => setAnalysisLoading(false));
  }, [analysisKey, game?.is_over, game?.game_id, game?.session_completed, showAnalysis]);

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  const handleStartGame = async () => {
    setLoading(true);
    setError(null);
    setAnalysis(null);
    try {
      const nextGame = await startGame(numDecks);
      setGame(nextGame);
    } catch (err) {
      setError(err instanceof Error ? err.message : "建立牌局時發生錯誤");
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (action: GameAction) => {
    if (!game) return;
    setLoading(true);
    setError(null);
    setAnalysis(null);
    try {
      const nextState = await sendAction(game.game_id, action);
      setGame(nextState);
    } catch (err) {
      setError(err instanceof Error ? err.message : "執行動作時發生錯誤");
    } finally {
      setLoading(false);
    }
  };

  const handleNextRound = async () => {
    if (!game) return;
    setLoading(true);
    setError(null);
    try {
      const nextState = await startNextRound(game.game_id);
      setGame(nextState);
    } catch (err) {
      setError(err instanceof Error ? err.message : "啟動下一局時發生錯誤");
    } finally {
      setLoading(false);
    }
  };

  const resetTable = () => {
    setGame(null);
    setAnalysis(null);
    setError(null);
  };

  return (
    <div className="app" data-theme={darkMode ? 'dark' : 'light'}>
      <header>
        <h1>Blackjack 模擬訓練</h1>
        <p>依據企劃書完成的最基礎版：支援指定牌副數、基本動作、蒙地卡羅建議。</p>
      </header>

      <section className="config">
        <label>
          牌組副數
          <input
            type="number"
            min={1}
            max={8}
            value={numDecks}
            onChange={(evt) => setNumDecks(Number(evt.target.value))}
          />
        </label>
        <label>
          <input
            type="checkbox"
            checked={showAnalysis}
            onChange={(evt) => setShowAnalysis(evt.target.checked)}
          />
          顯示建議
        </label>
        <label>
          <input
            type="checkbox"
            checked={darkMode}
            onChange={(evt) => setDarkMode(evt.target.checked)}
          />
          深色模式
        </label>
        <button onClick={handleStartGame} disabled={loading}>
          {game ? "重新開始" : "開始模擬"}
        </button>
        <button onClick={resetTable} className="secondary">
          清空桌面
        </button>
      </section>

      {error && <div className="error">{error}</div>}

      {game ? (
        <>
          <section className="table">
            <Hand title="莊家" cards={game.dealer_hand} score={game.is_over ? game.dealer_score ?? null : null} />
            <Hand title="玩家" cards={game.player_hand} score={game.player_score} highlight />
          </section>
          {game.shoe_composition && (
             <ShoeCompositionChart composition={game.shoe_composition} initialShoeSize={game.initial_shoe_size} />
          )}
          <section className="status">
            <p>{game.message}</p>
            <p>
              已完成 {game.rounds_played} 局・剩餘牌數：{game.shoe_remaining} / {game.initial_shoe_size}
            </p>
            {game.result && <p>結果：{game.result === "player" ? "玩家勝" : game.result === "dealer" ? "莊家勝" : "和局"}</p>}
          </section>
          {!game.is_over && !game.session_completed && (
            <GameControls available={game.available_actions} disabled={loading} onAction={handleAction} />
          )}
          {game.is_over && !game.session_completed && (
            <div className="next-round">
              <button onClick={handleNextRound} disabled={loading || !game.can_start_next_round}>
                下一局
              </button>
              <p className="hint">系統會在牌堆剩下一半時自動結束訓練。</p>
            </div>
          )}
          {game.is_over && game.round_mistakes.length > 0 && (
             <section className="round-mistakes">
               <h3>本局檢討</h3>
               <ul>
                 {game.round_mistakes.map((mistake) => (
                   <li key={`${mistake.round_index}-${mistake.decision_index}`}>
                     第 {mistake.decision_index} 步：建議 <strong>{mistake.recommended_action}</strong>，但你選擇了 {mistake.chosen_action}。
                   </li>
                 ))}
               </ul>
             </section>
          )}
        </>
      ) : (
        <section className="placeholder">
          <p>請先設定牌副數並點選「開始模擬」。</p>
        </section>
      )}

      {showAnalysis && analysis && !game?.is_over && !game?.session_completed && (
        <section className="analysis">
          <h2>蒙地卡羅建議</h2>
          {analysisLoading ? (
            <p>計算中...</p>
          ) : (
            <>
              <p>最佳動作：{analysis.best_action || "暫無"}</p>
              <table>
                <thead>
                  <tr>
                    <th>動作</th>
                    <th>EV</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(analysis.evaluations).map(([action, stats]) => {
                    // 計算 EV：EV = (勝率 - 敗率) * 倍數
                    // stand 或 hit: 倍數為 1
                    // double: 倍數為 2
                    const multiplier = action === "double" ? 2 : 1;
                    const ev = (stats.win_rate - stats.loss_rate) * multiplier;
                    return (
                      <tr key={action} className={analysis.best_action === action ? "best" : ""}>
                        <td>{action}</td>
                        <td className={ev > 0 ? "ev-positive" : ev < 0 ? "ev-negative" : ""}>
                          {ev > 0 ? "+" : ""}{ev.toFixed(3)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </>
          )}
        </section>
      )}

      {game?.session_completed && (
        <section className="summary">
          <h2>訓練摘要</h2>
          {game.mistakes.length === 0 ? (
            <p>恭喜！此輪訓練中的每一步都與建議一致。</p>
          ) : (
            <>
              <p>共有 {game.mistakes.length} 筆決策與建議不同，詳細如下：</p>
              <ol>
                {game.mistakes.map((mistake) => (
                  <li key={`${mistake.round_index}-${mistake.decision_index}`}>
                    第 {mistake.round_index} 局第 {mistake.decision_index} 步，建議採用{" "}
                    <strong>{mistake.recommended_action}</strong>，實際操作為 {mistake.chosen_action}。手牌：
                    {mistake.player_hand.map(formatCard).join(", ")}，莊家明牌：{formatCard(mistake.dealer_upcard ?? "?")}
                  </li>
                ))}
              </ol>
            </>
          )}
        </section>
      )}
    </div>
  );
}

export default App;

