import json

from knowledge_bank.artifact import Artifact

from llm.models.request import LLMRequest
from qabrain.brain_stage import BrainStage


SYSTEM_PROMPT = """
You are an expert QA Engineer.

You are given structured business knowledge.

Your responsibility is to discover business capabilities.

A capability is something that a business user can accomplish using the application.

Examples

- Create Part
- Edit Part
- Delete Part
- Archive Part

Rules

- Discover only capabilities supported by the supplied knowledge.
- Do not invent capabilities.
- Do not generate browser actions.
- Do not generate automation steps.
- Do not generate test cases.
- Remove duplicates.

Return ONLY valid JSON.

Format

{
    "capabilities": [
        {
            "name": "",
            "description": ""
        }
    ]
}
"""


class CapabilityDiscovery(BrainStage):

    def stage_name(self):

        return "Capabilities"

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

        capabilities = output.get(
            "capabilities",
            [],
        )

        if not capabilities:
            return 0.0

        return 1.0