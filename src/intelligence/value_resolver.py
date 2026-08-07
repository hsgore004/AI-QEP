class ValueResolver:
    """
    Resolves the value for a field.

    The caller never knows whether the value came from:

    - Execution Knowledge
    - Test Data Brain
    - Future external sources
    """

    def __init__(
        self,
        execution_config,
        execution_knowledge,
        test_data_brain,
    ):
        self.execution_config = execution_config
        self.execution_knowledge = execution_knowledge
        self.test_data_brain = test_data_brain

    # --------------------------------------------------
    # Resolve
    # --------------------------------------------------

    def resolve(
        self,
        field_metadata: dict,
    ):

        # ---------------------------------------------
        # Execution Configuration
        # ---------------------------------------------

        value = self.execution_config.get(
            field_metadata.label,
        )

        if value is not None:
            return value

        # ---------------------------------------------
        # Already learned?
        # ---------------------------------------------

        value = self.execution_knowledge.find(
            field_metadata,
        )

        if value is not None:
            return value

        # ---------------------------------------------
        # Generate new value
        # ---------------------------------------------

        value = self.test_data_brain.generate_value(
            field_metadata,
        )

        self.execution_knowledge.save(
            field_metadata,
            value,
        )

        return value