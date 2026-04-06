import logging
from fastmcp import FastMCP

# 1. 設置日誌系統 (muto.log)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("muto.log", encoding="utf-8"),
        logging.StreamHandler() # 同時輸出到控制台
    ]
)
logger = logging.getLogger("muto-server")

# 2. 建立 MCP 伺服器
mcp = FastMCP("MuTO")

@mcp.tool()
async def hello_tool(name: str) -> str:
    """A simple tool that greets the user by name."""
    logger.info(f"收到 hello_tool 請求: name='{name}'")
    
    response = f"Hello {name} from MuTO Skills! (SSE Connection Successful)"
    
    logger.info(f"hello_tool 執行完畢，即將回傳結果。")
    return response

if __name__ == "__main__":
    logger.info("MuTO MCP Server 正在啟動 (傳輸模式: SSE)...")
    mcp.run(transport="sse")
