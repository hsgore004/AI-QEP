from pathlib import Path
import shutil
import subprocess
import sys

sys.path.append(str(Path(__file__).parent / "src"))

from openai import OpenAI

from config import settings
from llm.providers.openai_provider import OpenAIProvider
from llm.service import LLMService

from agents.requirement_agent import RequirementAgent
from agents.ui_testcase_agent import UITestCaseAgent
from agents.api_testcase_agent import ApiTestCaseAgent
from agents.robot_framework_agent import RobotFrameworkAgent

from builders.robot_builder import RobotBuilder


def main():

    # ---------------------------------------------------------
    # LLM Initialization
    # ---------------------------------------------------------

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    provider = OpenAIProvider(client)

    llm_service = LLMService(provider)

    # ---------------------------------------------------------
    # Requirement
    # ---------------------------------------------------------

    requirement = """
    As a registered user,
    I should be able to login
    using my email address and password
    so that I can access my dashboard.

    Validation:
    - Email is mandatory
    - Password is mandatory
    - Invalid credentials should display an error message.

    API:
    POST /login
    """

    # ---------------------------------------------------------
    # Output folder
    # ---------------------------------------------------------

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # ---------------------------------------------------------
    # Requirement Agent
    # ---------------------------------------------------------

    requirement_agent = RequirementAgent(llm_service)

    requirement_model = requirement_agent.execute(requirement)

    # ---------------------------------------------------------
    # UI Test Case Agent
    # ---------------------------------------------------------

    ui_agent = UITestCaseAgent(llm_service)

    ui_test_cases = ui_agent.execute(requirement_model)

    ui_output = output_dir / "ui_test_cases.md"

    ui_output.write_text(ui_test_cases, encoding="utf-8")

    print(f"UI Test Cases generated: {ui_output}")

    # ---------------------------------------------------------
    # API Test Case Agent
    # ---------------------------------------------------------

    api_agent = ApiTestCaseAgent(llm_service)

    api_test_cases = api_agent.execute(requirement_model)

    api_output = output_dir / "api_test_cases.md"

    api_output.write_text(api_test_cases, encoding="utf-8")

    print(f"API Test Cases generated: {api_output}")

    # ---------------------------------------------------------
    # Robot Agent
    # ---------------------------------------------------------

    robot_agent = RobotFrameworkAgent(llm_service)

    robot_test_cases = robot_agent.execute(
        requirement_model,
        ui_test_cases,
    )

    # ---------------------------------------------------------
    # Robot Builder
    # ---------------------------------------------------------

    robot_builder = RobotBuilder()

    robot_suite = robot_builder.build(robot_test_cases)

    robot_output = output_dir / "generated.robot"

    robot_output.write_text(robot_suite, encoding="utf-8")

    print(f"Robot Framework generated: {robot_output}")

    # ---------------------------------------------------------
    # Copy to Robot execution folder
    # ---------------------------------------------------------

    robot_test_file = Path("robot/tests/generated.robot")

    shutil.copy(robot_output, robot_test_file)

    print(f"Robot copied to: {robot_test_file}")

    # ---------------------------------------------------------
    # Execute Robot Framework
    # ---------------------------------------------------------

    print("\nExecuting Robot Framework...\n")

    result = subprocess.run(
        [
            ".venv\\Scripts\\robot.exe",
            "-d",
            "robot/reports",
            str(robot_test_file),
        ],
        capture_output=True,
        text=True,
    )

    print("\nExecution completed.")


if __name__ == "__main__":
    main()