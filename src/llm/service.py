import asyncio
DEBUG = False
from llm.models.request import LLMRequest
from llm.models.response import LLMResponse
from llm.providers.base import BaseLLMProvider
from utils.logger import Logger


class LLMService:

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    async def generate(
        self,
        request,
    ):
        if DEBUG:
            Logger.section("SYSTEM PROMPT")
            Logger.text(request.system_prompt)

            Logger.section("USER PROMPT")
            Logger.text(request.user_prompt)

        # Run the synchronous OpenAI SDK in a worker thread
        response = await asyncio.to_thread(
            self.provider.generate,
            request,
        )

        Logger.section("LLM RESPONSE")
        Logger.text(response.content)

        return response