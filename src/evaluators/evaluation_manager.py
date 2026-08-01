from evaluators.deepeval_evaluator import DeepEvalEvaluator
from models.evaluation_result import EvaluationResult


class EvaluationManager:

    def __init__(self):

        self.evaluators = [
            DeepEvalEvaluator(),
        ]


    def evaluate(
        self,
        requirement: str,
        generated_output: str,
    ) -> list[EvaluationResult]:

        results = []

        for evaluator in self.evaluators:
            results.append(
                evaluator.evaluate(
                    requirement,
                    generated_output,
                )
            )

        return results