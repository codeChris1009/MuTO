# MuTO Logging 規範指南

為了確保 MuTO 在作為 MCP 主機的運行過程中，能清晰記錄下任務派發、Pipeline 執行與結果追蹤的過程，我們全面採用 `structlog` 作為日誌處理標準。

## 為什麼使用 structlog？

- **結構化資料**：能在日誌中帶入任意的 key-value，方便除錯與資料關聯。
- **Context 行為**：利用 ContextVars，一次綁定 `pipeline_id`，後續該請求的所有非同步 log 皆會自動帶上它，不需透過參數層層傳遞。
- **無阻塞 I/O**：移除了傳統的 FileHandler 檔案寫入，全面導向 `stdout`。讓 FastAPI 的原生 AsyncIO 事件迴圈不會被寫檔拖慢，寫檔工作一律交由外部容器或收集器處理。
- **非同步相容**：透過 `AsyncBoundLogger` 封裝，讓高併發的異步環境可以透過 `await logger.info()` 等方式直接寫入而不影響效能。

## 設定與使用步驟

### 1. 啟動階段初始化

在應用程式的進入點（如 `main.py` 或 FastAPI lifespan 中），加入並呼叫 `setup_logger()`，這會確保整體的環境被正確設定：

```python
from core.logger import setup_logger

setup_logger()
```

### 2. 獲取 Logger 物件

**請停止使用內建的 `print` 或是原生的 `logging`**。所有模組皆應透過我們封裝好的 `get_logger`。

```python
from core.logger import get_logger

# 建議傳入 __name__ 方便追蹤日誌來源模組
logger = get_logger(__name__)
```

### 3. 一般日誌寫法 (Sync vs Async)

由於 `get_logger()` 回傳的是 `BoundLogger`，它原生就支援同步與非同步的方法。

- **在一般同步的區塊 (如 config 讀取, 初始化)**：直接呼叫 `.info()`, `.error()` 等。
- **在非同步函數中 (如 `async def`, MCP Tools)**：必須呼叫非同步版本的方法如 `.ainfo()`, `.aerror()` 等，並加上 `await` 以防止 I/O 阻塞：

```python
# [在非同步任務、API Endpoints、MCP Tools 中]
async def handle_request():
    # 必須使用 ainfo 並加上 await
    await logger.ainfo("mcp_server_started", port=8000, host="0.0.0.0")
```

### 4. Pipeline / Task 上下文追蹤 (重要!)

在 MCP 技能被觸發，或開始一個新的 Pipeline 工作流時，請務必綁定上下文。
這樣在這個流程內所發出的**任何日誌**，都會自動帶入這些識別資訊。

```python
import uuid
from core.logger import get_logger, bind_pipeline_context, clear_context

logger = get_logger(__name__)

async def run_mcp_pipeline(task_name: str):
    # 1. 產生一個唯一 ID
    pl_id = str(uuid.uuid4())

    # 2. 綁定 Pipeline 資訊
    bind_pipeline_context(pipeline_id=pl_id, mcp_task_name=task_name)

    await logger.ainfo("pipeline_started", status="init")

    try:
        # 中間的任何模組、任何函數使用 logger，都會自動包含 pipeline_id
        await step_one()
        await step_two()
        await logger.ainfo("pipeline_completed", status="success")
    except Exception as e:
        # 若發生錯誤，加入 exc_info=True 以擷取完整的 Traceback
        await logger.aerror("pipeline_failed", error=str(e), exc_info=True)
    finally:
        # 3. 結束後務必清除 context，避免影響 Event Loop 下一個被排程的 Task！
        clear_context()
```

### 5. 日誌欄位命名約定

為了讓系統方便 Parse 與分析，請遵守以下規則：

- `event` (位置參數第一位): 清晰的事件名稱，請用**小寫加底線**，將動詞放末尾，例如 `db_connection_failed`, `mcp_tool_called`。
- `pipeline_id` / `request_id`: 任務或 API 請求的唯一識別碼。
- `mcp_task_name`: 目前處理的 MCP 工具/任務名稱。
- `duration_ms`: 記錄執行的計算時間 (毫秒)。
- `error`: 放置 Exception 轉換的字串 (如 `str(e)`)，保留原本的 `exc_info=True` 會自動捕獲系統 Stack Trace。

## TODO / 未來優化方向

### 1. 第三方庫的日誌未被攔截 (Log Routing)

- **問題**：您的專案內有使用 FastAPI、Uvicorn、SQLAlchemy、HTTPX 等套件。這些套件都有自己的 logging，它們預設不會通過您精心設計的 structlog 流程，導致終端機上會出現「一半是我們自定義的漂亮/JSON 格式，一半是原本亂糟糟的 Uvicorn 預設格式」的狀況。
- **優化方式**：需要在 `setup_logger()` 中，把這些第三方 Logger 的 Handler 全部攔截掉，並導向至我們現有的 structlog，讓全站 (即使是底層 DB 語法與 API 請求) 都統一輸出。

### 2. 生產環境 (prod) 應全面轉換為 JSON 輸出

- **問題**：目前的設定 `structlog.dev.ConsoleRenderer(colors=is_dev)` 是讓終端機無論在 Dev 還是 Prod 都是輸出純文字（只是 Prod 關閉顏色）。但在 Docker / K8s / 雲端環境中，外部收集工具（像是 FluentBit、Datadog、ELK）通常直接吃 stdout 的日誌，這時我們其實需要 stdout 吐出的直接是 JSON。
- **優化方式**：根據 `is_dev` 動態切換 Renderer：開發時用 `ConsoleRenderer`，上線時直接將 `ConsoleRenderer` 替換為 `JSONRenderer()`，無縫對接基礎設施。

### 3. Traceback (錯誤堆疊) 的結構化與安全性

- **問題**：目前的 `format_exc_info` 會把錯誤堆疊轉為一大串字串。在日誌收集系統中，這會造成搜尋困難。
- **優化方式**：如果是 JSON 模式（Prod 環境），建議引入 `structlog.processors.dict_tracebacks`，把整包 Traceback 解構成字典 (例如分別拆出 `exc_type`, `exc_value`, `frames` 等)，更利於後台系統下 SQL 查詢（例如搜「哪個 function 爆什麼異常」）。

### 4. 效能：Uvicorn 與非同步 I/O 的相容

- **問題**：Uvicorn 管理 Request 迴圈時，Access Log 每秒可能會發生百次。我們如果把 Uvicorn Access log 導向 Structlog，就能在 FastAPI 的每筆 Access log 中也吃到我們綁定的 `pipeline_id`（只要是在 Middleware 綁定）。
- **優化方式**：未來在 FastAPI 中增加一個 Logging Middleware，只要接到 Request 就 `bind_pipeline_context(request_id)`，這樣連 Request 到 Response 之間的 DB、HTTPX 都自動關聯。
