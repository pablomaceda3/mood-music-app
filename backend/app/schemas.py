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