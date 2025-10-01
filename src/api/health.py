"""Health check endpoint."""

from datetime import datetime
from fastapi import APIRouter, Response, status
from src.config import settings
from src.models.health import HealthStatus


router = APIRouter()


def check_api_health() -> bool:
    """Check if API is running (always true if this code executes)."""
    return True


def check_youtube_library() -> bool:
    """Check if youtube-transcript-api library can be imported."""
    try:
        import youtube_transcript_api
        return True
    except ImportError:
        return False


@router.get("/health", response_model=HealthStatus, tags=["Health"])
async def health_check(response: Response) -> HealthStatus:
    """Health check endpoint for monitoring service availability.
    
    Returns 200 for healthy/degraded, 503 for unhealthy.
    Does not require authentication.
    
    Returns:
        HealthStatus with component checks
    """
    # Perform health checks
    api_healthy = check_api_health()
    youtube_lib_healthy = check_youtube_library()
    
    # Determine overall status
    checks = {
        "api": api_healthy,
        "youtube_transcript_library": youtube_lib_healthy,
    }
    
    if api_healthy and youtube_lib_healthy:
        overall_status = "healthy"
        response.status_code = status.HTTP_200_OK
    elif api_healthy:
        overall_status = "degraded"
        response.status_code = status.HTTP_200_OK
    else:
        overall_status = "unhealthy"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return HealthStatus(
        status=overall_status,
        timestamp=datetime.utcnow(),
        checks=checks,
        version=settings.app_version,
    )
