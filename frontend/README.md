# Blackjack Trainer Frontend

以 React + Vite 製作的最基礎訓練介面，對接 FastAPI 後端以完成企劃書中 MVP 的基礎互動。

## 開發方式

```bash
cd frontend
npm install
npm run dev
```

開發伺服器會啟動在 `http://localhost:5173`，並透過 Vite proxy 轉發 `/api` 及 `/health` 到 `http://localhost:8000`。

## 主要頁面功能

- 設定牌組副數後建立牌局
- 顯示莊家與玩家手牌、分數、剩餘牌數
- 執行 Hit / Stand / Double
- 呼叫 `/analysis` API 取得蒙地卡羅建議與勝率

如需在生產環境部署，可先執行 `npm run build` 產出靜態檔案。

