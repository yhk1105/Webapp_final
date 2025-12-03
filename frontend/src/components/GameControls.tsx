import { GameAction } from "../types";

interface GameControlsProps {
  available: GameAction[];
  disabled?: boolean;
  onAction: (action: GameAction) => void;
}

const LABELS: Record<GameAction, string> = {
  hit: "Hit 要牌",
  stand: "Stand 停牌",
  double: "Double 加倍"
};

export function GameControls({ available, disabled, onAction }: GameControlsProps) {
  return (
    <div className="controls">
      {available.map((action) => (
        <button
          key={action}
          className="action-btn"
          disabled={disabled}
          onClick={() => onAction(action)}
        >
          {LABELS[action]}
        </button>
      ))}
    </div>
  );
}

