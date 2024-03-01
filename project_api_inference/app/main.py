from pathlib import Path
from typing import Any

from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from openai import AsyncOpenAI
from pydantic import BaseModel
from fastapi.requests import Request

from app import deps
from app.config import settings

# Project Directories
ROOT = Path(__file__).resolve().parent.parent
BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))

app = FastAPI(title="Inference App")
api_router = APIRouter()


@api_router.get("/", status_code=200)
async def root() -> Any:
    """
    Root GET
    """
    return "Navigate to /docs"


@api_router.get("/ui", status_code=200)
async def ui(request: Request) -> Any:
    """
    Root GET
    """
    return TEMPLATES.TemplateResponse(
        "index.html",
        {"request": request},
    )


# Define a Pydantic model for the chat message
class ChatInput(BaseModel):
    user_message: str = "Tell me about Paris"
    max_tokens: int = 300


@api_router.post("/inference/batch/", status_code=200)
async def run_chat_inference(
    chat_input: ChatInput,
    llm_client: AsyncOpenAI | None = Depends(deps.get_llm_client),
) -> Any:
    """
    Run batch inference.
    """
    chat_completion = await llm_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant",
            },
            {
                "role": "user",
                "content": f"{chat_input}",
            },
        ],
        model=settings.llm.MODEL,
        max_tokens=settings.llm.MAX_TOKENS,
    )

    if not chat_completion:
        raise HTTPException(status_code=404, detail="Chat completion empty")

    return chat_completion.choices[0].message.content.strip()


async def stream_generator(response):
    async for chunk in response:
        current_content = chunk.choices[0].delta.content
        yield current_content


@api_router.post("/inference/stream/", status_code=200, response_model=str)
async def run_chat_inference_stream(
    chat_input: ChatInput,
    llm_client: AsyncOpenAI | None = Depends(deps.get_llm_client),
) -> Any:
    """
    Run streaming inference.
    """
    response = await llm_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant",
            },
            {
                "role": "user",
                "content": chat_input.user_message,
            },
        ],
        stream=True,
        model=settings.llm.MODEL,
        max_tokens=chat_input.max_tokens,
    )
    return StreamingResponse(stream_generator(response), media_type="text/event-stream")


app.include_router(api_router)

if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8001, log_level="debug", reload=True
    )
