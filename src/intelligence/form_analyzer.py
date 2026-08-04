from intelligence.models.form_metadata import FormMetadata
from intelligence.models.field_metadata import FieldMetadata


class FormAnalyzer:
    """
    Discovers the structure of the currently visible business form.

    Responsibilities

    - Identify visible fields
    - Determine field types
    - Determine mandatory fields
    - Discover dropdown options
    - Discover validation constraints

    This class NEVER generates test data.

    It only describes the form.
    """

    def analyze(
        self,
        business_step: str,
        page_snapshot: str,
    ) -> FormMetadata:

        #
        # Placeholder implementation.
        #
        # Soon this will inspect the browser snapshot
        # and extract real field metadata.
        #

        return FormMetadata(
            name=business_step,
            fields=[
                FieldMetadata(
                    business_step=business_step,
                    label="Unknown Field",
                    field_type="text",
                    required=False,
                )
            ],
        )