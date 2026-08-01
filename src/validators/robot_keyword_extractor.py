class RobotKeywordExtractor:

    def extract(
        self,
        robot_suite: str,
    ) -> list[str]:

        keywords = []

        inside_test_cases = False

        for line in robot_suite.splitlines():

            if line.strip() == "*** Test Cases ***":
                inside_test_cases = True
                continue

            if not inside_test_cases:
                continue

            # Ignore comments and empty lines
            if not line.strip():
                continue

            if line.strip().startswith("#"):
                continue

            # Ignore test case names
            if not line.startswith("    "):
                continue

            keyword = line.strip().split("    ")[0]

            keywords.append(keyword)

        return sorted(set(keywords))