from validators.base_validator import BaseValidator
from validators.validation_result import ValidationResult


class RobotValidator(BaseValidator):
    """
    Validates AI-generated Robot Framework artifacts before
    they are assembled into the final executable suite.
    """

    TEST_CASE_SECTION = "*** Test Cases ***"


    FORBIDDEN_PATTERNS = [
        "markdown",
        "plaintext",
        "```",
        "|",
        "#",
        "${",
        "HTML",
        "XML",
        "JSON",
        "YAML",
        "CSV",
        "Should Be ",
        "Input Text",
        "Click Element",
        "Get Text",
        "Get Attribute",
        "Evaluate",
        "Execute JavaScript",
        "IF ",
        "FOR ",
        "WHILE ",
    ]

    def validate(
        self,
        content: str,
    ) -> ValidationResult:

        result = ValidationResult()

        self._validate_test_case_section(
            content,
            result,
        )

        self._validate_robot_structure(
            content,
            result,
        )

        self._validate_forbidden_syntax(
            content,
            result,
        )

        return result

    def normalize(
        self,
        content: str,
    ) -> str:

        return content

    def _validate_test_case_section(
        self,
        content: str,
        result: ValidationResult,
    ) -> None:

        if self.TEST_CASE_SECTION not in content:
            result.add_issue(
                code="RV001",
                message="Missing '*** Test Cases ***' section.",
                artifact="*** Test Cases ***",
                suggestion="Generate the required Robot Framework Test Cases section.",
            )


    def _validate_robot_structure(
        self,
        content: str,
        result: ValidationResult,
    ) -> None:

        lines = content.splitlines()

        # First non-empty line
        first = None

        for line in lines:
            if line.strip():
                first = line.strip()
                break

        if first != "*** Test Cases ***":
            result.add_issue(
                code="RV003",
                message="Robot output must start with *** Test Cases ***.",
                artifact=first or "",
                suggestion="Return only Robot Framework Test Cases.",
            )

        for line in lines:

            stripped = line.strip()

            if not stripped:
                continue

            if stripped.startswith("***"):
                continue

            # Executable keyword
            if line.startswith("    "):
                continue

            # Test case name
            if not line.startswith(" "):
                continue

            result.add_issue(
                code="RV004",
                message="Invalid Robot Framework structure.",
                artifact=line,
                suggestion="Test case names must not be indented. Keywords must use exactly four spaces.",
            )




    def _validate_forbidden_syntax(
        self,
        content: str,
        result: ValidationResult,
    ) -> None:
        """
        RV002

        Generated Robot test cases must contain only
        high-level business keywords.

        Implementation details such as Robot variables,
        Browser Library keywords, BuiltIn assertions,
        programming constructs, etc. are not allowed.
        """

        for line in content.splitlines():

            stripped = line.strip()

            # Ignore empty lines
            if not stripped:
                continue

            # Ignore section headers
            if stripped.startswith("***"):
                continue

            # Ignore test case names
            if stripped.startswith("TC_UI_"):
                continue

            for pattern in self.FORBIDDEN_PATTERNS:

                if pattern in stripped:

                    result.add_issue(
                        code="RV002",
                        message=f"Forbidden Robot syntax detected: {pattern}",
                        artifact=stripped,
                        suggestion="Replace implementation details with high-level business keywords.",
                    )

                    break