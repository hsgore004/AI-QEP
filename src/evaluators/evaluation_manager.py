from evaluators.deepeval_evaluator import DeepEvalEvaluator
from evaluators.requirement_coverage_evaluator import (
    RequirementCoverageEvaluator,
)

from models.evaluation_result import EvaluationResult


class EvaluationManager:

    def __init__(
        self,
        llm_service,
    ):

        self.evaluators = [
            DeepEvalEvaluator(),
            RequirementCoverageEvaluator(llm_service),
        ]

    def evaluate(
        self,
        requirement,
        generated_output,
    ) -> list[EvaluationResult]:

        results = []

        for evaluator in self.evaluators:

            if isinstance(evaluator, DeepEvalEvaluator):

                results.append(
                    evaluator.evaluate(
                        requirement.model_dump_json(indent=2),
                        generated_output,
                    )
                )

            else:

                results.append(
                    evaluator.evaluate(
                        requirement,
                        generated_output,
                    )
                )

        return results