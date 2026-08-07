from loaders.robot_keyword_scanner import RobotKeywordScanner
from validators.robot_keyword_extractor import RobotKeywordExtractor
from validators.capability_validator import CapabilityValidator
from models.capability_report import CapabilityReport


class CapabilityValidationService:

    def validate(
        self,
        robot_suite: str,
    ) -> CapabilityReport:

        available_keywords = RobotKeywordScanner().scan()

        used_keywords = RobotKeywordExtractor().extract(
            robot_suite
        )

        missing_keywords = CapabilityValidator().validate(
            available_keywords,
            used_keywords,
        )

        print("\n========== AVAILABLE KEYWORDS ==========")
        for k in sorted(available_keywords):
            print(k)

        print("\n========== USED KEYWORDS ==========")
        for k in sorted(used_keywords):
            print(k)

        print("\n========== MISSING KEYWORDS ==========")
        for k in sorted(missing_keywords):
            print(k)

        print("=======================================\n")

        return CapabilityReport(
            available_keywords=available_keywords,
            used_keywords=used_keywords,
            missing_keywords=missing_keywords,
        )