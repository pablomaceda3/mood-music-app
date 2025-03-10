from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app import models
from app import schemas
from app.spotify import spotify_router
from app.database import SessionLocal, engine

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Mood Transition API")

# Configure CORS to allow requests from our React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add the Spotify router to your FastAPI app
app.include_router(spotify_router, prefix="/spotify", tags=["spotify"])

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.get("/moods", response_model=List[schemas.Mood])
def get_moods(db: Session = Depends(get_db)):
    """Get all predefined moods"""
    return db.query(models.Mood).all()

@app.post("/transitions", response_model=schemas.MoodTransition)
def create_transition(
    transition: schemas.MoodTransitionCreate,
    db: Session = Depends(get_db)
):
    """Record a new mood transition"""
    db_transition = models.MoodTransition(
        initial_mood_id=transition.initial_mood_id,
        target_mood_id=transition.target_mood_id,
        timestamp=datetime.utcnow()
    )
    db.add(db_transition)
    db.commit()
    db.refresh(db_transition)
    return db_transition

@app.get("/transitions", response_model=List[schemas.MoodTransition])
def get_transitions(db: Session = Depends(get_db)):
    """Get all recorded mood transitions"""
    return db.query(models.MoodTransition).all()

@app.get("/debug/moods")
def debug_moods(db: Session = Depends(get_db)):
    """Debug endpoint to see raw mood data"""
    moods = db.query(models.Mood).all()
    transitions = db.query(models.MoodTransition).all()
    return {"moods": moods, "transitions": transitions}

@app.get("/")
def read_root():
    """Root endpoint to check if API is running"""
    return {
        "status": "online",
        "message": "Mood Transition API is running",
        "endpoints": [
            {"path": "/moods", "method": "GET", "description": "Get all moods"},
            {"path": "/transitions", "method": "GET", "description": "Get all transitions"},
            {"path": "/transitions", "method": "POST", "description": "Create a new transition"}
        ]
    }