from openai import OpenAI

from config import settings

from llm.providers.openai_provider import OpenAIProvider
from llm.service import LLMService

from models.run_context import RunContext

from agents.requirement_agent import RequirementAgent
from agents.ui_testcase_agent import UITestCaseAgent
from agents.api_testcase_agent import ApiTestCaseAgent
from agents.robot_framework_agent import RobotFrameworkAgent
from builders.robot_builder import RobotBuilder
from loaders.requirement_loader import RequirementLoader

from evaluators.deepeval_evaluator import DeepEvalEvaluator
from evaluators.evaluation_manager import EvaluationManager

from generators.generation_manager import GenerationManager
from loaders.keyword_catalog_loader import KeywordCatalogLoader


from validators.capability_validation_service import (
    CapabilityValidationService,
)


from pathlib import Path
import shutil
import subprocess


class AIQEPPipeline:

    def run(self):

        loader = RequirementLoader()

        context = RunContext(
            requirement_text=loader.load()
        )



        # LLM Initialization
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        provider = OpenAIProvider(client)

        llm_service = LLMService(provider)

        # Requirement Agent
        requirement_agent = RequirementAgent(llm_service)
        context.requirement_model = requirement_agent.execute(
            context.requirement_text
        )
        print("[✓] Requirement Agent completed")

        keyword_catalog = KeywordCatalogLoader().load()

        # Generation Layer

        generation_manager = GenerationManager(
            llm_service,
            keyword_catalog,
        )

        artifacts = generation_manager.generate(
            context.requirement_model
        )

        context.ui_test_cases = artifacts.ui_test_cases
        context.api_test_cases = artifacts.api_test_cases
        context.robot_test_cases = artifacts.robot_test_cases

        print("[✓] Generation Layer completed")


        # Evaluation Layer

        evaluation_manager = EvaluationManager()

        results = evaluation_manager.evaluate(
            context.requirement_text,
            context.ui_test_cases,
        )

        context.deep_eval_result = results[0]

        print(
            f"[✓] {context.deep_eval_result.name} completed "
            f"(Score: {context.deep_eval_result.score:.2f})"
        )


        # Robot Builder
        robot_builder = RobotBuilder()
        context.robot_suite = robot_builder.build(
            context.robot_test_cases
        )
        print("[✓] Robot Builder completed")

        capability_report = CapabilityValidationService().validate(
            context.robot_suite
        )

        print(capability_report.summary())

        if not capability_report.can_execute:
            return


        if not capability_report.can_execute:

            print("\n========================================")
            print("      AI-QEP CAPABILITY REPORT")
            print("========================================")

            print("\nExecution Blocked\n")

            print("Missing Business Keywords:\n")

            for keyword in capability_report.missing_keywords:
                print(f" - {keyword}")

            print("\nPlease implement the above business")
            print("keywords before executing the suite.")

            print("\n========================================")

            return


        # Robot Execution

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        context.robot_output = output_dir / "generated.robot"

        context.robot_output.write_text(
            context.robot_suite,
            encoding="utf-8",
        )

        robot_test_file = Path("robot/tests/generated.robot")

        shutil.copy(
            context.robot_output,
            robot_test_file,
        )

        subprocess.run(
            [
                ".venv\\Scripts\\robot.exe",
                "-d",
                "robot/reports",
                str(robot_test_file),
            ]
        )

        print("[✓] Robot Execution completed")


        print("\n========================================")
        print("         AI-QEP EXECUTION SUMMARY")
        print("========================================")

        print("[✓] Requirement Agent")
        print("[✓] UI Test Case Agent")
        print(
        f"[✓] {context.deep_eval_result.name:<22}: "
        f"{context.deep_eval_result.score:.2f}")
        print("[✓] API Test Case Agent")
        print("[✓] Robot Framework Agent")
        print("[✓] Robot Builder")
        print("[✓] Robot Execution")

        print("========================================")
        print("Execution completed successfully.")
        print("========================================")