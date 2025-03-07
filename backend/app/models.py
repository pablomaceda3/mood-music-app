from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Mood(Base):
    """Model for storing predefined moods"""
    __tablename__ = "moods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    color = Column(String)
    
    # Relationships for mood transitions
    as_initial = relationship("MoodTransition", foreign_keys="MoodTransition.initial_mood_id")
    as_target = relationship("MoodTransition", foreign_keys="MoodTransition.target_mood_id")

class MoodTransition(Base):
    """Model for storing mood transitions"""
    __tablename__ = "mood_transitions"

    id = Column(Integer, primary_key=True, index=True)
    initial_mood_id = Column(Integer, ForeignKey("moods.id"))
    target_mood_id = Column(Integer, ForeignKey("moods.id"))
    timestamp = Column(DateTime)
    
    # Relationships to get mood details
    initial_mood = relationship("Mood", foreign_keys=[initial_mood_id])
    target_mood = relationship("Mood", foreign_keys=[target_mood_id])


class SpotifyPlaylist(Base):
    """Model for storing Spotify playlists created from mood transitions"""
    __tablename__ = "spotify_playlists"

    id = Column(Integer, primary_key=True, index=True)
    transition_id = Column(Integer, ForeignKey("mood_transitions.id"))
    spotify_id = Column(String, unique=True, index=True)
    playlist_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to the mood transition
    transition = relationship("MoodTransition", backref="playlists")