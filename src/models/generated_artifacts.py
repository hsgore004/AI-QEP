from dataclasses import dataclass


@dataclass
class GeneratedArtifacts:

    ui_test_cases: str

    api_test_cases: str

    robot_test_cases: str