import asyncio

from executors.business_executor import BusinessExecutor
from config.settings import (
    INVENTREE_BASE_URL,
    PLAYWRIGHT_MCP_SERVER,
)


async def main():

    executor = BusinessExecutor(
        PLAYWRIGHT_MCP_SERVER,
        INVENTREE_BASE_URL,
    )

    async with executor.client:

        await executor.client.call_tool(
            "browser_close",
            {},
        )

        await executor.execute(
            "Open Login Page",
        )

        await executor.client.call_tool(
            "browser_evaluate",
            {
                "function": "() => window.location.href"
            },
        )


asyncio.run(main())