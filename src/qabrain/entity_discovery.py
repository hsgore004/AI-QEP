import json
from pathlib import Path

from llm.models.request import LLMRequest


SYSTEM_PROMPT = """
You are a Senior QA Architect.

You are given structured Business Knowledge extracted from an application's official documentation.

The supplied Business Knowledge is the ONLY source of truth.

Do NOT use any prior knowledge about the application.

--------------------------------------------------
OBJECTIVE
--------------------------------------------------

Discover the business entities described in the supplied Business Knowledge.

A business entity is an object that stores business information and participates
in one or more business processes.

--------------------------------------------------
RULES
--------------------------------------------------

Discover ONLY entities explicitly supported by the supplied Business Knowledge.

Never invent entities.

Never infer missing information.

Ignore:

- UI controls
- Buttons
- Menus
- Browser concepts
- Navigation
- Workflows

Return unique entities only.

Every entity should have a concise factual description.

--------------------------------------------------
OUTPUT
--------------------------------------------------

Return ONLY valid JSON.

{
    "entities": [

        {
            "name": "",
            "description": ""
        }

    ]

}
"""


class EntityDiscovery:

    # --------------------------------------------------
    # Constructor
    # --------------------------------------------------

    def __init__(
        self,
        llm_service,
    ):

        self.llm_service = llm_service

    # --------------------------------------------------
    # Run
    # --------------------------------------------------

    async def run(
        self,
        knowledge_file,
        output_dir,
    ) -> bool:

        knowledge_file = Path(
            knowledge_file,
        )

        output_dir = Path(
            output_dir,
        )

        print()
        print("=" * 80)
        print("ENTITY DISCOVERY")
        print("=" * 80)

        print(
            f"Reading : {knowledge_file}"
        )

        knowledge = self._read_json(
            knowledge_file,
        )

        #
        # Send only the information relevant for entity discovery
        #

        entity_input = {

            "application": knowledge.get(
                "application",
            ),

            "module": knowledge.get(
                "module",
            ),

            "purpose": knowledge.get(
                "purpose",
            ),

            "business_objects": knowledge.get(
                "business_objects",
                [],
            ),

            "relationships": knowledge.get(
                "relationships",
                [],
            ),

            "terminology": knowledge.get(
                "terminology",
                {},
            ),

        }

        request = LLMRequest(

            system_prompt=SYSTEM_PROMPT,

            user_prompt=f"""
Business Knowledge

{json.dumps(
    entity_input,
    indent=2,
    ensure_ascii=False,
)}

Return ONLY valid JSON.
""",

            response_format="json",

        )

        response = await self.llm_service.generate(
            request,
        )

        entities = json.loads(
            response.content,
        )

        self._validate(
            entities,
        )

        output_file = (
            output_dir
            / "entities.json"
        )

        self._write_json(
            output_file,
            entities,
        )

        print()

        print(
            f"Entities : {len(entities.get('entities', []))}"
        )

        print(
            f"Saved : {output_file}"
        )

        return True

    # --------------------------------------------------
    # Validate
    # --------------------------------------------------

    def _validate(
        self,
        output,
    ):

        if not isinstance(
            output,
            dict,
        ):

            raise RuntimeError(
                "Entity Discovery must return a JSON object."
            )

        entities = output.get(
            "entities",
        )

        if entities is None:

            raise RuntimeError(
                "Missing 'entities' field."
            )

        if not isinstance(
            entities,
            list,
        ):

            raise RuntimeError(
                "'entities' must be a list."
            )

        names = set()

        for entity in entities:

            name = entity.get(
                "name",
                "",
            ).strip()

            if not name:

                raise RuntimeError(
                    "Every entity must have a name."
                )

            if name.lower() in names:

                raise RuntimeError(
                    f"Duplicate entity '{name}'."
                )

            names.add(
                name.lower(),
            )

        return True

    # --------------------------------------------------
    # Read JSON
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
    # Write JSON
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