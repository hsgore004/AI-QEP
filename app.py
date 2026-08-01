from pathlib import Path
import sys
from unittest import result

sys.path.append(str(Path(__file__).parent / "src"))

from openai import OpenAI
from pathlib import Path
from config import settings
from llm.providers.openai_provider import OpenAIProvider
from llm.service import LLMService

from agents.requirement_agent import RequirementAgent
from agents.ui_testcase_agent import UITestCaseAgent
from agents.api_testcase_agent import ApiTestCaseAgent

def main():

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    provider = OpenAIProvider(client)

    llm_service = LLMService(provider)

    requirement_agent = RequirementAgent(llm_service)

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

    result = requirement_agent.execute(requirement)
    ui_agent = UITestCaseAgent(llm_service)

    ui_test_cases = ui_agent.execute(result)
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "ui_test_cases.md"

    output_file.write_text(ui_test_cases, encoding="utf-8")

    print(f"UI Test Cases generated successfully: {output_file}")

    api_agent = ApiTestCaseAgent(llm_service)

    api_test_cases = api_agent.execute(result)

    output_file = output_dir / "api_test_cases.md"

    output_file.write_text(api_test_cases, encoding="utf-8")

    print(f"API Test Cases generated successfully: {output_file}")

    print(result)


if __name__ == "__main__":
    main()