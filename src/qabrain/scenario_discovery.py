import json

from knowledge_bank.artifact import Artifact

from llm.models.request import LLMRequest
from qabrain.brain_stage import BrainStage


SYSTEM_PROMPT = """
You are a Senior QA Architect.

You are given structured business knowledge about an application.

Your responsibility is to identify the highest value business scenarios.

A business scenario represents a complete business objective that a user wants to accomplish.

A scenario MUST NOT contain:

- Browser actions
- UI steps
- Automation details
- Playwright
- Selenium
- Robot Framework
- Test data
- Assertions

A scenario should describe WHAT the user wants to achieve.

Examples

- Login as administrator
- Create a new Part
- Edit an existing Part
- Archive a Part
- Upload a Part Image
- Import Parts from CSV
- Assign Supplier to Part

Return ONLY valid JSON.

Format

{
    "scenarios": [
        {
            "id": "",
            "title": "",
            "objective": "",
            "priority": "High"
        }
    ]
}
"""


class ScenarioDiscovery(BrainStage):

    def stage_name(self):

        return "Scenarios"

    def execute(
        self,
        knowledge: Artifact,
    ):

        request = LLMRequest(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"""
Business Knowledge

{json.dumps(knowledge.data, indent=4)}

Generate the 10 highest value business scenarios.

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

        scenarios = output.get(
            "scenarios",
            [],
        )

        if len(scenarios) < 5:
            return 0.5

        return 1.0