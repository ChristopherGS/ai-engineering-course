# app/crud/crud_podcast.py
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.podcast import Podcast, Episode, Summary
from app.schemas.podcast import PodcastCreate, PodcastUpdate, SummaryCreate, SummaryUpdate, EpisodeCreate, EpisodeUpdate


class CRUDPodcast(CRUDBase[Podcast, PodcastCreate, PodcastUpdate]):
    pass

podcast = CRUDPodcast(Podcast)


class CRUDEpisode(CRUDBase[Episode, EpisodeCreate, EpisodeUpdate]):
    async def get(self, db: AsyncSession, id: Any) -> Episode | None:
        stmt = select(Episode).options(selectinload(Episode.summary)).filter(Episode.id == id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[Episode]:
        stmt = select(Episode).options(selectinload(Episode.summary)).offset(skip).limit(limit)
        results = await db.execute(stmt)
        return results.scalars().all()

episode = CRUDEpisode(Episode)

class CRUDSummary(CRUDBase[Summary, SummaryCreate, SummaryUpdate]):
    pass

summary = CRUDSummary(Summary)