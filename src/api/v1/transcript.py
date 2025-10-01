"""Transcript API endpoint."""

import time
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from src.models.request import VideoIdentifierInput
from src.models.response import APIResponse, ErrorDetail, ResponseMetadata
from src.models.transcript import Transcript
from src.services.video_id_parser import extract_video_id
from src.services.transcript_service import get_transcript
from src.api.dependencies import verify_api_key, get_request_id
from src.utils.exceptions import (
    InvalidVideoIdError,
    VideoNotFoundError,
    TranscriptUnavailableError,
    ServiceUnavailableError,
    TranscriptTimeoutError,
)
from src.config import settings


router = APIRouter(prefix="/api/v1", tags=["Transcript"])


@router.post("/transcript", response_model=APIResponse[Transcript])
async def get_video_transcript(
    video_input: VideoIdentifierInput,
    api_key_hash: str = Depends(verify_api_key),
    request_id: str = Depends(get_request_id),
) -> APIResponse[Transcript]:
    """Retrieve transcript for a YouTube video.
    
    Accepts video ID in multiple formats:
    - Raw 11-character ID
    - Full YouTube URL
    - Short youtu.be URL
    
    Args:
        video_input: Video identifier input
        api_key_hash: Hashed API key (from dependency)
        request_id: Request ID (from dependency)
        
    Returns:
        APIResponse with transcript data or error
    """
    start_time = time.time()
    
    try:
        # Extract video ID from input
        video_id = extract_video_id(video_input.video_identifier)
        
        # Get transcript
        transcript = await get_transcript(video_id)
        
        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Build success response
        return APIResponse(
            data=transcript,
            error=None,
            metadata=ResponseMetadata(
                request_id=request_id,
                timestamp=datetime.utcnow(),
                duration_ms=duration_ms,
                version=settings.app_version,
            ),
        )
        
    except InvalidVideoIdError as exc:
        # 400 Bad Request - Invalid format
        duration_ms = int((time.time() - start_time) * 1000)
        raise HTTPException(
            status_code=400,
            detail={
                "data": None,
                "error": {
                    "code": "INVALID_VIDEO_ID",
                    "message": exc.message,
                    "details": exc.details,
                },
                "metadata": {
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "duration_ms": duration_ms,
                    "version": settings.app_version,
                },
            },
        )
        
    except VideoNotFoundError as exc:
        # 404 Not Found - Video doesn't exist
        duration_ms = int((time.time() - start_time) * 1000)
        raise HTTPException(
            status_code=404,
            detail={
                "data": None,
                "error": {
                    "code": "VIDEO_NOT_FOUND",
                    "message": exc.message,
                    "details": exc.details,
                },
                "metadata": {
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "duration_ms": duration_ms,
                    "version": settings.app_version,
                },
            },
        )
        
    except TranscriptUnavailableError as exc:
        # 404 Not Found - No transcript available
        duration_ms = int((time.time() - start_time) * 1000)
        raise HTTPException(
            status_code=404,
            detail={
                "data": None,
                "error": {
                    "code": "TRANSCRIPT_UNAVAILABLE",
                    "message": exc.message,
                    "details": exc.details,
                },
                "metadata": {
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "duration_ms": duration_ms,
                    "version": settings.app_version,
                },
            },
        )
        
    except (ServiceUnavailableError, TranscriptTimeoutError) as exc:
        # 503 Service Unavailable
        duration_ms = int((time.time() - start_time) * 1000)
        raise HTTPException(
            status_code=503,
            detail={
                "data": None,
                "error": {
                    "code": "SERVICE_UNAVAILABLE",
                    "message": exc.message,
                    "details": exc.details,
                },
                "metadata": {
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "duration_ms": duration_ms,
                    "version": settings.app_version,
                },
            },
        )
        
    except Exception as exc:
        # 500 Internal Server Error
        duration_ms = int((time.time() - start_time) * 1000)
        raise HTTPException(
            status_code=500,
            detail={
                "data": None,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": f"The error has been logged. Please contact support with request ID if the issue persists. Error: {str(exc)}",
                },
                "metadata": {
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "duration_ms": duration_ms,
                    "version": settings.app_version,
                },
            },
        )
