from llm.models.request import LLMRequest
from llm.service import LLMService

from prompts.generation.keyword_generation_prompt import SYSTEM_PROMPT


class KeywordGenerationAgent:

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def execute(
        self,
        requirement,
        missing_keywords: list[str],
    ) -> str:

        user_prompt = f"""
Requirement

{requirement.model_dump_json(indent=2)}

========================================

Missing Business Keywords

{chr(10).join(missing_keywords)}
"""

        request = LLMRequest(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        response = self.llm_service.generate(request)

        return response.content