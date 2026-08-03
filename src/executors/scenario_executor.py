import json

from executors.business_executor import BusinessExecutor
from agents.business_planner_agent import BusinessPlannerAgent


class ScenarioExecutor:

    def __init__(
        self,
        business_executor: BusinessExecutor,
        business_planner: BusinessPlannerAgent,
    ):
        self.business_executor = business_executor
        self.business_planner = business_planner

    async def execute(
        self,
        scenario,
    ):

        # --------------------------------------------------
        # Support both:
        # 1. Plain string
        # 2. QA Brain scenario object
        # --------------------------------------------------

        if isinstance(scenario, str):

            business_goal = scenario

        else:

            business_goal = scenario["title"]

        print("\n" + "=" * 70)
        print("BUSINESS GOAL")
        print("=" * 70)
        print(business_goal)

        plan = self.business_planner.create_plan(
            business_goal,
        )

        print("\n" + "=" * 70)
        print("BUSINESS PLAN")
        print("=" * 70)

        for index, step in enumerate(plan, start=1):
            print(f"{index}. {step}")

        total_steps = len(plan)

        for index, step in enumerate(plan, start=1):

            print("\n" + "-" * 70)
            print(f"STEP {index}/{total_steps}")
            print("-" * 70)
            print(step)

            await self.business_executor.execute(
                step,
            )

        print("\n" + "=" * 70)
        print("[OK] BUSINESS SCENARIO COMPLETED")
        print("=" * 70)