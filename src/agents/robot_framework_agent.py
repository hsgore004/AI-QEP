from llm.models.request import LLMRequest
from llm.service import LLMService

from models.requirement import Requirement
from prompts.generation.robot_framework_prompt import SYSTEM_PROMPT


class RobotFrameworkAgent:

    def __init__(
        self,
        llm_service: LLMService,
    ):
        self.llm_service = llm_service

    def execute(
        self,
        requirement: Requirement,
        ui_test_cases: str,
        keyword_catalog: str,
        previous_artifact: str | None = None,
        judge_feedback: str | None = None,
    ) -> str:

        # --------------------------------------------------
        # First Generation
        # --------------------------------------------------

        if previous_artifact is None:

            user_prompt = f"""
Requirement

{requirement.model_dump_json(indent=2)}

==================================================

Manual UI Test Cases

{ui_test_cases}

==================================================

Available Robot Framework Keywords

{keyword_catalog}

==================================================

IMPORTANT

1. Use ONLY the available business keywords.
2. Never generate Browser Library keywords.
3. Never generate Selenium keywords.
4. Never generate Playwright keywords.
5. Never generate locators.
6. Never generate variables.
7. Never generate assertions.
"""

        # --------------------------------------------------
        # Regeneration after Judge feedback
        # --------------------------------------------------

        else:

            user_prompt = f"""
Requirement

{requirement.model_dump_json(indent=2)}

==================================================

Manual UI Test Cases

{ui_test_cases}

==================================================

Available Robot Framework Keywords

{keyword_catalog}

==================================================

Current Robot Test Cases

{previous_artifact}

==================================================

Judge Feedback

{judge_feedback}

==================================================

Generate a corrected Robot Framework artifact.

Requirements

- Preserve everything already correct.
- Fix ONLY the reported issues.
- Do NOT invent new business scenarios.
- Do NOT remove valid test cases.
- Return ONLY the *** Test Cases *** section.
"""

        request = LLMRequest(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        response = self.llm_service.generate(request)

        robot_test_cases = response.content

        robot_test_cases = robot_test_cases.replace(
            "```robot",
            "",
        )

        robot_test_cases = robot_test_cases.replace(
            "```",
            "",
        )

        return robot_test_cases.strip()