import json

from llm.models.request import LLMRequest
from llm.service import LLMService

from prompts.generation.business_planner_prompt import SYSTEM_PROMPT


class BusinessPlannerAgent:

    def __init__(
        self,
        llm_service: LLMService,
    ):
        self.llm_service = llm_service

    def create_plan(
        self,
        business_goal: str,
    ):

        request = LLMRequest(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"""
Business Goal:

{business_goal}

Return ONLY valid JSON.
""",
        )

        response = self.llm_service.generate(
            request,
        )

        print("\n========== BUSINESS PLAN ==========")
        print(response.content)
        print("===================================\n")

        plan = json.loads(response.content)

        # Support multiple possible keys returned by the LLM
        for key in ("steps", "result", "response"):

            if key in plan and isinstance(plan[key], list):
                return plan[key]

        raise ValueError(
            f"Unexpected planner response: {plan}"
)