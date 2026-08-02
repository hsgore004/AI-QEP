from dataclasses import dataclass, field


@dataclass
class ValidationIssue:
    """
    Represents a single validation issue.
    """

    code: str
    message: str
    artifact: str = ""
    suggestion: str = ""


@dataclass
class ValidationResult:
    """
    Result returned by every validator.
    """

    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.issues) == 0

    @property
    def errors(self) -> list[str]:
        """
        Backward compatibility.

        Existing code still loops over
        validation_result.errors.
        """
        return [
            f"{issue.code}: {issue.message}"
            for issue in self.issues
        ]

    def add_issue(
        self,
        code: str,
        message: str,
        artifact: str = "",
        suggestion: str = "",
    ) -> None:

        self.issues.append(
            ValidationIssue(
                code=code,
                message=message,
                artifact=artifact,
                suggestion=suggestion,
            )
        )

    def add_error(
        self,
        message: str,
    ) -> None:
        """
        Backward compatibility.

        Existing validators still call
        add_error().
        """

        code = "UNKNOWN"

        if ":" in message:
            code, message = message.split(":", 1)
            code = code.strip()
            message = message.strip()

        self.add_issue(
            code=code,
            message=message,
        )