from intelligence.execution_knowledge import ExecutionKnowledge
from intelligence.field_metadata_builder import FieldMetadataBuilder
from intelligence.test_data_brain import TestDataBrain
from intelligence.value_resolver import ValueResolver
from intelligence.execution_config import ExecutionConfig
from intelligence.form_analyzer import FormAnalyzer
from agents.form_fill_agent import FormFillAgent
import json



class ExecutionIntelligence:
    """
    Central orchestration layer for Execution Intelligence.

    Responsibilities

    - Build Field Metadata
    - Resolve field values
    - Reuse execution knowledge

    It never executes browser actions.
    """

    def __init__(
        self,
        llm_service,
    ):

        self.execution_knowledge = ExecutionKnowledge()
        self.execution_config = ExecutionConfig()
        self.field_metadata_builder = FieldMetadataBuilder()

        self.test_data_brain = TestDataBrain(
            llm_service,
        )

        self.form_fill_agent = FormFillAgent(
            llm_service,
        )

        self.form_analyzer = FormAnalyzer()

        self.value_resolver = ValueResolver(
            self.execution_config,
            self.execution_knowledge,
            self.test_data_brain,
        )

    # --------------------------------------------------
    # Resolve Field Value
    # --------------------------------------------------

    def resolve_value(
        self,
        business_step: str,
        field_name: str,
        field_type: str = "text",
        required: bool = False,
        options=None,
        placeholder: str = "",
        max_length=None,
    ):

        form_metadata = self.form_analyzer.analyze(
            business_step=business_step,
            page_snapshot="",
        )

        metadata = self.field_metadata_builder.build(
            business_step=business_step,
            field_name=field_name,
            field_type=field_type,
            required=required,
            options=options,
            placeholder=placeholder,
            max_length=max_length,
        )

        return self.value_resolver.resolve(
            metadata,
        )


        # --------------------------------------------------
        # Generate Complete Form Data
        # --------------------------------------------------

    async def generate_form_data(
        self,
        business_step: str,
        page_snapshot: str,
    ):

        print("[Execution Intelligence] AI Form Analysis...")

        form_json = await self.form_fill_agent.generate(
            business_step=business_step,
            page_snapshot=page_snapshot,
        )

        form = json.loads(form_json)

        for field in form.get("fields", []):

            field_name = field.get("name", "")

            value = self.execution_config.get(field_name)

            if value is not None:
                print(f"[Execution Intelligence] Using configured value for {field_name}")
                field["value"] = value

        return json.dumps(form, indent=2)