"""Integration tests for error handling scenarios (Scenarios 4-7).

Tests from quickstart.md Scenarios 4-7: error conditions and proper
error response formatting.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch


INVALID_VIDEO_ID = "invalid-format!!!"
NONEXISTENT_VIDEO_ID = "xxxxxxxxxxx"
VALID_VIDEO_ID = "dQw4w9WgXcQ"


@pytest.mark.asyncio
class TestErrorHandling:
    """Integration tests for error scenarios."""

    async def test_scenario_4_invalid_format(
        self, async_client: AsyncClient, test_api_key: str
    ):
        """Scenario 4: Invalid format returns 400 with INVALID_VIDEO_ID."""
        from src.main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/transcript",
                json={"video_identifier": INVALID_VIDEO_ID},
                headers={"X-API-Key": test_api_key},
            )

        # Validate error response
        assert response.status_code == 400
        data = response.json()
        
        # Validate error structure
        assert data["data"] is None
        assert data["error"] is not None
        assert data["error"]["code"] == "INVALID_VIDEO_ID"
        assert data["error"]["message"] is not None
        assert len(data["error"]["message"]) > 0
        
        # Error details should provide guidance
        assert "details" in data["error"]
        assert data["error"]["details"] is not None
        
        # Metadata should still be present
        assert "metadata" in data
        assert data["metadata"]["request_id"] is not None

    async def test_scenario_5_missing_api_key(self, async_client: AsyncClient):
        """Scenario 5: Missing API key returns 401."""
        from src.main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/transcript",
                json={"video_identifier": VALID_VIDEO_ID},
                # No X-API-Key header
            )

        # Validate unauthorized response
        assert response.status_code == 401
        data = response.json()
        
        assert data["error"]["code"] == "INVALID_API_KEY"
        assert "missing" in data["error"]["message"].lower() or \
               "invalid" in data["error"]["message"].lower()

    async def test_scenario_6_video_not_found(
        self, async_client: AsyncClient, test_api_key: str
    ):
        """Scenario 6: Non-existent video returns 404 with VIDEO_NOT_FOUND."""
        from src.main import app
        
        with patch("src.services.transcript_service.get_transcript") as mock:
            from src.utils.exceptions import VideoNotFoundError
            mock.side_effect = VideoNotFoundError(f"Video {NONEXISTENT_VIDEO_ID} not found")
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/transcript",
                    json={"video_identifier": NONEXISTENT_VIDEO_ID},
                    headers={"X-API-Key": test_api_key},
                )

        # Validate not found response
        assert response.status_code == 404
        data = response.json()
        
        assert data["data"] is None
        assert data["error"]["code"] == "VIDEO_NOT_FOUND"
        assert NONEXISTENT_VIDEO_ID in data["error"]["details"] or \
               NONEXISTENT_VIDEO_ID in data["error"]["message"]

    async def test_scenario_7_transcript_unavailable(
        self, async_client: AsyncClient, test_api_key: str
    ):
        """Scenario 7: No transcript returns 404 with TRANSCRIPT_UNAVAILABLE."""
        from src.main import app
        
        with patch("src.services.transcript_service.get_transcript") as mock:
            from src.utils.exceptions import TranscriptUnavailableError
            mock.side_effect = TranscriptUnavailableError(
                "Transcript not available for this video"
            )
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/transcript",
                    json={"video_identifier": VALID_VIDEO_ID},
                    headers={"X-API-Key": test_api_key},
                )

        # Validate transcript unavailable response
        assert response.status_code == 404
        data = response.json()
        
        assert data["error"]["code"] == "TRANSCRIPT_UNAVAILABLE"
        # Error details should explain possible reasons
        assert "details" in data["error"]
        assert len(data["error"]["details"]) > 0

    async def test_error_response_consistency(
        self, async_client: AsyncClient, test_api_key: str
    ):
        """Validate all errors follow consistent response format."""
        from src.main import app
        
        # Test invalid format error
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/transcript",
                json={"video_identifier": "bad!!!"},
                headers={"X-API-Key": test_api_key},
            )

        data = response.json()
        
        # All errors must have these fields
        assert "data" in data
        assert "error" in data
        assert "metadata" in data
        
        # data must be null on error
        assert data["data"] is None
        
        # error must have required structure
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert "details" in data["error"]
        
        # metadata always present
        assert "request_id" in data["metadata"]
        assert "timestamp" in data["metadata"]
        assert "version" in data["metadata"]

    async def test_invalid_api_key_format(self, async_client: AsyncClient):
        """Test various invalid API key formats."""
        from src.main import app
        
        invalid_keys = ["", "short", "invalid key", "a" * 100]
        
        for invalid_key in invalid_keys:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/transcript",
                    json={"video_identifier": VALID_VIDEO_ID},
                    headers={"X-API-Key": invalid_key},
                )
            
            assert response.status_code == 401
            data = response.json()
            assert data["error"]["code"] == "INVALID_API_KEY"
