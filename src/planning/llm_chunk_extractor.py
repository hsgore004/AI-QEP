import json
from abc import ABC, abstractmethod

from llm.models.request import LLMRequest


class LLMChunkExtractor(ABC):
    """
    Base class for all AI-powered chunk extractors.

    Responsibilities

    - Build LLM request
    - Call LLM
    - Parse JSON response
    - Validate response
    - Enrich original chunk
    - Preserve traceability

    This class NEVER

    - Reads files
    - Writes files
    - Knows about pages
    - Knows about documentation.json
    - Knows about the pipeline

    Child classes provide

    - System Prompt
    - Prompt Builder
    - Validation
    - Output Field
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
    # Extract
    # --------------------------------------------------

    async def extract(
        self,
        chunk,
    ):

        request = LLMRequest(

            system_prompt=self.system_prompt(),

            user_prompt=self._build_prompt(
                chunk,
            ),

            response_format="json",

        )

        response = await self.llm_service.generate(
            request,
        )

        parsed = self._parse_response(
            response.content,
        )

        self._validate(
            parsed,
        )

        enriched_chunk = dict(
            chunk,
        )

        enriched_chunk[
            self.output_field()
        ] = parsed[
            self.output_field()
        ]

        return enriched_chunk

    # --------------------------------------------------
    # Parse Response
    # --------------------------------------------------

    def _parse_response(
        self,
        response,
    ):

        if not response:

            raise RuntimeError(
                "LLM returned an empty response."
            )

        response = response.strip()

        #
        # Remove Markdown JSON fences
        #

        if response.startswith(
            "```json",
        ):

            response = response[
                len("```json"):
            ]

        if response.startswith(
            "```",
        ):

            response = response[
                len("```"):
            ]

        if response.endswith(
            "```",
        ):

            response = response[:-3]

        response = response.strip()

        try:

            return json.loads(
                response,
            )

        except Exception as ex:

            print()
            print("=" * 80)
            print("INVALID JSON FROM LLM")
            print("=" * 80)
            print(response)
            print("=" * 80)

            raise RuntimeError(
                f"Unable to parse JSON.\n{ex}"
            ) from ex

# --------------------------------------------------
# Part 1 ends here
# --------------------------------------------------

    # --------------------------------------------------
    # System Prompt
    # --------------------------------------------------

    @abstractmethod
    def system_prompt(
        self,
    ):
        """
        Return the system prompt for this extractor.
        """
        pass

    # --------------------------------------------------
    # Build Prompt
    # --------------------------------------------------

    @abstractmethod
    def _build_prompt(
        self,
        chunk,
    ):
        """
        Build the user prompt for one documentation chunk.
        """
        pass

    # --------------------------------------------------
    # Validate
    # --------------------------------------------------

    @abstractmethod
    def _validate(
        self,
        response,
    ):
        """
        Validate the JSON returned by the LLM.
        Raise RuntimeError if invalid.
        """
        pass

    # --------------------------------------------------
    # Output Field
    # --------------------------------------------------

    @abstractmethod
    def output_field(
        self,
    ):
        """
        Name of the field to enrich.

        Examples

        knowledge
        entities
        workflows
        test_scenarios
        """
        pass

    # --------------------------------------------------
    # Stage Name
    # --------------------------------------------------

    @abstractmethod
    def stage_name(
        self,
    ):
        """
        Human readable stage name.
        """
        pass