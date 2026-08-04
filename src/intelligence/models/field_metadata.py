from dataclasses import dataclass, field


@dataclass
class FieldMetadata:
    """
    Represents a single input field on the current page.
    """

    business_step: str

    label: str

    field_type: str = "text"

    required: bool = False

    options: list[str] = field(default_factory=list)

    placeholder: str = ""

    max_length: int | None = None

    readonly: bool = False

    visible: bool = True