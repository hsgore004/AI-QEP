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


        # UI Test Case Agent
        ui_agent = UITestCaseAgent(llm_service)
        context.ui_test_cases = ui_agent.execute(
            context.requirement_model
        )
        print("[✓] UI Test Case Agent completed")


        # API Test Case Agent
        api_agent = ApiTestCaseAgent(llm_service)
        context.api_test_cases = api_agent.execute(
            context.requirement_model
        )
        print("[✓] API Test Case Agent completed")


        # Robot Framework Agent
        robot_agent = RobotFrameworkAgent(llm_service)
        context.robot_test_cases = robot_agent.execute(
            context.requirement_model,
            context.ui_test_cases,
        )
        print("[✓] Robot Framework Agent completed")



        # Robot Builder
        robot_builder = RobotBuilder()
        context.robot_suite = robot_builder.build(
            context.robot_test_cases
        )
        print("[✓] Robot Builder completed")


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
        print("[✓] API Test Case Agent")
        print("[✓] Robot Framework Agent")
        print("[✓] Robot Builder")
        print("[✓] Robot Execution")
        print("========================================")
        print("Execution completed successfully.")
        print("========================================")