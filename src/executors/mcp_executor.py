class MCPExecutor:

    def __init__(self, mcp_client):
        self.client = mcp_client

    def execute(self, robot_test_cases: str):

        for line in robot_test_cases.splitlines():

            line = line.rstrip()

            if (
                not line
                or line.startswith("***")
                or not line.startswith("    ")
            ):
                continue

            business_step = line.strip()

            print(f"[MCP] {business_step}")

            self.client.execute(
                business_step,
            )