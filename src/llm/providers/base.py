from abc import ABC, abstractmethod

from llm.models.request import LLMRequest
from llm.models.response import LLMResponse


class BaseLLMProvider(ABC):

    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a response from an LLM provider.
        """
        pass