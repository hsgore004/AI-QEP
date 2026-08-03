import json

from llm.models.request import LLMRequest
from llm.service import LLMService

from prompts.verification.verification_prompt import SYSTEM_PROMPT


class VerificationAgent:

    def __init__(
        self,
        llm_service: LLMService,
    ):
        self.llm_service = llm_service

    def verify(
        self,
        business_step: str,
        page_snapshot: str,
    ):

        request = LLMRequest(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"""
Business Step:

{business_step}

Current Page Snapshot:

{page_snapshot}

Return ONLY valid JSON.
""",
        )

        response = self.llm_service.generate(
            request,
        )

        verification = json.loads(
            response.content,
        )

        return verification