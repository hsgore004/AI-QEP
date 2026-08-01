from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from models.requirement import Requirement
from models.execution_summary import ExecutionSummary
from models.evaluation_result import EvaluationResult

@dataclass
class RunContext:

    # Original Requirement
    requirement_text: str

    # Structured Requirement
    requirement_model: Optional[Requirement] = None

    # Generated Artifacts
    ui_test_cases: Optional[str] = None
    api_test_cases: Optional[str] = None
    robot_test_cases: Optional[str] = None

    # Final Robot Suite
    robot_suite: Optional[str] = None

    # Output Files
    ui_output: Optional[Path] = None
    api_output: Optional[Path] = None
    robot_output: Optional[Path] = None
    report_output: Optional[Path] = None

    # Execution
    execution_summary: Optional[ExecutionSummary] = None

    # Timing
    start_time: float = 0
    end_time: float = 0


    # Evaluation
    deep_eval_result: EvaluationResult | None = None