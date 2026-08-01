from abc import ABC, abstractmethod

from models.evaluation_result import EvaluationResult


class BaseOptimizer(ABC):

    @abstractmethod
    def optimize(
        self,
        requirement: str,
        generated_output: str,
        evaluation: EvaluationResult,
    ) -> str:
        """Return an improved version of the generated output."""
        pass