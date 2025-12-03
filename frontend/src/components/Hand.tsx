interface HandProps {
  title: string;
  cards: string[];
  score?: number | null;
  highlight?: boolean;
}

function formatCard(card: string): string {
  // 將 11、12、13 轉換為 J、Q、K
  if (card === "11") return "J";
  if (card === "12") return "Q";
  if (card === "13") return "K";
  return card;
}

export function Hand({ title, cards, score, highlight }: HandProps) {
  return (
    <div className={`hand ${highlight ? "hand-highlight" : ""}`}>
      <div className="hand-header">
        <h3>{title}</h3>
        {typeof score === "number" && <span className="score">分數：{score}</span>}
      </div>
      <div className="cards">
        {cards.length === 0 && <span className="card placeholder">--</span>}
        {cards.map((card, index) => (
          <span key={`${card}-${index}`} className="card">
            {formatCard(card)}
          </span>
        ))}
      </div>
    </div>
  );
}

