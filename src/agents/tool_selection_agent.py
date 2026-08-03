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
        current_url: str,
        available_tools: str,
        page_snapshot: str,
    ):

        prompt = self._build_prompt(
            business_step,
            current_url,
            available_tools,
            page_snapshot,
        )

        request = LLMRequest(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=prompt,
        )

        response = self.llm_service.generate(
            request,
        )


        response = response.content

        response = response.replace("```json", "")
        response = response.replace("```", "")
        response = response.strip()

        print("[LLM] Tool selected")

        return response


    def _build_prompt(
        self,
        business_step: str,
        current_url: str,
        available_tools: str,
        page_snapshot: str,
    ) -> str:

        return f"""
You MUST return valid JSON.
Business Goal:
{business_step}

Current URL:
{current_url}

Available MCP Tools:
{available_tools}

Current Page Snapshot:

{page_snapshot}
"""