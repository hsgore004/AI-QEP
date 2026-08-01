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

        return CapabilityReport(
            available_keywords=available_keywords,
            used_keywords=used_keywords,
            missing_keywords=missing_keywords,
        )