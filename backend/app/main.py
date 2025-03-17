import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.endpoints import mood, transitions, spotify
from app.db.session import engine
from app.db import base  # Import to register all models with SQLAlchemy

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for tracking mood transitions and creating Spotify playlists",
    version="1.0.0",
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    mood.router,
    prefix=f"{settings.API_V1_STR}/moods",
    tags=["moods"],
)
app.include_router(
    transitions.router,
    prefix=f"{settings.API_V1_STR}/transitions",
    tags=["transitions"],
)
app.include_router(
    spotify.router,
    prefix=f"{settings.API_V1_STR}/spotify",
    tags=["spotify"],
)

# Startup and shutdown events
@app.on_event("startup")
async def startup_db_client():
    """
    Initialize database and verify connections on startup.
    In a Docker environment, we need to handle potential delays
    in service availability.
    """
    logger.info("Starting application in Docker container")
    
    # In Docker, we might need to wait for the database to be ready
    if settings.DEBUG:
        # Create tables for development
        try:
            from app.db.base import Base
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
    
    required_env_vars = ["DATABASE_URL"]
    if settings.SPOTIFY_CLIENT_ID:
        logger.info("Spotify integration enabled")
    else:
        logger.warning("Spotify credentials not configured - integration disabled")

@app.on_event("shutdown")
async def shutdown_db_client():
    """
    Perform cleanup when the container is stopped.
    """
    logger.info("Shutting down application")
    # Any cleanup needed for container shutdown

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint to check if API is running.
    """
    return {
        "status": "online",
        "message": f"{settings.PROJECT_NAME} is running",
        "environment": "development" if settings.DEBUG else "production",
        "container_id": os.environ.get("HOSTNAME", "unknown"),
    }

# Health check endpoint for container orchestration
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for Docker health checks and monitoring.
    """
    # Add any health checks needed by Docker or orchestration tools
    try:
        # Check database connection
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "api_version": "1.0.0",
    }