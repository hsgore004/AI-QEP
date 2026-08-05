import json
from collections import defaultdict
from pathlib import Path


class QABrain:
    """
    QA Brain

    Converts qa_knowledge.json into a structured application model.

    No AI.
    No LLM.
    No reasoning.

    Structure

        Module
            └── Feature
                    └── Documentation Pages
                            └── Retrieval Chunks

    Output

        qa_brain.json
    """

    # --------------------------------------------------

    def build(
        self,
        knowledge_file: str | Path,
        output_file: str | Path,
    ):

        knowledge_file = Path(knowledge_file)
        output_file = Path(output_file)

        print("\n" + "=" * 80)
        print("QA BRAIN")
        print("=" * 80)

        print(f"Reading : {knowledge_file}")

        knowledge = json.loads(
            knowledge_file.read_text(
                encoding="utf-8",
            )
        )

        documents = {
            d["source_url"]: d
            for d in knowledge["documents"]
            if d.get("source_url")
        }

        # --------------------------------------------------
        # Group chunks by page
        # --------------------------------------------------

        page_chunks = defaultdict(list)

        for chunk in knowledge["chunks"]:

            page_chunks[
                chunk["source_url"]
            ].append(chunk)

        # --------------------------------------------------
        # Group pages into modules/features
        # --------------------------------------------------

        modules = defaultdict(
            lambda: defaultdict(list)
        )

        for url, chunks in page_chunks.items():

            document = documents.get(url)

            if not document:
                continue

            page_title = document["title"]

            #
            # URL
            #
            # https://docs.inventree.org/en/stable/part/create/
            #
            # module  = Part
            # feature = Create
            #

            path = (
                url.replace(
                    "https://docs.inventree.org/en/stable/",
                    "",
                )
                .strip("/")
                .split("/")
            )

            if len(path) == 0:
                continue

            module = path[0].replace(
                "-",
                " ",
            ).title()

            if len(path) > 1:
                feature = (
                    path[1]
                    .replace("-", " ")
                    .title()
                )
            else:
                feature = page_title

            page = {

                "title": page_title,

                "url": url,

                "chunk_ids": [
                    c["id"]
                    for c in chunks
                ],

                "chunks": chunks,
            }

            modules[module][feature].append(
                page
            )

        # --------------------------------------------------
        # Build final structure
        # --------------------------------------------------

        qa_brain = {

            "modules": []

        }

        for module_name in sorted(
            modules.keys()
        ):

            module = {

                "name": module_name,

                "features": []

            }

            for feature_name in sorted(
                modules[module_name].keys()
            ):

                feature = {

                    "name": feature_name,

                    "pages": modules[
                        module_name
                    ][feature_name]

                }

                module["features"].append(
                    feature
                )

            qa_brain["modules"].append(
                module
            )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file.write_text(
            json.dumps(
                qa_brain,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        print()

        print(
            f"Modules : {len(qa_brain['modules'])}"
        )

        feature_count = sum(
            len(m["features"])
            for m in qa_brain["modules"]
        )

        print(
            f"Features : {feature_count}"
        )

        print(
            f"Saved : {output_file}"
        )

        return qa_brain