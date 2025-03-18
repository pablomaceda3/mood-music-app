from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db
from app.models.mood import Mood
from app.schemas.mood import MoodResponse, MoodCreate, MoodUpdate

router = APIRouter()

@router.get("/", response_model=List[MoodResponse])
async def get_moods(db: Session = Depends(get_db)):
    """Get all predefined moods"""
    moods = db.query(Mood).all()
    return moods

@router.get("/{mood_id}", response_model=MoodResponse)
async def get_mood(mood_id: int, db: Session = Depends(get_db)):
    """Get a specific mood by ID"""
    mood = db.query(Mood).filter(Mood.id == mood_id).first()
    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mood with ID {mood_id} not found"
        )
    return mood

@router.post("/", response_model=MoodResponse, status_code=status.HTTP_201_CREATED)
async def create_mood(mood: MoodCreate, db: Session = Depends(get_db)):
    """Create a new mood (admin only)"""
    existing_mood = db.query(Mood).filter(Mood.name == mood.name).first()
    if existing_mood:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mood with name {mood.name} already exists"
        )
    
    db_mood = Mood(**mood.dict())
    db.add(db_mood)
    db.commit()
    db.refresh(db_mood)
    return db_mood

@router.put("/{mood_id}", response_model=MoodResponse)
async def update_mood(
    mood_id: int,
    mood_data: MoodUpdate,
    db: Session = Depends(get_db)
):
    """Update a mood (admin only)"""
    mood = db.query(Mood).filter(Mood.id == mood_id).first()
    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mood with ID {mood_id} not found"
        )
    for key, value in mood_data.dict(exclude_unset=True).items():
        setattr(mood, key, value)

    db.commit()
    db.refresh(mood)
    return mood

@router.delete("/{mood_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mood(mood_id: int, db: Session = Depends(get_db)):
    """Delete a mood (admin only)"""
    mood = db.query(Mood).filter(Mood.id == mood_id).first()
    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mood with ID {mood_id} not found"
        )
    db.delete(mood)
    db.commit
    return None