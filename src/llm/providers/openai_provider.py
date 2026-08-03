from openai import OpenAI

from config import settings
from llm.models.request import LLMRequest
from llm.models.response import LLMResponse
from llm.providers.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI implementation of the BaseLLMProvider.
    Responsible only for communicating with the OpenAI API.
    """

    def __init__(self, client: OpenAI):
        self.client = client


    def generate(self, request: LLMRequest) -> LLMResponse:

        model = request.model or settings.OPENAI_MODEL

        try:

            print("[LLM] Thinking...")

            response = self.client.responses.create(
                model=model,
                instructions=request.system_prompt,
                input=request.user_prompt,
                text={
                    "format": {
                        "type": "json_object"
                    }
                },
            )

            print("[LLM] OK Response received")

            return LLMResponse(
                content=response.output_text,
                model=response.model,
                success=True,
            )

        except Exception as ex:

            print("\n========== OPENAI ERROR ==========")
            print(type(ex).__name__)
            print(ex)
            print("==================================\n")

            return LLMResponse(
                content="",
                model=model,
                success=False,
                error=str(ex),
            )