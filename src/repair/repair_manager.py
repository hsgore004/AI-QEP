from validators.validation_result import ValidationResult


class RepairManager:

    MAX_RETRIES = 3

    def repair(
        self,
        artifact,
        validation_result: ValidationResult,
        generation_manager,
        validator,
        artifact_name,
        requirement,
        validator_args,
    ):

        repaired_artifact = artifact

        for attempt in range(self.MAX_RETRIES):

            print(
                f"[Repair] Attempt {attempt + 1}/{self.MAX_RETRIES}"
            )

            repaired_artifact = generation_manager.repair(
                artifact_name=artifact_name,
                validation_result=validation_result,
                current_artifact=repaired_artifact,
                requirement=requirement,
            )

            validation_result = validator.validate(
                repaired_artifact,
                *validator_args[1:]
            )

            if validation_result.is_valid:

                print("[Repair] Validation Passed")

                return repaired_artifact

        raise RuntimeError(
            f"Unable to repair '{artifact_name}' after "
            f"{self.MAX_RETRIES} attempts."
        )