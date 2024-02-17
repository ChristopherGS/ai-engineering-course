from app.db.base_class import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship


class Podcast(Base):
    __tablename__ = 'podcast'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    episodes = relationship("Episode", back_populates="podcast")

class Episode(Base):
    __tablename__ = 'episode'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    url = Column(String(512))
    podcast_id = Column(Integer, ForeignKey('podcast.id'), nullable=False)
    podcast = relationship("Podcast", back_populates="episodes")
    summary = relationship("Summary", back_populates="episode", uselist=False)

class Summary(Base):
    __tablename__ = 'summary'
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=True)
    episode_id = Column(Integer, ForeignKey('episode.id'), unique=True)
    episode = relationship("Episode", back_populates="summary")
