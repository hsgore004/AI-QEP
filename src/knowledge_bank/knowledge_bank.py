from pathlib import Path

from knowledge_bank.artifact import Artifact
from knowledge_bank.artifact_store import ArtifactStore


class KnowledgeBank:
    """
    Central repository for all QA Brain knowledge.

    Responsibilities

    - Store artifacts
    - Retrieve artifacts
    - Maintain history
    - Provide latest knowledge

    Future

    - Vector Search
    - RAG
    - Semantic Search
    - Similarity Search
    """

    def __init__(
        self,
        root: str = ".artifacts",
    ):

        self.store = ArtifactStore(
            root=root,
        )

    # --------------------------------------------------
    # Store
    # --------------------------------------------------

    def save(
        self,
        artifact: Artifact,
    ):

        return self.store.save(
            artifact,
        )

    # --------------------------------------------------
    # Load
    # --------------------------------------------------

    def load(
        self,
        path: str,
    ):

        return self.store.load(
            path,
        )

    # --------------------------------------------------
    # Latest Artifact
    # --------------------------------------------------

    def latest(
        self,
        stage: str,
    ):

        folder = (
            self.store.root /
            stage.lower()
        )

        if not folder.exists():
            return None

        files = sorted(
            folder.glob("*.json"),
            key=lambda x: x.stat().st_mtime,
        )

        if not files:
            return None

        return self.load(
            str(files[-1]),
        )

    # --------------------------------------------------
    # History
    # --------------------------------------------------

    def history(
        self,
        stage: str,
    ):

        folder = (
            self.store.root /
            stage.lower()
        )

        if not folder.exists():
            return []

        history = []

        for file in sorted(
            folder.glob("*.json")
        ):

            history.append(
                self.load(
                    str(file),
                )
            )

        return history