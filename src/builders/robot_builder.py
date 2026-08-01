from textwrap import dedent


class RobotBuilder:
    """
    Responsible for constructing a complete executable
    Robot Framework test suite from AI-generated test cases.
    """

    SETTINGS = dedent("""\
    *** Settings ***
    Resource    ../resources/common.resource
    Suite Setup    Open Login Page
    Suite Teardown    Close Browser Session

    """)

    def build(self, test_cases: str) -> str:
        """
        Returns a complete Robot Framework suite.
        """

        test_cases = test_cases.replace("```robot", "")
        test_cases = test_cases.replace("```", "")
        test_cases = test_cases.strip()

        return self.SETTINGS + "\n" + test_cases