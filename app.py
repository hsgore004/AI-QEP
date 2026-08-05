import asyncio

from config import settings
from pipeline.pipeline_v3 import AIQEPPipelineV3


async def main():

    pipeline = AIQEPPipelineV3()

    await pipeline.run(
        documentation_url=settings.DOCUMENTATION_URL,
    )


if __name__ == "__main__":

    asyncio.run(
        main(),
    )