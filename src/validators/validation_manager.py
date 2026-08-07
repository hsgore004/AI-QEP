from repair.repair_manager import RepairManager


class ValidationManager:

    def __init__(self):
        self.repair_manager = RepairManager()

    def validate(
        self,
        artifact_name,
        artifact,
        validator,
        generation_manager,
        requirement,
        *validator_args,
    ):

        validation_result = validator.validate(
            *validator_args
        )

        if validation_result.is_valid:
            return artifact

        return self.repair_manager.repair(
            artifact=artifact,
            validation_result=validation_result,
            generation_manager=generation_manager,
            validator=validator,
            artifact_name=artifact_name,
            requirement=requirement,
            validator_args=validator_args,
        )