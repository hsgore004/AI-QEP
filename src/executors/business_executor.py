from aiqep_mcp.playwright_mcp_client import PlaywrightMCPClient


class BusinessExecutor:

    def __init__(
        self,
        mcp_server: str,
        base_url: str,
    ):

        self.client = PlaywrightMCPClient(
            mcp_server,
        )

        self.base_url = base_url

    # --------------------------------------------
    # Lifecycle
    # --------------------------------------------

    def start(self):

        self.client.start()

    def stop(self):

        self.client.stop()

    # --------------------------------------------
    # Business Keywords
    # --------------------------------------------

    async def execute(
        self,
        keyword: str,
    ):

        keyword = keyword.strip()

        if keyword == "Open Login Page":

            await self.client.call_tool(
                "browser_navigate",
                {
                    "url": self.base_url,
                },
            )

            return

        elif keyword == "Verify Username Field Is Visible":

            await self.client.call_tool(
                "browser_snapshot",
                {},
            )
            return
        
        raise NotImplementedError(
            f"Business keyword not implemented: {keyword}"
        )