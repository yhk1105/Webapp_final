# Blackjack 模擬訓練系統

一個基於 Web 技術的 21 點（Blackjack）訓練應用程式，幫助玩家學習基本策略並提升決策能力。系統使用蒙地卡羅模擬來提供即時的動作建議與勝率分析。

## 📋 專案簡介

這個專案是一個完整的 21 點訓練平台，提供：

- **互動式遊戲介面**：模擬真實的 21 點遊戲場景
- **智能建議系統**：使用蒙地卡羅模擬（Monte Carlo Simulation）計算最佳動作與各動作的勝率
- **決策錯誤追蹤**：記錄玩家與建議不符的決策，並在回合結束後提供檢討
- **牌靴狀態監控**：顯示剩餘牌數、牌型分佈等資訊
- **多副牌支援**：支援 1-8 副牌的訓練模式

## 🛠️ 技術棧

### 前端 (Frontend)
- **React 18.3** - UI 框架
- **TypeScript 5.6** - 型別安全的 JavaScript
- **Vite 5.4** - 現代化建置工具與開發伺服器
- **CSS3** - 樣式設計（支援深色模式）

### 後端 (Backend)
- **Python 3** - 程式語言
- **FastAPI** - 現代化、快速的 Web API 框架
- **Pydantic** - 資料驗證與設定管理
- **Uvicorn** - ASGI 伺服器
- **SQLite** - 輕量級資料庫（用於記錄決策歷史）

## ✨ 主要功能

1. **遊戲流程管理**
   - 建立新遊戲（可設定牌組副數）
   - 執行基本動作（Hit、Stand、Double）
   - 多回合訓練（自動在牌靴剩餘 50% 時結束）

2. **智能分析**
   - 即時蒙地卡羅模擬建議
   - 各動作的勝率、和局率、敗率統計
   - 最佳動作標示

3. **學習輔助**
   - 決策錯誤記錄與檢討
   - 牌靴組成視覺化圖表
   - 訓練摘要報告

4. **使用者體驗**
   - 深色/淺色主題切換
   - 響應式設計
   - 即時狀態更新

## 📁 專案結構

```
Webapp_final/
├── frontend/                 # 前端專案
│   ├── src/
│   │   ├── components/      # React 組件
│   │   │   ├── GameControls.tsx
│   │   │   ├── Hand.tsx
│   │   │   └── ShoeCompositionChart.tsx
│   │   ├── api.ts           # API 呼叫封裝
│   │   ├── App.tsx          # 主應用組件
│   │   ├── types.ts         # TypeScript 型別定義
│   │   └── main.tsx         # 應用入口
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts       # Vite 配置（包含 API proxy）
│
├── backend/                  # 後端專案
│   ├── main.py              # FastAPI 應用主程式
│   ├── Manager.py           # 遊戲邏輯管理
│   ├── Game.py              # 遊戲規則實作
│   ├── Hand.py              # 手牌處理
│   ├── Shoe.py              # 牌靴管理
│   ├── Simulator.py         # 蒙地卡羅模擬器
│   ├── Utils.py             # 工具函數
│   ├── database.py          # 資料庫操作
│   ├── requirements.txt     # Python 依賴套件
│   └── blackjack.db         # SQLite 資料庫（執行後自動生成）
│
└── README.md                # 本文件
```

## 🚀 安裝與執行

### 前置需求

- **Node.js** 18+ 與 npm
- **Python** 3.8+
- **pip**（Python 套件管理器）

### 步驟 1：安裝後端依賴

```bash
cd backend
pip install -r requirements.txt
```

### 步驟 2：啟動後端伺服器

```bash
# 在 backend 目錄下
uvicorn main:app --reload
```

後端伺服器會啟動在 `http://127.0.0.1:8000`

> 💡 提示：可以訪問 `http://127.0.0.1:8000/docs` 查看 API 文件（Swagger UI）

### 步驟 3：安裝前端依賴

開啟新的終端視窗：

```bash
cd frontend
npm install
```

### 步驟 4：啟動前端開發伺服器

```bash
# 在 frontend 目錄下
npm run dev
```

前端應用會啟動在 `http://localhost:5173`

> 💡 注意：前端透過 Vite proxy 自動將 `/api` 請求轉發到後端

### 步驟 5：開始使用

在瀏覽器開啟 `http://localhost:5173` 即可開始使用訓練系統！

## 🎮 使用說明

1. **開始新遊戲**
   - 選擇牌組副數（1-8 副）
   - 點擊「開始模擬」按鈕

2. **進行遊戲**
   - 查看當前手牌與莊家明牌
   - 參考蒙地卡羅建議（可選擇顯示/隱藏）
   - 選擇動作：Hit（要牌）、Stand（停牌）、Double（加倍）

3. **檢視結果**
   - 回合結束後查看結果
   - 如有決策錯誤，會顯示檢討資訊
   - 點擊「下一局」繼續訓練

4. **訓練結束**
   - 當牌靴剩餘量 ≤ 50% 時，系統會自動結束訓練
   - 查看完整的訓練摘要報告

## 🔧 開發說明

### 前端開發

- **開發模式**：`npm run dev`
- **建置生產版本**：`npm run build`
- **預覽生產版本**：`npm run preview`

### 後端開發

- **開發模式（自動重載）**：`uvicorn main:app --reload`
- **生產模式**：`uvicorn main:app --host 0.0.0.0 --port 8000`

### API 端點

- `POST /api/games` - 建立新遊戲
- `POST /api/games/{game_id}/action` - 執行動作
- `GET /api/games/{game_id}/analysis` - 取得分析建議
- `POST /api/games/{game_id}/next-round` - 開始下一回合
- `GET /api/games/{game_id}` - 取得遊戲狀態

完整 API 文件可參考：`http://127.0.0.1:8000/docs`

## 📝 注意事項

1. **牌靴組成顯示**：為防止玩家作弊，`shoe_composition` 只在回合開始前或結束後顯示，進行中為空物件。

2. **資料庫**：首次啟動後端時會自動建立 `blackjack.db`，無需手動設定。

3. **CORS 設定**：後端已設定 CORS，允許前端跨域請求。

4. **開發環境**：本專案使用 Vite 的 proxy 功能在開發環境處理 API 轉發，生產環境部署時需要另行設定。

## 📄 授權

本專案為教育用途專案。

---

如有問題或建議，歡迎提出 Issue 或 Pull Request！





