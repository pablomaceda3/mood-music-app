from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from app.core.config import settings
from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    Creates a new SQLAlchemy session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_spotify_client() -> spotipy.Spotify:
    """
    Dependency for getting an authenticated Spotify client.
    Raises HTTPException if authentication is required or fails.
    """
    try:
        sp_oauth = SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIFY_REDIRECT_URI,
            scope=settings.SPOTIFY_SCOPE,
            cache_handler=settings.SPOTIFY_CACHE_HANDLER
        )

        token_info = sp_oauth.get_cached_token()
        if not token_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Spotify authentication required"
            )

        if sp_oauth.is_token_expired(token_info):
            token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])

        return spotipy.Spotify(auth=token_info["access_token"])
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating Spotify client: {e}"
        )