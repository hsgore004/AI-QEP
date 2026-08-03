import keyword

from aiqep_mcp.playwright_mcp_client import PlaywrightMCPClient
import json

from agents.tool_selection_agent import ToolSelectionAgent
from agents.verification_agent import VerificationAgent


class BusinessExecutor:

    def __init__(
        self,
        mcp_server: str,
        base_url: str,
        tool_selection_agent: ToolSelectionAgent,
        verification_agent: VerificationAgent,
    ):

        self.client = PlaywrightMCPClient(
            mcp_server,
        )

        self.base_url = base_url

        self.tool_selection_agent = tool_selection_agent

        self.verification_agent = verification_agent

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

        # --------------------------------------------
        # Infrastructure keywords
        # --------------------------------------------

        if keyword == "Open Login Page":


            await self.client.call_tool(
                "browser_run_code_unsafe",
                {
                    "code": """
            async (page) => {
                const context = page.context();

                await context.clearCookies();

                await page.goto("about:blank");

                await page.evaluate(() => {
                    localStorage.clear();
                    sessionStorage.clear();
                });

                return "Browser session cleared";
            }
            """
                },
            )



            await self.client.call_tool(
                "browser_navigate",
                {
                    "url": self.base_url,
                },
            )

            return

        tool_definitions = await self.client.list_tools()

        available_tools = ""

        for tool in tool_definitions.tools:

            required = tool.input_schema.get("required", [])

            available_tools += f"""
        Tool: {tool.name}
        Description: {tool.description}
        Required Arguments: {", ".join(required) if required else "None"}

        """

        await self.client.call_tool(
            "browser_wait_for",
            {
                "time": 2,
            },
        )

        MAX_STEPS = 10

        for step in range(MAX_STEPS):

            snapshot = await self.client.call_tool(
                "browser_snapshot",
                {},
            )

            snapshot_text = ""

            if snapshot.content:
                snapshot_text = snapshot.content[0].text

            print("[MCP] Snapshot captured")

            print(f"\n[ACTION] {keyword}")

            # ====================================================
            # Verification Flow
            # ====================================================

            if keyword.lower().startswith("verify"):

                result = self.verification_agent.verify(
                    business_step=keyword,
                    page_snapshot=snapshot_text,
                )

                status = result["status"]

                print(f"[VERIFY] {status}")

                if status == "SUCCESS":
                    print("[DONE]")
                    return

                if status == "FAILED":
                    raise Exception(
                        f"Verification failed: {keyword}"
                    )

                await self.client.call_tool(
                    "browser_wait_for",
                    {
                        "time": 2,
                    },
                )

                continue

            # ====================================================
            # Action Flow
            # ====================================================

            tool_json = self.tool_selection_agent.select_tool(
                business_step=keyword,
                current_url=self.base_url,
                available_tools=available_tools,
                page_snapshot=snapshot_text,
            )

            tool = json.loads(tool_json)
            print(f"[AI] -> {tool['tool']}")
            if tool["tool"] == "FINISHED":
                print("[DONE]")
                return

            await self.client.call_tool(
                tool["tool"],
                tool["arguments"],
            )

        
        raise Exception(
            f"Maximum retries exceeded for step: {keyword}"
        )