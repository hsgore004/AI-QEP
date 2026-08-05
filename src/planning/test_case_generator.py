from planning.llm_chunk_extractor import (
    LLMChunkExtractor,
)


SYSTEM_PROMPT = """
You are a Senior QA Architect.

You are given:

1. Documentation
2. Extracted business knowledge
3. Business entities

Your responsibility is to generate comprehensive manual test cases.

Generate test cases that validate:

- Functional behaviour
- Business rules
- Valid user actions
- Invalid user actions
- Boundary conditions where applicable

Use only the supplied documentation.

Do not invent application features.

Return ONLY valid JSON.

Format

{
    "test_cases": [

        {

            "id": "TC-001",

            "title": "",

            "objective": "",

            "preconditions": [],

            "steps": [],

            "expected_results": [],

            "priority": "High"

        }

    ]
}
"""


class TestCaseGenerator(
    LLMChunkExtractor,
):

    """
    Stage 5

    Input

        One enriched documentation chunk

            Documentation
            +
            Knowledge
            +
            Entities

    Output

        Same chunk

            +

        test_cases
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

        return "test_cases"

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
                "Test Case Generator must return JSON."
            )

        if "test_cases" not in response:

            response["test_cases"] = []

        if not isinstance(
            response["test_cases"],
            list,
        ):

            raise RuntimeError(
                "'test_cases' must be a list."
            )

        for test_case in response["test_cases"]:

            if not isinstance(
                test_case,
                dict,
            ):

                raise RuntimeError(
                    "Each test case must be an object."
                )

            test_case.setdefault(
                "id",
                "",
            )

            test_case.setdefault(
                "title",
                "",
            )

            test_case.setdefault(
                "objective",
                "",
            )

            test_case.setdefault(
                "preconditions",
                [],
            )

            test_case.setdefault(
                "steps",
                [],
            )

            test_case.setdefault(
                "expected_results",
                [],
            )

            test_case.setdefault(
                "priority",
                "Medium",
            )

            if not isinstance(
                test_case["preconditions"],
                list,
            ):

                raise RuntimeError(
                    "'preconditions' must be a list."
                )

            if not isinstance(
                test_case["steps"],
                list,
            ):

                raise RuntimeError(
                    "'steps' must be a list."
                )

            if not isinstance(
                test_case["expected_results"],
                list,
            ):

                raise RuntimeError(
                    "'expected_results' must be a list."
                )

        return True

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

Documentation
-------------
{chunk.get("text", "")}

Knowledge
---------
{chunk.get("knowledge", {})}

Entities
--------
{chunk.get("entities", {})}

Generate comprehensive test cases.

Requirements

- Cover positive scenarios.
- Cover negative scenarios.
- Cover business rules.
- Cover validations.
- Cover important user flows.

Return ONLY valid JSON.
"""

    # --------------------------------------------------
    # Stage Name
    # --------------------------------------------------

    def stage_name(
        self,
    ):

        return "Test Case Generator"