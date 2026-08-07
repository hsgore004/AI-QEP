import asyncio

from llm.models.request import LLMRequest
from llm.models.response import LLMResponse
from llm.providers.base import BaseLLMProvider
from utils.logger import Logger


DEBUG = False


class LLMService:

    def __init__(
        self,
        provider: BaseLLMProvider,
    ):

        self.provider = provider

    # --------------------------------------------------
    # Generate
    # --------------------------------------------------

    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:

        if DEBUG:

            Logger.section("SYSTEM PROMPT")
            Logger.text(request.system_prompt)

            Logger.section("USER PROMPT")
            Logger.text(request.user_prompt)

        #
        # Execute synchronous provider in a worker thread.
        # This keeps the AI-QEP event loop responsive.
        #

        response = await asyncio.to_thread(

            self.provider.generate,

            request,

        )

        if DEBUG:

            Logger.section("LLM RESPONSE")
            Logger.text(response.content)

        return response