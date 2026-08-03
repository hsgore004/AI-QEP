from config import settings

from llm.providers.openai_provider import OpenAIProvider
from llm.service import LLMService

from openai import OpenAI

from loaders.documentation_loader import DocumentationLoader
from qabrain.qa_brain import QABrain


def main():

    print("=" * 80)
    print("AI-QEP QA BRAIN TEST")
    print("=" * 80)

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
    # Documentation
    # --------------------------------------------------

    loader = DocumentationLoader()

    documentation = loader.load(
        "https://docs.inventree.org/en/stable/part/"
    )

    # --------------------------------------------------
    # QA Brain
    # --------------------------------------------------

    brain = QABrain(
        llm_service,
    )

    result = brain.learn(
        documentation,
    )

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    print("\n" + "=" * 80)
    print("QA BRAIN OUTPUT")
    print("=" * 80)

    # --------------------------------------------------
    # Modules
    # --------------------------------------------------

    print("\nMODULES")
    print("-" * 80)

    for module in result["modules"].data.get("modules", []):
        print(f"• {module['name']}")

    # --------------------------------------------------
    # Entities
    # --------------------------------------------------

    print("\nENTITIES")
    print("-" * 80)

    for entity in result["entities"].data.get("entities", []):
        print(f"• {entity['name']}")

    # --------------------------------------------------
    # Capabilities
    # --------------------------------------------------

    print("\nCAPABILITIES")
    print("-" * 80)

    for capability in result["capabilities"].data.get("capabilities", []):
        print(f"• {capability['name']}")

    # --------------------------------------------------
    # Scenarios
    # --------------------------------------------------

    print("\nSCENARIOS")
    print("-" * 80)

    for scenario in result["scenarios"].data.get("scenarios", []):

        print(f"[{scenario['id']}] {scenario['title']}")

        print(f"    Objective : {scenario['objective']}")

        print(f"    Priority  : {scenario['priority']}")

        print()


if __name__ == "__main__":
    main()