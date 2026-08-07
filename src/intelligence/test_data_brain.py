import json
from intelligence.models.field_metadata import FieldMetadata
from llm.models.request import LLMRequest
from dataclasses import asdict

SYSTEM_PROMPT = """
You are a Senior QA Test Data Engineer.

Your responsibility is to generate ONE valid business value for ONE field.

You are given field metadata.

Generate a realistic value that satisfies the field constraints.

Rules

- Generate only ONE value.
- Respect the field type.
- Respect dropdown options.
- Respect maximum length if provided.
- Respect business context.
- Return ONLY valid JSON.

Format

{
    "value": ""
}
"""


class TestDataBrain:

    def __init__(
        self,
        llm_service,
    ):
        self.llm_service = llm_service

    def generate_value(
        self,
        field_metadata: FieldMetadata,
    ):
        metadata_json = json.dumps(
            asdict(field_metadata),
            indent=4,
        )
        request = LLMRequest(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"""
Field Metadata

{metadata_json}

Generate ONE valid value.

Return ONLY valid JSON.
""",
        )

        response = self.llm_service.generate(
            request,
        )

        result = json.loads(
            response.content,
        )

        return result["value"]