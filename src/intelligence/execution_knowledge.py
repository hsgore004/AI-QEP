
from intelligence.models.field_metadata import FieldMetadata

class ExecutionKnowledge:
    """
    Stores execution knowledge learned during runtime.

    Initially this is an in-memory store.

    Future versions may use:

    - JSON
    - SQLite
    - Vector Database
    - RAG
    """

    def __init__(self):

        self._knowledge = {}

    # --------------------------------------------------
    # Lookup
    # --------------------------------------------------

    def find(
    self,
    field_metadata: FieldMetadata,
    ):

        key = self._create_key(
            field_metadata,
        )

        return self._knowledge.get(
            key,
        )

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    def save(   
        self,
        field_metadata: FieldMetadata,
        value,
    ):

        key = self._create_key(
            field_metadata,
        )

        self._knowledge[key] = value

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _create_key(
        self,
        field_metadata: dict,
    ) -> str:

        business_step = field_metadata.business_step
        field_name = field_metadata.label

        return (
            f"{business_step}|{field_name}"
        ).lower()