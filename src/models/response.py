"""Response models for consistent API output."""

from datetime import datetime
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, Field, field_validator


class ErrorDetail(BaseModel):
    """Structured error information."""

    code: str = Field(..., description="Machine-readable error code (UPPERCASE_SNAKE_CASE)")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[str] = Field(None, description="Additional context or troubleshooting guidance")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "code": "INVALID_VIDEO_ID",
                "message": "Invalid YouTube video identifier format",
                "details": "Video identifier must be an 11-character ID, full YouTube URL, or short youtu.be URL",
            }
        }


class ResponseMetadata(BaseModel):
    """Request tracking and performance metrics."""

    request_id: str = Field(..., description="UUID matching APIRequest")
    timestamp: datetime = Field(..., description="Response timestamp (ISO 8601)")
    duration_ms: int = Field(..., description="Request processing time in milliseconds", ge=0)
    version: str = Field(..., description="API version")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2025-10-01T12:34:56.789Z",
                "duration_ms": 1234,
                "version": "1.0.0",
            }
        }


T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standardized API response structure.
    
    Exactly one of 'data' or 'error' must be non-null.
    """

    data: Optional[T] = None
    error: Optional[ErrorDetail] = None
    metadata: ResponseMetadata

    @field_validator("error")
    @classmethod
    def validate_data_or_error(cls, v: Optional[ErrorDetail], info) -> Optional[ErrorDetail]:
        """Ensure exactly one of data or error is set."""
        data = info.data.get("data")
        if data is not None and v is not None:
            raise ValueError("Cannot have both data and error set")
        if data is None and v is None:
            raise ValueError("Must have either data or error set")
        return v

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "data": {"example": "data"},
                "error": None,
                "metadata": {
                    "request_id": "550e8400-e29b-41d4-a716-446655440000",
                    "timestamp": "2025-10-01T12:34:56.789Z",
                    "duration_ms": 1234,
                    "version": "1.0.0",
                },
            }
        }
