from abc import ABC, abstractmethod

from validators.validation_result import ValidationResult


class BaseValidator(ABC):

    @abstractmethod
    def validate(
        self,
        content: str,
    ) -> ValidationResult:
        """
        Validate the supplied artifact.

        Returns a ValidationResult describing
        all validation errors and warnings.
        """
        pass

    @abstractmethod
    def normalize(
        self,
        content: str,
    ) -> str:
        """
        Normalize the supplied artifact.

        Normalization should never change the
        business meaning of the artifact.
        It should only improve structural consistency.
        """
        pass