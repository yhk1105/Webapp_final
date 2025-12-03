import { useMemo } from "react";

interface ShoeCompositionChartProps {
  composition: Record<string, number>;
  initialShoeSize: number;
}

const RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"];

export function ShoeCompositionChart({ composition, initialShoeSize }: ShoeCompositionChartProps) {
  const maxCount = useMemo(() => {
    return Math.max(...Object.values(composition), 1);
  }, [composition]);

  // Calculate max possible count per rank (4 suits * 8 decks = 32 max)
  // We can use a fixed height scale or relative to current max.
  // Relative to current max is better for visibility.

  return (
    <div className="shoe-chart">
      <h3>剩餘牌堆分佈</h3>
      <div className="chart-container">
        {RANKS.map((rank) => {
          const count = composition[rank] || 0;
          const heightPercent = (count / maxCount) * 100;
          
          // Determine color intensity based on count relative to initial average
          // Initial average per rank = initialShoeSize / 13
          // This is just a visual flair, optional.
          
          return (
            <div key={rank} className="chart-bar-column">
              <div className="bar-wrapper">
                <div 
                  className="bar" 
                  style={{ height: `${heightPercent}%` }}
                  title={`${rank}: ${count}張`}
                ></div>
              </div>
              <div className="label">{rank}</div>
              <div className="count">{count}</div>
            </div>
          );
        })}
      </div>
      <style>{`
        .shoe-chart {
          margin-top: 2rem;
          padding: 1rem;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 8px;
        }
        .shoe-chart h3 {
          margin-bottom: 1rem;
          font-size: 1.1rem;
          color: #aaa;
        }
        .chart-container {
          display: flex;
          justify-content: space-between;
          align-items: flex-end;
          height: 150px;
          gap: 4px;
        }
        .chart-bar-column {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          height: 100%;
        }
        .bar-wrapper {
          flex: 1;
          width: 100%;
          display: flex;
          align-items: flex-end;
          justify-content: center;
          margin-bottom: 4px;
        }
        .bar {
          width: 80%;
          background: #646cff;
          border-radius: 2px 2px 0 0;
          transition: height 0.3s ease;
          min-height: 1px;
        }
        .label {
          font-weight: bold;
          font-size: 0.9rem;
        }
        .count {
          font-size: 0.8rem;
          color: #888;
        }
      `}</style>
    </div>
  );
}
