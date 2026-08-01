import json
from urllib import response

from llm.models.request import LLMRequest
from llm.service import LLMService

from models.requirement import Requirement
from prompts.requirement_prompt import SYSTEM_PROMPT


class RequirementAgent:

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def execute(self, requirement_text: str) -> Requirement:

        request = LLMRequest(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=requirement_text,
        )

        response = self.llm_service.generate(request)

        #print(response.content)

        data = json.loads(response.content)

        return Requirement(**data)