from llm.models.request import LLMRequest
from llm.service import LLMService

from prompts.generation.tool_selection_prompt import SYSTEM_PROMPT


class ToolSelectionAgent:

    def __init__(
        self,
        llm_service: LLMService,
    ):
        self.llm_service = llm_service

    def select_tool(
        self,
        business_step: str,
        available_tools: list[str],
        current_url: str,
    ):

        prompt = self._build_prompt(
            business_step,
            available_tools,
            current_url,
        )

        request = LLMRequest(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=prompt,
        )

        response = self.llm_service.generate(
            request,
        )

        response = response.content

        print("\n========== TOOL SELECTION ==========")
        print(response)
        print("====================================\n")

        return response


    def _build_prompt(
        self,
        business_step: str,
        available_tools: list[str],
        current_url: str,
    ) -> str:

        return f"""
{SYSTEM_PROMPT}

Business Step:
{business_step}

Current URL:
{current_url}

Available MCP Tools:

{chr(10).join(available_tools)}
"""