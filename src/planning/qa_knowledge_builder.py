import json
import re
from datetime import datetime, timezone
from pathlib import Path


class QAKnowledgeBuilder:
    """
    Stage 2

    documentation.json
            │
            ▼
    Read Documentation
            │
            ▼
    Split Markdown into Knowledge Chunks
            │
            ▼
    qa_knowledge.json

    This stage performs NO AI reasoning.

    Responsibilities

    - Read canonical documentation
    - Split markdown by headings
    - Preserve traceability
    - Generate deterministic chunk IDs

    This stage never:

    - Uses an LLM
    - Creates embeddings
    - Infers features
    - Generates test cases
    """

    # --------------------------------------------------
    # Public
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
        print("QA KNOWLEDGE BUILDER")
        print("=" * 80)

        print(
            f"Reading : {documentation_file}"
        )

        documentation = self._read_json(
            documentation_file,
        )

        knowledge = {

            "documentation_url": documentation.get(
                "documentation_url",
                "",
            ),

            "generated_at": datetime.now(
                timezone.utc,
            ).isoformat(),

            "statistics": {

                "pages": 0,

                "chunks": 0,

            },

            "pages": [],

        }

        pages = documentation.get(
            "pages",
            [],
        )

        knowledge["statistics"]["pages"] = len(
            pages,
        )

        total_chunks = 0

        for page in pages:

            page_chunks = self._build_chunks(
                page,
                total_chunks + 1,
            )

            knowledge["pages"].append(

                {

                    "title": page.get(
                        "title",
                        "",
                    ),

                    "url": page.get(
                        "url",
                        "",
                    ),

                    "chunks": page_chunks,

                }

            )

            total_chunks += len(
                page_chunks,
            )

        knowledge["statistics"]["chunks"] = total_chunks

        output_file = (
            output_dir
            / "qa_knowledge.json"
        )

        self._write_json(
            output_file,
            knowledge,
        )

        print()

        print(
            f"Pages  : {knowledge['statistics']['pages']}"
        )

        print(
            f"Chunks : {knowledge['statistics']['chunks']}"
        )

        print(
            f"Saved : {output_file}"
        )

        return True

    # --------------------------------------------------
    # Build Chunks
    # --------------------------------------------------

    def _build_chunks(
        self,
        page,
        start_index,
    ):

        markdown = page.get(
            "markdown",
            "",
        )

#
        # Remove MkDocs navigation/header.
        #
        # Keep everything starting from the first real documentation heading.
        #
        # Example:
        #
        # Skip to content
        # ...
        # Table of contents
        #
        # # Parts
        #
        # becomes
        #
        # # Parts
        #

        # match = re.search(
        #     r"(?m)^#\s+",
        #     markdown,
        # )

        # if match:
        #     markdown = markdown[match.start():]


        if not markdown.strip():
            return []

        sections = self._split_markdown(
            markdown,
        )

        total_chunks = len(
            sections,
        )

        chunks = []

        page_slug = self._slugify(

            page.get(
                "title",
                "page",
            )

        )

        for index, section in enumerate(
            sections,
            start=1,
        ):

            heading = section["heading"]

            text = section["content"].strip()

            #
            # Remove markdown image hyperlinks
            #
            # Example:
            # [ ![Image](image.png) ](...)
            #

            text = re.sub(

                r'\[\s*!\[.*?\]\(.*?\)\s*\]\(.*?\)',

                '',

                text,

                flags=re.DOTALL,

            )

            #
            # Remove standalone markdown images
            #
            # Example:
            # ![Image](image.png)
            #

            text = re.sub(

                r'!\[.*?\]\(.*?\)',

                '',

                text,

            )

            #
            # Collapse excessive blank lines
            #

            text = re.sub(

                r'\n{3,}',

                '\n\n',

                text,

            ).strip()

            if not text:
                continue

            chunks.append(

                {

                    "id": f"{page_slug}_{index:03d}",

                    "page_title": page.get(
                        "title",
                        "",
                    ),

                    "page_url": page.get(
                        "url",
                        "",
                    ),

                    "heading": heading,

                    "heading_level": section[
                        "heading_level"
                    ],

                    "text": text,

                    "chunk_number": index,

                    "total_chunks": total_chunks,

                }

            )

        return chunks


    def _split_markdown(
        self,
        markdown,
    ):

        lines = markdown.splitlines()

        sections = []

        current_heading = "Introduction"

        current_level = 1

        current_content = []

        heading_pattern = re.compile(
            r"^(#{1,6})\s+(.*)$"
        )

        for line in lines:

            match = heading_pattern.match(
                line,
            )

            if match:

                #
                # Save previous section
                #

                if current_content:

                    sections.append(

                        {

                            "heading": current_heading,

                            "heading_level": current_level,

                            "content": "\n".join(
                                current_content,
                            ).strip(),

                        }

                    )

                #
                # New Heading
                #

                current_level = len(
                    match.group(1),
                )

                current_heading = match.group(
                    2,
                ).strip()

                #
                # Remove MkDocs permalink
                #
                # Example:
                # Part Category [¶](...)
                #

                current_heading = re.sub(

                    r"\[¶\]\(.*?\)",

                    "",

                    current_heading,

                ).strip()

                current_content = []

                continue

            current_content.append(
                line,
            )

        #
        # Save final section
        #

        if current_content:

            sections.append(

                {

                    "heading": current_heading,

                    "heading_level": current_level,

                    "content": "\n".join(
                        current_content,
                    ).strip(),

                }

            )

        return sections

    # --------------------------------------------------
    # Slugify
    # --------------------------------------------------

    def _slugify(
        self,
        text,
    ):

        if not text:
            return "page"

        text = text.lower()

        text = re.sub(
            r"[^a-z0-9]+",
            "_",
            text,
        )

        text = text.strip("_")

        while "__" in text:

            text = text.replace(
                "__",
                "_",
            )

        return text or "page"

    # --------------------------------------------------
    # Utility
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