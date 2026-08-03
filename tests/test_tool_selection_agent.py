import os
import sys

from openai import OpenAI

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
        )
    ),
)

import config.settings as settings

from llm.providers.openai_provider import OpenAIProvider
from llm.service import LLMService

from agents.tool_selection_agent import ToolSelectionAgent


client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
)

provider = OpenAIProvider(
    client,
)

llm_service = LLMService(
    provider,
)

agent = ToolSelectionAgent(
    llm_service,
)

agent.select_tool(
    business_step="Verify Username Field Is Visible",
    current_url="https://demo.inventree.org/web/login",
    available_tools=[
        "browser_find",
        "browser_snapshot",
        "browser_evaluate",
        "browser_click",
        "browser_type",
    ],
)