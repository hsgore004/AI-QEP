import json

from llm.models.request import LLMRequest
from llm.service import LLMService

from prompts.generation.test_case_generation_prompt import SYSTEM_PROMPT


class BusinessPlannerAgent:

    def __init__(
        self,
        llm_service: LLMService,
    ):
        self.llm_service = llm_service

    async def create_plan(
        self,
        business_goal: str,
    ):

        request = LLMRequest(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"""
Generate executable business test cases.

Application:
InvenTree

Business Goal:
{business_goal}

Instructions:

- Generate the smallest possible executable test case.
- Each test step must perform exactly ONE browser-level action.
- Every action must be immediately followed by its own implicit validation step.
- Do not combine multiple actions into one step.
- Do not skip navigation steps.
- Do not skip page transitions.
- Do not skip dialog transitions.
- When a page or dialog is expected to appear, add a dedicated wait step.
- If a form contains multiple mandatory fields, generate ONE step:
  Populate all mandatory fields with valid business data.
- Do not mention browser tools.
- Do not mention Playwright.
- Return ONLY valid JSON.
""",
    response_format="json"
        )

        response = await self.llm_service.generate(
            request,
        )

        plan = json.loads(response.content)

        if "steps" in plan:
            return plan

        raise ValueError(
            f"Unexpected planner response: {plan}"
        )