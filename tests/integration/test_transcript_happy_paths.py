"""Integration tests for happy path scenarios (Scenarios 1-3).

Tests from quickstart.md Scenarios 1-3: successful transcript retrieval
with different video identifier formats.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch


VALID_VIDEO_ID = "dQw4w9WgXcQ"
VALID_FULL_URL = f"https://www.youtube.com/watch?v={VALID_VIDEO_ID}"
VALID_SHORT_URL = f"https://youtu.be/{VALID_VIDEO_ID}"

MOCK_TRANSCRIPT = [
    {"text": "We're no strangers to love", "start": 0.0, "duration": 2.5},
    {"text": "You know the rules and so do I", "start": 2.5, "duration": 3.0},
    {"text": "A full commitment's what I'm thinking of", "start": 5.5, "duration": 3.5},
]


@pytest.fixture
def mock_youtube_api():
    """Mock youtube_transcript_api for happy path tests."""
    with patch("src.services.transcript_service.YouTubeTranscriptApi") as mock:
        mock.get_transcript.return_value = MOCK_TRANSCRIPT
        yield mock


@pytest.mark.asyncio
class TestHappyPaths:
    """Integration tests for successful transcript retrieval."""

    async def test_scenario_1_raw_video_id(
        self, async_client: AsyncClient, test_api_key: str, mock_youtube_api
    ):
        """Scenario 1: Raw video ID retrieves transcript successfully."""
        from src.main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/transcript",
                json={"video_identifier": VALID_VIDEO_ID},
                headers={"X-API-Key": test_api_key},
            )

        # Validate response
        assert response.status_code == 200
        data = response.json()
        
        # Validate data structure
        assert data["data"] is not None
        assert data["error"] is None
        assert data["data"]["video_id"] == VALID_VIDEO_ID
        assert isinstance(data["data"]["segments"], list)
        assert len(data["data"]["segments"]) > 0
        
        # Validate segments
        first_segment = data["data"]["segments"][0]
        assert "text" in first_segment
        assert "start" in first_segment
        assert "duration" in first_segment
        assert isinstance(first_segment["start"], (int, float))
        assert isinstance(first_segment["duration"], (int, float))
        
        # Validate metadata
        assert data["metadata"]["request_id"] is not None
        assert data["metadata"]["timestamp"] is not None
        assert data["metadata"]["version"] is not None

    async def test_scenario_2_full_youtube_url(
        self, async_client: AsyncClient, test_api_key: str, mock_youtube_api
    ):
        """Scenario 2: Full YouTube URL works and extracts video ID."""
        from src.main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/transcript",
                json={"video_identifier": VALID_FULL_URL},
                headers={"X-API-Key": test_api_key},
            )

        # Validate response
        assert response.status_code == 200
        data = response.json()
        
        # System should extract video ID from URL
        assert data["data"]["video_id"] == VALID_VIDEO_ID
        assert data["data"]["segments"] is not None
        assert len(data["data"]["segments"]) > 0

    async def test_scenario_3_short_youtube_url(
        self, async_client: AsyncClient, test_api_key: str, mock_youtube_api
    ):
        """Scenario 3: Short youtu.be URL works and extracts video ID."""
        from src.main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/transcript",
                json={"video_identifier": VALID_SHORT_URL},
                headers={"X-API-Key": test_api_key},
            )

        # Validate response
        assert response.status_code == 200
        data = response.json()
        
        # System should extract video ID from short URL
        assert data["data"]["video_id"] == VALID_VIDEO_ID
        assert data["data"]["segments"] is not None
        
        # Response should be identical to using raw video ID
        assert data["error"] is None
        assert "metadata" in data

    async def test_complete_transcript_structure(
        self, async_client: AsyncClient, test_api_key: str, mock_youtube_api
    ):
        """Validate complete transcript data structure."""
        from src.main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/transcript",
                json={"video_identifier": VALID_VIDEO_ID},
                headers={"X-API-Key": test_api_key},
            )

        data = response.json()
        transcript = data["data"]
        
        # Validate all required fields
        assert "video_id" in transcript
        assert "language" in transcript
        assert "is_generated" in transcript
        assert "segments" in transcript
        assert "total_duration" in transcript
        assert "segment_count" in transcript
        assert "retrieved_at" in transcript
        
        # Validate types
        assert isinstance(transcript["video_id"], str)
        assert isinstance(transcript["language"], str)
        assert isinstance(transcript["is_generated"], bool)
        assert isinstance(transcript["segments"], list)
        assert isinstance(transcript["total_duration"], (int, float))
        assert isinstance(transcript["segment_count"], int)
