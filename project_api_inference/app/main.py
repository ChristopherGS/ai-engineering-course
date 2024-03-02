from pathlib import Path
from typing import Any, AsyncGenerator

from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from openai import AsyncOpenAI
from pydantic import BaseModel

from app import deps  # Assuming this is correctly implemented elsewhere
from app.config import settings

# Project Directories
BASE_PATH: Path = Path(__file__).resolve().parent
TEMPLATES: Jinja2Templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))

app: FastAPI = FastAPI(title="Inference App")
api_router: APIRouter = APIRouter()


@api_router.get("/", status_code=200)
async def root() -> Any:
    """
    Serves the root endpoint. Directs users to navigate to /docs for API documentation.

    Returns:
        str: A simple instruction to navigate to the API documentation.
    """
    return "Navigate to /docs"


@api_router.get("/ui", status_code=200)
async def ui(request: Request) -> Any:
    """
    Serves a UI page from the 'templates' directory.

    Args:
        request (Request): The request object.

    Returns:
        Any: A template response rendering the UI.
    """
    return TEMPLATES.TemplateResponse("index.html", {"request": request})


class ChatInput(BaseModel):
    """
    Represents the input for the chat inference endpoint.

    Attributes:
        user_message (str): The user's message to the AI model.
        max_tokens (int): The maximum number of tokens to generate in the response.
    """

    user_message: str = "Tell me about Paris"
    max_tokens: int = 100


@api_router.post("/inference/batch/", status_code=200)
async def run_chat_inference(
    chat_input: ChatInput,
    llm_client: AsyncOpenAI | None = Depends(deps.get_llm_client),
) -> Any:
    """
    Executes a batch inference using the provided chat input and returns the AI model's response.

    Args:
        chat_input (ChatInput): The chat input containing the user's message and configuration for the inference.
        llm_client (AsyncOpenAI | None): The asynchronous OpenAI client, obtained via dependency injection.

    Returns:
        Any: The cleaned and formatted response from the AI model.

    Raises:
        HTTPException: If the chat completion is empty.
    """
    chat_completion = await llm_client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an AI assistant"},
            {"role": "user", "content": f"{chat_input.user_message}"},
        ],
        model=settings.llm.MODEL,
        max_tokens=chat_input.max_tokens,
        temperature=settings.llm.TEMPERATURE,
    )

    if not chat_completion:
        raise HTTPException(status_code=404, detail="Chat completion empty")

    cleaned_response = chat_completion.choices[0].message.content.strip()
    cleaned_response = cleaned_response.replace("\\n", "\n")  # New line characters
    cleaned_response = cleaned_response.replace("\\", "")  # Remove backslashes

    return cleaned_response


async def stream_generator(response: AsyncGenerator) -> AsyncGenerator[str, None]:
    """
    Generates streaming content from the AI model's response.

    Args:
        response (AsyncGenerator): The streaming response from the AI model.

    Yields:
        str: Current content chunk from the AI model's response.
    """
    async for chunk in response:
        current_content = chunk.choices[0].delta.content
        yield current_content


@api_router.post("/inference/stream/", status_code=200, response_model=str)
async def run_chat_inference_stream(
    chat_input: ChatInput,
    llm_client: AsyncOpenAI | None = Depends(deps.get_llm_client),
) -> Any:
    """
    Executes a streaming inference using the provided chat input and streams the AI model's response.

    Args:
        chat_input (ChatInput): The chat input containing the user's message and configuration for the inference.
        llm_client (AsyncOpenAI | None): The asynchronous OpenAI client, obtained via dependency injection.

    Returns:
        Any: A streaming response with the AI model's outputs.
    """
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


app.include_router(api_router)

if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8001, log_level="debug", reload=True
    )
