from executors.business_executor import BusinessExecutor

from config.settings import (
    PLAYWRIGHT_MCP_SERVER,
)


class RobotExecutor:

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

        self.executor.start()

        try:

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

                self.executor.execute(
                    keyword,
                )

        finally:

            self.executor.stop()