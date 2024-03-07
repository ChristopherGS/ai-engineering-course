from typing import AsyncGenerator

from llama_index.llms.together import TogetherLLM

from app.config import settings
from app.db.session import AsyncSessionLocal

async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as db:
        yield db


def get_llm():
    return TogetherLLM(
        model=settings.llm.MODEL,
        api_key=settings.llm.TOGETHER_API_KEY,
        max_tokens=settings.llm.MAX_TOKENS,
        context_window=settings.llm.CONTEXT_WINDOW
    )