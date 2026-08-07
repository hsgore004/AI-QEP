from pathlib import Path


class RobotKeywordScanner:

    def scan(self) -> list[str]:

        keywords = []

        resources_path = Path("robot/resources")

        for resource_file in resources_path.rglob("*.resource"):

            lines = resource_file.read_text(
                encoding="utf-8"
            ).splitlines()

            inside_keywords = False

            for line in lines:

                stripped = line.strip()

                if stripped == "*** Keywords ***":
                    inside_keywords = True
                    continue

                if inside_keywords:

                    if stripped.startswith("***"):
                        break

                    if (
                        stripped
                        and not stripped.startswith("#")
                        and not stripped.startswith("...")
                        and "    " not in line
                    ):
                        keywords.append(stripped)

        return sorted(set(keywords))