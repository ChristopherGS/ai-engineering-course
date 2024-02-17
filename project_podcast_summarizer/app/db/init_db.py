import logging
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db.base_class import Base  # noqa: F401
from app.models.podcast import Podcast, Episode, Summary

logger = logging.getLogger(__name__)

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)
    # Create a new podcast
    podcast = Podcast(name="Developer Tea")

    # Create episodes
    episodes = [
        Episode(
            title="Finding Leverage by Escaping Functional Fixedness",
            url="https://podcasts.apple.com/gb/podcast/finding-leverage-by-escaping-functional-fixedness/id955596067?i=1000643042262",
            podcast=podcast  # Associate with the "Finding Leverage in Life and Work" podcast
        ),
        Episode(
            title="9 Years Persistence by Reducing Expectation",
            url="https://podcasts.apple.com/gb/podcast/9-years-persistence-by-reducing-expectation/id955596067?i=1000640625251",
            podcast=podcast  # Associate with the "Finding Leverage in Life and Work" podcast
        )
    ]

    # Add the podcast and episodes to the session and commit them to the database
    db.add(podcast)
    db.add_all(episodes)
    db.commit()

    # Close the session
    db.close()
