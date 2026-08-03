import json
from dataclasses import asdict
from pathlib import Path

from knowledge_bank.artifact import Artifact


class ArtifactStore:
    """
    Persists QA Brain artifacts.

    Current implementation:
        JSON files

    Future implementations:
        SQLite
        Vector Database
        Cloud Storage
    """

    def __init__(
        self,
        root: str = ".artifacts",
    ):

        self.root = Path(root)

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    def save(
        self,
        artifact: Artifact,
    ) -> Path:

        stage_folder = (
            self.root /
            artifact.stage.lower()
        )

        stage_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = (
            stage_folder /
            f"v{artifact.version}_{artifact.id}.json"
        )

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                asdict(artifact),
                f,
                indent=4,
                ensure_ascii=False,
            )

        return path

    # --------------------------------------------------
    # Load
    # --------------------------------------------------

    def load(
        self,
        path: str,
    ) -> dict:

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as f:

            return json.load(f)