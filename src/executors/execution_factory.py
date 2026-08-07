from openai import OpenAI

import config.settings as settings

from config.settings import (
    INVENTREE_BASE_URL,
    PLAYWRIGHT_MCP_SERVER,
)

from llm.providers.openai_provider import (
    OpenAIProvider,
)

from llm.service import (
    LLMService,
)

from agents.tool_selection_agent import (
    ToolSelectionAgent,
)

from agents.business_planner_agent import (
    BusinessPlannerAgent,
)

from agents.verification_agent import (
    VerificationAgent,
)

from executors.business_executor import (
    BusinessExecutor,
)

from executors.scenario_executor import (
    ScenarioExecutor,
)

from executors.execution_runner import (
    ExecutionRunner,
)


def create_execution_runner():

    #
    # LLM
    #

    client = OpenAI(

        api_key=settings.OPENAI_API_KEY,

    )

    provider = OpenAIProvider(

        client,

    )

    llm_service = LLMService(

        provider,

    )

    #
    # Agents
    #

    tool_selection_agent = ToolSelectionAgent(

        llm_service,

    )

    business_planner = BusinessPlannerAgent(

        llm_service,

    )

    verification_agent = VerificationAgent(

        llm_service,

    )

    #
    # Business Executor
    #

    business_executor = BusinessExecutor(

        PLAYWRIGHT_MCP_SERVER,

        INVENTREE_BASE_URL,

        tool_selection_agent,

        verification_agent,

        llm_service,

    )

    #
    # Scenario Executor
    #

    scenario_executor = ScenarioExecutor(

        business_executor,

        business_planner,

    )

    #
    # Execution Runner
    #

    execution_runner = ExecutionRunner(

        scenario_executor=scenario_executor,
        business_executor=business_executor,

    )

    return execution_runner