from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator, Dict

from fastapi import FastAPI, APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from llama_index.core import StorageContext, load_index_from_storage, VectorStoreIndex
from llama_index.core.indices.base import BaseIndex, BaseQueryEngine
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app import deps
from app.config import INDEX_DIR
from app.schemas.chatbot import ChatInput
from app.schemas.podcast import Episode

# Project Directories
ROOT: Path = Path(__file__).resolve().parent.parent
BASE_PATH: Path = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))

# Global index storage
INDEX: Dict[str, Any] = {}

async def load_rag_index(index_dir: Path) -> BaseIndex:
    """
    Asynchronously loads the RAG index from the specified directory.

    Args:
        index_dir (Path): The directory path where the index is stored.

    Returns:
        BaseIndex: The loaded index.
    """
    storage_context = StorageContext.from_defaults(persist_dir=index_dir)
    embed_model = HuggingFaceEmbedding(model_name="WhereIsAI/UAE-Large-V1")
    return load_index_from_storage(storage_context, embed_model=embed_model)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    An asynchronous context manager for application startup and shutdown logic.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None
    """
    # Startup logic
    INDEX['rag_index'] = await load_rag_index(index_dir=INDEX_DIR)
    yield  # Yield control back to the event loop
    # Shutdown logic
    INDEX.clear()

app = FastAPI(title="Podcast Summarizer", lifespan=lifespan)
api_router = APIRouter()

@api_router.get("/", status_code=200)
async def root(
    request: Request,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Serves the homepage with a list of podcast episodes.

    Args:
        request (Request): The request object.
        db (AsyncSession): Database session dependency.

    Returns:
        Any: A template response rendering the homepage.
    """
    episodes = await crud.episode.get_multi(db=db, limit=10)
    return TEMPLATES.TemplateResponse("index.html", {"request": request, "episodes": episodes})

@api_router.get("/episode/{episode_id}", status_code=200, response_model=Episode)
async def fetch_episode(
    *,
    episode_id: int,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Fetches a single episode by its ID.

    Args:
        episode_id (int): The unique identifier of the episode.
        db (AsyncSession): Database session dependency.

    Returns:
        Any: The episode data or an HTTP 404 error if not found.
    """
    result = await crud.episode.get(db=db, id=episode_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Episode with ID {episode_id} not found")
    return result

@api_router.post("/inference/stream/", status_code=200, response_model=str)
async def run_chat_inference_stream(
    chat_input: ChatInput,
    llm: OpenAILike = Depends(deps.get_llm),
) -> Any:
    """
    Streams the response of a chat inference query.

    Args:
        chat_input (ChatInput): The input data for the chat query.
        llm (OpenAILike): The LLM dependency for query processing.

    Returns:
        Any: A streaming response of the query result.
    """
    index: VectorStoreIndex = INDEX["rag_index"]
    query_engine: BaseQueryEngine = index.as_query_engine(streaming=True, llm=llm)
    response = query_engine.query(chat_input.user_message)
    return StreamingResponse(response.response_gen, media_type="text/event-stream")

@api_router.get("/chatbot", status_code=200)
async def ui(request: Request) -> Any:
    """
    Serves the chatbot page.

    Args:
        request (Request): The request object.

    Returns:
        Any: A template response rendering the chatbot UI page.
    """
    return TEMPLATES.TemplateResponse("chatbot.html", {"request": request})

app.include_router(api_router)

if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, log_level="debug", reload=True)
