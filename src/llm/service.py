from llm.models.request import LLMRequest
from llm.models.response import LLMResponse
from llm.providers.base import BaseLLMProvider


class LLMService:

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    def generate(self, request: LLMRequest) -> LLMResponse:
        return self.provider.generate(request)