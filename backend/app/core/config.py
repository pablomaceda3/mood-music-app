import os
import certifi
from pathlib import Path
from pydantic import BaseSettings, PosgresDsn, validator
from typing import Any, Dict, Optional
from spotipy.cache_handler import CacheFileHandler

class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Mood Transitions API"
    DEBUG: bool = False


    # CORS Configuration
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173"]


    # Database Configuration
    DATABASE_URL: PostgresDsn = "postgresql://postgres:password@localhost:5432/mood_transitions"


    # Spotify Configuration
    SPOTIFY_CLIENT_ID: Optional[str] = None
    SPOTIFY_CLIENT_SECRET: Optional[str] = None
    SPOTIFY_REDIRECT_URI: str = "http://localhost:8000/api/v1/spotify/callback"
    SPOTIFY_SCOPE: str = "playlist-modify-private playlist-modify-public"
    SPOTIFY_CACHE_PATH: str = "/app/.spotify_cache"

    # Frontend URL for redirects
    FRONTEND_URL: str = "http://localhost:5173"


    # SSL Configuration
    SSL_CERT_FILE: str = certiif.where()

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
            host=os.getenv("POSTGRES_HOST", "postgres"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            path=f"/{os.getenv('POSTGRES_DB', 'mood_transitions')}",
        )
        
    @property
    def SPOTIFY_CACHE_HANDLER(self):
        """Create a Spotify cache handler instance."""
        Path(self.SPOTIFY_CACHE_PATH).parent.mkdir(parents=True, exist_ok=True)
        return CacheFileHandler(cache_path=self.SPOTIFY_CACHE_PATH)

    class Config:
        """Configuration for the settings class."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()

# Set environment variables for SSL certificates
os.environ["SSL_CERT_FILE"] = settings.SSL_CERT_FILE
os.environ["REQUESTS_CA_BUNDLE"] = settings.SSL_CERT_FILE