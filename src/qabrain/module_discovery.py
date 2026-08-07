import json

from knowledge_bank.artifact import Artifact

from llm.models.request import LLMRequest
from qabrain.brain_stage import BrainStage


SYSTEM_PROMPT = """
You are an expert Enterprise QA Architect.

You are given structured business knowledge.

Your responsibility is to discover application modules.

A module is a top-level business area of the application.

Examples

Inventory
Sales
Orders
Manufacturing
Administration

Rules

- Discover ONLY modules explicitly supported by the supplied knowledge.
- Do NOT invent modules.
- Do NOT generate entities.
- Do NOT generate capabilities.
- Do NOT generate workflows.
- Do NOT generate scenarios.
- Remove duplicates.

Return ONLY valid JSON.

Format

{
    "modules": [
        {
            "name": "",
            "description": ""
        }
    ]
}
"""


class ModuleDiscovery(BrainStage):

    def stage_name(self):

        return "Modules"

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

        modules = output.get(
            "modules",
            [],
        )

        if not modules:
            return 0.0

        return 1.0