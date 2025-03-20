from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
from typing import Dict, List, Any

from app.core.config import settings
from app.api.dependencies import get_db, get_spotify_client
from app.models.mood import MoodTransition, Mood
from app.models.spotify import SpotifyPlaylist
from app.schemas.spotify import PlaylistRequest, PlaylistResponse

import random

router = APIRouter()

@router.get("/login")
async def spotify_login():
    """Initiate Spotify OAuth login flow"""
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope=settings.SPOTIFY_SCOPE,
        cache_handler=settings.SPOTIFY_CACHE_HANDLER
    )
    auth_url = sp_oauth.get_authorize_url()
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def spotify_callback(code: str):
    """Handle Spotify OAuth callback"""
    try:
        sp_oauth = SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIFY_REDIRECT_URI,
            scope=settings.SPOTIFY_SCOPE,
            cache_handler=settings.SPOTIFY_CACHE_HANDLER
        )

        token_info = sp_oauth.get_access_token(code)

        return RedirectResponse(url=settings.FRONTEND_URL)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error handling Spotify callback: {e}"
        )

@router.get("/me", response_model=Dict[str, Any])
async def get_user_profile(
    spotify: spotipy.Spotify = Depends(get_spotify_client)
):
    """Get the current user's Spotify profile"""
    try:
        user_info = spotify.current_user()
        return {
            "success": True,
            "display_name": user_info["display_name"],
            "id": user_info["id"],
            "profile_url": user_info["external_urls"].get("spotify")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching Spotify profile: {e}"
        )

@router.post("/create-playlist", response_model=PlaylistResponse)
async def create_mood_transition_playlist(
    request: PlaylistRequest,
    spotify: spotipy.Spotify = Depends(get_spotify_client),
    db: Session = Depends(get_db)
):
    """Create a Spotify playlist based on a mood transition"""
    try:
        transition = db.query(MoodTransition).filter(
            MoodTransition.id == request.transition_id
        ).first()

        if not transition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mood transition not found"
            )

        initial_mood = db.query(Mood).filter(
            Mood.id == request.initial_mood_id
        ).first()

        target_mood = db.query(Mood).filter(
            Mood.id == request.target_mood_id
        ).first()

        if not initial_mood or not target_mood:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Initial or target mood not found"
            )

        user_info = spotify.current_user()
        user_id = user_info["id"]

        playlist_name = f"Transition: {initial_mood.name} to {target_mood.name}"
        playlist_description = f"A playlist to help transition from {initial_mood.name} to {target_mood.name}"

        playlist = spotify.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False,
            description=playlist_description
        )

        tracks = get_mood_transition_tracks(spotify, initial_mood, target_mood)

        track_count = 0
        if tracks:
            spotify.playlist_add_items(playlist["id"], tracks)
            track_count = len(tracks)

        db_playlist = SpotifyPlaylist(
            transition_id=request.transition_id,
            spotify_id=playlist["id"],
            playlist_url=playlist["external_urls"]["spotify"],
            created_at=datetime.utcnow()
        )

        db.add(db_playlist)
        db.commit()
        db.refresh(db_playlist)

        return {
            "id": db_playlist.id,
            "transition_id": db_playlist.transition_id,
            "spotify_id": db_playlist.spotify_id,
            "playlist_url": db_playlist.playlist_url,
            "created_at": db_playlist.created_at,
            "track_count": track_count
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating playlist: {e}"
        )

@router.get("/playlists", response_model=List[PlaylistResponse])
async def get_playlists(db: Session = Depends(get_db)):
    """Get all created Spotify playlists"""
    playlists = db.query(SpotifyPlaylist).all()
    return playlists

def get_mood_transition_tracks(
    spotify: spotipy.Spotify,
    initial_mood: Mood,
    target_mood: Mood
) -> List[str]:
    """Get tracks that match the mood transition with randomization.
    Returns a list of Spotify track URIs.
    """
    mood_features = {
        "Angry": {"target_energy": 0.8, "target_valence": 0.2, 
                "genres": ["metal", "punk", "hard-rock", "rage", "intense", "heavy"]},
        "Happy": {"target_energy": 0.7, "target_valence": 0.8, 
                "genres": ["pop", "dance", "happy", "upbeat", "feel-good", "cheerful"]},
        "Sad": {"target_energy": 0.4, "target_valence": 0.2, 
            "genres": ["sad", "indie", "chill", "melancholy", "acoustic", "blues"]},
        "Indifferent": {"target_energy": 0.5, "target_valence": 0.5, 
                    "genres": ["ambient", "study", "focus", "background", "neutral", "calm"]}
    }

    initial_params = mood_features.get(initial_mood.name, mood_features["Indifferent"])
    target_params = mood_features.get(target_mood.name, mood_features["Indifferent"])

    track_uris = []
    
    # Randomly select a subset of genres for initial mood (2-3 genres)
    initial_genres = random.sample(initial_params["genres"], 
                                min(random.randint(2, 3), len(initial_params["genres"])))
    
    # Add some randomization to energy and valence
    initial_energy = initial_params["target_energy"] * random.uniform(0.85, 1.15)
    initial_energy = max(0.0, min(1.0, initial_energy))  # Keep within 0-1 range
    
    initial_valence = initial_params["target_valence"] * random.uniform(0.85, 1.15)
    initial_valence = max(0.0, min(1.0, initial_valence))  # Keep within 0-1 range

    # Get tracks for initial mood with randomized parameters
    for genre in initial_genres:
        # Add random year ranges occasionally
        year_filter = ""
        if random.random() > 0.5:
            decade_start = random.choice([1970, 1980, 1990, 2000, 2010])
            year_filter = f" year:{decade_start}-{decade_start+9}"
            
        results = spotify.search(
            q=f"genre:{genre}{year_filter}",
            type="track",
            limit=random.randint(2, 4)  # Random number of tracks per genre
        )

        for item in results["tracks"]["items"]:
            track_uris.append(item["uri"])
    
    # Calculate transition parameters with slight randomization
    mid_energy = (initial_energy + target_params["target_energy"]) / 2
    mid_energy = mid_energy * random.uniform(0.9, 1.1)
    mid_energy = max(0.0, min(1.0, mid_energy))
    
    mid_valence = (initial_valence + target_params["target_valence"]) / 2
    mid_valence = mid_valence * random.uniform(0.9, 1.1)
    mid_valence = max(0.0, min(1.0, mid_valence))

    # Get recommendations for transition tracks
    seed_tracks = random.sample(track_uris, min(2, len(track_uris))) if track_uris else None
    if seed_tracks:
        try:
            recommendations = spotify.recommendations(
                seed_tracks=seed_tracks,
                target_energy=mid_energy,
                target_valence=mid_valence,
                limit=random.randint(4, 6)  # Random number of transition tracks
            )
            
            for track in recommendations["tracks"]:
                track_uris.append(track["uri"])
        except Exception as e:
            # Fallback if recommendations fail
            fallback_genres = ["electronic", "indie", "alternative"]
            genre = random.choice(fallback_genres)
            results = spotify.search(
                q=f"genre:{genre}",
                type="track",
                limit=5
            )

            for item in results["tracks"]["items"]:
                track_uris.append(item["uri"])
    
    # Randomly select genres for target mood (2-3 genres)
    target_genres = random.sample(target_params["genres"], 
                                min(random.randint(2, 3), len(target_params["genres"])))
    
    # Get tracks for target mood
    for genre in target_genres:
        # Add random popularity filter occasionally
        popularity_filter = ""
        if random.random() > 0.5:
            min_pop = random.randint(50, 80)
            popularity_filter = f" popularity:{min_pop}-100"
            
        results = spotify.search(
            q=f"genre:{genre}{popularity_filter}",
            type="track",
            limit=random.randint(2, 4)  # Random number of tracks per genre
        )

        for item in results["tracks"]["items"]:
            track_uris.append(item["uri"])
    
    # Remove duplicates while preserving order
    unique_tracks = []
    seen = set()
    for uri in track_uris:
        if uri not in seen:
            unique_tracks.append(uri)
            seen.add(uri)
    
    return unique_tracks