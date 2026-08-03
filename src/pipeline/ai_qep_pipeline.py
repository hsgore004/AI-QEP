from openai import OpenAI
import time
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

from validators.robot_validator import RobotValidator

from validators.capability_validation_service import (
    CapabilityValidationService,
)

from validators.ui_testcase_validator import UITestCaseValidator



from pathlib import Path
import shutil
import subprocess


class AIQEPPipeline:

    def run(
        self,
        requirement_file: str,
    ):
        start_time = time.time()
        loader = RequirementLoader()

        context = RunContext(
            requirement_text=loader.load(
                requirement_file
            )
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

        print("\n===== Requirement Model =====")
        print(context.requirement_model.model_dump_json(indent=2))
        print("=============================\n")

        print("[OK] Requirement Agent completed")

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

        print("\n===== UI TEST CASES =====")
        print(context.ui_test_cases)
        print("=========================\n")

        context.api_test_cases = artifacts.api_test_cases
        context.robot_test_cases = artifacts.robot_test_cases


        # UI Test Case Validation + Repair

        context.ui_test_cases = self._validate_and_repair(
            "ui_test_cases",
            context.ui_test_cases,
            UITestCaseValidator(),
            generation_manager,
            context.requirement_model,
            context.requirement_model,
            context.ui_test_cases,
        )

        print("[OK] UI Test Case Validation completed")

#===============================================


#===============================================



        robot_validator = RobotValidator()

        validation_result = robot_validator.validate(
            context.robot_test_cases
        )

        if not validation_result.is_valid:

            print("\n========================================")
            print(" Robot Validation Failed")
            print("========================================")

            for error in validation_result.errors:
                print(f" - {error}")

            return

        context.robot_test_cases = robot_validator.normalize(
            context.robot_test_cases
        )

        print("\n===== UI TEST CASES =====")
        print(context.ui_test_cases)
        print("=========================\n")

        print("\n===== ROBOT TEST CASES =====")
        print(context.robot_test_cases)
        print("============================\n")

        print("[OK] Generation Layer completed")


        # Evaluation Layer

        evaluation_manager = EvaluationManager(
            llm_service,
        )

        results = evaluation_manager.evaluate(
            context.requirement_model,
            context.ui_test_cases,
        )

        for result in results:

            print(
                f"[OK] {result.name} completed"
            )

            print(result.reason)
#========================================

        # Robot Validation
        robot_validator = RobotValidator()
        validation_result = robot_validator.validate(
            context.robot_test_cases
        )
        if not validation_result.is_valid:
            print("\n========================================")
            print(" Robot Validation Failed")
            print("========================================")
            for error in validation_result.errors:
                print(f" - {error}")
            return

        normalized_robot = robot_validator.normalize(
            context.robot_test_cases
        )

        validation_result = robot_validator.validate(
            normalized_robot
        )

        if not validation_result.is_valid:

            print("\n========================================")
            print(" Robot Validation Failed After Normalization")
            print("========================================")

            for error in validation_result.errors:
                print(f" - {error}")

            return

        # Robot Builder

        robot_builder = RobotBuilder()

        context.robot_suite = robot_builder.build(
            normalized_robot
        )

        print("[OK] Robot Validation completed")
        print("[OK] Robot Builder completed")

#========================================
        capability_report = CapabilityValidationService().validate(
            context.robot_suite
        )

        print(capability_report.summary())


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

        print("[OK] Robot Execution completed")


        print("\n========================================")
        print("         AI-QEP EXECUTION SUMMARY")
        print("========================================")

        print("[OK] Requirement Agent")
        print("[OK] UI Test Case Agent")
        print(
        f"[OK] {context.deep_eval_result.name:<22}: "
        f"{context.deep_eval_result.score:.2f}")
        print("[OK] API Test Case Agent")
        print("[OK] Robot Framework Agent")
        print("[OK] Robot Builder")
        print("[OK] Robot Execution")

        execution_time = time.time() - start_time

        print("========================================")
        print("Execution completed successfully.")
        print("----------------------------------------")
        print(f"Execution Time : {execution_time:.2f} sec")
        print("========================================")



    def _validate_and_repair(
        self,
        artifact_name,
        artifact,
        validator,
        generation_manager,
        requirement,
        *validator_args,
    ):
        validation_result = validator.validate(*validator_args)

        if validation_result.is_valid:
            return artifact

        return generation_manager.repair(
            artifact_name=artifact_name,
            validation_result=validation_result,
            current_artifact=artifact,
            requirement=requirement,
        )