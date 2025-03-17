from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from app.schemas.mood import MoodResponse


class TransitionBase(BaseModel):
    """Base schema for mood transition data."""
    initial_mood_id: int = Field(..., title="Initial mood ID")
    target_mood_id: int = Field(..., title="Final mood ID")


class TransitionCreate(TransitionBase):
    """Schema for creating a new mood transition."""
    pass


class TransitionUpdate(BaseModel):
    initial_mood_id: Optional[int] = Field(None, description="ID of the starting mood")
    target_mood_id: Optional[int] = Field(None, description="ID of the target mood")


class TransitionResponse(TransitionBase):
    """Schema for mood transition responses."""
    id: int = Field(..., description="Unique identifier for the mood transition")
    timestamp: datetime = Field(..., description="When the transition was recorded")

    class Config:
        orm_mode = True


class TransitionWithMoods(TransitionResponse):
    """Schema for transitions with related mood data."""
    initial_mood: MoodResponse = Field(..., description="Details of the starting mood")
    target_mood: MoodResponse = Field(..., description="Details of the target mood")

    class Config:
        orm_mode = True


class TransitionStats(BaseModel):
    """Schema for transition statistics."""
    initial_mood: MoodResponse
    target_mood: MoodResponse
    count: int = Field(..., description="Number of times this transition has occurred")