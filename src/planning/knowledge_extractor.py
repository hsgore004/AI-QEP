from planning.llm_chunk_extractor import (
    LLMChunkExtractor,
)


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


class KnowledgeExtractor(
    LLMChunkExtractor,
):
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
    # System Prompt
    # --------------------------------------------------

    def system_prompt(
        self,
    ):

        return SYSTEM_PROMPT

    # --------------------------------------------------
    # Output Field
    # --------------------------------------------------

    def output_field(
        self,
    ):

        return "knowledge"

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

        field = self.output_field()

        if field not in response:

            raise RuntimeError(
                f"Missing '{field}' object."
            )

        knowledge = response[
            field
        ]

        if not isinstance(
            knowledge,
            dict,
        ):

            raise RuntimeError(
                f"'{field}' must be an object."
            )

        #
        # Allow the LLM to omit empty sections.
        #

        knowledge.setdefault(
            "facts",
            [],
        )

        knowledge.setdefault(
            "definitions",
            [],
        )

        knowledge.setdefault(
            "business_rules",
            [],
        )

        for item in (

            "facts",

            "definitions",

            "business_rules",

        ):

            if not isinstance(
                knowledge[item],
                list,
            ):

                raise RuntimeError(
                    f"'{item}' must be a list."
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
    # Stage Name
    # --------------------------------------------------

    def stage_name(
        self,
    ):

        return "Knowledge Extractor"