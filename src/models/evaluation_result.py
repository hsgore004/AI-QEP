from dataclasses import dataclass


@dataclass
class EvaluationResult:

    name: str

    score: float

    passed: bool

    reason: str