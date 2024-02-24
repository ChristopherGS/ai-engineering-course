# Import all the models, so that Base has them before being
# imported by Alembic
from app.models.podcast import Podcast, Episode, Summary  # noqa