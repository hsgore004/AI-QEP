from pathlib import Path


class RequirementLoader:

    def load(self) -> str:

        requirement_file = Path("requirements/login_requirement.md")

        return requirement_file.read_text(
            encoding="utf-8"
        )