from enum import Enum


class ExecutionMode(str, Enum):

    MCP = "mcp"

    ROBOT = "robot"

    BOTH = "both"