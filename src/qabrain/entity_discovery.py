import json

from knowledge_bank.artifact import Artifact

from llm.models.request import LLMRequest
from qabrain.brain_stage import BrainStage


SYSTEM_PROMPT = """
You are an expert QA Engineer.

You are given structured business knowledge.

Your responsibility is to discover the business entities.

A business entity is something that stores business information and participates
in one or more business processes.

Rules

- Discover only entities supported by the supplied knowledge.
- Do not invent entities.
- Ignore UI controls.
- Ignore buttons.
- Ignore menus.
- Ignore browser concepts.
- Ignore workflows.
- Remove duplicates.

Return ONLY valid JSON.

Format

{
    "entities": [
        {
            "name": "",
            "description": ""
        }
    ]
}
"""


class EntityDiscovery(BrainStage):

    def stage_name(self):

        return "Entities"

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

        entities = output.get(
            "entities",
            [],
        )

        if not entities:
            return 0.0

        return 1.0