"""
Custom exception classes and handlers for consistent error responses.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError


class EduTrackException(Exception):
    """Base exception for EduTrack application."""
    
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class AuthenticationError(EduTrackException):
    """Raised when authentication fails."""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=401, detail=detail)


class AuthorizationError(EduTrackException):
    """Raised when user lacks required permissions."""
    
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(status_code=403, detail=detail)


class ResourceNotFoundError(EduTrackException):
    """Raised when requested resource not found."""
    
    def __init__(self, resource: str):
        super().__init__(status_code=404, detail=f"{resource} not found")


class ValidationError(EduTrackException):
    """Raised when input validation fails."""
    
    def __init__(self, detail: str):
        super().__init__(status_code=422, detail=detail)


class ConflictError(EduTrackException):
    """Raised when resource already exists or state conflict."""
    
    def __init__(self, detail: str):
        super().__init__(status_code=409, detail=detail)


class ServerError(EduTrackException):
    """Raised for unexpected server errors."""
    
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(status_code=500, detail=detail)


def register_exception_handlers(app: FastAPI):
    """Register all custom exception handlers with FastAPI app."""
    
    @app.exception_handler(EduTrackException)
    async def edutrack_exception_handler(request: Request, exc: EduTrackException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error": exc.detail,
                "path": str(request.url.path),
            },
        )
    
    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error": "Validation failed",
                "detail": exc.detail,
                "path": str(request.url.path),
            },
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "error": "Internal server error",
                "detail": str(exc) if app.debug else "An unexpected error occurred",
                "path": str(request.url.path),
            },
        )
