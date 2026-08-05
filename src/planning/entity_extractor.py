from planning.llm_chunk_extractor import (
    LLMChunkExtractor,
)


SYSTEM_PROMPT = """
You are a Senior Software Architect, Business Analyst and QA Architect.

You are given a single documentation chunk.

Your responsibility is ONLY to identify business entities explicitly mentioned
inside the supplied documentation.

Never summarize.

Never rewrite.

Never infer.

Never invent entities.

Only identify entities that are explicitly present.

------------------------------------------------------------
Entity Types
------------------------------------------------------------

BusinessEntity

Examples

- Part
- Supplier
- Supplier Part
- Stock Item
- Purchase Order
- Sales Order
- Build Order
- Part Category
- Part Template

------------------------------------------------------------

Return ONLY valid JSON.

Format

{
    "entities": [

        {
            "name": "",
            "type": "",
            "description": ""
        }

    ]

}
"""


class EntityExtractor(
    LLMChunkExtractor,
):
    """
    Stage 4

    Input

        One Knowledge Chunk

    Output

        Same Chunk
            +
        entities
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

        return "entities"

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
                "Entity extractor must return JSON."
            )

        if "entities" not in response:

            raise RuntimeError(
                "Missing 'entities'."
            )

        entities = response["entities"]

        if not isinstance(
            entities,
            list,
        ):

            raise RuntimeError(
                "'entities' must be a list."
            )

        for entity in entities:

            if not isinstance(
                entity,
                dict,
            ):

                raise RuntimeError(
                    "Each entity must be an object."
                )

            entity.setdefault(
                "name",
                "",
            )

            entity.setdefault(
                "type",
                "",
            )

            entity.setdefault(
                "description",
                "",
            )

            if not isinstance(
                entity["name"],
                str,
            ):

                raise RuntimeError(
                    "'name' must be string."
                )

            if not isinstance(
                entity["type"],
                str,
            ):

                raise RuntimeError(
                    "'type' must be string."
                )

            if not isinstance(
                entity["description"],
                str,
            ):

                raise RuntimeError(
                    "'description' must be string."
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

Previously Extracted Knowledge
------------------------------

{chunk.get("knowledge", {})}

Remember

- Identify ONLY explicit business entities.
- Never infer.
- Never invent.
- Never summarize.
- Return ONLY valid JSON.
"""

    # --------------------------------------------------
    # Stage Name
    # --------------------------------------------------

    def stage_name(
        self,
    ):

        return "Entity Extractor"