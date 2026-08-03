from abc import ABC, abstractmethod

from knowledge_bank.artifact import Artifact
from knowledge_bank.knowledge_bank import KnowledgeBank


class BrainStage(ABC):
    """
    Base class for every QA Brain stage.

    Every stage follows the same lifecycle.

        Input
          ↓
      Execute
          ↓
     Quality Gate
          ↓
    Create Artifact
          ↓
    Store Artifact
          ↓
        Output
    """

    def __init__(
        self,
        llm_service,
        knowledge_bank: KnowledgeBank,
    ):
        self.llm_service = llm_service
        self.knowledge_bank = knowledge_bank

    # --------------------------------------------------
    # Public Pipeline
    # --------------------------------------------------

    def run(
        self,
        input_data,
    ) -> Artifact:

        print(f"\n[{self.stage_name()}]")

        output = self.execute(
            input_data,
        )

        confidence = self.validate(
            output,
        )

        artifact = Artifact(
            stage=self.stage_name(),
            confidence=confidence,
            approved=confidence >= 0.90,
            data=output,
        )

        self.knowledge_bank.save(
            artifact,
        )

        return artifact

    # --------------------------------------------------
    # Stage implementation
    # --------------------------------------------------

    @abstractmethod
    def stage_name(
        self,
    ) -> str:
        pass

    @abstractmethod
    def execute(
        self,
        input_data,
    ):
        pass

    # --------------------------------------------------
    # Default Quality Gate
    # --------------------------------------------------

    def validate(
        self,
        output,
    ) -> float:
        """
        Default validation.

        Individual stages can override this
        with more sophisticated quality gates.
        """

        if output:
            return 1.0

        return 0.0