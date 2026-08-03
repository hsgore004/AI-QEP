from knowledge_bank.knowledge_bank import KnowledgeBank

from qabrain.knowledge_builder import KnowledgeBuilder
from qabrain.module_discovery import ModuleDiscovery
from qabrain.entity_discovery import EntityDiscovery
from qabrain.capability_discovery import CapabilityDiscovery
from qabrain.scenario_discovery import ScenarioDiscovery


class QABrain:
    """
    AI-QEP Quality Intelligence Engine

        Documentation
                │
                ▼
        Knowledge Builder
                │
        ┌───────┼────────┬────────────┐
        ▼       ▼        ▼            ▼
    Modules  Entities  Capabilities  Scenarios
    """

    def __init__(
        self,
        llm_service,
    ):

        self.knowledge_bank = KnowledgeBank()

        self.knowledge_builder = KnowledgeBuilder(
            llm_service,
            self.knowledge_bank,
        )

        self.module_discovery = ModuleDiscovery(
            llm_service,
            self.knowledge_bank,
        )

        self.entity_discovery = EntityDiscovery(
            llm_service,
            self.knowledge_bank,
        )

        self.capability_discovery = CapabilityDiscovery(
            llm_service,
            self.knowledge_bank,
        )

        self.scenario_discovery = ScenarioDiscovery(
            llm_service,
            self.knowledge_bank,
        )

    # --------------------------------------------------
    # Learn Application
    # --------------------------------------------------

    def learn(
        self,
        documentation: str,
    ):

        print("\n" + "=" * 80)
        print("AI-QEP QA BRAIN")
        print("=" * 80)

        # --------------------------------------------------
        # Knowledge
        # --------------------------------------------------

        knowledge = self.knowledge_builder.run(
            documentation,
        )

        # --------------------------------------------------
        # Independent Reasoning
        # --------------------------------------------------

        modules = self.module_discovery.run(
            knowledge,
        )

        entities = self.entity_discovery.run(
            knowledge,
        )

        capabilities = self.capability_discovery.run(
            knowledge,
        )

        scenarios = self.scenario_discovery.run(
            knowledge,
        )

        print("\n" + "=" * 80)
        print("QA BRAIN COMPLETED")
        print("=" * 80)

        return {
            "knowledge": knowledge,
            "modules": modules,
            "entities": entities,
            "capabilities": capabilities,
            "scenarios": scenarios,
        }