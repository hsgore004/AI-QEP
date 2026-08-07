import json
from pathlib import Path

from config import settings


class ExecutionRunner:

    # --------------------------------------------------
    # Constructor
    # --------------------------------------------------

    def __init__(
        self,
        scenario_executor,
        business_executor,
    ):

        self.scenario_executor = scenario_executor
        self.business_executor = business_executor
    # --------------------------------------------------
    # Execute
    # --------------------------------------------------

    async def execute(
        self,
        output_dir,
    ):

        #
        # Determine input file
        #

        if settings.TEST_CASE_FILE is None:

            test_case_file = (
                Path(output_dir)
                / "test_cases.json"
            )

        else:

            test_case_file = Path(
                settings.TEST_CASE_FILE,
            )

        print()
        print("=" * 80)
        print("EXECUTION RUNNER")
        print("=" * 80)
        print(f"Input File : {test_case_file}")
        print(f"TC Count   : {settings.TC_COUNT_TO_EXECUTE}")

        data = json.loads(

            test_case_file.read_text(
                encoding="utf-8",
            )

        )

        #
        # Collect test cases
        #

        test_cases = []

        for page in data.get(
            "pages",
            [],
        ):

            for chunk in page.get(
                "chunks",
                [],
            ):

                for test_case in chunk.get(
                    "test_cases",
                    [],
                ):

                    test_cases.append(
                        test_case,
                    )

        #
        # Limit execution count
        #

        if settings.TC_COUNT_TO_EXECUTE is not None:

            test_cases = test_cases[
                :settings.TC_COUNT_TO_EXECUTE
            ]

        print(
            f"Test Cases Selected : {len(test_cases)}"
        )

        #
        # Open Playwright MCP session
        #

        business_executor = (
            self.scenario_executor.business_executor
        )

        async with business_executor.client:

            business_executor.tool_catalog = (

                await business_executor.client.get_tool_catalog()

            )

            await business_executor.client.call_tool(

                "browser_close",

                {},

            )   


            #
            # Login
            #

            print()
            print("=" * 80)
            print("LOGIN")
            print("=" * 80)

            await self.business_executor.execute(
                "Open Login Page",
            )

            await self.scenario_executor.execute(
                "Login as admin",
            )

            print("[OK] Login completed")


            #
            # Execute test cases
            #

            for index, test_case in enumerate(

                test_cases,

                start=1,

            ):

                print()
                print("=" * 80)

                print(
                    f"Executing Test Case "
                    f"{index}/{len(test_cases)}"
                )

                print(
                    test_case.get(
                        "title",
                        "",
                    )
                )

                print("=" * 80)

                try:

                    await self.scenario_executor.execute(

                        test_case,

                    )

                    print(
                        "[PASS]"
                    )

                except Exception as ex:

                    print(
                        f"[FAIL] {ex}"
                    )

                    #
                    # Continue with next test case
                    #
                    continue

        print()
        print("=" * 80)
        print("EXECUTION COMPLETED")
        print("=" * 80)