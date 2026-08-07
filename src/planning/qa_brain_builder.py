import json
from pathlib import Path

from llm.models.request import LLMRequest
from prompts.qa_brain_prompt import SYSTEM_PROMPT


class QABrainBuilder:
    """
    Stage 3

    qa_knowledge.json
            │
            ▼
    LLM
            │
            ▼
    qa_brain.json
    """

    # --------------------------------------------------
    # Constructor
    # --------------------------------------------------

    def __init__(
        self,
        llm_service,
    ):

        self.llm_service = llm_service

    # --------------------------------------------------
    # Public
    # --------------------------------------------------

    async def run(
        self,
        qa_knowledge_file,
        output_dir,
    ) -> bool:

        qa_knowledge_file = Path(
            qa_knowledge_file,
        )

        output_dir = Path(
            output_dir,
        )

        print()
        print("=" * 80)
        print("QA BRAIN BUILDER")
        print("=" * 80)

        print(
            f"Reading : {qa_knowledge_file}"
        )

        qa_knowledge = self._read_json(
            qa_knowledge_file,
        )

        prompt = self._build_prompt(
            qa_knowledge,
        )

        request = LLMRequest(

            system_prompt=SYSTEM_PROMPT,

            user_prompt=prompt,

            response_format="json",

        )

        response = await self.llm_service.generate(
            request,
        )

        qa_brain = self._parse_response(
            response.content,
        )

        self._validate(
            qa_brain,
        )

        output_file = (
            output_dir
            / "qa_brain.json"
        )

        self._write_json(
            output_file,
            qa_brain,
        )

        modules = qa_brain.get(
            "modules",
            [],
        )

        features = sum(

            len(
                module.get(
                    "features",
                    [],
                )
            )

            for module in modules

        )

        print()

        print(
            f"Modules  : {len(modules)}"
        )

        print(
            f"Features : {features}"
        )

        print(
            f"Saved : {output_file}"
        )

        return True

    # --------------------------------------------------
    # Prompt
    # --------------------------------------------------

    def _build_prompt(
        self,
        qa_knowledge,
    ):

        statistics = qa_knowledge.get(
            "statistics",
            {},
        )

        chunks = qa_knowledge.get(
            "chunks",
            [],
        )

        prompt = f"""
QA Knowledge

Documentation URL:
{qa_knowledge.get("documentation_url", "")}

Statistics

Pages  : {statistics.get("pages", 0)}
Chunks : {statistics.get("chunks", 0)}

Below is the complete QA Knowledge extracted from the documentation.

Every chunk contains:

- page title
- page url
- heading
- documentation text
- chunk id

Use ONLY this information to build the QA Brain.

Return ONLY valid JSON.

QA KNOWLEDGE
====================

"""

        for chunk in chunks:

            prompt += f"""

--------------------------------------------------
Chunk ID
--------------------------------------------------
{chunk.get("id", "")}

Page
--------------------------------------------------
{chunk.get("page_title", "")}

URL
--------------------------------------------------
{chunk.get("page_url", "")}

Heading
--------------------------------------------------
{chunk.get("heading", "")}

Content
--------------------------------------------------
{chunk.get("text", "")}

"""

        return prompt


    # --------------------------------------------------
    # Parse Response
    # --------------------------------------------------

    def _parse_response(
        self,
        response,
    ):

        try:

            return json.loads(
                response,
            )

        except json.JSONDecodeError as ex:

            raise RuntimeError(
                "LLM did not return valid JSON."
            ) from ex

    # --------------------------------------------------
    # Validate
    # --------------------------------------------------

    def _validate(
        self,
        qa_brain,
    ):

        if not isinstance(
            qa_brain,
            dict,
        ):

            raise RuntimeError(
                "QA Brain must be a JSON object."
            )

        modules = qa_brain.get(
            "modules",
        )

        if modules is None:

            raise RuntimeError(
                "QA Brain is missing 'modules'."
            )

        if not isinstance(
            modules,
            list,
        ):

            raise RuntimeError(
                "'modules' must be a list."
            )

        for module in modules:

            if not isinstance(
                module,
                dict,
            ):

                raise RuntimeError(
                    "Every module must be a JSON object."
                )

            if not module.get(
                "name",
            ):

                raise RuntimeError(
                    "Every module must have a name."
                )

            features = module.get(
                "features",
            )

            if features is None:

                raise RuntimeError(
                    f"Module '{module['name']}' is missing features."
                )

            if not isinstance(
                features,
                list,
            ):

                raise RuntimeError(
                    f"Module '{module['name']}' features must be a list."
                )

            for feature in features:

                if not feature.get(
                    "name",
                ):

                    raise RuntimeError(
                        f"Module '{module['name']}' contains a feature without a name."
                    )

        return True

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