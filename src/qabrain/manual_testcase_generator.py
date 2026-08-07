import json
from pathlib import Path

from llm.models.request import LLMRequest


class ManualTestCaseGenerator:
    """
    Generates hierarchical Manual UI Test Cases from qa_brain.json.

    Flow

        qa_brain.json

            Module

                Feature

                    Pages

                        Chunks

                            ↓

                    LLM

                            ↓

                Test Cases

            ↓

        manual_testcases.json
    """

    # --------------------------------------------------

    def __init__(
        self,
        llm_service,
    ):

        self.llm_service = llm_service

    # --------------------------------------------------
    # Public
    # --------------------------------------------------

    async def generate(
        self,
        qa_brain_file,
        output_file,
    ):

        qa_brain_file = Path(
            qa_brain_file,
        )

        output_file = Path(
            output_file,
        )

        print("\n" + "=" * 80)
        print("MANUAL TEST CASE GENERATOR")
        print("=" * 80)

        print(
            f"Reading : {qa_brain_file}"
        )

        qa_brain = json.loads(
            qa_brain_file.read_text(
                encoding="utf-8",
            )
        )

        output = {

            "modules": []

        }

        testcase_counter = 1

        for module in qa_brain["modules"]:

            print()
            print("=" * 80)
            print(
                f"MODULE : {module['name']}"
            )
            print("=" * 80)

            module_output = {

                "name": module["name"],

                "features": []

            }

            for feature in module["features"]:

                print(
                    f"Generating : {feature['name']}"
                )

                generated = await self._generate_feature(
                    module["name"],
                    feature,
                )

                #
                # Stable IDs
                #

                for tc in generated:

                    tc["id"] = (
                        f"TC-{testcase_counter:05d}"
                    )

                    testcase_counter += 1

                feature_output = {

                    "name": feature["name"],

                    "pages": feature["pages"],

                    "test_cases": generated,

                }

                module_output["features"].append(
                    feature_output,
                )

            output["modules"].append(
                module_output,
            )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file.write_text(

            json.dumps(
                output,
                indent=2,
                ensure_ascii=False,
            ),

            encoding="utf-8",

        )

        print()
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)

        print(
            f"Modules : {len(output['modules'])}"
        )

        total = sum(
            len(f["test_cases"])
            for m in output["modules"]
            for f in m["features"]
        )

        print(
            f"Generated Test Cases : {total}"
        )

        print(
            f"Saved : {output_file}"
        )

        return output

    # --------------------------------------------------
    # Generate One Feature
    # --------------------------------------------------

    async def _generate_feature(

        self,

        module_name,

        feature,

    ):

        prompt = self._build_prompt(

            module_name,

            feature,

        )

        request = LLMRequest(

            system_prompt=self._system_prompt(),

            user_prompt=prompt,

        )

        response = await self.llm_service.generate(
            request,
        )

        return self._parse_response(
            response.content,
        )

    # --------------------------------------------------
    # System Prompt
    # --------------------------------------------------

    def _system_prompt(
        self,
    ):

        return """
You are a Principal QA Architect specializing in documentation-driven test design.

Your task is to convert software documentation into exhaustive manual UI test cases.

Your responsibility is to completely analyze the supplied documentation before generating any test cases.

Internally perform the following analysis:

1. Read every documentation section.
2. Identify every user workflow.
3. Identify every UI page involved.
4. Identify every user action.
5. Identify every field, button, dialog, table, tab and control.
6. Identify every business rule.
7. Identify every validation rule.
8. Identify every navigation path.
9. Identify every confirmation dialog.
10. Identify every warning or error message.
11. Identify every documented note or restriction.
12. Identify every precondition.

After completing the analysis, generate manual UI test cases.

Generate test cases only for functionality explicitly described in the documentation.

Do NOT invent functionality.

Generate scenarios including, where applicable:

- Positive scenarios
- Negative scenarios
- Validation scenarios
- Navigation scenarios
- Business rule scenarios
- Error handling scenarios
- Confirmation dialog scenarios
- Permission scenarios (only if documented)
- Configuration scenarios (only if documented)

Requirements:

- Every documented workflow should have at least one corresponding test case.
- Every test case must be traceable to the supplied documentation.
- Populate source_chunk_ids.
- Populate source_urls.
- Each test step must contain exactly ONE user action.
- Each test step must contain exactly ONE verification.
- Never combine multiple user actions into one step.
- Never combine multiple verifications into one step.
- Avoid duplicate test cases.
- Return ONLY valid JSON.
- Do not include explanations outside the JSON.
"""

    # --------------------------------------------------
    # Prompt
    # --------------------------------------------------

    def _build_prompt(

        self,

        module_name,

        feature,

    ):

        pages = []

        for page in feature["pages"]:

            pages.append(

                {

                    "title": page["title"],

                    "url": page["url"],

                    "documentation": [

                        {

                            "chunk_id": chunk["id"],

                            "section": chunk["section_title"],

                            "content": chunk["text"],

                        }

                        for chunk in page["chunks"]

                    ],

                }

            )

        prompt = {

            "module": module_name,

            "feature": feature["name"],

            "documentation": pages,

            "instructions": [

    "STEP 1 - Read every documentation section carefully.",

    "STEP 2 - Identify every documented feature.",

    "STEP 3 - Identify every user workflow.",

    "STEP 4 - Identify every UI page involved in each workflow.",

    "STEP 5 - Identify every field, control, table, dialog and button mentioned.",

    "STEP 6 - Identify every business rule explicitly documented.",

    "STEP 7 - Identify every validation rule.",

    "STEP 8 - Identify every documented success flow.",

    "STEP 9 - Identify every documented error flow.",

    "STEP 10 - Generate exhaustive manual UI test cases.",

    "Generate positive scenarios.",

    "Generate negative scenarios.",

    "Generate validation scenarios.",

    "Generate navigation scenarios.",

    "Generate business rule scenarios.",

    "Generate confirmation dialog scenarios.",

    "Generate permission scenarios if documentation mentions roles.",

    "Generate boundary scenarios only if documentation supports them.",

    "Do not invent functionality.",

    "Every generated test case must reference source chunk ids.",

    "Each test step must contain exactly ONE action.",

    "Each test step must contain exactly ONE verification.",

    "Return valid JSON only."
]

            

        }

        return json.dumps(

            prompt,

            indent=2,

            ensure_ascii=False,

        )

    # --------------------------------------------------
    # Parse LLM Response
    # --------------------------------------------------

    def _parse_response(
        self,
        response_text,
    ):

        if not response_text:

            return []

        response_text = response_text.strip()

        #
        # Remove markdown fences if present
        #

        if response_text.startswith("```json"):

            response_text = response_text.replace(
                "```json",
                "",
                1,
            )

        if response_text.startswith("```"):

            response_text = response_text.replace(
                "```",
                "",
                1,
            )

        if response_text.endswith("```"):

            response_text = response_text[:-3]

        response_text = response_text.strip()

        #
        # Parse JSON
        #

        try:

            data = json.loads(
                response_text,
            )

        except Exception as ex:

            print()

            print("=" * 80)
            print("FAILED TO PARSE LLM RESPONSE")
            print("=" * 80)

            print(ex)

            return []

        #
        # Validate root
        #

        if not isinstance(
            data,
            dict,
        ):

            return []

        testcases = data.get(
            "test_cases",
            [],
        )

        if not isinstance(
            testcases,
            list,
        ):

            return []

        normalized = []

        for testcase in testcases:

            if not isinstance(
                testcase,
                dict,
            ):
                continue

            normalized.append(

                {

                    "id": "",

                    "title": testcase.get(
                        "title",
                        "",
                    ),

                    "priority": testcase.get(
                        "priority",
                        "Medium",
                    ),

                    "preconditions": testcase.get(
                        "preconditions",
                        [],
                    ),

                    "steps": self._normalize_steps(

                        testcase.get(
                            "steps",
                            [],
                        )

                    ),

                    "expected_result": testcase.get(
                        "expected_result",
                        "",
                    ),

                    "source_chunk_ids": testcase.get(
                        "source_chunk_ids",
                        [],
                    ),

                    "source_urls": testcase.get(
                        "source_urls",
                        [],
                    ),

                }

            )

        return normalized

    # --------------------------------------------------
    # Normalize Steps
    # --------------------------------------------------

    def _normalize_steps(
        self,
        steps,
    ):

        if not isinstance(
            steps,
            list,
        ):

            return []

        normalized = []

        step_number = 1

        for step in steps:

            if not isinstance(
                step,
                dict,
            ):
                continue

            action = str(

                step.get(
                    "action",
                    "",
                )

            ).strip()

            verification = str(

                step.get(
                    "verification",
                    "",
                )

            ).strip()

            if not action:
                continue

            normalized.append(

                {

                    "step": step_number,

                    "action": action,

                    "verification": verification,

                }

            )

            step_number += 1

        return normalized