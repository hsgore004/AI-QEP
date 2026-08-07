from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExecutionSummary:
    requirement_agent: bool
    ui_agent: bool
    api_agent: bool
    robot_agent: bool
    robot_builder: bool
    robot_execution: bool

    report_path: Path

    ui_output: Path
    api_output: Path
    robot_output: Path

    execution_time: float