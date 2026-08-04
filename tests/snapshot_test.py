import asyncio

from aiqep_mcp.playwright_mcp_client import PlaywrightMCPClient
from config.settings import INVENTREE_BASE_URL
async def main():

    async with PlaywrightMCPClient("http://localhost:8931") as client:

        await client.call_tool(
            "browser_navigate",
            {
                "url": INVENTREE_BASE_URL,
            },
        )

        result = await client.call_tool(
            "browser_console_messages",
            {}
        )

        print(result)

        print("Navigation OK")

        await client.call_tool(
            "browser_wait_for",
            {
                "time": 5
            }
        )

        print("Waiting finished")

        snapshot = await client.call_tool(
            "browser_snapshot",
            {}
        )

        print(snapshot)

asyncio.run(main())