# app/crud/crud_podcast.py
import json
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
        episode = result.scalars().first()

        if episode and episode.summary and episode.summary.content:
            # Assuming summary.content is a stringified JSON, parse it into a Python object
            episode.summary.content = json.loads(episode.summary.content)

        return episode

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[Episode]:
        stmt = select(Episode).options(selectinload(Episode.summary)).offset(skip).limit(limit)
        results = await db.execute(stmt)
        episodes = results.scalars().all()
        for episode in episodes:
            if episode.summary and episode.summary.content:
                # Assuming summary.content is a stringified JSON
                # n.b. this is very inefficient
                episode.summary.content = json.loads(episode.summary.content)
        return episodes

episode = CRUDEpisode(Episode)

class CRUDSummary(CRUDBase[Summary, SummaryCreate, SummaryUpdate]):
    pass

summary = CRUDSummary(Summary)