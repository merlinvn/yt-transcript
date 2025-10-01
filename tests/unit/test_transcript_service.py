"""Unit tests for transcript service."""

import pytest
from unittest.mock import patch, MagicMock
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
from src.services.transcript_service import get_transcript
from src.utils.exceptions import (
    VideoNotFoundError,
    TranscriptUnavailableError,
    ServiceUnavailableError,
    TranscriptTimeoutError,
)


# Mock raw data as returned by to_raw_data()
MOCK_RAW_DATA = [
    {"text": "Hello world", "start": 0.0, "duration": 2.0},
    {"text": "Test transcript", "start": 2.0, "duration": 3.0},
]

# Mock metadata
MOCK_METADATA = (MOCK_RAW_DATA, "English", "en", False)


@pytest.mark.asyncio
class TestTranscriptService:
    """Unit tests for get_transcript function."""

    async def test_successful_transcript_retrieval(self):
        """Test successful transcript retrieval."""
        with patch("src.services.transcript_service._fetch_transcript_sync") as mock:
            mock.return_value = MOCK_METADATA
            
            result = await get_transcript("dQw4w9WgXcQ")
            
            assert result.video_id == "dQw4w9WgXcQ"
            assert len(result.segments) == 2
            assert result.segments[0].text == "Hello world"
            assert result.total_duration == 5.0
            assert result.segment_count == 2
            assert result.language == "en"
            assert result.is_generated == False

    async def test_video_not_found_raises_error(self):
        """Test that VideoUnavailable raises VideoNotFoundError."""
        with patch("src.services.transcript_service._fetch_transcript_sync") as mock:
            mock.side_effect = VideoUnavailable("Video not found")
            
            with pytest.raises(VideoNotFoundError):
                await get_transcript("nonexistent")

    async def test_transcripts_disabled_raises_error(self):
        """Test that TranscriptsDisabled raises TranscriptUnavailableError."""
        with patch("src.services.transcript_service._fetch_transcript_sync") as mock:
            mock.side_effect = TranscriptsDisabled("video_id")
            
            with pytest.raises(TranscriptUnavailableError):
                await get_transcript("dQw4w9WgXcQ")

    async def test_no_transcript_found_raises_error(self):
        """Test that NoTranscriptFound raises TranscriptUnavailableError."""
        with patch("src.services.transcript_service._fetch_transcript_sync") as mock:
            mock.side_effect = NoTranscriptFound("video_id", [], None)
            
            with pytest.raises(TranscriptUnavailableError):
                await get_transcript("dQw4w9WgXcQ")

    async def test_timeout_raises_error(self):
        """Test that timeout raises TranscriptTimeoutError."""
        import asyncio
        
        with patch("src.services.transcript_service._fetch_transcript_sync") as mock:
            with patch("src.services.transcript_service.settings.timeout_seconds", 1):
                with patch("src.services.transcript_service.settings.max_retries", 1):
                    
                    async def slow_fetch(*args):
                        await asyncio.sleep(2)
                        return MOCK_METADATA
                    
                    mock.side_effect = lambda *args: asyncio.sleep(2)
                    
                    with pytest.raises((TranscriptTimeoutError, ServiceUnavailableError)):
                        await get_transcript("dQw4w9WgXcQ")

    async def test_retry_logic_with_exponential_backoff(self):
        """Test that service retries with exponential backoff."""
        with patch("src.services.transcript_service._fetch_transcript_sync") as mock:
            with patch("src.services.transcript_service.settings.max_retries", 3):
                # Fail twice, succeed on third attempt
                mock.side_effect = [
                    Exception("Temporary error"),
                    Exception("Temporary error"),
                    MOCK_METADATA,
                ]
                
                result = await get_transcript("dQw4w9WgXcQ")
                
                # Should eventually succeed
                assert result.video_id == "dQw4w9WgXcQ"
                assert mock.call_count == 3

    async def test_service_unavailable_after_retries(self):
        """Test that ServiceUnavailableError raised after max retries."""
        with patch("src.services.transcript_service._fetch_transcript_sync") as mock:
            with patch("src.services.transcript_service.settings.max_retries", 3):
                # Fail all attempts
                mock.side_effect = Exception("Persistent error")
                
                with pytest.raises(ServiceUnavailableError):
                    await get_transcript("dQw4w9WgXcQ")
                
                # Should have tried 3 times
                assert mock.call_count == 3

    async def test_transcript_model_fields(self):
        """Test that transcript model has all required fields."""
        with patch("src.services.transcript_service._fetch_transcript_sync") as mock:
            mock.return_value = MOCK_METADATA
            
            result = await get_transcript("dQw4w9WgXcQ")
            
            # Check all required fields exist
            assert hasattr(result, "video_id")
            assert hasattr(result, "language")
            assert hasattr(result, "is_generated")
            assert hasattr(result, "segments")
            assert hasattr(result, "total_duration")
            assert hasattr(result, "segment_count")
            assert hasattr(result, "retrieved_at")
            
            # Validate segment structure
            segment = result.segments[0]
            assert hasattr(segment, "text")
            assert hasattr(segment, "start")
            assert hasattr(segment, "duration")
            
            # Validate metadata extraction
            assert result.language == "en"
            assert result.is_generated == False
