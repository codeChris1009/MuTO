import asyncio
from core.logger import setup_logger, get_logger, bind_pipeline_context

# 1. 啟動時先呼叫 setup_logger() 來設定格式與輸出路徑 (包含 Console 與檔案)
setup_logger()

# 2. 獲取 logger 實例
logger = get_logger(__name__)

async def main():
    print("=== 同步/非同步 Log 測試 ===")
    # 同步日誌呼叫
    logger.info("starting_system", info="這是一條普通(同步)的 info 日誌", user="admin")
    logger.warning("found_issue", warning_msg="有東西可能不太對勁")

    print("\n=== 非同步與 Context 綁定測試 ===")
    # 綁定全域 ContextVars (例如 pipeline_id 等)
    bind_pipeline_context(pipeline_id="測試_UUID_12345", mcp_task_name="test_log")

    # 在 Async 環境下的非同步寫入 (使用 ainfo, aerror 等)
    await logger.ainfo("execution_started", step=1)
    await asyncio.sleep(0.1)

    try:
        # 測試錯誤拋出
        1 / 0
    except Exception as e:
        # 若發生 Exception，可以使用 exc_info=True 讓 structlog 自動擷取 Traceback
        await logger.aerror("execution_failed", error="除以零錯誤", exc_info=True)

    await logger.ainfo("execution_finished", step="done")

if __name__ == "__main__":
    asyncio.run(main())
