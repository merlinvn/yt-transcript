# API Contract: Get Transcript Endpoint

**Endpoint**: `POST /api/v1/transcript`  
**Purpose**: Retrieve YouTube video transcript by video identifier  
**Authentication**: Required (API Key via X-API-Key header)

## Request

### HTTP Method
```
POST
```

### Headers
```
Content-Type: application/json
X-API-Key: <api-key-value>
```

### Request Body
```json
{
  "video_identifier": "string"
}
```

### Request Schema
```typescript
{
  video_identifier: string  // Required: YouTube video ID or URL
}
```

### Valid Examples

**Example 1: Raw Video ID**
```json
{
  "video_identifier": "dQw4w9WgXcQ"
}
```

**Example 2: Full YouTube URL**
```json
{
  "video_identifier": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Example 3: Short YouTube URL**
```json
{
  "video_identifier": "https://youtu.be/dQw4w9WgXcQ"
}
```

## Response

### Success Response (200 OK)

**Status Code**: `200 OK`

**Response Body**:
```json
{
  "data": {
    "video_id": "dQw4w9WgXcQ",
    "language": "en",
    "is_generated": false,
    "segments": [
      {
        "text": "We're no strangers to love",
        "start": 0.0,
        "duration": 2.5
      },
      {
        "text": "You know the rules and so do I",
        "start": 2.5,
        "duration": 3.0
      }
    ],
    "total_duration": 212.5,
    "segment_count": 85,
    "retrieved_at": "2025-10-01T12:34:56Z"
  },
  "error": null,
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-10-01T12:34:56.789Z",
    "duration_ms": 1234,
    "version": "1.0.0"
  }
}
```

**Response Schema**:
```typescript
{
  data: {
    video_id: string,           // 11-character YouTube video ID
    language: string,            // ISO 639-1 language code
    is_generated: boolean,       // true if auto-generated, false if manual
    segments: Array<{
      text: string,              // Transcript segment text
      start: number,             // Start time in seconds
      duration: number           // Duration in seconds
    }>,
    total_duration: number,      // Total duration of all segments
    segment_count: number,       // Number of segments
    retrieved_at: string         // ISO 8601 timestamp
  },
  error: null,
  metadata: {
    request_id: string,          // UUID v4
    timestamp: string,           // ISO 8601 timestamp
    duration_ms: number,         // Processing time in milliseconds
    version: string              // API version
  }
}
```

### Error Responses

#### 400 Bad Request - Invalid Video Identifier

**Status Code**: `400 Bad Request`

**Response Body**:
```json
{
  "data": null,
  "error": {
    "code": "INVALID_VIDEO_ID",
    "message": "Invalid YouTube video identifier format",
    "details": "Video identifier must be an 11-character ID, full YouTube URL, or short youtu.be URL"
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-10-01T12:34:56Z",
    "duration_ms": 12,
    "version": "1.0.0"
  }
}
```

#### 401 Unauthorized - Missing or Invalid API Key

**Status Code**: `401 Unauthorized`

**Response Body**:
```json
{
  "data": null,
  "error": {
    "code": "INVALID_API_KEY",
    "message": "Invalid or missing API key",
    "details": "Provide a valid API key in the X-API-Key header"
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-10-01T12:34:56Z",
    "duration_ms": 5,
    "version": "1.0.0"
  }
}
```

#### 404 Not Found - Video Not Found

**Status Code**: `404 Not Found`

**Response Body**:
```json
{
  "data": null,
  "error": {
    "code": "VIDEO_NOT_FOUND",
    "message": "Video not found or does not exist",
    "details": "The video ID 'dQw4w9WgXcQ' could not be found on YouTube"
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-10-01T12:34:56Z",
    "duration_ms": 856,
    "version": "1.0.0"
  }
}
```

#### 404 Not Found - Transcript Unavailable

**Status Code**: `404 Not Found`

**Response Body**:
```json
{
  "data": null,
  "error": {
    "code": "TRANSCRIPT_UNAVAILABLE",
    "message": "No transcript available for this video",
    "details": "This video may have captions disabled, be too new, or be private/age-restricted"
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-10-01T12:34:56Z",
    "duration_ms": 1523,
    "version": "1.0.0"
  }
}
```

#### 503 Service Unavailable - YouTube Service Down

**Status Code**: `503 Service Unavailable`

**Response Body**:
```json
{
  "data": null,
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "YouTube service temporarily unavailable",
    "details": "Unable to retrieve transcript after 3 retry attempts. Please try again later."
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-10-01T12:34:56Z",
    "duration_ms": 30245,
    "version": "1.0.0"
  }
}
```

#### 500 Internal Server Error

**Status Code**: `500 Internal Server Error`

**Response Body**:
```json
{
  "data": null,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred",
    "details": "The error has been logged. Please contact support with request ID if the issue persists."
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-10-01T12:34:56Z",
    "duration_ms": 234,
    "version": "1.0.0"
  }
}
```

## Test Cases

### TC-001: Valid Raw Video ID
**Given**: A valid 11-character video ID  
**When**: POST /api/v1/transcript with {"video_identifier": "dQw4w9WgXcQ"}  
**Then**: Returns 200 OK with transcript data

### TC-002: Valid Full YouTube URL
**Given**: A full YouTube URL with video ID  
**When**: POST /api/v1/transcript with {"video_identifier": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}  
**Then**: Returns 200 OK with transcript data

### TC-003: Valid Short YouTube URL
**Given**: A short youtu.be URL  
**When**: POST /api/v1/transcript with {"video_identifier": "https://youtu.be/dQw4w9WgXcQ"}  
**Then**: Returns 200 OK with transcript data

### TC-004: Invalid Video ID Format
**Given**: A malformed video identifier  
**When**: POST /api/v1/transcript with {"video_identifier": "invalid!!!"}  
**Then**: Returns 400 Bad Request with INVALID_VIDEO_ID error

### TC-005: Missing API Key
**Given**: No X-API-Key header provided  
**When**: POST /api/v1/transcript  
**Then**: Returns 401 Unauthorized with INVALID_API_KEY error

### TC-006: Invalid API Key
**Given**: An invalid API key in X-API-Key header  
**When**: POST /api/v1/transcript  
**Then**: Returns 401 Unauthorized with INVALID_API_KEY error

### TC-007: Non-existent Video
**Given**: A valid format video ID that doesn't exist  
**When**: POST /api/v1/transcript with non-existent video ID  
**Then**: Returns 404 Not Found with VIDEO_NOT_FOUND error

### TC-008: Video Without Transcript
**Given**: A video ID for a video without transcripts  
**When**: POST /api/v1/transcript  
**Then**: Returns 404 Not Found with TRANSCRIPT_UNAVAILABLE error

### TC-009: Concurrent Requests
**Given**: Multiple simultaneous requests for different videos  
**When**: POST /api/v1/transcript from multiple clients  
**Then**: Each request processes independently, returns correct transcript

### TC-010: Response Contains Request ID
**Given**: Any valid request  
**When**: POST /api/v1/transcript  
**Then**: Response metadata.request_id matches request tracking

## Performance Requirements

- **P95 Latency**: < 5 seconds
- **Timeout**: 30 seconds maximum
- **Concurrent Requests**: Support 10+ req/s

## Security Requirements

- API key required in X-API-Key header
- No sensitive data in logs (hash API keys)
- Request ID tracking for audit

## Versioning

- Current version: v1
- Version in URL path: /api/v1/
- Version in response metadata
