from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.api.dependencies import get_db
from app.models.mood import MoodTransition, Mood
from app.schemas.transition import (
    TransitionResponse,
    TransitionCreate,
    TransitionUpdate,
    TransitionWithMoods
)


router = APIRouter()

@router.get("/", response_model=List[TransitionWithMoods])
async def get_transitions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all recorded mood transitions with pagination"""
    transitions = db.query(MoodTransition).offset(skip).limit(limit).all()
    return transitions

@router.get("/{transition_id}", response_model=TransitionWithMoods)
async def get_transition(transition_id: int, db: Session = Depends(get_db)):
    """Get a specific mood transition by ID"""
    transition = db.query(MoodTransition).filter(MoodTransition.id == transition_id).first()
    if not transition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transition with ID {transition_id} not found"
        )
    return transition

@router.post("/", response_model=TransitionWithMoods, status_code=status.HTTP_201_CREATED)
async def create_transition(
    transition: TransitionCreate,
    db: Session = Depends(get_db)
):
    """Record a new mood transition"""
    initial_mood = db.query(Mood).filter(Mood.id == transition.initial_mood_id).first()
    target_mood = db.query(Mood).filter(Mood.id == transition.target_mood_id).first()

    if not initial_mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Initial mood with ID {transition.initial_mood_id} not found"
        )
    
    if not target_mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target mood with ID {transition.target_mood_id} not found"
        )

    db_transition = MoodTransition(
        initial_mood_id=transition.initial_mood_id,
        target_mood_id=transition.target_mood_id,
        timestamp=datetime.utcnow()
    )

    db.add(db_transition)
    db.commit()
    db.refresh(db_transition)
    return db_transition

@router.delete("/{transition_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transition(transition_id: int, db: Session = Depends(get_db)):
    """Delete a mood transition"""
    transition = db.query(MoodTransition).filter(MoodTransition.id == transition_id).first()
    if not transition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transition with ID {transition_id} not found"
        )
    
    db.delete(transition)
    db.commit()
    return None

@router.get("/stats/common", response_model=List[dict])
async def get_common_transitions(db: Session = Depends(get_db), limit: int = 5):
    """Get the most common mood transitions"""
    from sqlalchemy import func, desc

    common_transitions = (
        db.query(
            MoodTransition.initial_mood_id,
            MoodTransition.target_mood_id,
            func.count().label("count")
        )
        .group_by(MoodTransition.initial_mood_id, MoodTransition.target_mood_id)
        .order_by(desc("count"))
        .limit(limit)
        .all()
    )
    
    result = []
    for t in common_transitions:
        initial_mood = db.query(Mood).filter(Mood.id == t.initial_mood_id).first()
        target_mood = db.query(Mood).filter(Mood.id == t.target_mood_id).first()

        result.append({
            "initial_mood": {
                "id": initial_mood.id,
                "name": initial_mood.name,
                "color": initial_mood.color
            },
            "target_mood": {
                "id": target_mood.id,
                "name": target_mood.name,
                "color": target_mood.color
            },
            "count": t.count
        })

    return result