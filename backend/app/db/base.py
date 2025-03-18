"""
Import all models here to ensure they are registered with SQLAlchemy
before creating the tables.
"""
from app.db.session import Base

from app.models.mood import Mood, MoodTransition
from app.models.spotify import SpotifyPlaylist