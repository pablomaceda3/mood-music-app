# app/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MoodBase(BaseModel):
    """Base schema for mood data"""
    name: str
    color: str

class Mood(MoodBase):
    """Schema for reading mood data"""
    id: int

    class Config:
        orm_mode = True

class MoodTransitionBase(BaseModel):
    """Base schema for mood transition data"""
    initial_mood_id: int
    target_mood_id: int

class MoodTransitionCreate(MoodTransitionBase):
    """Schema for creating mood transitions"""
    pass

class MoodTransition(MoodTransitionBase):
    """Schema for reading mood transitions"""
    id: int
    timestamp: datetime
    initial_mood: Mood
    target_mood: Mood

    class Config:
        orm_mode = True

class PlaylistRequest(BaseModel):
    """Schema for playlist creation requests"""
    initial_mood_id: int
    target_mood_id: int
    transition_id: int

class SpotifyPlaylistBase(BaseModel):
    """Base schema for Spotify playlist data"""
    transition_id: int
    spotify_id: str
    playlist_url: str

class SpotifyPlaylistCreate(SpotifyPlaylistBase):
    """Schema for creating Spotify playlist records"""
    pass

class SpotifyPlaylist(SpotifyPlaylistBase):
    """Schema for reading Spotify playlist data"""
    id: int
    created_at: datetime

    class Config:
        orm_mode = True