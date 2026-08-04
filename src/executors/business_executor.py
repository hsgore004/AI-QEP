import keyword
from unittest import result

from aiqep_mcp.playwright_mcp_client import PlaywrightMCPClient
import json

from agents.tool_selection_agent import ToolSelectionAgent
from agents.verification_agent import VerificationAgent
from agents.page_context_agent import FocusedContextAgent
from intelligence.execution_intelligence import ExecutionIntelligence
DEBUG = False
from utils.logger import Logger

import asyncio
class BusinessExecutor:

    def __init__(
        self,
        mcp_server: str,
        base_url: str,
        tool_selection_agent: ToolSelectionAgent,
        verification_agent: VerificationAgent,
        llm_service,
    ):

        self.client = PlaywrightMCPClient(
            mcp_server,
        )
        self.tool_catalog = ""
        self.base_url = base_url

        self.tool_selection_agent = tool_selection_agent

        self.verification_agent = verification_agent

        self.execution_intelligence = ExecutionIntelligence(
            llm_service,
        )

        self.focused_context_agent = FocusedContextAgent(
            llm_service,
        )

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
        previous_step: str | None = None,
        next_step: str | None = None,
        expected_result: str | None = None,
    ):
        print("\n========== BUSINESS EXECUTOR ENTER ==========")
        print(self.client.session)
        keyword = keyword.strip()
        print("\n")
        print("=" * 80)
        print("BUSINESS STEP")
        print("=" * 80)
        print(keyword)
        print("=" * 80)
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
#========================
        # print(">>> About to call list_tools()")

        # tool_definitions = await self.client.list_tools()

        # print(">>> list_tools() completed")


        # for tool in tool_definitions.tools:

        #     if tool.name == "browser_fill_form":

        #         print("\n==============================")
        #         print("browser_fill_form")
        #         print("==============================")
        #         print(tool.description)
        #         print(tool.input_schema)
        #         print("==============================\n")

        # available_tools = ""

        # for tool in tool_definitions.tools:

        #     required = tool.input_schema.get("required", [])

        #     available_tools += f"""
        # Tool: {tool.name}
        # Description: {tool.description}
        # Required Arguments: {", ".join(required) if required else "None"}

        # """
        available_tools = self.tool_catalog
#===========================
        # await self.client.call_tool(
        #     "browser_wait_for",
        #     {
        #         "time": 2,
        #     },
        # )

        last_action = None
        MAX_STEPS = 5

        for step in range(MAX_STEPS):

            # snapshot = await self.client.call_tool(
            #     "browser_snapshot",
            #     {},
            # )

            print("Taking snapshot...")

            try:

                print("========== BEFORE FIRST SNAPSHOT ==========")
                print("session =", self.client.session)
                print("dispatcher =", self.client.session._dispatcher)

                print("session =", self.client.session)
                print("read =", self.client.read_stream)
                print("write =", self.client.write_stream)

                print("session dict:")
                print(vars(self.client.session))


                snapshot = await self.client.call_tool(
                    "browser_snapshot",
                    {},
                )
                print("FIRST SNAPSHOT COMPLETED")
                print("Snapshot OK")
            except Exception as e:
                print("Snapshot FAILED")
                print(repr(e))
                raise

            snapshot_text = ""

            if snapshot.content:
                snapshot_text = snapshot.content[0].text

            if DEBUG:
                Logger.subsection("Browser Snapshot")
                Logger.text(snapshot_text)

            if DEBUG:
                print("\n================ SNAPSHOT ================\n")
                print(snapshot_text)
                print("\n==========================================\n")



            # ====================================================
            # Verification Flow
            # ====================================================

            if keyword.lower().startswith("verify"):

                result = await self.verification_agent.verify(
                keyword,
                snapshot_text,
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

            # Prevent repeating the exact same action for the same step
            if last_action:

                Logger.subsection("Previous Browser Action")
                Logger.text(last_action)

                last = json.loads(last_action)

                # ----------------------------------------------------
                # Typing steps
                # ----------------------------------------------------
                if (
                    last["tool"] == "browser_type"
                    and keyword.lower().startswith("enter")
                ):
                    print("[Executor] Typing already performed. Marking step complete.")
                    return

                # ----------------------------------------------------
                # Click-based steps
                # ----------------------------------------------------
                if (
                    last["tool"] == "browser_click"
                    and (
                        keyword.lower().startswith("click")
                        or keyword.lower().startswith("navigate")
                        or keyword.lower().startswith("create")
                    )
                ):
                    print("[Executor] Click already performed. Marking step complete.")
                    return

                if (
                    last["tool"] == "browser_fill_form"
                    and keyword.lower().startswith("enter")
                ):
                    print("[Executor] Form already populated. Marking step complete.")
                    return

            Logger.section("Focused Context")
            Logger.text("Extracting relevant context...")

            focused_snapshot = await self.focused_context_agent.extract_context(
                    keyword,
                    snapshot_text,
                )

            Logger.subsection("Focused Snapshot")
            Logger.text(focused_snapshot)

            tool_json = await self.tool_selection_agent.select_tool(
                keyword,
                self.base_url,
                available_tools,
                focused_snapshot,
                previous_step,
                next_step,
                expected_result,
                last_action,
            )

            tool = json.loads(tool_json)
            Logger.section("Tool Selection")
            Logger.text(tool["tool"])

            Logger.subsection("Arguments")
            Logger.json(tool["arguments"])

            if tool["tool"] == "FINISHED":
                print("[DONE]")
                return
            # ----------------------------------------------------
            # Resolve value before typing
            # ----------------------------------------------------

            if tool["tool"] == "browser_type":

                print("[Execution Intelligence] Resolving value...")

                field_name = "Unknown Field"

                keyword_lower = keyword.lower()

                if "username" in keyword_lower:
                    field_name = "Username"

                elif "password" in keyword_lower:
                    field_name = "Password"

                value = self.execution_intelligence.resolve_value(
                    business_step=keyword,
                    field_name=field_name,
                )

                print(f"[Execution Intelligence] Value: {value}")

            # ----------------------------------------------------
            # Special handling for browser_fill_form
            # ----------------------------------------------------

            if tool["tool"] == "browser_fill_form":

                Logger.section("Execution Intelligence")
                Logger.text("Form detected")

                form_json = await self.execution_intelligence.generate_form_data(
                keyword,
                snapshot_text,
                )

                Logger.subsection("Generated MCP Form")
                Logger.text(form_json)

                try:
                    form_arguments = json.loads(form_json)
                except Exception as ex:
                    raise Exception(
                        f"AI returned invalid JSON:\n\n{form_json}"
                    ) from ex

                result = await self.client.call_tool(
                    "browser_fill_form",
                    form_arguments,
                )

                Logger.subsection("browser_fill_form Result")
                Logger.text(result)

                last_action = json.dumps(
                    {
                        "tool": "browser_fill_form",
                        "arguments": form_arguments,
                    },
                    indent=2,
                )

                await self.client.call_tool(
                    "browser_wait_for",
                    {
                        "time": 1,
                    },
                )

                continue

            # ----------------------------------------------------
            # Normal MCP execution
            # ----------------------------------------------------

            result = await self.client.call_tool(
                tool["tool"],
                tool["arguments"],
            )

            Logger.subsection(f"{tool['tool']} Result")
            Logger.text(result)

            last_action = json.dumps(
                {
                    "tool": tool["tool"],
                    "arguments": tool["arguments"],
                },
                indent=2,
            )

            await self.client.call_tool(
                "browser_wait_for",
                {
                    "time": 1,
                },
            )
        
        raise Exception(
            f"Maximum retries exceeded for step: {keyword}"
        )