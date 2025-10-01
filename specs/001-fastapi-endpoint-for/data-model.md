# Data Model: YouTube Transcript API

**Feature**: YouTube Transcript API Endpoint  
**Date**: 2025-10-01

## Overview

This document defines the data structures used in the YouTube Transcript API. The system is stateless and does not persist data, but uses well-defined models for request validation, response formatting, and internal processing.

## Domain Entities

### 1. VideoIdentifier

**Purpose**: Represents a YouTube video reference in any supported format

**Attributes**:
- `raw_input` (str): Original user-provided identifier
- `video_id` (str): Extracted 11-character YouTube video ID
- `format_type` (str): One of: "raw_id", "full_url", "short_url"

**Validation Rules**:
- `video_id` must match pattern: `^[A-Za-z0-9_-]{11}$`
- `raw_input` must match one of three supported formats
- Extracted `video_id` must be exactly 11 characters

**Example**:
```json
{
  "raw_input": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "video_id": "dQw4w9WgXcQ",
  "format_type": "full_url"
}
```

### 2. TranscriptSegment

**Purpose**: Individual timestamped portion of a transcript

**Attributes**:
- `text` (str): Text content of this segment
- `start` (float): Start time in seconds
- `duration` (float): Duration of segment in seconds

**Derived Attributes**:
- `end` (float): Computed as `start + duration`

**Validation Rules**:
- `text` cannot be empty
- `start` must be >= 0
- `duration` must be > 0

**Example**:
```json
{
  "text": "Hello and welcome to this video",
  "start": 0.0,
  "duration": 2.5
}
```

### 3. Transcript

**Purpose**: Complete transcript data for a video

**Attributes**:
- `video_id` (str): YouTube video ID
- `language` (str): Language code (e.g., "en", "es", "fr")
- `is_generated` (bool): True if auto-generated, False if manual
- `segments` (List[TranscriptSegment]): Ordered list of transcript segments

**Metadata**:
- `total_duration` (float): Sum of all segment durations
- `segment_count` (int): Number of segments
- `retrieved_at` (datetime): When transcript was fetched

**Validation Rules**:
- `segments` must not be empty
- `language` must be valid ISO 639-1 code
- `segments` must be ordered by `start` time

**Example**:
```json
{
  "video_id": "dQw4w9WgXcQ",
  "language": "en",
  "is_generated": false,
  "segments": [...],
  "total_duration": 212.5,
  "segment_count": 85,
  "retrieved_at": "2025-10-01T12:34:56Z"
}
```

### 4. APIRequest

**Purpose**: Encapsulates incoming API request data

**Attributes**:
- `request_id` (str): Unique UUID for request tracking
- `video_identifier` (str): Raw video identifier from request
- `api_key_hash` (str): SHA256 hash of API key (for logging, not validation)
- `timestamp` (datetime): Request received timestamp
- `user_agent` (Optional[str]): Client user agent
- `client_ip` (Optional[str]): Client IP address (for monitoring)

**Lifecycle**:
- Created: On request receipt
- Used: Throughout request processing
- Logged: In all log entries for correlation

**Example**:
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "video_identifier": "dQw4w9WgXcQ",
  "api_key_hash": "2c26b46b68ffc68ff99b453c1d30413413422d706...",
  "timestamp": "2025-10-01T12:34:56.789Z",
  "user_agent": "Mozilla/5.0 ...",
  "client_ip": "192.168.1.100"
}
```

### 5. APIResponse

**Purpose**: Standardized API response structure

**Attributes**:
- `data` (Optional[Transcript]): Transcript data on success, null on error
- `error` (Optional[ErrorDetail]): Error information on failure, null on success
- `metadata` (ResponseMetadata): Request tracking and timing information

**Validation Rules**:
- Exactly one of `data` or `error` must be non-null
- `metadata` is always present

**Success Example**:
```json
{
  "data": {
    "video_id": "dQw4w9WgXcQ",
    "language": "en",
    "segments": [...]
  },
  "error": null,
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-10-01T12:34:56Z",
    "duration_ms": 1234
  }
}
```

**Error Example**:
```json
{
  "data": null,
  "error": {
    "code": "VIDEO_NOT_FOUND",
    "message": "Video not found or transcript unavailable",
    "details": "No transcript could be retrieved for video ID: dQw4w9WgXcQ"
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-10-01T12:34:56Z",
    "duration_ms": 856
  }
}
```

### 6. ErrorDetail

**Purpose**: Structured error information

**Attributes**:
- `code` (str): Machine-readable error code (uppercase, underscore-separated)
- `message` (str): Human-readable error message
- `details` (Optional[str]): Additional context or troubleshooting guidance

**Error Codes**:
- `INVALID_VIDEO_ID`: Malformed video identifier
- `VIDEO_NOT_FOUND`: Video doesn't exist
- `TRANSCRIPT_UNAVAILABLE`: Video exists but no transcript available
- `INVALID_API_KEY`: Authentication failure
- `SERVICE_UNAVAILABLE`: YouTube service temporarily unavailable
- `TIMEOUT_ERROR`: Request exceeded timeout
- `INTERNAL_ERROR`: Unexpected server error

**Example**:
```json
{
  "code": "TRANSCRIPT_UNAVAILABLE",
  "message": "No transcript available for this video",
  "details": "This video may have captions disabled, be too new, or be private/age-restricted"
}
```

### 7. ResponseMetadata

**Purpose**: Request tracking and performance metrics

**Attributes**:
- `request_id` (str): UUID matching APIRequest
- `timestamp` (datetime): Response timestamp (ISO 8601)
- `duration_ms` (int): Request processing time in milliseconds
- `version` (str): API version (e.g., "1.0.0")

**Example**:
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-10-01T12:34:56.789Z",
  "duration_ms": 1234,
  "version": "1.0.0"
}
```

### 8. HealthStatus

**Purpose**: Health check endpoint response

**Attributes**:
- `status` (str): One of: "healthy", "degraded", "unhealthy"
- `timestamp` (datetime): Health check timestamp
- `checks` (Dict[str, bool]): Individual component health status
- `version` (str): Application version

**Example**:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-01T12:34:56Z",
  "checks": {
    "api": true,
    "youtube_transcript_library": true
  },
  "version": "1.0.0"
}
```

## Pydantic Models

All entities will be implemented as Pydantic v2 models for:
- Automatic request validation
- Response serialization
- OpenAPI schema generation
- Type safety

### Model Hierarchy

```
BaseModel (Pydantic)
├── VideoIdentifierInput (request body)
├── TranscriptSegmentSchema
├── TranscriptSchema
├── ErrorDetailSchema
├── ResponseMetadataSchema
├── APIResponseSchema[TranscriptSchema]
└── HealthStatusSchema
```

## Relationships

```
APIRequest
    ├── contains → VideoIdentifier (1:1)
    └── produces → APIResponse (1:1)

APIResponse
    ├── contains → Transcript (0:1) [on success]
    ├── contains → ErrorDetail (0:1) [on error]
    └── contains → ResponseMetadata (1:1) [always]

Transcript
    └── contains → TranscriptSegment (1:many)
```

## Data Flow

1. **Request Receipt**:
   ```
   HTTP Request → VideoIdentifierInput → VideoIdentifier extraction
   ```

2. **Processing**:
   ```
   VideoIdentifier → youtube-transcript-api → Raw segments
   → TranscriptSegment list → Transcript
   ```

3. **Response Formation**:
   ```
   Transcript → APIResponse(data=Transcript, error=null) → JSON
   OR
   Exception → ErrorDetail → APIResponse(data=null, error=ErrorDetail) → JSON
   ```

## State Management

**Stateless Design**: No data persistence required
- API keys: Stored in environment variables (read-only)
- Request state: In-memory during request lifecycle only
- No database, no cache (for MVP)
- Each request is independent

## Validation Rules Summary

| Entity | Key Validations |
|--------|----------------|
| VideoIdentifier | 11-char alphanumeric format, valid URL structure |
| TranscriptSegment | Non-empty text, positive start/duration |
| Transcript | Non-empty segments list, ordered by time |
| APIRequest | Valid UUID, non-empty identifier |
| APIResponse | Exactly one of data/error is non-null |
| ErrorDetail | Non-empty code and message |
| ResponseMetadata | Valid UUID, positive duration |

## Future Enhancements (Out of Scope)

- Language preference parameter (currently default only)
- Transcript caching (Redis/memcached)
- User management database
- Request history/analytics
- Webhook notifications
