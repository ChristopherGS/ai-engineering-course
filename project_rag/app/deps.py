from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from llama_index.llms.together import TogetherLLM

from app.config import settings
from app.db.session import AsyncSessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Asynchronous generator that provides a database session.

    This function asynchronously provides a scoped session for interacting with the database. It ensures that the session
    is correctly closed after use, even in the event of errors, by using an async context manager.

    Yields:
        AsyncSession: The SQLAlchemy asynchronous session object for database operations.
    """
    async with AsyncSessionLocal() as db:
        yield db

def get_llm() -> TogetherLLM:
    """
    Configures and returns a TogetherLLM instance.

    This function initializes a TogetherLLM object with configuration parameters specified in the application settings.
    It sets up the Large Language Model (LLM) with the appropriate model, API key, maximum token count, and context window
    size for use in processing language-based tasks.

    Returns:
        TogetherLLM: An instance of TogetherLLM configured for language model operations.
    """
    return TogetherLLM(
        model=settings.llm.MODEL,
        api_key=settings.llm.TOGETHER_API_KEY,
        max_tokens=settings.llm.MAX_TOKENS,
        context_window=settings.llm.CONTEXT_WINDOW
    )
