"""Test helpers and utilities."""

from unittest.mock import MagicMock


class MockTranscriptSegment:
    """Mock transcript segment matching API structure."""
    def __init__(self, text, start, duration):
        self.text = text
        self.start = start
        self.duration = duration


def create_mock_transcript_api(mock_data):
    """Create a properly mocked YouTubeTranscriptApi.
    
    Args:
        mock_data: List of dicts with text, start, duration
        
    Returns:
        Mock class that can be used in patches
    """
    def mock_fetch(video_id):
        return [MockTranscriptSegment(**item) for item in mock_data]
    
    return mock_fetch
