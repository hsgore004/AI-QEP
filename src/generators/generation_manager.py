from llm.service import LLMService

from agents.ui_testcase_agent import UITestCaseAgent
from agents.api_testcase_agent import ApiTestCaseAgent
from agents.robot_framework_agent import RobotFrameworkAgent

from evaluators.requirement_coverage_evaluator import (
    RequirementCoverageEvaluator,
)

from models.generated_artifacts import GeneratedArtifacts


class GenerationManager:

    MAX_REPAIR_ATTEMPTS = 3

    def __init__(
        self,
        llm_service: LLMService,
        keyword_catalog: str,
    ):

        self.ui_agent = UITestCaseAgent(llm_service)
        self.api_agent = ApiTestCaseAgent(llm_service)
        self.robot_agent = RobotFrameworkAgent(llm_service)

        self.coverage_evaluator = RequirementCoverageEvaluator(
            llm_service,
        )

        self.keyword_catalog = keyword_catalog

    def generate(
        self,
        requirement_model,
    ) -> GeneratedArtifacts:

        # =====================================================
        # UI TEST CASES
        # =====================================================

        ui_test_cases = self.ui_agent.execute(
            requirement_model,
        )

        for attempt in range(self.MAX_REPAIR_ATTEMPTS):

            coverage = self.coverage_evaluator.evaluate(
                requirement_model,
                ui_test_cases,
            )

            print(
                f"[Coverage Judge] Attempt {attempt + 1}: "
                f"{'PASS' if coverage.passed else 'FAIL'}"
            )

            if coverage.passed:
                break

            ui_test_cases = self.ui_agent.execute(
                requirement=requirement_model,
                previous_artifact=ui_test_cases,
                judge_feedback=coverage.reason,
            )

        # =====================================================
        # API TEST CASES
        # =====================================================

        api_test_cases = self.api_agent.execute(
            requirement_model,
        )

        # =====================================================
        # ROBOT TEST CASES
        # =====================================================

        robot_test_cases = self.robot_agent.execute(
            requirement_model,
            ui_test_cases,
            self.keyword_catalog,
        )

        return GeneratedArtifacts(
            ui_test_cases=ui_test_cases,
            api_test_cases=api_test_cases,
            robot_test_cases=robot_test_cases,
        )