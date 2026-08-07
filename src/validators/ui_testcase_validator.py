from validators.base_validator import BaseValidator
from validators.validation_result import ValidationResult

from models.requirement import Requirement


class UITestCaseValidator(BaseValidator):
    """
    Validates AI-generated Manual UI Test Cases before
    they are consumed by downstream agents.
    """

    def validate(
        self,
        requirement: Requirement,
        ui_test_cases: str,
    ) -> ValidationResult:

        result = ValidationResult()

        self._validate_ui_component_coverage(
            requirement,
            ui_test_cases,
            result,
        )

        return result

    def normalize(
        self,
        content: str,
    ) -> str:

        return content

    def _validate_ui_component_coverage(
        self,
        requirement: Requirement,
        ui_test_cases: str,
        result: ValidationResult,
    ) -> None:
        """
        UI001

        Every UI Component present in the Requirement
        must appear in at least one Manual UI Test Case.
        """

        for component in requirement.ui_components:

            normalized_test_cases = (
                ui_test_cases.lower()
                .replace('"', "")
                .replace("'", "")
            )

            for component in requirement.ui_components:

                normalized_component = (
                    component.lower()
                    .replace('"', "")
                    .replace("'", "")
                )

                if normalized_component not in normalized_test_cases:

                    result.add_error(
                        f"UI001: Missing UI Test Case coverage for '{component}'."
                    )