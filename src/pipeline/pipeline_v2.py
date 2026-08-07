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


from generators.keyword_generation_manager import (
    KeywordGenerationManager,
)


from pathlib import Path
import shutil
import subprocess


from config.settings import EXECUTION_MODE
from models.execution_mode import ExecutionMode



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

        if settings.GENERATE_ROBOT:
            context.robot_test_cases = artifacts.robot_test_cases
        else:
            context.robot_test_cases = ""

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

        print("[OK] UI Validation completed")

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

#==========================================

            print("\n========================================")
            print(f"ROBOT JUDGE - ATTEMPT {attempt + 1}")
            print("========================================")

            print("\nCurrent Robot Test Cases:\n")
            print(context.robot_test_cases)

            judge_feedback = "\n".join(
                validation_result.errors
            )

            print("\nJudge Feedback:\n")
            print(judge_feedback)
#==========================================
            context.robot_test_cases = generation_manager.robot_agent.execute(
                requirement=context.requirement_model,
                ui_test_cases=context.ui_test_cases,
                keyword_catalog=keyword_catalog,
                previous_artifact=context.robot_test_cases,
                judge_feedback=judge_feedback,
            )

            print("\nRegenerated Robot Test Cases:\n")
            print(context.robot_test_cases)
            print("========================================\n")


        else:

            print("\n========================================")
            print(" Robot Validation Failed")
            print("========================================")

            for error in validation_result.errors:
                print(f"- {error}")

            return

        print("[OK] Robot Validation completed")

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

            print("\n========== NORMALIZED ROBOT TEST CASES ==========\n")
            print(normalized_robot)
            print("\n================================================\n")

            context.robot_suite = robot_builder.build(
                normalized_robot,
            )

            capability_report = CapabilityValidationService().validate(
                context.robot_suite,
            )

            if capability_report.can_execute:
                break

            print("\n========================================")
            print(f"CAPABILITY JUDGE - ATTEMPT {attempt + 1}")
            print("========================================")

            print("\nCurrent Robot Suite:\n")
            print(context.robot_suite)

            print("\nCapability Report:\n")
            print(capability_report.summary())

            judge_feedback = capability_report.summary()

            context.robot_test_cases = generation_manager.robot_agent.execute(
                requirement=context.requirement_model,
                ui_test_cases=context.ui_test_cases,
                keyword_catalog=keyword_catalog,
                previous_artifact=context.robot_test_cases,
                judge_feedback=judge_feedback,
            )

            print("\nRegenerated Robot Test Cases:\n")
            print(context.robot_test_cases)
            print("========================================\n")


        else:

            print(capability_report.summary())

            print("\nGenerating missing business keywords...\n")

            keyword_manager = KeywordGenerationManager(
                llm_service,
            )

            generated_keywords = keyword_manager.generate(
                context.requirement_model,
                capability_report.missing_keywords,
            )

            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)

            keyword_file = Path("robot/resources/generated_keywords.resource")

            keyword_file.write_text(
                generated_keywords,
                encoding="utf-8",
            )

            print(generated_keywords)

            print("\nGenerated keyword file:")
            print(keyword_file)

            return

        print("[OK] Capability Validation completed")
        print("[OK] Robot Builder completed")


#==========================================


        # ==========================================
        # Business Execution
        # ==========================================

        from executors.suite_executor import SuiteExecutor

        executor = SuiteExecutor(
            base_url=settings.INVENTREE_BASE_URL,
        )

        executor.execute(
            context.robot_test_cases
        )

        print("[OK] Business Execution completed")


        print("\n========================================")
        print("         AI-QEP V2 SUMMARY")
        print("========================================")
        print("[OK] Requirement Agent")
        print("[OK] UI Generation")
        print("[OK] UI Validation")
        print("[OK] API Generation")
        print("[OK] Robot Generation")
        print("[OK] Robot Validation")
        print("[OK] Capability Validation")
        print("[OK] Robot Builder")
        print("[OK] Robot Execution")
        print("========================================")