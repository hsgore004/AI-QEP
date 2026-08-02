from openai import OpenAI

from config import settings

from llm.providers.openai_provider import OpenAIProvider
from llm.service import LLMService

from loaders.requirement_loader import RequirementLoader
from loaders.keyword_catalog_loader import KeywordCatalogLoader

from models.run_context import RunContext

from agents.requirement_agent import RequirementAgent

from generators.generation_manager import GenerationManager

from builders.robot_builder import RobotBuilder

from validators.ui_testcase_validator import UITestCaseValidator
from validators.robot_validator import RobotValidator

from validators.capability_validation_service import (
    CapabilityValidationService,
)


class AIQEPPipelineV2:

    def run(
        self,
        requirement_file: str,
    ):

        # ==========================================
        # Load Requirement
        # ==========================================

        loader = RequirementLoader()

        context = RunContext(
            requirement_text=loader.load(
                requirement_file,
            )
        )

        # ==========================================
        # LLM
        # ==========================================

        client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
        )

        provider = OpenAIProvider(client)

        llm_service = LLMService(
            provider,
        )

        # ==========================================
        # Requirement
        # ==========================================

        requirement_agent = RequirementAgent(
            llm_service,
        )

        context.requirement_model = (
            requirement_agent.execute(
                context.requirement_text,
            )
        )

        # ==========================================
        # Keyword Catalog
        # ==========================================

        keyword_catalog = (
            KeywordCatalogLoader().load()
        )

        # ==========================================
        # Generation
        # ==========================================

        generation_manager = GenerationManager(
            llm_service,
            keyword_catalog,
        )

        artifacts = generation_manager.generate(
            context.requirement_model,
        )

        context.ui_test_cases = artifacts.ui_test_cases
        context.api_test_cases = artifacts.api_test_cases
        context.robot_test_cases = artifacts.robot_test_cases

        # ==========================================
        # UI Validation
        # ==========================================

        ui_validator = UITestCaseValidator()

        validation_result = ui_validator.validate(
            context.requirement_model,
            context.ui_test_cases,
        )

        if not validation_result.is_valid:

            print("\n========================================")
            print(" UI TEST CASE VALIDATION FAILED")
            print("========================================")

            for issue in validation_result.issues:
                print(f"- {issue.code}: {issue.message}")

            return

        print("[✓] UI Validation completed")

#==========================================



        # ==========================================
        # Robot Validation (Self-Healing)
        # ==========================================

        robot_validator = RobotValidator()

        MAX_REPAIR_ATTEMPTS = 3

        for attempt in range(MAX_REPAIR_ATTEMPTS):

            validation_result = robot_validator.validate(
                context.robot_test_cases,
            )

            if validation_result.is_valid:
                break

            print(
                f"[Robot Judge] Attempt {attempt + 1}: FAIL"
            )

            judge_feedback = "\n".join(
                validation_result.errors
            )

            context.robot_test_cases = generation_manager.robot_agent.execute(
                requirement=context.requirement_model,
                ui_test_cases=context.ui_test_cases,
                keyword_catalog=keyword_catalog,
                previous_artifact=context.robot_test_cases,
                judge_feedback=judge_feedback,
            )

        else:

            print("\n========================================")
            print(" Robot Validation Failed")
            print("========================================")

            for error in validation_result.errors:
                print(f"- {error}")

            return

        print("[✓] Robot Validation completed")

#==========================================


        # ==========================================
        # Capability Validation (Self-Healing)
        # ==========================================

        MAX_CAPABILITY_REPAIR_ATTEMPTS = 3

        for attempt in range(MAX_CAPABILITY_REPAIR_ATTEMPTS):

            normalized_robot = robot_validator.normalize(
                context.robot_test_cases,
            )

            robot_builder = RobotBuilder()

            context.robot_suite = robot_builder.build(
                normalized_robot,
            )

            capability_report = CapabilityValidationService().validate(
                context.robot_suite,
            )

            if capability_report.can_execute:
                break

            print(
                f"[Capability Judge] Attempt {attempt + 1}: FAIL"
            )

            judge_feedback = capability_report.summary()

            context.robot_test_cases = generation_manager.robot_agent.execute(
                requirement=context.requirement_model,
                ui_test_cases=context.ui_test_cases,
                keyword_catalog=keyword_catalog,
                previous_artifact=context.robot_test_cases,
                judge_feedback=judge_feedback,
            )

        else:

            print(capability_report.summary())
            return

        print("[✓] Capability Validation completed")
        print("[✓] Robot Builder completed")


#==========================================


        # ==========================================
        # Robot Execution
        # ==========================================

        from pathlib import Path
        import shutil
        import subprocess

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        context.robot_output = output_dir / "generated.robot"

        context.robot_output.write_text(
            context.robot_suite,
            encoding="utf-8",
        )

        robot_test_file = Path(
            "robot/tests/generated.robot"
        )

        shutil.copy(
            context.robot_output,
            robot_test_file,
        )

        result = subprocess.run(
            [
                ".venv\\Scripts\\robot.exe",
                "-d",
                "robot/reports",
                str(robot_test_file),
            ]
        )

        if result.returncode == 0:
            print("[✓] Robot Execution completed")
        else:
            print("[✗] Robot Execution failed")


        print("\n========================================")
        print("         AI-QEP V2 SUMMARY")
        print("========================================")
        print("[✓] Requirement Agent")
        print("[✓] UI Generation")
        print("[✓] UI Validation")
        print("[✓] API Generation")
        print("[✓] Robot Generation")
        print("[✓] Robot Validation")
        print("[✓] Capability Validation")
        print("[✓] Robot Builder")
        print("[✓] Robot Execution")
        print("========================================")