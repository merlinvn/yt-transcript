"""Request models for API input validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class VideoIdentifierInput(BaseModel):
    """Input model for video identifier in various formats."""

    video_identifier: str = Field(
        ...,
        min_length=1,
        description="YouTube video ID, full URL, or short URL",
        examples=["dQw4w9WgXcQ", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "https://youtu.be/dQw4w9WgXcQ"],
    )


class APIRequest(BaseModel):
    """Internal model for tracking API request metadata."""

    request_id: str
    video_identifier: str
    api_key_hash: str
    timestamp: datetime
    user_agent: Optional[str] = None
    client_ip: Optional[str] = None

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "video_identifier": "dQw4w9WgXcQ",
                "api_key_hash": "2c26b46b68ffc68ff99b453c1d30413413422d706...",
                "timestamp": "2025-10-01T12:34:56.789Z",
                "user_agent": "Mozilla/5.0...",
                "client_ip": "192.168.1.100",
            }
        }
