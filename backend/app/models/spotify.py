from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


class SpotifyPlaylist(Base):
    """
    Model for storing Spotify playlists created from mood transitions.

    Attributes:
        id: Primary key
        transition_id: Foreign key to the mood transiiton this playlist was created for
        spotify_id: Spotify's own ID for the playlist
        playlist_url: Public URL to access the playlist on Spotify
        created_at: When the playlist was created
    """
    __tablename__ = "spotify_playlists"

    id = Column(Integer, primary_key=True, index=True)
    transition_id = Column(Integer, ForeignKey("mood_transitions.id"))
    spotify_id = Column(String, unique=True, index=True)
    playlist_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    transition = relationship(
        "MoodTransition",
        backref="playlists"
    )

    def __repr__(self):
        return f"<SpotifyPlaylist(id={self.id}, spotify_id='{self.spotify_id}'>"