import json
from pathlib import Path

from llm.models.request import LLMRequest


SYSTEM_PROMPT = """
You are a Senior Technical Documentation Analyst.

Your ONLY responsibility is to extract structured knowledge from application documentation.

The supplied documentation is the ONLY source of truth.

Never use prior knowledge.

Never infer.

Never summarize.

Never invent.

Never classify beyond what is explicitly stated.

--------------------------------------------------
OBJECTIVE
--------------------------------------------------

Extract every documentation chunk into structured knowledge.

The goal is to preserve ALL business information for later reasoning.

This stage performs ZERO reasoning.

This stage performs ZERO feature discovery.

This stage performs ZERO capability discovery.

This stage performs ZERO entity discovery.

--------------------------------------------------
EXTRACTION RULES
--------------------------------------------------

For every documentation chunk extract:

- facts
- definitions
- business_rules
- constraints
- relationships
- events
- examples
- warnings
- terminology

If a section does not exist,

return an empty array.

Never fabricate information.

Never rewrite the documentation.

The original text MUST remain unchanged.

--------------------------------------------------
OUTPUT
--------------------------------------------------

Return ONLY valid JSON.

{
    "application": {
        "name": ""
    },

    "pages": [

        {

            "title": "",

            "url": "",

            "chunks": [

                {

                    "chunk_id": "",

                    "heading": "",

                    "heading_level": 0,

                    "original_text": "",

                    "facts": [],

                    "definitions": [],

                    "business_rules": [],

                    "constraints": [],

                    "relationships": [],

                    "events": [],

                    "examples": [],

                    "warnings": [],

                    "terminology": []

                }

            ]

        }

    ]
}
"""


class KnowledgeBuilder:

    # --------------------------------------------------

    def __init__(
        self,
        llm_service,
    ):

        self.llm_service = llm_service

    # --------------------------------------------------

    async def run(
        self,
        documentation_file,
        output_dir,
    ) -> bool:

        documentation_file = Path(
            documentation_file,
        )

        output_dir = Path(
            output_dir,
        )

        print()
        print("=" * 80)
        print("KNOWLEDGE EXTRACTOR")
        print("=" * 80)

        print(
            f"Reading : {documentation_file}"
        )

        documentation = self._read_json(
            documentation_file,
        )

        prompt = self._build_prompt(
            documentation,
        )

        request = LLMRequest(

            system_prompt=SYSTEM_PROMPT,

            user_prompt=prompt,

            response_format="json",

        )

        response = await self.llm_service.generate(
            request,
        )

        knowledge = json.loads(
            response.content,
        )

        self._validate(
            knowledge,
        )

        output_file = (
            output_dir
            / "knowledge.json"
        )

        self._write_json(
            output_file,
            knowledge,
        )

        print()

        print(
            f"Pages : {len(knowledge.get('pages', []))}"
        )

        print(
            f"Saved : {output_file}"
        )

        return True

    # --------------------------------------------------

    def _build_prompt(
        self,
        documentation,
    ):

        pages = documentation.get(
            "pages",
            [],
        )

        document = []

        for page in pages:

            document.append("=" * 80)

            document.append(
                f"PAGE TITLE : {page.get('title','')}"
            )

            document.append(
                f"URL : {page.get('url','')}"
            )

            document.append("")

            for chunk in page.get(
                "chunks",
                [],
            ):

                document.append(
                    "-" * 80
                )

                document.append(
                    f"Chunk ID : {chunk.get('id','')}"
                )

                document.append(
                    f"Heading : {chunk.get('heading','')}"
                )

                document.append(
                    f"Heading Level : {chunk.get('heading_level',0)}"
                )

                document.append("")

                document.append(
                    chunk.get(
                        "text",
                        "",
                    )
                )

                document.append("")

        return f"""
Application Documentation

{chr(10).join(document)}

Return ONLY valid JSON.
"""

    # --------------------------------------------------

    def _validate(
        self,
        knowledge,
    ):

        if "pages" not in knowledge:

            raise RuntimeError(
                "Knowledge extraction failed. Missing 'pages'."
            )

        return True

    # --------------------------------------------------

    def _read_json(
        self,
        file,
    ):

        return json.loads(

            Path(file).read_text(
                encoding="utf-8",
            )

        )

    # --------------------------------------------------

    def _write_json(
        self,
        file,
        data,
    ):

        Path(file).write_text(

            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
            ),

            encoding="utf-8",

        )