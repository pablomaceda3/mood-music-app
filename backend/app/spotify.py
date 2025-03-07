# Update the import section at the top of spotify.py
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app import models, schemas
from app.database import SessionLocal

# Create a router for Spotify endpoints
spotify_router = APIRouter()

# Environment variables for Spotify Credentials
SPOTIFY_CLIENT_ID = "your-client-id"
SPOTIFY_CLIENT_SECRET = "your-client-secret" 
SPOTIFY_REDIRECT_URI = "http://localhost:8000/spotify/callback"
SCOPE = "playlist-modify-private playlist-modify-public"

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create a Spotify client
def get_spotify_client():
    sp_oauth = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE
    )

    # This will require user login at first
    token_info = sp_oauth.get_cached_token()

    if not token_info:
        # Handle the need to authenticate
        raise HTTPException(status_code=401, detail="Spotify authentication required")

    return spotipy.Spotify(auth=token_info["access_token"])

# Login route that redirects to Spotify
@spotify_router.get("/login")
def spotify_login():
    sp_oauth = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE
    )
    auth_url = sp_oauth.get_authorize_url()
    return RedirectResponse(url=auth_url)

# Callback route that Spotify redirects to after login
@spotify_router.get("/callback")
def spotify_callback(code: str):
    sp_oauth = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE
    )
    token_info = sp_oauth.get_access_token(code)
    return {"success": True, "message": "Successfully authenticated with Spotify"}

# Test endpoint to verify Spotify client is working
@spotify_router.get("/me")
def get_user_profile(spotify: spotipy.Spotify = Depends(get_spotify_client)):
    """
    Get the current user's Spotify profile.
    This is a simple way to test if our authentication is working.
    """
    try:
        # This calls the Spotify API to get the user's profile
        user_info = spotify.current_user()
        return {
            "success": True,
            "display_name": user_info["display_name"],
            "id": user_info["id"],
            "profile_url": user_info["external_urls"]["spotify"] if "external_urls" in user_info else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Spotify profile: {str(e)}")

# Endpoint to create a playlist based on mood transition
@spotify_router.post("/create-playlist", response_model=schemas.SpotifyPlaylist)
def create_mood_transition_playlist(
    request: schemas.PlaylistRequest,
    spotify: spotipy.Spotify = Depends(get_spotify_client),
    db: Session = Depends(get_db)
):
    """
    Create a Spotify playlist based on a mood transition.
    Takes a mood transition and creates a playlist that goes from one mood to another.
    """
    try:
        # Check if the transition exists
        transition = db.query(models.MoodTransition).filter(models.MoodTransition.id == request.transition_id).first()
        if not transition:
            raise HTTPException(status_code=404, detail="Mood transition not found")
        
        # Get mood information
        initial_mood = db.query(models.Mood).filter(models.Mood.id == request.initial_mood_id).first()
        target_mood = db.query(models.Mood).filter(models.Mood.id == request.target_mood_id).first()
        
        if not initial_mood or not target_mood:
            raise HTTPException(status_code=404, detail="Mood not found")
        
        # Get the user profile to use their ID for playlist creation
        user_info = spotify.current_user()
        user_id = user_info["id"]
        
        # Create playlist name based on mood transition
        playlist_name = f"Transition: {initial_mood.name} to {target_mood.name}"
        playlist_description = f"A playlist to help transition from {initial_mood.name} to {target_mood.name}"
        
        # Create the playlist
        playlist = spotify.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False,
            description=playlist_description
        )
        
        # Get tracks based on mood characteristics
        tracks = get_mood_transition_tracks(spotify, initial_mood, target_mood)
        
        # Add tracks to the playlist
        if tracks:
            spotify.playlist_add_items(playlist["id"], tracks)
        
        # Save the playlist to the database
        db_playlist = models.SpotifyPlaylist(
            transition_id=request.transition_id,
            spotify_id=playlist["id"],
            playlist_url=playlist["external_urls"]["spotify"]
        )
        db.add(db_playlist)
        db.commit()
        db.refresh(db_playlist)
        
        return db_playlist
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating playlist: {str(e)}")

def get_mood_transition_tracks(spotify, initial_mood, target_mood):
    """
    Get tracks that match the mood transition.
    This is a simplified implementation - in a real app, you'd want more sophisticated logic.
    """
    # Define some basic audio feature parameters for each mood
    mood_features = {
        "Angry": {"target_energy": 0.8, "target_valence": 0.2, "genres": ["metal", "hard-rock", "punk"]},
        "Happy": {"target_energy": 0.7, "target_valence": 0.8, "genres": ["pop", "dance", "happy"]},
        "Sad": {"target_energy": 0.4, "target_valence": 0.2, "genres": ["sad", "indie", "chill"]},
        "Indifferent": {"target_energy": 0.5, "target_valence": 0.5, "genres": ["ambient", "study", "focus"]}
    }
    
    # Get parameters for the initial and target moods
    initial_params = mood_features.get(initial_mood.name, mood_features["Indifferent"])
    target_params = mood_features.get(target_mood.name, mood_features["Indifferent"])
    
    track_uris = []
    
    # Step 1: Get tracks matching the initial mood (first third of the playlist)
    for genre in initial_params["genres"]:
        results = spotify.search(
            q=f"genre:{genre}",
            type="track",
            limit=3
        )
        for item in results["tracks"]["items"]:
            track_uris.append(item["uri"])
    
    # Step 2: Get tracks for the transition (middle third of the playlist)
    mid_energy = (initial_params["target_energy"] + target_params["target_energy"]) / 2
    mid_valence = (initial_params["target_valence"] + target_params["target_valence"]) / 2
    
    # This would work better with Spotify's recommendations API which requires a seed
    # For simplicity, we're searching genres that might fit the middle ground
    results = spotify.search(
        q="genre:electronic",
        type="track",
        limit=5
    )
    for item in results["tracks"]["items"]:
        track_uris.append(item["uri"])
    
    # Step 3: Get tracks matching the target mood (final third of the playlist)
    for genre in target_params["genres"]:
        results = spotify.search(
            q=f"genre:{genre}",
            type="track",
            limit=3
        )
        for item in results["tracks"]["items"]:
            track_uris.append(item["uri"])
    
    return track_uris