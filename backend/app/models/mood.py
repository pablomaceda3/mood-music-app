from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


class Mood(Base):
    """
    Model for storing predefined moods.
    
    Attributes:
        id: Primary key
        name: Name of the mood (e.g., "Happy", "Sad")
        color: Hex color code representing the mood (e.g., "#FFD700" for happy)
    """
    __tablename__ = "moods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    color = Column(String)

    
    as_initial = relationship(
        "MoodTransition",
        foreign_keys="MoodTransition.initial_mood_id",
        back_populates="initial_mood"
    )

    as_target = relationship(
        "MoodTransition",
        foreign_keys="MoodTransition.target_mood_id",
        back_populates="target_mood"
    )

    def __repr__(self):
        return f"<Mood(id={self.id}, name='{self.name}', color='{self.color}')>"


class MoodTransition(Base):
    """
    Model for storing mood transitions - records when a user transitions
    from one mood to another.

    Attributes:
        id: Primary key
        initial_mood_id: Foreign key to the initial mood
        target_mood_id: Foreign key to the target mood
        user_id: Foreign key to the user who created the mood transition
        timestamp: Timestamp of the transition
    """
    __tablename__ = "mood_transitions"

    id = Column(Integer, primary_key=True, index=True)
    initial_mood_id = Column(Integer, ForeignKey("moods.id"))
    target_mood_id = Column(Integer, ForeignKey("moods.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)

    initial_mood = relationship(
        "Mood", 
        foreign_keys=[initial_mood_id], 
        back_populates="as_initial"
    )
    target_mood = relationship(
        "Mood", 
        foreign_keys=[target_mood_id], 
        back_populates="as_target"
        )

    user = relationship(
        "User", 
        back_populates="transitions")

    def __repr__(self):
        return f"<MoodTransition(id={self.id}, initial_mood_id={self.initial_mood_id}, target_mood_id={self.target_mood_id}, timestamp='{self.timestamp}')>"
