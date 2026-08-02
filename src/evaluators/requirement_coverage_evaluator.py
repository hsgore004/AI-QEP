from llm.models.request import LLMRequest
from llm.service import LLMService

from models.evaluation_result import EvaluationResult

from prompts.evaluation.requirement_coverage_prompt import SYSTEM_PROMPT


class RequirementCoverageEvaluator:

    def __init__(
        self,
        llm_service: LLMService,
    ):
        self.llm_service = llm_service


    def passed(
        self,
        result: EvaluationResult,
    ) -> bool:

        return result.passed

    def evaluate(
        self,
        requirement,
        artifact: str,
    ) -> EvaluationResult:

        request = LLMRequest(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"""
Requirement

{requirement.model_dump_json(indent=2)}

==================================================

Generated Artifact

{artifact}
""",
        )

        response = self.llm_service.generate(request)

        passed = response.content.strip().upper().startswith("PASS")

        return EvaluationResult(
            name="Requirement Coverage",
            score=1.0 if passed else 0.0,
            passed=passed,
            reason=response.content,
        )