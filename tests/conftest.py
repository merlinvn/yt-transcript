"""Pytest configuration and shared fixtures."""

import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
from fastapi import FastAPI


@pytest.fixture
def test_api_key() -> str:
    """Provide a test API key."""
    return "test-api-key-12345"


@pytest.fixture
def test_api_keys() -> str:
    """Provide multiple test API keys as comma-separated string."""
    return "test-key-1,test-key-2,test-key-3"


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP client for testing."""
    async with AsyncClient() as client:
        yield client


@pytest.fixture
def mock_transcript_data() -> dict:
    """Provide mock transcript data for testing."""
    return {
        "video_id": "dQw4w9WgXcQ",
        "segments": [
            {"text": "We're no strangers to love", "start": 0.0, "duration": 2.5},
            {"text": "You know the rules and so do I", "start": 2.5, "duration": 3.0},
        ],
    }
