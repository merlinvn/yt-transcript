"""Transcript service for retrieving YouTube transcripts.

Uses youtube-transcript-api package to fetch transcripts with retry logic
and proper error handling.
"""

import asyncio
from datetime import datetime
from typing import List
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)

from src.config import settings
from src.models.transcript import Transcript, TranscriptSegment
from src.utils.exceptions import (
    VideoNotFoundError,
    TranscriptUnavailableError,
    ServiceUnavailableError,
    TranscriptTimeoutError,
)


async def get_transcript(video_id: str) -> Transcript:
    """Retrieve transcript for a YouTube video.
    
    Implements:
    - 30-second timeout
    - 3 retries with exponential backoff
    - Proper error mapping from youtube-transcript-api exceptions
    
    Args:
        video_id: 11-character YouTube video ID
        
    Returns:
        Transcript model with segments and metadata
        
    Raises:
        VideoNotFoundError: Video doesn't exist
        TranscriptUnavailableError: Video exists but no transcript
        ServiceUnavailableError: YouTube service temporarily down
        TranscriptTimeoutError: Request exceeded timeout
    """
    max_retries = settings.max_retries
    timeout = settings.timeout_seconds
    
    for attempt in range(max_retries):
        try:
            # Wrap sync API call in async
            transcript_list = await asyncio.wait_for(
                asyncio.to_thread(_fetch_transcript_sync, video_id),
                timeout=timeout,
            )
            
            # Convert to our model
            return _build_transcript_model(video_id, transcript_list)
            
        except asyncio.TimeoutError:
            if attempt == max_retries - 1:
                raise TranscriptTimeoutError(
                    f"Transcript retrieval exceeded {timeout}s timeout",
                    f"Failed after {max_retries} attempts with {timeout}s timeout each",
                )
            # Exponential backoff: 1s, 2s, 4s
            await asyncio.sleep(2**attempt)
            
        except VideoUnavailable:
            # Don't retry for video not found
            raise VideoNotFoundError(
                "Video not found or does not exist",
                f"The video ID '{video_id}' could not be found on YouTube",
            )
            
        except (TranscriptsDisabled, NoTranscriptFound):
            # Don't retry for no transcript
            raise TranscriptUnavailableError(
                "No transcript available for this video",
                "This video may have captions disabled, be too new, or be private/age-restricted",
            )
            
        except Exception as e:
            if attempt == max_retries - 1:
                # Final attempt failed
                raise ServiceUnavailableError(
                    "YouTube service temporarily unavailable",
                    f"Unable to retrieve transcript after {max_retries} retry attempts: {str(e)}",
                )
            # Exponential backoff
            await asyncio.sleep(2**attempt)
    
    # Should never reach here, but just in case
    raise ServiceUnavailableError(
        "YouTube service temporarily unavailable",
        f"Failed after {max_retries} attempts",
    )


def _fetch_transcript_sync(video_id: str) -> List[dict]:
    """Synchronous wrapper for youtube-transcript-api call.
    
    This is called via asyncio.to_thread() to avoid blocking.
    """
    return YouTubeTranscriptApi.get_transcript(video_id)


def _build_transcript_model(video_id: str, transcript_list: List[dict]) -> Transcript:
    """Build Transcript model from youtube-transcript-api response.
    
    Args:
        video_id: Video ID
        transcript_list: List of dicts with 'text', 'start', 'duration' keys
        
    Returns:
        Transcript model
    """
    segments = [
        TranscriptSegment(
            text=item["text"],
            start=item["start"],
            duration=item["duration"],
        )
        for item in transcript_list
    ]
    
    total_duration = sum(seg.duration for seg in segments)
    
    # Note: youtube-transcript-api doesn't provide language info consistently,
    # so we default to 'en' and assume auto-generated unless proven otherwise
    return Transcript(
        video_id=video_id,
        language="en",  # Default, would need additional API call to determine
        is_generated=True,  # youtube-transcript-api typically returns auto-generated
        segments=segments,
        total_duration=total_duration,
        segment_count=len(segments),
        retrieved_at=datetime.utcnow(),
    )
