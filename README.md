# 需求軌跡監控（demand-trace）

觀察名單公司的經營軌跡監控：購置／處分／擴產／收縮／上下游動態 → 交叉判讀 → 工業地產切入點。

- **閱讀介面（GitHub Pages）**：`docs/index.html` — 事件時間軸＋公司軌跡檔
- **資料**：`docs/data/records.json`（每日排程 append，與 Google 試算表雙寫）
- **軌跡檔**：`docs/companies/<公司名>.md`（累積式，每家一份；`index.json` 為清單）

## 資料流

```
雲端排程（每日 08:00 台北）
  ├─ 觀察名單／查重：Apps Script 端點（Google 試算表）
  ├─ 來源：TWSE OpenAPI 重訊、MOPS、新聞搜尋、自建實價登錄／監控表
  ├─ 判讀：大宇範式（處分≠經營不善，需交叉購置動作判讀真實意圖）
  └─ 輸出：試算表 POST ＋ 本 repo（records.json、companies/*.md）commit push
```

## 相關

- 紀錄試算表：需求軌跡監控紀錄（Google Sheets）
- 本機專案：`C:\Users\dell\Documents\Claude-DT\projects\20260808-需求軌跡`（系統設計.md）
- 排程：claude.ai routines「需求軌跡監控（每日）」
