from llm.models.request import LLMRequest
from llm.service import LLMService

from models.requirement import Requirement
from prompts.robot_framework_prompt import SYSTEM_PROMPT


class RobotFrameworkAgent:

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def execute(
        self,
        requirement: Requirement,
        ui_test_cases: str,
    ) -> str:

        user_prompt = f"""
Requirement:
{requirement.model_dump_json(indent=2)}

----------------------------------------

Manual UI Test Cases:

{ui_test_cases}
"""

        request = LLMRequest(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        response = self.llm_service.generate(request)

        robot_test_cases = response.content

        # Remove markdown if the LLM accidentally returns it
        robot_test_cases = robot_test_cases.replace("```robot", "")
        robot_test_cases = robot_test_cases.replace("```", "")
        robot_test_cases = robot_test_cases.strip()

        return robot_test_cases