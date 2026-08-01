from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
from models.evaluation_result import EvaluationResult
from evaluators.base_evaluator import BaseEvaluator


class DeepEvalEvaluator(BaseEvaluator):

    def evaluate(
        self,
        requirement: str,
        generated_output: str,
    ) -> EvaluationResult:

        metric = AnswerRelevancyMetric()

        test_case = LLMTestCase(
            input=requirement,
            actual_output=generated_output,
        )

        
        metric.measure(test_case)

        if metric.score is None:
            raise ValueError("DeepEval did not return a score.")

        reason = metric.reason

        if reason is None:
            reason = "No evaluation reason returned."

        return EvaluationResult(
            name="DeepEval",
            score=metric.score,
            passed=metric.score >= 0.80,
            reason=reason,
        )