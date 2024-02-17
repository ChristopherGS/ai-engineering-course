import logging
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db import base  # noqa: F401
from app.recipe_data import RECIPES

logger = logging.getLogger(__name__)

FIRST_SUPERUSER = "admin@recipeapi.com"

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)
    for recipe in RECIPES:
        recipe_in = schemas.RecipeCreate(
            label=recipe["label"],
            source=recipe["source"],
            url=recipe["url"],
        )
        crud.recipe.create(db, obj_in=recipe_in)
