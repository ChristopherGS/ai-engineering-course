# app/schemas/podcast.py
from pydantic import BaseModel


class PodcastBase(BaseModel):
    title: str


class PodcastCreate(PodcastBase):
    pass


class PodcastUpdate(PodcastBase):
    pass


class PodcastInDBBase(PodcastBase):
    id: int

    class Config:
        from_attributes = True


class EpisodeBase(BaseModel):
    title: str
    url: str
    podcast_id: int


class EpisodeCreate(EpisodeBase):
    pass


class EpisodeUpdate(EpisodeBase):
    pass


class EpisodeInDBBase(EpisodeBase):
    id: int

    class Config:
        from_attributes = True


# Properties to return to client
class Episode(EpisodeInDBBase):
    pass


class SummaryBase(BaseModel):
    content: str
    episode_id: int


class SummaryCreate(SummaryBase):
    pass


class SummaryUpdate(SummaryBase):
    pass


class SummaryInDBBase(SummaryBase):
    id: int

    class Config:
        from_attributes = True
