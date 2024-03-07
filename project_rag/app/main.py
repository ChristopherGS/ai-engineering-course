from pathlib import Path
from typing import Any, AsyncGenerator

from fastapi import FastAPI, APIRouter, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from openai import AsyncOpenAI, AsyncStream
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import StreamingResponse
from llama_index.llms.openai_like import OpenAILike

from app import crud
from app import deps
from app.schemas.podcast import Episode
from app.config import settings
from app.schemas.chatbot import ChatInput

# Project Directories
ROOT = Path(__file__).resolve().parent.parent
BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))

app = FastAPI(title="Podcast Summarizer")
api_router = APIRouter()


@api_router.get("/", status_code=200)
async def root(
    request: Request,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Root GET
    """
    episodes = await crud.episode.get_multi(db=db, limit=10)
    return TEMPLATES.TemplateResponse(
        "index.html",
        {"request": request, "episodes": episodes},
    )

@api_router.get("/episode/{episode_id}", status_code=200, response_model=Episode)
async def fetch_episode(
    *,
    episode_id: int,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Fetch a single episode by ID
    """
    result = await crud.episode.get(db=db, id=episode_id)
    if not result:
        raise HTTPException(
            status_code=404, detail=f"Episode with ID {episode_id} not found"
        )
    return result


async def stream_generator(response: AsyncStream) -> AsyncGenerator[str, None]:
    """
    Generates streaming content from the AI model's response.

    Args:
        response (AsyncStream): The streaming response from the AI model.

    Yields:
        str: Current content chunk from the AI model's response.
    """
    async for chunk in response:
        current_content = chunk.choices[0].delta.content
        yield current_content


@api_router.post("/inference/stream/", status_code=200, response_model=str)
async def run_chat_inference_stream(
    chat_input: ChatInput,
    llm: OpenAILike = Depends(deps.get_llm),
) -> Any:

    # TODO: Figure out fastapi startup for index
    # could just use a cache and dependency injection
    # query_engine = request.app.state.llama_index.as_query_engine(llm=llm)
    response = await llm_client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an AI assistant"},
            {"role": "user", "content": chat_input.user_message},
        ],
        stream=True,
        model=settings.llm.MODEL,
        max_tokens=chat_input.max_tokens,
        temperature=settings.llm.TEMPERATURE,
    )
    return StreamingResponse(stream_generator(response), media_type="text/event-stream")


@api_router.get("/chatbot", status_code=200)
async def ui(request: Request) -> Any:
    """
    Serves a chatbot page from the 'templates' directory.

    Args:
        request (Request): The request object.

    Returns:
        Any: A template response rendering the UI.
    """
    return TEMPLATES.TemplateResponse("chatbot.html", {"request": request})

app.include_router(api_router)

if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, log_level="debug", reload=True)