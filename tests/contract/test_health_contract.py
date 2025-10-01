"""Contract tests for GET /health endpoint.

These tests validate the health check contract as specified in contracts/health-check.md.
Tests MUST fail initially (RED phase) before implementation.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch
import time


@pytest.mark.asyncio
class TestHealthContract:
    """Contract tests for health check endpoint."""

    async def test_tch01_service_healthy(self, async_client: AsyncClient):
        """TC-H01: Service healthy returns 200 with status='healthy'."""
        from src.main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "checks" in data
        assert data["checks"]["api"] is True
        assert data["checks"]["youtube_transcript_library"] is True
        assert "version" in data

    async def test_tch02_service_degraded(self, async_client: AsyncClient):
        """TC-H02: Service degraded returns 200 with status='degraded'."""
        from src.main import app
        
        # Mock library import failure
        with patch("src.api.health.check_youtube_library") as mock:
            mock.return_value = False
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["checks"]["api"] is True
        assert data["checks"]["youtube_transcript_library"] is False

    async def test_tch03_service_unhealthy(self, async_client: AsyncClient):
        """TC-H03: Service unhealthy returns 503 with status='unhealthy'."""
        from src.main import app
        
        # Mock critical failure
        with patch("src.api.health.check_api_health") as mock:
            mock.return_value = False
            
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"

    async def test_tch04_response_time(self, async_client: AsyncClient):
        """TC-H04: Health check responds within 2 seconds."""
        from src.main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            start_time = time.time()
            response = await client.get("/health")
            duration = time.time() - start_time

        assert response.status_code == 200
        assert duration < 2.0, f"Health check took {duration:.2f}s, should be < 2s"

    async def test_tch05_no_authentication_required(self, async_client: AsyncClient):
        """TC-H05: Health check does not require authentication."""
        from src.main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Request without X-API-Key header
            response = await client.get("/health")

        # Should succeed without authentication
        assert response.status_code in [200, 503]  # Either healthy or unhealthy
        data = response.json()
        # Should not return auth error
        assert "error" not in data or data.get("error") is None
        assert "status" in data
