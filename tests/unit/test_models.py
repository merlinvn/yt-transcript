"""Unit tests for Pydantic models."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from src.models.transcript import TranscriptSegment, Transcript
from src.models.response import APIResponse, ErrorDetail, ResponseMetadata


class TestTranscriptSegment:
    """Unit tests for TranscriptSegment model."""

    def test_valid_segment(self):
        """Test creating valid transcript segment."""
        segment = TranscriptSegment(text="Hello world", start=0.0, duration=2.5)
        assert segment.text == "Hello world"
        assert segment.start == 0.0
        assert segment.duration == 2.5
        assert segment.end == 2.5

    def test_empty_text_fails(self):
        """Test that empty text fails validation."""
        with pytest.raises(ValidationError):
            TranscriptSegment(text="", start=0.0, duration=2.5)

    def test_negative_start_fails(self):
        """Test that negative start time fails validation."""
        with pytest.raises(ValidationError):
            TranscriptSegment(text="Hello", start=-1.0, duration=2.5)

    def test_zero_duration_fails(self):
        """Test that zero duration fails validation."""
        with pytest.raises(ValidationError):
            TranscriptSegment(text="Hello", start=0.0, duration=0.0)

    def test_negative_duration_fails(self):
        """Test that negative duration fails validation."""
        with pytest.raises(ValidationError):
            TranscriptSegment(text="Hello", start=0.0, duration=-1.0)


class TestTranscript:
    """Unit tests for Transcript model."""

    def test_valid_transcript(self):
        """Test creating valid transcript."""
        segments = [
            TranscriptSegment(text="Hello", start=0.0, duration=2.0),
            TranscriptSegment(text="World", start=2.0, duration=2.0),
        ]
        transcript = Transcript(
            video_id="dQw4w9WgXcQ",
            language="en",
            is_generated=False,
            segments=segments,
            total_duration=4.0,
            segment_count=2,
            retrieved_at=datetime.utcnow(),
        )
        assert transcript.video_id == "dQw4w9WgXcQ"
        assert transcript.segment_count == 2

    def test_video_id_length_validation(self):
        """Test that video ID must be exactly 11 characters."""
        segments = [TranscriptSegment(text="Hello", start=0.0, duration=2.0)]
        
        # Too short
        with pytest.raises(ValidationError):
            Transcript(
                video_id="short",
                language="en",
                is_generated=False,
                segments=segments,
                total_duration=2.0,
                segment_count=1,
                retrieved_at=datetime.utcnow(),
            )
        
        # Too long
        with pytest.raises(ValidationError):
            Transcript(
                video_id="toolongvideoid",
                language="en",
                is_generated=False,
                segments=segments,
                total_duration=2.0,
                segment_count=1,
                retrieved_at=datetime.utcnow(),
            )

    def test_empty_segments_fails(self):
        """Test that empty segments list fails validation."""
        with pytest.raises(ValidationError):
            Transcript(
                video_id="dQw4w9WgXcQ",
                language="en",
                is_generated=False,
                segments=[],
                total_duration=0.0,
                segment_count=0,
                retrieved_at=datetime.utcnow(),
            )

    def test_segments_must_be_ordered(self):
        """Test that segments must be ordered by start time."""
        # Out of order segments
        segments = [
            TranscriptSegment(text="Second", start=2.0, duration=2.0),
            TranscriptSegment(text="First", start=0.0, duration=2.0),
        ]
        
        with pytest.raises(ValidationError):
            Transcript(
                video_id="dQw4w9WgXcQ",
                language="en",
                is_generated=False,
                segments=segments,
                total_duration=4.0,
                segment_count=2,
                retrieved_at=datetime.utcnow(),
            )


class TestAPIResponse:
    """Unit tests for APIResponse model."""

    def test_success_response(self):
        """Test creating success response with data."""
        metadata = ResponseMetadata(
            request_id="test-123",
            timestamp=datetime.utcnow(),
            duration_ms=100,
            version="1.0.0",
        )
        response = APIResponse(data={"test": "data"}, error=None, metadata=metadata)
        assert response.data == {"test": "data"}
        assert response.error is None

    def test_error_response(self):
        """Test creating error response."""
        metadata = ResponseMetadata(
            request_id="test-123",
            timestamp=datetime.utcnow(),
            duration_ms=100,
            version="1.0.0",
        )
        error = ErrorDetail(code="TEST_ERROR", message="Test error", details="Details")
        response = APIResponse(data=None, error=error, metadata=metadata)
        assert response.data is None
        assert response.error.code == "TEST_ERROR"

    def test_both_data_and_error_fails(self):
        """Test that having both data and error fails validation."""
        metadata = ResponseMetadata(
            request_id="test-123",
            timestamp=datetime.utcnow(),
            duration_ms=100,
            version="1.0.0",
        )
        error = ErrorDetail(code="TEST_ERROR", message="Test error")
        
        with pytest.raises(ValidationError):
            APIResponse(data={"test": "data"}, error=error, metadata=metadata)

    def test_neither_data_nor_error_fails(self):
        """Test that having neither data nor error fails validation."""
        metadata = ResponseMetadata(
            request_id="test-123",
            timestamp=datetime.utcnow(),
            duration_ms=100,
            version="1.0.0",
        )
        
        with pytest.raises(ValidationError):
            APIResponse(data=None, error=None, metadata=metadata)


class TestErrorDetail:
    """Unit tests for ErrorDetail model."""

    def test_valid_error_detail(self):
        """Test creating valid error detail."""
        error = ErrorDetail(
            code="TEST_ERROR",
            message="Test error message",
            details="Additional details",
        )
        assert error.code == "TEST_ERROR"
        assert error.message == "Test error message"
        assert error.details == "Additional details"

    def test_error_detail_without_details(self):
        """Test creating error detail without optional details field."""
        error = ErrorDetail(code="TEST_ERROR", message="Test error message")
        assert error.code == "TEST_ERROR"
        assert error.details is None
