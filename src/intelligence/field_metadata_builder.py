from intelligence.models.field_metadata import FieldMetadata


class FieldMetadataBuilder:
    """
    Builds structured metadata for a single input field.

    This class does NOT inspect the browser.

    It converts known facts into a strongly typed
    FieldMetadata object.
    """

    def build(
        self,
        business_step: str,
        field_name: str,
        field_type: str = "text",
        required: bool = False,
        options: list | None = None,
        placeholder: str = "",
        max_length: int | None = None,
    ) -> FieldMetadata:

        return FieldMetadata(
            business_step=business_step,
            label=field_name,
            field_type=field_type,
            required=required,
            options=options or [],
            placeholder=placeholder,
            max_length=max_length,
        )