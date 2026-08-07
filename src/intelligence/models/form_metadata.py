from dataclasses import dataclass, field

from intelligence.models.field_metadata import FieldMetadata


@dataclass
class FormMetadata:
    """
    Represents an entire business form.
    """

    name: str

    fields: list[FieldMetadata] = field(default_factory=list)