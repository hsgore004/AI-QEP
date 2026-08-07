import asyncio

from openai import OpenAI

import config.settings as settings
from config.settings import (
    INVENTREE_BASE_URL,
    PLAYWRIGHT_MCP_SERVER,
)

from llm.providers.openai_provider import OpenAIProvider
from llm.service import LLMService

from agents.tool_selection_agent import ToolSelectionAgent
from agents.business_planner_agent import BusinessPlannerAgent
from agents.verification_agent import VerificationAgent

from executors.business_executor import BusinessExecutor
from executors.scenario_executor import ScenarioExecutor

async def main():

    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
    )

    provider = OpenAIProvider(
        client,
    )

    llm_service = LLMService(
        provider,
    )


    # ---------------------------------------------
    # QA Brain
    # ---------------------------------------------

    # ---------------------------------------------
    # Agents
    # ---------------------------------------------

    tool_selection_agent = ToolSelectionAgent(
        llm_service,
    )

    business_planner = BusinessPlannerAgent(
        llm_service,
    )

    verification_agent = VerificationAgent(
        llm_service,
    )

    # ---------------------------------------------
    # Business Executor
    # ---------------------------------------------

    business_executor = BusinessExecutor(
        PLAYWRIGHT_MCP_SERVER,
        INVENTREE_BASE_URL,
        tool_selection_agent,
        verification_agent,
        llm_service,
    )

    # ---------------------------------------------
    # Scenario Executor
    # ---------------------------------------------

    scenario_executor = ScenarioExecutor(
        business_executor,
        business_planner,
    )


    # ---------------------------------------------
    # Learn Application
    # ---------------------------------------------

    async with business_executor.client:

        business_executor.tool_catalog = (
            await business_executor.client.get_tool_catalog()
        )

        await business_executor.client.call_tool(
            "browser_close",
            {},
        )

        await business_executor.execute(
            "Open Login Page",
        )

        snapshot = await business_executor.client.call_tool(
            "browser_snapshot",
            {},
        )

        print(snapshot)

        await scenario_executor.execute(
            "Login as admin",
        )


        import asyncio

        print("\nSleeping for 7 seconds...\n")

        await asyncio.sleep(7)

        print("\nSleep finished.\n")

        for i in range(5):
            print(f"Heartbeat {i}")

            result = await business_executor.client.call_tool(
                "browser_snapshot",
                {},
            )

            print(result)

            await asyncio.sleep(3)


        print("\n========== TAKING SNAPSHOT AGAIN ==========\n")

        snapshot = await business_executor.client.call_tool(
            "browser_snapshot",
            {},
        )

        print(snapshot)


        print("========== BEFORE SCENARIO ==========")
        print("session =", business_executor.client.session)
        print("dispatcher =", business_executor.client.session._dispatcher)

        await scenario_executor.execute(
            {
                "title": "Create a new Part"
            }
        )

        print("\nWaiting 30 seconds WITHOUT calling OpenAI...\n")

        await asyncio.sleep(30)

        print("\n30 seconds completed.\n")

        snapshot = await business_executor.client.call_tool(
            "browser_snapshot",
            {},
        )

        print(snapshot)
        


if __name__ == "__main__":
    asyncio.run(main())
