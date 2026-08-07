from abc import ABC, abstractmethod

from models.evaluation_result import EvaluationResult


class BaseEvaluator(ABC):

    @abstractmethod
    def evaluate(
        self,
        requirement: str,
        generated_output: str,
    ) -> EvaluationResult:
        pass