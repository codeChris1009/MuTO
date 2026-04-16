"""
Muto 專案的核心日誌 (Logging) 模組。

基於 structlog 封裝，提供所有開發人員統一的日誌標準。
確保我們在處理 MCP (Model Context Protocol) 請求與 Pipeline 執行時，
能有結構化、具備一致欄位資訊的日誌，方便後續分析與追蹤。
"""

import logging
import sys
import os
from pathlib import Path
import structlog
from config.app_config import app_settings
from config.log_config import log_settings

def setup_logger():
    """
    初始化與設定 structlog。
    請在程式啟動 (例如 main.py 或 FastAPI lifespan) 時呼叫此函數。
    """
    # 判斷是否為開發環境
    is_dev = app_settings.environment.lower() in ("dev", "development", "local")

    # 清除非預期的 root logger 以免配置重疊
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # 定義共用的處理器 (Processors)
    shared_processors = [
        structlog.stdlib.filter_by_level,               # 根據設定層級過濾
        structlog.stdlib.add_log_level,                 # 加入 log level (INFO, ERROR...)
        structlog.stdlib.add_logger_name,               # 加入 logger 名稱
        structlog.processors.TimeStamper(fmt="iso"),    # ISO 8601 時間戳
        structlog.contextvars.merge_contextvars,        # 允許使用 bind_contextvars 綁定全域變數 (例如 pipeline_id)
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,           # 格式化錯誤資訊 (Exception)
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter, # 重要：將資料拋轉給底下的標準 Logging Formatter 處理
    ]

    structlog.configure(
        processors=shared_processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # --- 1. 配置 Console 輸出 (人類可讀的彩色純文字，或者是開發者想要的自定義 Format) ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = structlog.stdlib.ProcessorFormatter(
        # 即使在 prod，終端機通常還是看文字比較方便；如果是純後台，您可以判斷 is_dev 來決定 render 方式
        processor=structlog.dev.ConsoleRenderer(colors=is_dev)
    )
    console_handler.setFormatter(console_formatter)
    handlers = [console_handler]

    # 套用整體設定 (force=True 確保取代任何殘留的 root handler)
    logging.basicConfig(
        level=log_settings.log_level.upper(),
        handlers=handlers,
        force=True
    )

def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    取得符合規範的日誌實例 (BoundLogger 已內建 ainfo 等非同步方法)。

    Usage:
        from core.logger import get_logger
        logger = get_logger(__name__)
    """
    return structlog.get_logger(name)

def bind_pipeline_context(pipeline_id: str, mcp_task_name: str, **kwargs):
    """
    綁定本次 Pipeline/Task 執行的 Context。
    這樣同一個異步流程內的所有 log 都會自動帶上這兩個欄位。

    Args:
        pipeline_id: 流程 ID (例如可使用 uuid4)
        mcp_task_name: 當前執行的 MCP 任務名稱或技能名稱
        **kwargs: 其他需要全域綁定的變數
    """
    structlog.contextvars.bind_contextvars(
        pipeline_id=pipeline_id,
        mcp_task_name=mcp_task_name,
        **kwargs
    )

def clear_context():
    """清除當前的 Context"""
    structlog.contextvars.clear_contextvars()

