interface HandProps {
  title: string;
  cards: string[];
  score?: number | null;
  highlight?: boolean;
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
            {card}
          </span>
        ))}
      </div>
    </div>
  );
}

