from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

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