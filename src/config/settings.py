import os
from dotenv import load_dotenv
from models.execution_mode import ExecutionMode

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")
EXECUTION_MODE = ExecutionMode.MCP
GENERATE_ROBOT = True
INVENTREE_BASE_URL = "https://demo.inventree.org/"
PLAYWRIGHT_MCP_SERVER = "http://localhost:8931"