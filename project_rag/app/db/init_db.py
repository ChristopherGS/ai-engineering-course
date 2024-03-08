import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import TRANSCRIPT_DIR
from app.db.base_class import Base  # noqa: F401
from app.models.podcast import Podcast, Episode

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

    episodes_data = [
        {
            "title": "Finding Leverage by Escaping Functional Fixedness",
            "url": "https://podcasts.apple.com/gb/podcast/finding-leverage-by-escaping-functional-fixedness/id955596067?i=1000643042262",
            "transcript_file": "developer_tea_episode_1191.txt"  # Adjust filename as necessary
        },
        {
            "title": "9 Years Persistence by Reducing Expectation",
            "url": "https://podcasts.apple.com/gb/podcast/9-years-persistence-by-reducing-expectation/id955596067?i=1000640625251",
            "transcript_file": "developer_tea_episode_1191.txt"  # Adjust filename as necessary
        },
        # Add more episodes as needed
    ]
    # Create episodes with transcripts
    episodes = []
    for entry in episodes_data:
        try:
            transcript_path = TRANSCRIPT_DIR / entry["transcript_file"]
            with open(transcript_path, 'r', encoding='utf-8') as file:
                transcript = file.read()
        except IOError as e:
            logger.error(f"Failed to read transcript file {entry['transcript_file']}: {e}")
            transcript = None  # Use None or some placeholder text if the transcript cannot be read

        episode = Episode(
            title=entry["title"],
            url=entry["url"],
            podcast=podcast,
            transcript=transcript
        )
        episodes.append(episode)

    # Add the episodes to the session
    db.add_all(episodes)
    await db.flush()  # Flushing is necessary to populate the episodes with IDs before committing

    # Commit the changes
    await db.commit()

    # Close the session
    await db.close()
