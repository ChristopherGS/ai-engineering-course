import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import TRANSCRIPT_DIR
from app.db.base_class import Base  # noqa: F401
from app.models.podcast import Podcast, Episode, Summary

logger = logging.getLogger(__name__)

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


async def update_db(db: AsyncSession) -> None:
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
            "summary_file": "finding_leverage_by_escaping_functional_fixedness_summary.txt"
        },
        {
            "title": "9 Years Persistence by Reducing Expectation",
            "summary_file": "9_years_persistence_by_reducing_expectation_summary.txt"
        },
        # Add more episodes as needed
    ]

    # Iterate over episodes to read summaries and update
    for entry in episodes_data:
        # Read the summary file
        try:
            summary_path = SUMMARY_DIR / entry["summary_file"]
            with open(summary_path, 'r', encoding='utf-8') as file:
                summary_text = file.read()
        except IOError as e:
            logger.error(f"Failed to read summary file {entry['summary_file']}: {e}")
            continue  # Skip this episode if summary file can't be read

        # Fetch the corresponding episode from the database
        episode_result = await db.execute(select(Episode).where(Episode.title == entry['title']))
        episode = episode_result.scalars().first()

        if episode:
            # Create or update the summary
            if episode.summary:
                episode.summary.content = summary_text  # Update the existing summary
            else:
                new_summary = Summary(content=summary_text, episode=episode)  # Create a new summary
                db.add(new_summary)
        else:
            logger.error(f"Episode not found in database: {entry['title']}")

    # Commit the changes to the database
    await db.commit()

    # Close the session
    await db.close()