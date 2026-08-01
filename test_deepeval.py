from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase


metric = AnswerRelevancyMetric()

test_case = LLMTestCase(
    input="""
As a registered user,
I should be able to login using email and password.
""",
    actual_output="""
1. Verify successful login
2. Verify invalid password
3. Verify empty email
4. Verify empty password
""",
)

metric.measure(test_case)

print(f"Score : {metric.score}")
print(f"Reason: {metric.reason}")