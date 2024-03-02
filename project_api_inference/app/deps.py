from typing import AsyncGenerator
from openai import AsyncOpenAI
from app.config import settings


async def get_llm_client() -> AsyncGenerator[AsyncOpenAI, None]:
    """
    Asynchronously generates and provides an AsyncOpenAI client configured with API key and base URL from settings.

    This asynchronous generator function initializes an AsyncOpenAI client using configuration details specified in the
    application settings, particularly leveraging the Large Language Model (LLM) settings for the API key and the base URL.
    It then yields this client for use in asynchronous operations involving the OpenAI API.

    Yields:
        AsyncOpenAI: An instance of AsyncOpenAI client configured for interacting with the OpenAI API asynchronously.
    """
    client = AsyncOpenAI(
        api_key=settings.llm.TOGETHER_API_KEY,
        base_url=settings.llm.BASE_URL,
    )
    yield client
