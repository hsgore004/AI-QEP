from planning.llm_chunk_extractor import (
    LLMChunkExtractor,
)


SYSTEM_PROMPT = """
You are a Senior QA Architect.

You are given:

1. Documentation
2. Extracted business knowledge
3. Business entities

Your responsibility is to generate comprehensive executable manual test cases.

Use only the supplied documentation.

Do not invent application features.

Generate test cases that cover:

- Functional behaviour
- Business rules
- Positive scenarios
- Negative scenarios
- User validations
- Boundary conditions where applicable

Each test case must be directly executable.

Rules

- Every test case must contain executable steps.
- Every step must be one of:
    ACTION
    VERIFY
    SYNC
- ACTION performs a user action.
- VERIFY validates the UI or business outcome.
- SYNC is used only when waiting is required.
- VERIFY steps MUST contain "expected_result".
- ACTION steps MUST NOT contain "expected_result".
- Number steps sequentially starting from 1.

==================================================
EXECUTION REQUIREMENTS
==================================================

The generated test case will be executed directly by an autonomous execution engine.

Therefore every test case MUST contain executable business steps.

Rules:

1. Every step must represent exactly ONE business action.

2. Never combine multiple actions.

3. Never skip intermediate navigation.

4. Never assume a page or dialog is already open.

5. If a business function requires navigating through multiple pages, generate every intermediate business destination.

6. If a form must be completed:

   - Populate all mandatory fields.
   - Click the appropriate action button.
   - Verify the final business outcome.

7. Do NOT generate generic steps such as:

   - Create Part
   - Fill Details
   - Submit Form

Instead generate executable business steps such as:

- Navigate to Parts
- Open Create Part page
- Populate all mandatory Part details
- Click Create button
- Verify Part was created


Return ONLY valid JSON.

Format

{
    "test_cases": [

        {

            "id": "TC-001",

            "title": "",

            "objective": "",

            "preconditions": [],

            "priority": "High",

            "steps": [

                {

                    "step": 1,

                    "type": "ACTION",

                    "description": ""

                },

                {

                    "step": 2,

                    "type": "VERIFY",

                    "description": "",

                    "expected_result": ""

                }

            ]

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

        response.setdefault(
            "test_cases",
            [],
        )

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
                "priority",
                "Medium",
            )

            test_case.setdefault(
                "steps",
                [],
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

            for step in test_case["steps"]:

                if not isinstance(
                    step,
                    dict,
                ):

                    raise RuntimeError(
                        "Each step must be an object."
                    )

                step.setdefault(
                    "step",
                    1,
                )

                step.setdefault(
                    "type",
                    "ACTION",
                )

                step.setdefault(
                    "description",
                    "",
                )

                if step["type"] not in (

                    "ACTION",

                    "VERIFY",

                    "SYNC",

                ):

                    raise RuntimeError(
                        f"Invalid step type: {step['type']}"
                    )

                if step["type"] == "VERIFY":

                    step.setdefault(
                        "expected_result",
                        "",
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

==================================================
APPLICATION DOCUMENTATION
==================================================

Chunk ID
--------
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

==================================================
EXTRACTED KNOWLEDGE
==================================================

{chunk.get("knowledge", {})}

==================================================
BUSINESS ENTITIES
==================================================

{chunk.get("entities", {})}

==================================================
TEST CASE GENERATION REQUIREMENTS
==================================================

Generate comprehensive executable manual test cases.

The documentation above is the ONLY source of truth.

Use the documentation to understand:

- application navigation
- menus
- pages
- dialogs
- business workflows
- business rules
- validations
- relationships between pages
- relationships between business entities

Never invent application behaviour.

Never invent navigation.

Never assume shortcuts.

If the documentation describes intermediate navigation,
generate those navigation steps.

Example

Documentation

Parts
    ->
Create Part

Generate

- Navigate to Parts
- Open Create Part page

Do NOT generate

- Navigate directly to Create Part page

unless the documentation explicitly supports direct navigation.

==================================================
TEST CASE REQUIREMENTS
==================================================

Generate:

- Positive scenarios
- Negative scenarios
- Validation scenarios
- Business rule scenarios
- End-to-end business workflows

Every generated test case must be executable.

Every step must represent ONE business action.

Never combine multiple business actions into one step.

Never skip:

- navigation
- intermediate pages
- dialogs
- workflow transitions

When a form is encountered:

- Populate all mandatory fields.
- Click the appropriate business action.
- Verify the final business outcome.

Do not generate execution-engine checks such as:

- Verify textbox populated
- Verify button clicked
- Verify dialog opened

Those are handled by the execution engine.

Generate realistic business workflows based only on the supplied documentation.

Return ONLY valid JSON.
"""

    # --------------------------------------------------
    # Stage Name
    # --------------------------------------------------

    def stage_name(
        self,
    ):

        return "Test Case Generator"