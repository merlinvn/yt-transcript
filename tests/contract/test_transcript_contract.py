"""Contract tests for POST /api/v1/transcript endpoint.

These tests validate the API contract as specified in contracts/get-transcript.md.
Tests MUST fail initially (RED phase) before implementation.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock


# Test data
VALID_VIDEO_ID = "dQw4w9WgXcQ"
VALID_FULL_URL = f"https://www.youtube.com/watch?v={VALID_VIDEO_ID}"
VALID_SHORT_URL = f"https://youtu.be/{VALID_VIDEO_ID}"
INVALID_VIDEO_ID = "invalid!!!"
NONEXISTENT_VIDEO_ID = "xxxxxxxxxxx"

MOCK_TRANSCRIPT = [
    {"text": "We're no strangers to love", "start": 0.0, "duration": 2.5},
    {"text": "You know the rules and so do I", "start": 2.5, "duration": 3.0},
]


@pytest.fixture
def mock_youtube_transcript():
    """Mock youtube_transcript_api responses."""
    with patch("src.services.transcript_service.YouTubeTranscriptApi") as mock_class:
        mock_instance = mock_class.return_value
        mock_instance.fetch.return_value = [
            MagicMock(text="We're no strangers to love", start=0.0, duration=2.5),
            MagicMock(text="You know the rules and so do I", start=2.5, duration=3.0),
        ]
        yield mock_class


@pytest.mark.asyncio
class TestTranscriptContract:
    """Contract tests for transcript endpoint."""

    async def test_tc001_valid_raw_video_id(
        self, async_client: AsyncClient, test_api_key: str, mock_youtube_transcript
    ):
        """TC-001: Valid raw video ID returns 200 with transcript data."""
        from src.main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/transcript",
                json={"video_identifier": VALID_VIDEO_ID},
                headers={"X-API-Key": test_api_key},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["data"] is not None
        assert data["error"] is None
        assert data["data"]["video_id"] == VALID_VIDEO_ID
        assert isinstance(data["data"]["segments"], list)
        assert len(data["data"]["segments"]) > 0
        assert "metadata" in data
        assert "request_id" in data["metadata"]

    async def test_tc002_valid_full_youtube_url(
        self, async_client: AsyncClient, test_api_key: str, mock_youtube_transcript
    ):
        """TC-002: Valid full YouTube URL returns 200 with transcript data."""
        from src.main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/transcript",
                json={"video_identifier": VALID_FULL_URL},
                headers={"X-API-Key": test_api_key},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["video_id"] == VALID_VIDEO_ID

    async def test_tc003_valid_short_youtube_url(
        self, async_client: AsyncClient, test_api_key: str, mock_youtube_transcript
    ):
        """TC-003: Valid short YouTube URL returns 200 with transcript data."""
        from src.main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/transcript",
                json={"video_identifier": VALID_SHORT_URL},
                headers={"X-API-Key": test_api_key},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["video_id"] == VALID_VIDEO_ID

    async def test_tc004_invalid_video_id_format(
        self, async_client: AsyncClient, test_api_key: str
    ):
        """TC-004: Invalid video ID format returns 400 Bad Request."""
        from src.main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/transcript",
                json={"video_identifier": INVALID_VIDEO_ID},
                headers={"X-API-Key": test_api_key},
            )

        assert response.status_code == 400
        data = response.json()
        assert data["data"] is None
        assert data["error"] is not None
        assert data["error"]["code"] == "INVALID_VIDEO_ID"
        assert "metadata" in data

    async def test_tc005_missing_api_key(self, async_client: AsyncClient):
        """TC-005: Missing API key returns 401 Unauthorized."""
        from src.main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/transcript",
                json={"video_identifier": VALID_VIDEO_ID},
            )

        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "INVALID_API_KEY"

    async def test_tc006_invalid_api_key(self, async_client: AsyncClient):
        """TC-006: Invalid API key returns 401 Unauthorized."""
        from src.main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/transcript",
                json={"video_identifier": VALID_VIDEO_ID},
                headers={"X-API-Key": "invalid-key"},
            )

        assert response.status_code == 401

    async def test_tc007_nonexistent_video(
        self, async_client: AsyncClient, test_api_key: str
    ):
        """TC-007: Non-existent video returns 404 Not Found."""
        from src.main import app
        from youtube_transcript_api._errors import VideoUnavailable
        
        with patch("src.services.transcript_service.YouTubeTranscriptApi") as mock_class:
            mock_instance = mock_class.return_value
            mock_instance.fetch.side_effect = VideoUnavailable("Video not found")
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/transcript",
                    json={"video_identifier": NONEXISTENT_VIDEO_ID},
                    headers={"X-API-Key": test_api_key},
                )

        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "VIDEO_NOT_FOUND"

    async def test_tc008_video_without_transcript(
        self, async_client: AsyncClient, test_api_key: str
    ):
        """TC-008: Video without transcript returns 404 with specific error."""
        from src.main import app
        from youtube_transcript_api._errors import TranscriptsDisabled
        
        with patch("src.services.transcript_service.YouTubeTranscriptApi") as mock_class:
            mock_instance = mock_class.return_value
            mock_instance.fetch.side_effect = TranscriptsDisabled("video_id")
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/transcript",
                    json={"video_identifier": VALID_VIDEO_ID},
                    headers={"X-API-Key": test_api_key},
                )

        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "TRANSCRIPT_UNAVAILABLE"

    async def test_tc009_concurrent_requests(
        self, async_client: AsyncClient, test_api_key: str, mock_youtube_transcript
    ):
        """TC-009: Concurrent requests process independently."""
        from src.main import app
        import asyncio
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Send 10 concurrent requests
            tasks = [
                client.post(
                    "/api/v1/transcript",
                    json={"video_identifier": VALID_VIDEO_ID},
                    headers={"X-API-Key": test_api_key},
                )
                for _ in range(10)
            ]
            responses = await asyncio.gather(*tasks)

        # All should succeed
        assert all(r.status_code == 200 for r in responses)
        
        # All should have unique request IDs
        request_ids = [r.json()["metadata"]["request_id"] for r in responses]
        assert len(set(request_ids)) == 10

    async def test_tc010_response_contains_request_id(
        self, async_client: AsyncClient, test_api_key: str, mock_youtube_transcript
    ):
        """TC-010: Response metadata contains request_id."""
        from src.main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/transcript",
                json={"video_identifier": VALID_VIDEO_ID},
                headers={"X-API-Key": test_api_key},
            )

        data = response.json()
        assert "metadata" in data
        assert "request_id" in data["metadata"]
        assert "timestamp" in data["metadata"]
        assert "duration_ms" in data["metadata"]
        assert "version" in data["metadata"]
