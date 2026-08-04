from urllib import response

from llm.models.request import LLMRequest
from llm.service import LLMService

from prompts.generation.tool_selection_prompt import SYSTEM_PROMPT


class ToolSelectionAgent:

    def __init__(
        self,
        llm_service: LLMService,
    ):
        self.llm_service = llm_service

    async def select_tool(
        self,
        business_step: str,
        current_url: str,
        available_tools: str,
        page_snapshot: str,
        previous_step: str | None = None,
        next_step: str | None = None,
        expected_result: str | None = None,
        last_action: str | None = None,
    ):

        prompt = self._build_prompt(
            business_step,
            current_url,
            available_tools,
            page_snapshot,
            last_action,
        )
        request = LLMRequest(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=prompt,
            response_format="json",
        )

        response = await self.llm_service.generate(
            request,
        )


        response = response.content

        response = response.replace("```json", "")
        response = response.replace("```", "")
        response = response.strip()

        return response


    def _build_prompt(
        self,
        business_step: str,
        current_url: str,
        available_tools: str,
        page_snapshot: str,
        previous_step: str | None = None,
        next_step: str | None = None,
        expected_result: str | None = None,
        last_action: str | None = None,
    ) -> str:

        return f"""
Do not wrap the JSON in markdown.

Current Business Step

BUSINESS GOAL

Current Step
-------------
{business_step}

Previous Step
-------------
{previous_step}

Next Step
---------
{next_step}

Expected Result
---------------
{expected_result}

Current URL
-----------
{current_url}

Available MCP Tools
-------------------
{available_tools}

Current Page Snapshot
---------------------
{page_snapshot}


Return ONLY valid JSON.

The response MUST match this schema exactly:

{{
  "tool": "browser_click",
  "arguments": {{
    "target": "e42"
  }}
}}

or

{{
  "tool": "browser_fill_form",
  "arguments": {{}}
}}

or

{{
  "tool": "FINISHED",
  "arguments": {{}}
}}
"""