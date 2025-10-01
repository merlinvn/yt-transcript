"""Transcript service for retrieving YouTube transcripts.

Uses youtube-transcript-api package to fetch transcripts with retry logic
and proper error handling.
"""

import asyncio
from datetime import datetime
from typing import List
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
from youtube_transcript_api.proxies import GenericProxyConfig
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    YouTubeRequestFailed,
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
            transcript_data = await asyncio.wait_for(
                asyncio.to_thread(_fetch_transcript_sync, video_id),
                timeout=timeout,
            )

            # Convert to our model
            return _build_transcript_model(video_id, transcript_data)

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

        except YouTubeRequestFailed as e:
            if attempt == max_retries - 1:
                # Final attempt failed
                raise ServiceUnavailableError(
                    "YouTube service temporarily unavailable",
                    f"YouTube API request failed after {max_retries} attempts: {str(e)}",
                )
            # Exponential backoff
            await asyncio.sleep(2**attempt)

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


def _fetch_transcript_sync(video_id: str) -> tuple:
    """Synchronous wrapper for youtube-transcript-api call.

    This is called via asyncio.to_thread() to avoid blocking.

    Returns:
        Tuple of (raw_data, language, language_code, is_generated)
    """
    proxy_config = None
    if settings.proxy_username and settings.proxy_password:
        proxy_config = WebshareProxyConfig(
            proxy_username=settings.proxy_username,
            proxy_password=settings.proxy_password,
        )
    
    api = YouTubeTranscriptApi(proxy_config=proxy_config)

    result = api.fetch(video_id)

    # Use the official to_raw_data() method as per documentation
    raw_data = result.to_raw_data()

    # Extract metadata from FetchedTranscript object
    language = getattr(result, "language", "en")
    language_code = getattr(result, "language_code", "en")
    is_generated = getattr(result, "is_generated", True)

    return raw_data, language, language_code, is_generated


def _build_transcript_model(video_id: str, transcript_data: tuple) -> Transcript:
    """Build Transcript model from youtube-transcript-api response.

    Args:
        video_id: Video ID
        transcript_data: Tuple of (raw_data, language, language_code, is_generated)

    Returns:
        Transcript model
    """
    transcript_list, language, language_code, is_generated = transcript_data

    segments = [
        TranscriptSegment(
            text=item["text"],
            start=item["start"],
            duration=item["duration"],
        )
        for item in transcript_list
    ]

    total_duration = sum(seg.duration for seg in segments)

    return Transcript(
        video_id=video_id,
        language=language_code,  # Use actual language code from API
        is_generated=is_generated,  # Use actual value from API
        segments=segments,
        total_duration=total_duration,
        segment_count=len(segments),
        retrieved_at=datetime.utcnow(),
    )
