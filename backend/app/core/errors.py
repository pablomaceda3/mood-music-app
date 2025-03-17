"""Custom exception classes and error handlers for the application."""
from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class AppError(HTTPException):
    """Base class for application-specific HTTP exceptions."""
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers
        )

class NotFoundError(AppError):
    """Resource not found error."""
    def __init__(
        self,
        detail: Any = "Resource not found",
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            headers=headers,
        )


class UnauthorizedError(AppError):
    """Unauthorized access error."""
    def __init__(
        self,
        detail: Any = "Not authenticated",
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        if headers is None:
            headers = {}
        headers["WWW-Authenticate"] = "Bearer"
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers=headers,
        )


class ForbiddenError(AppError):
    """Forbidden access error."""
    def __init__(
        self,
        detail: Any = "Not authorized to perform this action",
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            headers=headers,
        )


class SpotifyError(AppError):
    """Spotify-specific error."""
    def __init__(
        self,
        detail: Any = "Spotify service error",
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            headers=headers,
        )