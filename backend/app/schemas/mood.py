from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MoodBase(BaseModel):
    """Base schema for mood data."""
    name: str = Field(..., title="Name of the mood")
    color: str = Field(..., title="Hex color code representing the mood")


class MoodCreate(MoodBase):
    """Schema for creating a new mood."""
    pass


class MoodUpdate(BaseModel):
    """Schema for updating an existing mood."""
    name: Optional[str] = None
    color: Optional[str] = None 


class MoodResponse(MoodBase):
    """Schema for mood responses."""
    id: int = Field(..., description="Unique identifier for the mood")

    class Config:
        orm_mode = True