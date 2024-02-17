from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URI = "sqlite+aiosqlite:///example.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URI,
    # No need for "check_same_thread" in async mode since aiosqlite handles async access
    echo=True,  # Optional, for debugging
)

# AsyncSession configuration
AsyncSessionLocal = sessionmaker(
    expire_on_commit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
)
