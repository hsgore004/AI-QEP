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
    )

    # ---------------------------------------------
    # Scenario Executor
    # ---------------------------------------------

    scenario_executor = ScenarioExecutor(
        business_executor,
        business_planner,
    )

    async with business_executor.client:

        await business_executor.client.call_tool(
            "browser_close",
            {},
        )

        await business_executor.execute(
            "Open Login Page",
        )

        await scenario_executor.execute(
            "Login as admin",
        )


if __name__ == "__main__":
    asyncio.run(main())