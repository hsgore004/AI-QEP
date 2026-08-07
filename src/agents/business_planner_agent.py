import json

from llm.models.request import LLMRequest
from llm.service import LLMService

from prompts.generation.test_case_generation_prompt import SYSTEM_PROMPT


class BusinessPlannerAgent:

    def __init__(
        self,
        llm_service: LLMService,
    ):
        self.llm_service = llm_service

    async def create_plan(
        self,
        business_goal: str,
    ):

        request = LLMRequest(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"""
Generate executable business test cases.

Application:
InvenTree

Business Goal:
{business_goal}

Instructions:

- Generate the smallest possible executable test case.
- Each test step must perform exactly ONE browser-level action.
- Every action must be immediately followed by its own implicit validation step.
- Do not combine multiple actions into one step.
- Do not skip navigation steps.
- Do not skip page transitions.
- Do not skip dialog transitions.
- When a page or dialog is expected to appear, generate a dedicated wait step.
- When navigating inside the application, generate every intermediate navigation action required to reach the destination.
- Never assume that a page or dialog is already open.

--------------------------------------------------
FORM HANDLING
--------------------------------------------------

If a form contains multiple mandatory fields:

1. Generate ONE ACTION step:

   Populate all mandatory fields with valid business data.

2. If the form contains an action button such as:

   - Login
   - Sign In
   - Save
   - Submit
   - Create
   - Add
   - Register
   - Continue
   - Next
   - Finish
   - Update
   - Apply

   generate a separate ACTION step to click that button.

3. If clicking the button causes navigation, page transition or dialog transition,
   generate ONE WAIT step.

4. Generate ONE VERIFY step that validates the final business outcome.

Examples:

Login
------
Populate login credentials.
Click Login button.
Wait until Dashboard is displayed.
Verify Dashboard is displayed.

Create Part
-----------
Populate all mandatory Part details.
Click Create button.
Wait until Part Details page is displayed.
Verify Part was created.

Never generate verification steps that only confirm
that form fields have been populated.

Never generate verification steps such as:

- Verify all mandatory fields are populated.
- Verify textbox values.
- Verify button was clicked.

These are handled automatically by the execution layer.

--------------------------------------------------
GENERAL RULES
--------------------------------------------------

- Do not mention browser tools.
- Do not mention Playwright.
- Do not mention MCP.
- Return ONLY valid JSON.
""",
    response_format="json"
        )

        response = await self.llm_service.generate(
            request,
        )

        plan = json.loads(response.content)

        if "steps" in plan:
            return plan

        raise ValueError(
            f"Unexpected planner response: {plan}"
        )