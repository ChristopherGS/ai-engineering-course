import asyncio
import logging

from app.db.update_db import update_db
from app.db.session import AsyncSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def update() -> None:
    async with AsyncSessionLocal() as db:
        await update_db(db)


async def main() -> None:
    logger.info("Adding summary data")
    await update()
    logger.info("Summary data added")


if __name__ == "__main__":
    asyncio.run(main())
