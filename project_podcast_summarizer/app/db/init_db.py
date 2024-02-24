import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import crud, schemas
from app.db.base_class import Base  # noqa: F401
from app.models.podcast import Podcast, Episode, Summary

logger = logging.getLogger(__name__)

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


async def init_db(db: AsyncSession) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables uncommenting the next line
    # Base.metadata.create_all(bind=engine)

    # Check if the podcast already exists
    result = await db.execute(select(Podcast).where(Podcast.name == "Developer Tea"))
    podcast = result.scalars().first()

    # Create a new podcast if it doesn't exist
    if not podcast:
        podcast = Podcast(name="Developer Tea")
        db.add(podcast)
        await db.flush()  # Flushing is necessary to populate the podcast with an ID before committing

        # Create episodes
        episodes = [
            Episode(
                title="Finding Leverage by Escaping Functional Fixedness",
                url="https://podcasts.apple.com/gb/podcast/finding-leverage-by-escaping-functional-fixedness/id955596067?i=1000643042262",
                podcast=podcast  # Associate with the "Developer Tea" podcast
            ),
            Episode(
                title="9 Years Persistence by Reducing Expectation",
                url="https://podcasts.apple.com/gb/podcast/9-years-persistence-by-reducing-expectation/id955596067?i=1000640625251",
                podcast=podcast  # Associate with the "Developer Tea" podcast
            )
        ]

        # Add the episodes to the session
        db.add_all(episodes)

    # Commit the changes
    await db.commit()

    # Close the session
    await db.close()
