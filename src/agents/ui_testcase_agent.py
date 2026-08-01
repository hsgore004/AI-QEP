from llm.models.request import LLMRequest
from llm.service import LLMService

from models.requirement import Requirement
from prompts.ui_testcase_prompt import SYSTEM_PROMPT


class UITestCaseAgent:

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def execute(self, requirement: Requirement) -> str:

        request = LLMRequest(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=requirement.model_dump_json(indent=2),
        )

        response = self.llm_service.generate(request)

        return response.content