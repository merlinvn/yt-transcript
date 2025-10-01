"""Transcript data models."""

from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, field_validator


class TranscriptSegment(BaseModel):
    """Individual timestamped portion of a transcript."""

    text: str = Field(..., min_length=1, description="Text content of this segment")
    start: float = Field(..., ge=0.0, description="Start time in seconds")
    duration: float = Field(..., gt=0.0, description="Duration of segment in seconds")

    @property
    def end(self) -> float:
        """Computed end time."""
        return self.start + self.duration

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "text": "Hello and welcome to this video",
                "start": 0.0,
                "duration": 2.5,
            }
        }


class Transcript(BaseModel):
    """Complete transcript data for a video."""

    video_id: str = Field(..., min_length=11, max_length=11, description="11-character YouTube video ID")
    language: str = Field(..., min_length=2, max_length=10, description="ISO 639-1 language code")
    is_generated: bool = Field(..., description="True if auto-generated, False if manual")
    segments: List[TranscriptSegment] = Field(..., min_length=1, description="Ordered list of transcript segments")
    total_duration: float = Field(..., ge=0.0, description="Sum of all segment durations")
    segment_count: int = Field(..., ge=1, description="Number of segments")
    retrieved_at: datetime = Field(..., description="When transcript was fetched")

    @field_validator("segments")
    @classmethod
    def validate_segments_ordered(cls, v: List[TranscriptSegment]) -> List[TranscriptSegment]:
        """Ensure segments are ordered by start time."""
        if len(v) > 1:
            for i in range(1, len(v)):
                if v[i].start < v[i - 1].start:
                    raise ValueError("Segments must be ordered by start time")
        return v

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "language": "en",
                "is_generated": False,
                "segments": [
                    {"text": "We're no strangers to love", "start": 0.0, "duration": 2.5},
                    {"text": "You know the rules and so do I", "start": 2.5, "duration": 3.0},
                ],
                "total_duration": 212.5,
                "segment_count": 85,
                "retrieved_at": "2025-10-01T12:34:56Z",
            }
        }
