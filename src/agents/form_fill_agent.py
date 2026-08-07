from llm.models.request import LLMRequest
from llm.service import LLMService

SYSTEM_PROMPT = """
You are an expert AI Form Filling Agent.

Your task is to examine the browser snapshot and generate the exact JSON
required by the Playwright MCP browser_fill_form tool.

Rules:

1. Only use fields visible in the snapshot.

2. Never invent target ids.

3. Preserve the exact target reference.

4. Generate sensible business values.

5. Return ONLY JSON.

Required schema:

{
  "fields":[
    {
      "target":"e123",
      "name":"Name",
      "type":"textbox",
      "value":"Example"
    }
  ]
}

Supported field types

textbox
checkbox
combobox
radio
slider
"""


class FormFillAgent:

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def generate(
        self,
        business_step: str,
        page_snapshot: str,
    ):

        prompt = f"""
Return ONLY valid JSON.

The response MUST be a valid JSON object.

Do not wrap the JSON in markdown.

Do not include explanations.

Do not include any text before or after the JSON.

The response MUST be a JSON object matching this schema:

{{
  "fields": [
    {{
      "target": "e123",
      "name": "Part Name",
      "type": "textbox",
      "value": "Example"
    }}
  ]
}}

Business Step:
{business_step}

Browser Snapshot:
{page_snapshot}
"""

        request = LLMRequest(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=prompt,
            response_format="json",
        )

        response = await self.llm_service.generate(
            request,
        )

        response = response.content
        response = response.replace("```json", "")
        response = response.replace("```", "")
        response = response.strip()

        return response