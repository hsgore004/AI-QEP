import json

from knowledge_bank.artifact import Artifact

from llm.models.request import LLMRequest
from qabrain.brain_stage import BrainStage


SYSTEM_PROMPT = """
You are an expert QA Engineer.

You are given structured business knowledge.

Your responsibility is to discover business features.

A feature represents a major functional area of the application.

Rules

- Discover only features supported by the supplied knowledge.
- Do not invent features.
- Do not generate capabilities.
- Do not generate business rules.
- Do not generate workflows.
- Do not generate test cases.
- Remove duplicates.

Return ONLY valid JSON.

Format

{
    "features": [
        {
            "name": "",
            "description": ""
        }
    ]
}
"""


class FeatureDiscovery(BrainStage):

    def stage_name(self):

        return "Features"

    def execute(
        self,
        knowledge: Artifact,
    ):

        request = LLMRequest(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"""
Business Knowledge

{json.dumps(knowledge.data, indent=4)}

Return ONLY valid JSON.
""",
        )

        response = self.llm_service.generate(
            request,
        )

        return json.loads(
            response.content,
        )

    # --------------------------------------------------
    # Quality Gate
    # --------------------------------------------------

    def validate(
        self,
        output,
    ) -> float:

        features = output.get(
            "features",
            [],
        )

        if not features:
            return 0.0

        return 1.0