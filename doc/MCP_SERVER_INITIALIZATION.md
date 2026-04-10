# MuTO MCP Server 初始化與日誌實作說明

本文件記載了 MuTO 作為專案核心工具伺服器 (MCP Server) 的基礎建設細節。

## 📡 通訊協議 (Transport)
*   **SSE (Server-Sent Events)**: 採用 FastAPI + MCP 官方適配器實作，優化了跨服務調用的連線穩定度。
*   **端點設計**:
    *   `/sse`: SSE 連線入口。
    *   `/messages/`: 工具訊息交換通道。

## 🛠️ 已實作工具 (Tools)
*   **hello_tool**: 基礎通訊驗證工具，支援接收 `name` 參數並回傳格式化問候訊息，用於驗證 AleT (Client) 與 MuTO (Server) 的連線狀態。

## 📝 日誌系統 (Logging Architecture)
*   **實作檔案**: `muto.log`
*   **特性**: 採用 UTF-8 編碼，具備時戳與模組標籤。
*   **追蹤內容**:
    *   MCP 初始化狀態
    *   工具調用時間
    *   連線異常細節

## 🏗️ 未來擴展 (Future Roadmap)
*   **EIDo 整合**: 未來將在此處新增 `search_flights` 與 `carbon_data_retrieval` 等核心 RAG 工具，並負責向向量資料庫進行檢索。

---
**維護者備註**: 
本地專用之 `.env` 與 `muto.log` 已經透過 `.gitignore` 過濾，請勿嘗試將其推至遠端倉庫。
