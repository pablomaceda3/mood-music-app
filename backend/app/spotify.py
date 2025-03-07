import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse

# Create a router for Spotify endpoints
spotify_router = APIRouter()

# Environment variables for Spotify Credentials
SPOTIFY_CLIENT_ID = "your-client-id"
SPOTIFY_CLIENT_SECRET = "your-client-secret"
SPOTIFY_REDIRECT_URI = "http://localhost:5173/api/spotify/callback"
SCOPE = "playlist-modify-private playlist-modify-public"

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