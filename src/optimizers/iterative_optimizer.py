from optimizers.base_optimizer import BaseOptimizer
from models.evaluation_result import EvaluationResult


class IterativeOptimizer(BaseOptimizer):

    def optimize(
        self,
        requirement: str,
        generated_output: str,
        evaluation: EvaluationResult,
    ) -> str:

        return generated_output