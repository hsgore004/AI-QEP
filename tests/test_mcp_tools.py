import asyncio

from config.settings import PLAYWRIGHT_MCP_SERVER
from aiqep_mcp.playwright_mcp_client import PlaywrightMCPClient


async def main():

    async with PlaywrightMCPClient(
        PLAYWRIGHT_MCP_SERVER,
    ) as client:

        tools = await client.list_tools()

        print("\n========== AVAILABLE TOOLS ==========\n")

        print(tools)

        print("\n=====================================\n")


asyncio.run(main())