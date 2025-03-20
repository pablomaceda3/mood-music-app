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
    """Get tracks that match the mood transition.
    Returns a list of Spotify track URIs.
    """
    mood_features = {
        "Angry": {"target_energy": 0.8, "target_valence": 0.2, "genres": ["metal", "punk", "hard-rock"]},
        "Happy": {"target_energy": 0.7, "target_valence": 0.8, "genres": ["pop", "dance", "happy"]},
        "Sad": {"target_energy": 0.4, "target_valence": 0.2, "genres": ["sad", "indie", "chill"]},
        "Indifferent": {"target_energy": 0.5, "target_valence": 0.5, "genres": ["ambient", "study", "focus"]}
    }

    initial_params = mood_features.get(initial_mood.name, mood_features["Indifferent"])
    target_params = mood_features.get(target_mood.name, mood_features["Indifferent"])

    track_uris = []

    for genre in initial_params["genres"]:
        results = spotify.search(
            q=f"genre:{genre}",
            type="track",
            limit=3
        )

        for item in results["tracks"]["items"]:
            track_uris.append(item["uri"])
    
    mid_energy = (initial_params["target_energy"] + target_params["target_energy"]) / 2
    mid_valence = (initial_params["target_valence"] + target_params["target_valence"]) / 2

    seed_tracks = track_uris[:2] if track_uris else None
    if seed_tracks:
        try:
            recommendations = spotify.recommendations(
                seed_tracks=seed_tracks,
                target_energy=mid_energy,
                target_valence=mid_valence,
                limit=5
            )
        except:
            results = spotify.search(
                q="genre:electronic",
                type="track",
                limit=5
            )

            for item in results["tracks"]["items"]:
                track_uris.append(item["uri"])
    else:
        results = spotify.search(
            q="genre:electronic",
            type="track",
            limit=5
        )

        for item in results["tracks"]["items"]:
            track_uris.append(item["uri"])
    
    for genre in target_params["genres"]:
        results = spotify.search(
            q=f"genre:{genre}",
            type="track",
            limit=3
        )

        for item in results["tracks"]["items"]:
            track_uris.append(item["uri"])
    
    return list(dict.fromkeys(track_uris))