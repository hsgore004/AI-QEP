import json

from llm.models.request import LLMRequest
from qabrain.brain_stage import BrainStage


SYSTEM_PROMPT = """
You are an expert Technical Documentation Analyst.

Your responsibility is to convert application documentation into structured business knowledge.

Extract ONLY facts that are explicitly stated or directly supported by the documentation.

Do NOT infer.
Do NOT summarize.
Do NOT invent.
Do NOT classify beyond what is documented.

This stage builds the Knowledge Base for later reasoning.

Do NOT generate:

- Features
- Capabilities
- Test scenarios
- Test cases
- Browser actions
- Automation
- Recommendations
- Assumptions

Return ONLY valid JSON.

Format

{
    "application": "",
    "module": "",
    "purpose": "",

    "business_objects": [],

    "user_roles": [],

    "business_rules": [],

    "relationships": [],

    "constraints": [],

    "events": [],

    "terminology": {},

    "raw_summary": ""
}
"""


class KnowledgeBuilder(BrainStage):

    def stage_name(self):

        return "Knowledge"

    def execute(
        self,
        documentation: str,
    ):

        request = LLMRequest(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"""
Application Documentation

{documentation}

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

        score = 0.0

        if output.get("application"):
            score += 0.2

        if output.get("purpose"):
            score += 0.2

        if output.get("features"):
            score += 0.2

        if output.get("entities"):
            score += 0.2

        if output.get("workflows"):
            score += 0.2

        return score