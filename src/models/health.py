"""Health status models."""

from datetime import datetime
from typing import Dict, Literal
from pydantic import BaseModel, Field


class HealthStatus(BaseModel):
    """Health check endpoint response."""

    status: Literal["healthy", "degraded", "unhealthy"] = Field(
        ..., description="Overall health status"
    )
    timestamp: datetime = Field(..., description="Health check timestamp")
    checks: Dict[str, bool] = Field(..., description="Individual component health status")
    version: str = Field(..., description="Application version")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-10-01T12:34:56Z",
                "checks": {"api": True, "youtube_transcript_library": True},
                "version": "1.0.0",
            }
        }
