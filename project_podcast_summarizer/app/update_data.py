import asyncio
import logging

from app.db.base_class import Base
from app.db.init_db import init_db
from app.db.session import AsyncSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def update_data() -> None:
    async with AsyncSessionLocal() as db:
        await init_db(db)


async def main() -> None:
    logger.info("Creating initial data")
    await update_data()
    logger.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
