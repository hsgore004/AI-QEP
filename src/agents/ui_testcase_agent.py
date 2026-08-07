from llm.models.request import LLMRequest
from llm.service import LLMService

from models.requirement import Requirement
from prompts.generation.ui_testcase_prompt import SYSTEM_PROMPT


class UITestCaseAgent:

    def __init__(
        self,
        llm_service: LLMService,
    ):
        self.llm_service = llm_service

    def execute(
        self,
        requirement: Requirement,
        previous_artifact: str | None = None,
        judge_feedback: str | None = None,
    ) -> str:

        # First generation
        if previous_artifact is None:

            user_prompt = requirement.model_dump_json(
                indent=2,
            )

        # Regeneration after Judge feedback
        else:

            user_prompt = f"""
Requirement

{requirement.model_dump_json(indent=2)}

==================================================

Current Artifact

{previous_artifact}

==================================================

Judge Feedback

{judge_feedback}

==================================================

Generate a corrected version.

Requirements:

- Preserve everything that is already correct.
- Fix ONLY the issues reported by the Judge.
- Do NOT invent additional scenarios.
- Return ONLY the corrected Markdown table.
"""

        request = LLMRequest(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        response = self.llm_service.generate(request)

        return response.content