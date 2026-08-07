import os
from dotenv import load_dotenv
from models.execution_mode import ExecutionMode

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")
EXECUTION_MODE = ExecutionMode.MCP
GENERATE_ROBOT = True
INVENTREE_BASE_URL = "https://demo.inventree.org/web/login"
PLAYWRIGHT_MCP_SERVER = "http://localhost:8931"
DOCUMENTATION_URL = "https://docs.inventree.org/en/stable/part/"
DEBUG = False


# --------------------------------------------------
# Application Credentials
# --------------------------------------------------

APP_USERNAME = "allaccess"

APP_PASSWORD = "nolimits"

# --------------------------------------------------
# Execution Settings
# --------------------------------------------------

#
# Number of test cases to execute.
#
# None -> Execute all test cases.
#
#TC_COUNT_TO_EXECUTE = 1
TC_COUNT_TO_EXECUTE = None


#
# Optional test case file.
#
# None -> Use the current pipeline output.
#

#TEST_CASE_FILE = "D:\\epam_ai_agent\\AI-QEP\\output\\20260807_021400\\test_cases.json"
TEST_CASE_FILE = None