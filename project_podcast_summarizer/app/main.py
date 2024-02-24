from pathlib import Path
from typing import Any

from fastapi import FastAPI, APIRouter, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app import deps
from app.schemas.podcast import Episode

# Project Directories
ROOT = Path(__file__).resolve().parent.parent
BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))

app = FastAPI(title="Recipe API", openapi_url="/openapi.json")
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

app.include_router(api_router)

if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, log_level="debug", reload=True)
