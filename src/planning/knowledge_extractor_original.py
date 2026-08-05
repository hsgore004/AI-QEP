import json

from llm.models.request import LLMRequest


SYSTEM_PROMPT = """
You are a Senior Software Architect, Business Analyst and QA Architect.

You are given a single documentation chunk extracted from an application's
official documentation.

Your responsibility is ONLY to enrich this chunk with structured business
knowledge.

Never summarize.

Never rewrite the documentation.

Never modify the supplied text.

Never infer information that is not explicitly supported.

Never invent business rules.

The original documentation will always be preserved.

You must only identify knowledge explicitly present inside the supplied chunk.

------------------------------------------------------------
Extract
------------------------------------------------------------

1. Facts

Business facts explicitly stated.

Example

A Part may have Supplier Parts.

------------------------------------------------------------

2. Definitions

Definitions of business concepts.

Example

A Template Part is a reusable definition.

------------------------------------------------------------

3. Business Rules

Explicit rules or restrictions.

Example

A serial number must be unique.

------------------------------------------------------------

Return ONLY valid JSON.

Format

{
    "knowledge": {

        "facts": [],

        "definitions": [],

        "business_rules": []

    }

}
"""


class KnowledgeExtractor:
    """
    Stage 3

    Input

        One QA Knowledge Chunk

    Output

        Same Chunk
            +
        knowledge

    This class NEVER

    - Reads files
    - Writes files
    - Knows about pages
    - Knows about documentation.json

    It enriches ONE chunk only.
    """

    # --------------------------------------------------
    # Constructor
    # --------------------------------------------------

    def __init__(
        self,
        llm_service,
    ):

        self.llm_service = llm_service

    # --------------------------------------------------
    # Extract
    # --------------------------------------------------

    async def extract(
        self,
        chunk,
    ):

        request = LLMRequest(

            system_prompt=SYSTEM_PROMPT,

            user_prompt=self._build_prompt(
                chunk,
            ),

            response_format="json",

        )

        response = await self.llm_service.generate(
            request,
        )

        knowledge = self._parse_response(
            response.content,
        )

        self._validate(
            knowledge,
        )

        enriched_chunk = dict(
            chunk,
        )

        enriched_chunk["knowledge"] = knowledge[
            "knowledge"
        ]

        return enriched_chunk

    # --------------------------------------------------
    # Validate
    # --------------------------------------------------

    def _validate(
        self,
        response,
    ):

        if not isinstance(
            response,
            dict,
        ):

            raise RuntimeError(
                "Knowledge extractor must return JSON."
            )

        if "knowledge" not in response:

            raise RuntimeError(
                "Missing 'knowledge' object."
            )

        knowledge = response[
            "knowledge"
        ]

        if not isinstance(
            knowledge,
            dict,
        ):

            raise RuntimeError(
                "'knowledge' must be an object."
            )

        for field in (

            "facts",

            "definitions",

            "business_rules",

        ):

            # if field not in knowledge:

            #     raise RuntimeError(
            #         f"Missing '{field}'."
            #     )

            knowledge.setdefault("facts", [])
            knowledge.setdefault("definitions", [])
            knowledge.setdefault("business_rules", [])

            if not isinstance(
                knowledge[field],
                list,
            ):

                raise RuntimeError(
                    f"'{field}' must be a list."
                )

        return True

# --------------------------------------------------
# Part 1 ends here
# --------------------------------------------------
    # --------------------------------------------------
    # Build Prompt
    # --------------------------------------------------

    def _build_prompt(
        self,
        chunk,
    ):

        return f"""
Documentation Chunk

Chunk ID
---------
{chunk.get("id", "")}

Page Title
----------
{chunk.get("page_title", "")}

Page URL
--------
{chunk.get("page_url", "")}

Heading
-------
{chunk.get("heading", "")}

Heading Level
-------------
{chunk.get("heading_level", "")}

Documentation
-------------
{chunk.get("text", "")}

Remember

- Extract ONLY knowledge explicitly stated.
- Never infer.
- Never summarize.
- Never rewrite.
- Preserve traceability.
- Return ONLY valid JSON.
"""

    # --------------------------------------------------
    # Parse Response
    # --------------------------------------------------

    def _parse_response(
        self,
        response,
    ):

        if not response:

            raise RuntimeError(
                "LLM returned an empty response."
            )

        response = response.strip()

        #
        # Remove Markdown JSON fences
        #

        if response.startswith(
            "```json"
        ):

            response = response[
                len("```json"):
            ]

        if response.startswith(
            "```"
        ):

            response = response[
                len("```"):
            ]

        if response.endswith(
            "```"
        ):

            response = response[:-3]

        response = response.strip()

        try:

            return json.loads(
                response,
            )

        except Exception as ex:

            print()
            print("=" * 80)
            print("INVALID JSON FROM LLM")
            print("=" * 80)
            print(response)
            print("=" * 80)

            raise RuntimeError(
                f"Unable to parse JSON.\n{ex}"
            ) from ex

    # --------------------------------------------------
    # Stage Name
    # --------------------------------------------------

    def stage_name(
        self,
    ):

        return "Knowledge Extractor"