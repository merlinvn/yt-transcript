# Quickstart Guide: YouTube Transcript API

**Feature**: YouTube Transcript API Endpoint  
**Date**: 2025-10-01

## Integration Scenarios

This guide provides complete integration scenarios for testing the YouTube Transcript API, covering both success and failure paths.

---

## Scenario 1: Happy Path - Get Transcript with Raw Video ID

**User Story**: As an API consumer, I want to retrieve a transcript using just the video ID.

### Setup
```bash
# Set API key environment variable
export API_KEY="your-api-key-here"
```

### Request
```bash
curl -X POST http://localhost:8000/api/v1/transcript \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "video_identifier": "dQw4w9WgXcQ"
  }'
```

### Expected Response (200 OK)
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
      ...
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

### Validation Points
- ✅ Status code is 200
- ✅ `data` is not null
- ✅ `error` is null
- ✅ `video_id` matches input
- ✅ `segments` is a non-empty array
- ✅ Each segment has `text`, `start`, `duration`
- ✅ `request_id` is present in metadata

---

## Scenario 2: Input Flexibility - Full YouTube URL

**User Story**: As an API consumer, I want to provide a full YouTube URL instead of extracting the ID myself.

### Request
```bash
curl -X POST http://localhost:8000/api/v1/transcript \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "video_identifier": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  }'
```

### Expected Response (200 OK)
Same structure as Scenario 1, with `video_id` extracted as "dQw4w9WgXcQ"

### Validation Points
- ✅ System correctly parses video ID from full URL
- ✅ Response contains extracted video_id
- ✅ Transcript data is returned successfully

---

## Scenario 3: Input Flexibility - Short YouTube URL

**User Story**: As an API consumer, I want to use short youtu.be URLs.

### Request
```bash
curl -X POST http://localhost:8000/api/v1/transcript \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "video_identifier": "https://youtu.be/dQw4w9WgXcQ"
  }'
```

### Expected Response (200 OK)
Same structure as Scenario 1

### Validation Points
- ✅ System correctly parses video ID from short URL
- ✅ Response identical to using raw video ID

---

## Scenario 4: Error Handling - Invalid Video ID Format

**User Story**: As an API consumer, I want clear feedback when I provide an invalid video identifier.

### Request
```bash
curl -X POST http://localhost:8000/api/v1/transcript \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "video_identifier": "invalid-format!!!"
  }'
```

### Expected Response (400 Bad Request)
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

### Validation Points
- ✅ Status code is 400
- ✅ `data` is null
- ✅ `error.code` is "INVALID_VIDEO_ID"
- ✅ Error message is descriptive
- ✅ `details` provides guidance

---

## Scenario 5: Authentication - Missing API Key

**User Story**: As a system administrator, I want unauthorized requests to be rejected.

### Request
```bash
curl -X POST http://localhost:8000/api/v1/transcript \
  -H "Content-Type: application/json" \
  -d '{
    "video_identifier": "dQw4w9WgXcQ"
  }'
```

### Expected Response (401 Unauthorized)
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

### Validation Points
- ✅ Status code is 401
- ✅ Request is rejected before processing
- ✅ Clear guidance on authentication requirement

---

## Scenario 6: Error Handling - Video Not Found

**User Story**: As an API consumer, I want clear feedback when a video doesn't exist.

### Request
```bash
curl -X POST http://localhost:8000/api/v1/transcript \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "video_identifier": "xxxxxxxxxxx"
  }'
```

### Expected Response (404 Not Found)
```json
{
  "data": null,
  "error": {
    "code": "VIDEO_NOT_FOUND",
    "message": "Video not found or does not exist",
    "details": "The video ID 'xxxxxxxxxxx' could not be found on YouTube"
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-10-01T12:34:56Z",
    "duration_ms": 856,
    "version": "1.0.0"
  }
}
```

### Validation Points
- ✅ Status code is 404
- ✅ Error distinguishes "not found" from other errors
- ✅ Video ID included in error details

---

## Scenario 7: Error Handling - Transcript Unavailable

**User Story**: As an API consumer, I want to know when a video exists but has no transcript.

### Request
```bash
# Use a video ID known to have no transcript
curl -X POST http://localhost:8000/api/v1/transcript \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "video_identifier": "VIDEO_WITHOUT_TRANSCRIPT"
  }'
```

### Expected Response (404 Not Found)
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

### Validation Points
- ✅ Status code is 404
- ✅ Error code distinguishes from VIDEO_NOT_FOUND
- ✅ Details explain possible reasons

---

## Scenario 8: Health Check - Service Availability

**User Story**: As a DevOps engineer, I want to monitor service health.

### Request
```bash
curl -X GET http://localhost:8000/health
```

### Expected Response (200 OK)
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

### Validation Points
- ✅ Status code is 200
- ✅ No authentication required
- ✅ Response time < 2 seconds
- ✅ All checks return true
- ✅ Status is "healthy"

---

## Scenario 9: Concurrent Requests

**User Story**: As a system under load, I want to handle multiple simultaneous requests.

### Setup
```bash
# Create a test script
cat > test_concurrent.sh << 'EOF'
#!/bin/bash
API_KEY="your-api-key-here"
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/v1/transcript \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"video_identifier": "dQw4w9WgXcQ"}' &
done
wait
EOF

chmod +x test_concurrent.sh
```

### Execute
```bash
./test_concurrent.sh
```

### Validation Points
- ✅ All 10 requests complete successfully
- ✅ Each response has unique request_id
- ✅ No race conditions or errors
- ✅ Average response time < 5 seconds

---

## Scenario 10: API Documentation Access

**User Story**: As a new developer, I want to explore the API interactively.

### Request
```bash
# Open in browser
open http://localhost:8000/docs
```

### Expected Result
- ✅ Swagger UI loads successfully
- ✅ Endpoints are listed: POST /api/v1/transcript, GET /health
- ✅ Request/response schemas are documented
- ✅ "Try it out" functionality works
- ✅ Authentication can be configured in UI

---

## Environment Setup

### Local Development
```bash
# 1. Clone repository
git clone <repo-url>
cd yt-transcript

# 2. Install dependencies
poetry install

# 3. Set environment variables
cp .env.example .env
# Edit .env and set API_KEYS="test-key-1,test-key-2"

# 4. Run locally
poetry run uvicorn src.main:app --reload --port 8000
```

### Docker
```bash
# 1. Build image
docker build -t yt-transcript-api .

# 2. Run container
docker run -d \
  -p 8000:8000 \
  -e API_KEYS="test-key-1,test-key-2" \
  --name yt-transcript \
  yt-transcript-api

# 3. Check health
curl http://localhost:8000/health

# 4. View logs
docker logs -f yt-transcript
```

---

## Integration Testing Checklist

Use this checklist to verify complete integration:

- [ ] **Scenario 1**: Raw video ID retrieves transcript
- [ ] **Scenario 2**: Full YouTube URL works
- [ ] **Scenario 3**: Short youtu.be URL works
- [ ] **Scenario 4**: Invalid format returns 400
- [ ] **Scenario 5**: Missing API key returns 401
- [ ] **Scenario 6**: Non-existent video returns 404
- [ ] **Scenario 7**: No transcript returns 404 with specific code
- [ ] **Scenario 8**: Health check responds quickly
- [ ] **Scenario 9**: Concurrent requests handled
- [ ] **Scenario 10**: API docs accessible at /docs

---

## Common Issues & Troubleshooting

### Issue: 401 Unauthorized on valid request
**Solution**: Check that API_KEYS environment variable is set and includes your test key

### Issue: 503 Service Unavailable
**Solution**: Check YouTube connectivity, review logs for retry attempts

### Issue: Timeout errors
**Solution**: Verify 30-second timeout is configured, check for network issues

### Issue: Health check fails
**Solution**: Ensure port 8000 is accessible, check container logs

---

## Performance Benchmarking

```bash
# Install Apache Bench (if not already installed)
# Ubuntu: sudo apt-get install apache2-utils
# macOS: pre-installed

# Test with 100 requests, 10 concurrent
ab -n 100 -c 10 \
  -H "X-API-Key: test-key-1" \
  -H "Content-Type: application/json" \
  -p payload.json \
  http://localhost:8000/api/v1/transcript

# payload.json:
echo '{"video_identifier":"dQw4w9WgXcQ"}' > payload.json
```

**Expected Results**:
- Requests per second: > 10
- Mean time per request: < 1000ms
- 95th percentile: < 5000ms
