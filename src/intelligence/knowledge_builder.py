import json

from llm.models.request import LLMRequest
from llm.service import LLMService


SYSTEM_PROMPT = """
You are a Senior QA Architect.

Your job is to read application documentation and convert it into structured business knowledge.

Extract ONLY business information.

Do NOT generate test cases.

Do NOT generate browser actions.

Do NOT generate automation.

Return ONLY valid JSON.

The JSON schema is:

{
    "application": "",
    "module": "",

    "purpose": "",

    "entities": [],

    "business_rules": [],

    "features": [],

    "capabilities": [],

    "workflows": []
}

Definitions

application
    Name of the application.

module
    Name of the current feature/module.

purpose
    One paragraph describing what this module does.

entities
    Business objects.
    Example:
    Part
    Supplier
    Category

business_rules
    Rules or constraints.
    Example:
    Part Name is mandatory.

features
    Major feature areas.

capabilities
    Things a user can do.

workflows
    End-to-end business workflows.
"""


class KnowledgeBuilder:

    def __init__(
        self,
        llm_service: LLMService,
    ):
        self.llm_service = llm_service

    def build(
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