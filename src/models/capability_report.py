from dataclasses import dataclass


@dataclass
class CapabilityReport:

    available_keywords: list[str]

    used_keywords: list[str]

    missing_keywords: list[str]

    @property
    def can_execute(self) -> bool:

        return len(self.missing_keywords) == 0

    def summary(self) -> str:

        if self.can_execute:

            return (
                "========================================\n"
                " AI-QEP Capability Report\n"
                "========================================\n"
                "Status : PASS\n\n"
                "All required automation capabilities are available.\n"
                "Robot execution can continue.\n"
                "========================================"
            )

        lines = [
            "========================================",
            " AI-QEP Capability Report",
            "========================================",
            "Status : BLOCKED",
            "",
            "Missing Automation Capabilities:",
            "",
        ]

        for keyword in self.missing_keywords:
            lines.append(f" - {keyword}")

        lines.extend(
            [
                "",
                "Required Action:",
                "Implement the missing automation capabilities",
                "before executing the generated Robot suite.",
                "========================================",
            ]
        )

        return "\n".join(lines)