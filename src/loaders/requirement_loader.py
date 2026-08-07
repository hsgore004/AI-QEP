from pathlib import Path


class RequirementLoader:

    def load(
        self,
        requirement_file: str,
    ) -> str:

        requirement_path = Path(requirement_file)
        

        return requirement_path.read_text(
            encoding="utf-8"
        )