"""Pytest configuration and shared fixtures."""

import pytest
import os
from typing import AsyncGenerator
from httpx import AsyncClient
from fastapi import FastAPI
from unittest.mock import MagicMock, patch


# Set test environment variables before importing app
os.environ["API_KEYS"] = "test-key-1,test-key-2,test-key-3"
os.environ["LOG_LEVEL"] = "ERROR"  # Reduce noise in tests
os.environ["TIMEOUT_SECONDS"] = "30"
os.environ["MAX_RETRIES"] = "3"


@pytest.fixture
def test_api_key() -> str:
    """Provide a test API key that matches environment."""
    return "test-key-1"


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


@pytest.fixture
def mock_youtube_transcript_api():
    """Global mock for YouTubeTranscriptApi that works with new API (0.6.2+)."""
    with patch("src.services.transcript_service.YouTubeTranscriptApi") as mock_class:
        mock_instance = mock_class.return_value
        
        # Create a mock FetchedTranscript object with all required attributes
        mock_result = MagicMock()
        mock_result.to_raw_data.return_value = [
            {"text": "We're no strangers to love", "start": 0.0, "duration": 2.5},
            {"text": "You know the rules and so do I", "start": 2.5, "duration": 3.0},
        ]
        mock_result.video_id = "dQw4w9WgXcQ"
        mock_result.language = "English"
        mock_result.language_code = "en"
        mock_result.is_generated = False
        
        mock_instance.fetch.return_value = mock_result
        
        yield mock_class
