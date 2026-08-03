from executors.business_executor import BusinessExecutor

import asyncio

from config.settings import (
    PLAYWRIGHT_MCP_SERVER,
)


class SuiteExecutor:

    def __init__(
        self,
        base_url: str,
    ):

        self.executor = BusinessExecutor(
            mcp_server=PLAYWRIGHT_MCP_SERVER,
            base_url=base_url,
        )

    def execute(
        self,
        robot_test_cases: str,
    ):

        asyncio.run(
            self._execute_suite(
                robot_test_cases,
            )
        )




    async def _execute_suite(
        self,
        robot_test_cases: str,
    ):

        async with self.executor.client:

            for line in robot_test_cases.splitlines():

                line = line.rstrip()

                if not line:
                    continue

                if line.startswith("***"):
                    continue

                if not line.startswith("    "):
                    continue

                keyword = line.strip()

                print(f"[EXECUTE] {keyword}")

                await self.executor.execute(
                    keyword,
                )