"""Unit tests for video ID parser."""

import pytest
from src.services.video_id_parser import extract_video_id
from src.utils.exceptions import InvalidVideoIdError


class TestVideoIdParser:
    """Unit tests for extract_video_id function."""

    def test_raw_video_id(self):
        """Test extraction from raw 11-character ID."""
        video_id = "dQw4w9WgXcQ"
        result = extract_video_id(video_id)
        assert result == video_id

    def test_full_youtube_url(self):
        """Test extraction from full YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = extract_video_id(url)
        assert result == "dQw4w9WgXcQ"

    def test_full_youtube_url_with_http(self):
        """Test extraction from HTTP (not HTTPS) URL."""
        url = "http://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = extract_video_id(url)
        assert result == "dQw4w9WgXcQ"

    def test_short_youtube_url(self):
        """Test extraction from short youtu.be URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        result = extract_video_id(url)
        assert result == "dQw4w9WgXcQ"

    def test_short_youtube_url_with_params(self):
        """Test extraction from short URL with query params."""
        url = "https://youtu.be/dQw4w9WgXcQ?t=10"
        result = extract_video_id(url)
        assert result == "dQw4w9WgXcQ"

    def test_url_with_multiple_params(self):
        """Test extraction from URL with multiple query parameters."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s&list=PLtest"
        result = extract_video_id(url)
        assert result == "dQw4w9WgXcQ"

    def test_video_id_with_dash(self):
        """Test video ID containing dash character."""
        video_id = "dQw4w9Wg-cQ"
        result = extract_video_id(video_id)
        assert result == video_id

    def test_video_id_with_underscore(self):
        """Test video ID containing underscore character."""
        video_id = "dQw4w9Wg_cQ"
        result = extract_video_id(video_id)
        assert result == video_id

    def test_whitespace_trimmed(self):
        """Test that leading/trailing whitespace is trimmed."""
        video_id = "  dQw4w9WgXcQ  "
        result = extract_video_id(video_id)
        assert result == "dQw4w9WgXcQ"

    def test_empty_string_raises_error(self):
        """Test that empty string raises InvalidVideoIdError."""
        with pytest.raises(InvalidVideoIdError):
            extract_video_id("")

    def test_invalid_characters_raises_error(self):
        """Test that invalid characters raise InvalidVideoIdError."""
        with pytest.raises(InvalidVideoIdError):
            extract_video_id("invalid!!!")

    def test_too_short_raises_error(self):
        """Test that ID shorter than 11 chars raises error."""
        with pytest.raises(InvalidVideoIdError):
            extract_video_id("short")

    def test_too_long_raises_error(self):
        """Test that ID longer than 11 chars raises error."""
        with pytest.raises(InvalidVideoIdError):
            extract_video_id("toolongvideoid123")

    def test_invalid_url_format_raises_error(self):
        """Test that invalid URL format raises error."""
        with pytest.raises(InvalidVideoIdError):
            extract_video_id("https://notayoutubeurl.com/video")

    def test_none_raises_error(self):
        """Test that None input raises error."""
        with pytest.raises(InvalidVideoIdError):
            extract_video_id(None)

    def test_url_without_video_id_raises_error(self):
        """Test that YouTube URL without v parameter raises error."""
        with pytest.raises(InvalidVideoIdError):
            extract_video_id("https://www.youtube.com/watch")

    def test_special_characters_in_url(self):
        """Test URL with special characters but valid video ID."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=share"
        result = extract_video_id(url)
        assert result == "dQw4w9WgXcQ"
