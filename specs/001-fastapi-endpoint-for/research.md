# Technical Research: YouTube Transcript API

**Feature**: YouTube Transcript API Endpoint  
**Date**: 2025-10-01

## Problem Statement

Build a FastAPI-based REST API service that retrieves YouTube video transcripts by accepting various video identifier formats (raw ID, full URL, short URL), with API key authentication and proper error handling.

## Technical Decisions

### 1. Core Technology Stack

**Decision**: Python 3.11+ with FastAPI framework

**Rationale**:
- FastAPI provides automatic OpenAPI documentation (FR-009)
- Native async/await support for non-blocking I/O operations
- Built-in request validation with Pydantic models
- Excellent performance characteristics for 10 req/s target (NFR-002)
- Constitutional requirement (Python 3.11+, FastAPI with async patterns)

**Alternatives Considered**:
- Flask: Less built-in validation, no native async support
- Django REST Framework: Heavier framework, overkill for single-endpoint service

### 2. YouTube Transcript Retrieval

**Decision**: Use `youtube-transcript-api` Python package

**Rationale**:
- Mature, actively maintained library (1000+ stars on GitHub)
- No YouTube Data API quota concerns (uses internal YouTube APIs)
- Supports multiple transcript formats (auto-generated, manual)
- Handles language detection automatically
- Simple interface: `YouTubeTranscriptApi.get_transcript(video_id)`
- Built-in error handling for common scenarios (no transcript, private videos)

**Alternatives Considered**:
- YouTube Data API v3: Requires API keys, has quota limits, more complex
- Web scraping: Fragile, breaks with YouTube changes, violates ToS

**Package**: `youtube-transcript-api==0.6.1` (latest stable)

### 3. URL Parsing & Video ID Extraction

**Decision**: Custom regex-based parser with validation

**Rationale**:
- YouTube video IDs are 11 characters: alphanumeric, dash, underscore
- Need to support 3 formats (FR-001):
  - Raw: `dQw4w9WgXcQ`
  - Full: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
  - Short: `https://youtu.be/dQw4w9WgXcQ`
- Lightweight, no external dependencies
- Clear error messages for invalid formats (FR-002)

**Implementation**:
```python
import re
from urllib.parse import urlparse, parse_qs

def extract_video_id(identifier: str) -> str:
    """Extract video ID from various YouTube URL formats."""
    # Pattern 1: Raw video ID (11 chars)
    if re.match(r'^[A-Za-z0-9_-]{11}$', identifier):
        return identifier
    
    # Pattern 2: Full URL (youtube.com/watch?v=...)
    if 'youtube.com/watch' in identifier:
        parsed = urlparse(identifier)
        video_id = parse_qs(parsed.query).get('v', [None])[0]
        if video_id:
            return video_id
    
    # Pattern 3: Short URL (youtu.be/...)
    if 'youtu.be/' in identifier:
        parsed = urlparse(identifier)
        video_id = parsed.path.lstrip('/')
        if video_id:
            return video_id
    
    raise ValueError("Invalid YouTube video identifier format")
```

### 4. API Key Authentication

**Decision**: Custom API key middleware with environment variable storage

**Rationale**:
- Simple, stateless authentication (NFR-005)
- API keys stored in environment variables (12-factor, constitutional requirement)
- FastAPI dependency injection for clean implementation
- No database required for MVP
- Supports multiple API keys via comma-separated list

**Implementation**:
```python
from fastapi import Security, HTTPException, Header
from typing import Optional

VALID_API_KEYS = set(os.getenv("API_KEYS", "").split(","))

async def verify_api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key
```

### 5. Error Handling Strategy

**Decision**: Structured error responses with HTTP status code mapping

**Rationale**:
- Constitutional requirement: consistent JSON structure with data/error/metadata
- Clear mapping of failure scenarios to HTTP status codes (FR-005)
- Actionable error messages (FR-006)

**Error Mapping**:
- 400 Bad Request: Invalid video ID format
- 401 Unauthorized: Missing/invalid API key
- 404 Not Found: Video doesn't exist or transcript unavailable
- 422 Unprocessable Entity: Valid format but processing failed
- 503 Service Unavailable: YouTube service temporarily unavailable
- 500 Internal Server Error: Unexpected failures

**Response Format**:
```json
{
  "data": null,
  "error": {
    "code": "TRANSCRIPT_UNAVAILABLE",
    "message": "No transcript available for this video",
    "details": "Video may have captions disabled or be too new"
  },
  "metadata": {
    "request_id": "uuid-here",
    "timestamp": "2025-10-01T12:34:56Z"
  }
}
```

### 6. Timeout & Retry Logic

**Decision**: 30-second timeout with 3 retries using exponential backoff

**Rationale**:
- NFR-003 specifies 30-second timeout
- NFR-004 requires retry with exponential backoff
- YouTube transcript API can be slow for long videos
- Transient failures (network issues, rate limits) should be retried

**Configuration**:
- Initial timeout: 30 seconds
- Retry attempts: 3
- Backoff: 1s, 2s, 4s (exponential)
- Only retry on specific exceptions (network errors, timeouts)

### 7. Logging & Observability

**Decision**: Structured JSON logging with request ID tracking

**Rationale**:
- Constitutional requirement: structured logging, request ID tracking
- FR-011: Log request ID, video ID, response time, outcome
- JSON format enables log aggregation (ELK, CloudWatch, etc.)

**Implementation**:
- Use Python `structlog` library
- Log levels: INFO (success), WARNING (retries), ERROR (failures)
- Include: request_id, video_id, api_key_hash, duration_ms, status_code

### 8. Health Check Endpoint

**Decision**: Simple `/health` endpoint with dependency checks

**Rationale**:
- FR-010 requires health check endpoint
- Constitutional requirement for container health checks
- Kubernetes/Docker readiness probes

**Checks**:
- Service is running (200 OK)
- Can import youtube-transcript-api (dependency check)
- Optional: Test YouTube connectivity (may add latency)

### 9. Containerization

**Decision**: Multi-stage Docker build with Alpine Linux base

**Rationale**:
- Constitutional requirement: optimized for size and security
- Multi-stage build: smaller final image (~50-80 MB)
- Alpine Linux: minimal attack surface
- Non-root user: security best practice
- Pinned dependencies: reproducible builds

**Dockerfile Structure**:
```dockerfile
FROM python:3.11-alpine AS builder
# Install dependencies
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt

FROM python:3.11-alpine
# Non-root user
RUN addgroup -S appuser && adduser -S appuser -G appuser
WORKDIR /app
COPY --from=builder requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
USER appuser
HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 10. Testing Strategy

**Decision**: pytest with TDD approach (contract → integration → unit)

**Rationale**:
- Constitutional requirement: TDD mandatory
- pytest: industry standard for Python, excellent fixtures
- Test pyramid: contract tests → integration → unit tests

**Test Levels**:
1. **Contract Tests** (Phase 3.2):
   - API endpoint contracts (request/response schemas)
   - HTTP status code validation
   - Error response format validation
   
2. **Integration Tests** (Phase 3.2):
   - End-to-end flows with mocked youtube-transcript-api
   - Authentication middleware
   - Error handling paths
   
3. **Unit Tests** (Phase 3.5):
   - URL parser logic
   - Video ID extraction
   - Response formatter

**Mock Strategy**:
- Mock `youtube-transcript-api` responses to avoid real YouTube calls
- Use `pytest-mock` or `unittest.mock`
- Test fixtures for common scenarios (success, no transcript, invalid video)

### 11. Dependency Management

**Decision**: Poetry for dependency management

**Rationale**:
- Constitutional requirement: poetry or pip-tools for deterministic builds
- Poetry provides: dependency resolution, lock file, virtual env management
- Better than pip-tools for new projects
- pyproject.toml: modern Python standard (PEP 518)

**Core Dependencies**:
```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
youtube-transcript-api = "^0.6.1"
pydantic = "^2.5.0"
structlog = "^23.2.0"
python-dotenv = "^1.0.0"

[tool.poetry.dev-dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.1.0"
pytest-mock = "^3.12.0"
httpx = "^0.25.0"  # For testing async endpoints
black = "^23.11.0"
ruff = "^0.1.5"
mypy = "^1.7.0"
```

### 12. Performance Considerations

**Decision**: Async endpoint with connection pooling

**Rationale**:
- NFR-001: P95 < 5 seconds
- NFR-002: 10 req/s minimum capacity
- Async allows concurrent request handling
- Single worker can handle 10 req/s easily with async

**Optimizations**:
- Use async FastAPI endpoints
- youtube-transcript-api is synchronous, wrap in `asyncio.to_thread()`
- Uvicorn with 2-4 workers for production
- No caching initially (simplicity), can add later

### 13. Configuration Management

**Decision**: Environment variables with pydantic-settings

**Rationale**:
- Constitutional requirement: 12-factor config via env vars
- Type-safe configuration with validation
- Default values for development

**Configuration**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_keys: str  # Comma-separated
    log_level: str = "INFO"
    timeout_seconds: int = 30
    max_retries: int = 3
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
```

## Risk Assessment

### High Risks
- **YouTube API Changes**: youtube-transcript-api relies on internal APIs that could change
  - **Mitigation**: Pin version, monitor for updates, add integration tests to catch breaks

### Medium Risks
- **Long Video Timeouts**: 10+ hour videos may exceed 30s timeout
  - **Mitigation**: Document limitation, consider async job queue for future enhancement
  
- **Rate Limiting by YouTube**: Heavy usage may trigger YouTube rate limits
  - **Mitigation**: Implement exponential backoff, add monitoring to detect limits

### Low Risks
- **API Key Management**: Environment variable approach requires manual key distribution
  - **Mitigation**: Document key generation process, consider key management service later

## Open Questions

None - all clarifications resolved during `/clarify` phase.

## Dependencies

**External Services**:
- YouTube (via youtube-transcript-api library)

**Build/Runtime**:
- Docker 20.10+
- Python 3.11+

## Performance Estimates

**Expected Performance**:
- P50 latency: ~500ms (YouTube API call dominates)
- P95 latency: ~2-3 seconds (well under 5s requirement)
- Throughput: 10-20 req/s per worker (exceeds 10 req/s requirement)
- Memory: ~50-100MB per worker
- CPU: Low (<10% under normal load)

## Success Criteria

- All functional requirements (FR-001 through FR-014) implemented
- All non-functional requirements (NFR-001 through NFR-008) met
- 80%+ test coverage (constitutional requirement)
- Docker image builds successfully and passes health checks
- API documentation available at /docs (Swagger UI)
- Code passes black, ruff, mypy checks
