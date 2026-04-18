import uuid

from fastmcp import FastMCP

from core.logger import bind_pipeline_context, clear_context, get_logger, setup_logger

# 1. 設置結構化日誌系統
setup_logger()
logger = get_logger(__name__)

# 2. 建立 MCP 伺服器
mcp = FastMCP("MuTO")


@mcp.tool()
async def hello_tool(name: str) -> str:
    """A simple tool that greets the user by name."""
    # 綁定此次任務的 Context
    pipeline_id = str(uuid.uuid4())
    bind_pipeline_context(pipeline_id=pipeline_id, mcp_task_name="hello_tool")

    await logger.ainfo("tool_execution_started", requested_name=name)

    try:
        response = f"Hello {name} from MuTO Skills! (SSE Connection Successful)"

        await logger.ainfo("tool_execution_completed")
        return response
    except Exception as e:
        await logger.aerror("tool_execution_failed", error=str(e), exc_info=True)
        raise
    finally:
        # 清除 Context 避免干擾下一個獨立任務
        clear_context()


if __name__ == "__main__":
    logger.info("server_starting", transport="sse", server_name="MuTO")
    mcp.run(transport="sse")
