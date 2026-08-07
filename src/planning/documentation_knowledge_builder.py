from pathlib import Path

from playground.documentation_crawler import crawl


class DocumentationKnowledgeBuilder:
    """
    Stage 1

    Documentation URL
            │
            ▼
    Documentation Crawler
            │
            ▼
    documentation.json
    """

    # --------------------------------------------------
    # Run
    # --------------------------------------------------

    async def run(
        self,
        documentation_url: str,
        output_dir: Path,
    ) -> bool:

        print(
            f"Documentation : {documentation_url}"
        )

        await crawl(

            root_url=documentation_url,

            output_dir=output_dir,

        )

        return True