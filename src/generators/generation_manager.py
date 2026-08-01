from llm.service import LLMService

from agents.ui_testcase_agent import UITestCaseAgent
from agents.api_testcase_agent import ApiTestCaseAgent
from agents.robot_framework_agent import RobotFrameworkAgent

from models.generated_artifacts import GeneratedArtifacts

from loaders.keyword_catalog_loader import KeywordCatalogLoader

class GenerationManager:

    def __init__(
        self,
        llm_service: LLMService,
        keyword_catalog: str,
    ):

        self.ui_agent = UITestCaseAgent(llm_service)
        self.api_agent = ApiTestCaseAgent(llm_service)
        self.robot_agent = RobotFrameworkAgent(llm_service)
        self.keyword_catalog = keyword_catalog

    def generate(
        self,
        requirement_model,
    ) -> GeneratedArtifacts:

        ui_test_cases = self.ui_agent.execute(
            requirement_model
        )

        api_test_cases = self.api_agent.execute(
            requirement_model
        )

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