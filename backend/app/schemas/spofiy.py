from pydantic import BaseModel, Field, AnyHttpUrl
from datetime import datetime
from typing import Optional, List


class PlaylistRequest(BaseModel):
    """Schema for playlist creation requests."""
    initial_mood_id: int = Field(..., title="ID of the initial mood")
    target_mood_id: int = Field(..., title="ID of the target mood")
    transition_id: int = Field(..., title="ID of the mood transition")


class PlaylistBase(BaseModel):
    """Base schema for Spotify playlist data."""
    transition_id: int = Field(..., description="Id of the associated mood transition")
    spotify_id: str = Field(..., description="Spotify's ID for the playlist")
    playlist_url: AnyHttpUrl = Field(..., description="Public URL to view the playlist on Spotify")


class PlaylistCreate(PlaylistBase):
    """Schema for creating a Spotify playlist record."""
    pass


class PlaylistResponse(PlaylistBase):
    """Schema for Spotify playlist responses."""
    id: int = Field(..., description="Unique identifier for the playlist record")
    created_at: datetime = Field(..., description="When the playlist was created")
    track_count: Optional[int] = Field(None, description="Number of tracks in the playlist")

    class Config:
        orm_mode = True


class UserProfile(BaseModel):
    """Schema for Spotify user profile data."""
    success: bool = Field(..., description="Whether the request was successful")
    display_name: str = Field(..., description="User's display name on Spotify")
    id: str = Field(..., description="User's Spotify ID")
    profile_url: Optional[AnyHttpUrl] = Field(None, description="Public URL to view the user's profile on Spotify")