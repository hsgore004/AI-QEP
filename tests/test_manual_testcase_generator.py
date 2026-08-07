import asyncio

from openai import OpenAI

import config.settings as settings

from llm.providers.openai_provider import OpenAIProvider
from llm.service import LLMService

from qabrain.manual_testcase_generator import (
    ManualTestCaseGenerator,
)


async def main():

    # --------------------------------------------------
    # LLM
    # --------------------------------------------------

    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
    )

    provider = OpenAIProvider(
        client,
    )

    llm_service = LLMService(
        provider,
    )

    # --------------------------------------------------
    # Manual Test Case Generator
    # --------------------------------------------------

    generator = ManualTestCaseGenerator(
        llm_service,
    )

    # --------------------------------------------------
    # Generate Manual Test Cases
    # --------------------------------------------------

    result = await generator.generate(
        qa_brain_file="src/crawl_output/qa_brain.json",
        output_file="src/crawl_output/manual_testcases.json",
    )

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    module_count = len(
        result["modules"]
    )

    feature_count = sum(
        len(module["features"])
        for module in result["modules"]
    )

    testcase_count = sum(
        len(feature["test_cases"])
        for module in result["modules"]
        for feature in module["features"]
    )

    print(
        f"Modules      : {module_count}"
    )

    print(
        f"Features     : {feature_count}"
    )

    print(
        f"Test Cases   : {testcase_count}"
    )


if __name__ == "__main__":
    asyncio.run(main())