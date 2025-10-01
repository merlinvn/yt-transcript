"""Integration tests for concurrent request handling (Scenario 9).

Tests from quickstart.md Scenario 9: concurrent request processing.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch
import asyncio


VALID_VIDEO_ID = "dQw4w9WgXcQ"
MOCK_TRANSCRIPT = [
    {"text": "Test transcript", "start": 0.0, "duration": 2.0},
]


@pytest.fixture
def mock_transcript_service():
    """Mock transcript service for concurrent tests."""
    with patch("src.services.transcript_service.get_transcript") as mock:
        mock.return_value = {
            "video_id": VALID_VIDEO_ID,
            "segments": MOCK_TRANSCRIPT,
            "language": "en",
            "is_generated": False,
        }
        yield mock


@pytest.mark.asyncio
class TestConcurrentRequests:
    """Integration tests for concurrent request handling."""

    async def test_scenario_9_concurrent_requests(
        self, async_client: AsyncClient, test_api_key: str, mock_transcript_service
    ):
        """Scenario 9: 10 concurrent requests all process successfully."""
        from src.main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Create 10 concurrent requests
            tasks = [
                client.post(
                    "/api/v1/transcript",
                    json={"video_identifier": VALID_VIDEO_ID},
                    headers={"X-API-Key": test_api_key},
                )
                for _ in range(10)
            ]
            
            # Execute concurrently
            responses = await asyncio.gather(*tasks)

        # All requests should succeed
        assert all(r.status_code == 200 for r in responses)
        
        # All responses should have data
        assert all(r.json()["data"] is not None for r in responses)
        assert all(r.json()["error"] is None for r in responses)

    async def test_unique_request_ids(
        self, async_client: AsyncClient, test_api_key: str, mock_transcript_service
    ):
        """Each concurrent request has unique request_id."""
        from src.main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            tasks = [
                client.post(
                    "/api/v1/transcript",
                    json={"video_identifier": VALID_VIDEO_ID},
                    headers={"X-API-Key": test_api_key},
                )
                for _ in range(10)
            ]
            
            responses = await asyncio.gather(*tasks)

        # Extract all request IDs
        request_ids = [r.json()["metadata"]["request_id"] for r in responses]
        
        # All request IDs should be unique
        assert len(request_ids) == 10
        assert len(set(request_ids)) == 10, "Request IDs should be unique"

    async def test_no_race_conditions(
        self, async_client: AsyncClient, test_api_key: str, mock_transcript_service
    ):
        """No race conditions or data corruption in concurrent requests."""
        from src.main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Send many concurrent requests
            tasks = [
                client.post(
                    "/api/v1/transcript",
                    json={"video_identifier": VALID_VIDEO_ID},
                    headers={"X-API-Key": test_api_key},
                )
                for _ in range(20)
            ]
            
            responses = await asyncio.gather(*tasks)

        # Verify all responses are valid and consistent
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            
            # Validate response structure
            assert "data" in data
            assert "error" in data
            assert "metadata" in data
            
            # No data corruption
            assert data["data"]["video_id"] == VALID_VIDEO_ID
            assert isinstance(data["metadata"]["request_id"], str)
            assert len(data["metadata"]["request_id"]) > 0

    async def test_average_response_time(
        self, async_client: AsyncClient, test_api_key: str, mock_transcript_service
    ):
        """Average response time under load < 5 seconds."""
        from src.main import app
        import time
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            start_time = time.time()
            
            tasks = [
                client.post(
                    "/api/v1/transcript",
                    json={"video_identifier": VALID_VIDEO_ID},
                    headers={"X-API-Key": test_api_key},
                )
                for _ in range(10)
            ]
            
            responses = await asyncio.gather(*tasks)
            
            total_time = time.time() - start_time

        # All should complete
        assert all(r.status_code == 200 for r in responses)
        
        # Average time per request should be reasonable
        avg_time = total_time / 10
        assert avg_time < 5.0, f"Average response time {avg_time:.2f}s exceeds 5s"

    async def test_different_videos_concurrent(
        self, async_client: AsyncClient, test_api_key: str, mock_transcript_service
    ):
        """Concurrent requests for different videos work independently."""
        from src.main import app
        
        video_ids = [f"video{i:03d}xxxx" for i in range(5)]
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            tasks = [
                client.post(
                    "/api/v1/transcript",
                    json={"video_identifier": vid},
                    headers={"X-API-Key": test_api_key},
                )
                for vid in video_ids
            ]
            
            responses = await asyncio.gather(*tasks)

        # All should process (success or failure)
        assert len(responses) == 5
        
        # Each response should have unique request ID
        request_ids = [r.json()["metadata"]["request_id"] for r in responses]
        assert len(set(request_ids)) == 5
