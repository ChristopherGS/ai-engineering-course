# app/crud/crud_podcast.py
from app.crud.base import CRUDBase
from app.models.podcast import Podcast, Episode, Summary
from app.schemas.podcast import PodcastCreate, PodcastUpdate, SummaryCreate, SummaryUpdate, EpisodeCreate, EpisodeUpdate

class CRUDPodcast(CRUDBase[Podcast, PodcastCreate, PodcastUpdate]):
    pass

podcast = CRUDPodcast(Podcast)


class CRUDEpisode(CRUDBase[Episode, EpisodeCreate, EpisodeUpdate]):
    pass

episode = CRUDEpisode(Episode)

class CRUDSummary(CRUDBase[Summary, SummaryCreate, SummaryUpdate]):
    pass

summary = CRUDSummary(Summary)