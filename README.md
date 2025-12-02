【後端啟動與對接注意事項 / Backend Integration Notes】

1. 啟動方式 (How to start):
   (1) 安裝套件: pip install -r requirements.txt
   (2) 啟動伺服器: uvicorn main:app --reload
   
   → 成功後會跑在 http://127.0.0.1:8000

2. API 文件 (Swagger UI):
   http://127.0.0.1:8000/docs
   (可以直接在這裡測試 API 是否正常回傳)

3. 開發注意事項 (Important Notes):
   - shoe_composition (剩餘牌分佈): 為了防止玩家作弊，只有在「回合結束」或「剛開局」時才會回傳資料，回合進行中會是空物件 {}。
   - session_completed: 當牌靴剩餘量 <= 50% 時，該回合結束後此欄位會變 true，請記得顯示結算畫面。
   - 資料庫: 啟動後會自動建立 blackjack.db，不用手動設定。

有問題隨時跟我說！謝謝！
