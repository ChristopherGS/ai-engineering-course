from typing import AsyncGenerator

from openai import AsyncOpenAI

from app.config import settings


async def get_llm_client() -> AsyncGenerator[AsyncOpenAI, None]:
    client = AsyncOpenAI(
        api_key=settings.llm.TOGETHER_API_KEY,
        base_url="https://api.together.xyz",
    )
    yield client
