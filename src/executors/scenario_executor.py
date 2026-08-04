import json

from executors.business_executor import BusinessExecutor
from agents.business_planner_agent import BusinessPlannerAgent
from executors.sync_executor import SyncExecutor
from utils.logger import Logger

class ScenarioExecutor:

    def __init__(
        self,
        business_executor: BusinessExecutor,
        business_planner: BusinessPlannerAgent,
    ):
        self.business_executor = business_executor
        self.business_planner = business_planner

        self.sync_executor = SyncExecutor(
            business_executor.client,
        )

    async def execute(
        self,
        scenario,
    ):


        import asyncio

        print(f"\nScenario START task={id(asyncio.current_task())}")

        # --------------------------------------------------
        # Support both:
        # 1. Plain string
        # 2. QA Brain scenario object
        # --------------------------------------------------

        if isinstance(scenario, str):
            business_goal = scenario
        else:
            business_goal = scenario["title"]

        print("========== SCENARIO ENTRY ==========")
        print("session =", self.business_executor.client.session)
        print("dispatcher =", self.business_executor.client.session._dispatcher)

        Logger.section("Business Goal")
        Logger.text(business_goal)

        # --------------------------------------------------
        # Generate Test Case
        # --------------------------------------------------

        test_case = await self.business_planner.create_plan(
            business_goal,
        )

        Logger.section("Generated Test Case")
        Logger.json(test_case)

        steps = test_case["steps"]
        total_steps = len(steps)

        # --------------------------------------------------
        # Execute Test Case
        # --------------------------------------------------

        for item in steps:

            Logger.section(f"Step {item['step']}/{total_steps}")
            Logger.text(item["description"])

            step_type = item["type"].upper()

            if step_type == "ACTION":

                previous_step = None
                next_step = None

                index = item["step"] - 1

                if index > 0:
                    previous_step = steps[index - 1]["description"]

                if index < len(steps) - 1:
                    next_step = steps[index + 1]["description"]
                print("\n========== BEFORE BUSINESS EXECUTOR ==========")
                print(self.business_executor.client.session)
                await self.business_executor.execute(
                    keyword=item["description"],
                    previous_step=previous_step,
                    next_step=next_step,
                    expected_result=item.get("expected_result"),
                )
                print("\n========== AFTER BUSINESS EXECUTOR ==========")
                print(self.business_executor.client.session)
            elif step_type == "SYNC":

                await self.sync_executor.execute(
                    item["description"],
                )

            elif step_type == "VERIFY":

                previous_step = None
                next_step = None

                index = item["step"] - 1

                if index > 0:
                    previous_step = steps[index - 1]["description"]

                if index < len(steps) - 1:
                    next_step = steps[index + 1]["description"]
                print("\n========== AFTER BUSINESS EXECUTOR ==========")
                print(self.business_executor.client.session)
                await self.business_executor.execute(
                    keyword=item["description"],
                    previous_step=previous_step,
                    next_step=next_step,
                    expected_result=item.get("expected_result"),
                )
                print("\n========== AFTER BUSINESS EXECUTOR ==========")
                print(self.business_executor.client.session)
            else:

                raise Exception(
                    f"Unknown step type: {step_type}"
                )

        Logger.section("Business Scenario Completed")
        print(
        f"\nScenarioExecutor END "
        f"id={id(asyncio.current_task())}"
        )