import logging
import asyncio

from app.db.session import AsyncSessionLocal

from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init() -> None:
    async with AsyncSessionLocal() as db:
        try:
            # Try to create session to check if DB is awake
            await db.execute(text("SELECT 1"))
            await db.commit()  # Ensure any transaction is committed.
        except Exception as e:
            logger.error(e)
            raise e

async def main() -> None:
    logger.info("Initializing service")
    await init()
    logger.info("Service finished initializing")

if __name__ == "__main__":
    asyncio.run(main())