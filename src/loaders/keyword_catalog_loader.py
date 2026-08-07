from pathlib import Path


class KeywordCatalogLoader:

    def load(self) -> str:

        catalog_path = Path(
            "robot/keyword_catalog.md"
        )

        return catalog_path.read_text(
            encoding="utf-8"
        )