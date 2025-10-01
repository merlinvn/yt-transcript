# YouTube Transcript API

FastAPI-based REST API service for retrieving YouTube video transcripts. Accepts video identifiers in multiple formats (raw ID, full URL, short URL) and returns structured transcript data with timestamps.

## Features

- 🎯 **Multiple Input Formats**: Accepts raw video IDs, full YouTube URLs, and short youtu.be URLs
- 🔒 **API Key Authentication**: Secure access via X-API-Key header
- 📝 **Structured JSON Responses**: Consistent response format with data/error/metadata
- ⚡ **Async/Await**: Fast, non-blocking request handling
- 🔄 **Retry Logic**: Exponential backoff for transient failures
- 📊 **Structured Logging**: JSON-formatted logs with request tracking
- 🏥 **Health Checks**: Built-in health endpoint for monitoring
- 📖 **OpenAPI Documentation**: Interactive API docs at /docs
- 🐳 **Docker Ready**: Fully containerized with optimized images
- ✅ **Comprehensive Tests**: 80%+ test coverage with TDD approach

## Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Docker (optional, for containerized deployment)

## Quick Start

### Local Development with Poetry

```bash
# 1. Clone repository
git clone <repository-url>
cd yt-transcript

# 2. Install dependencies
poetry install

# 3. Set up environment variables
cp .env.example .env
# Edit .env and set API_KEYS

# 4. Run the application
poetry run uvicorn src.main:app --reload --port 8000

# 5. Access API documentation
open http://localhost:8000/docs
```

### Docker

```bash
# 1. Build Docker image
docker build -t yt-transcript-api .

# 2. Run container
docker run -d \
  -p 8000:8000 \
  -e API_KEYS="your-api-key-here,another-key" \
  --name yt-transcript \
  yt-transcript-api

# 3. Check health
curl http://localhost:8000/health

# 4. View logs
docker logs -f yt-transcript
```

### Docker Compose

```bash
# 1. Start services
docker-compose up -d

# 2. Check status
docker-compose ps

# 3. View logs
docker-compose logs -f

# 4. Stop services
docker-compose down
```

## Configuration

Configuration is managed via environment variables (12-factor app principles):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_KEYS` | Yes | - | Comma-separated list of valid API keys |
| `LOG_LEVEL` | No | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `TIMEOUT_SECONDS` | No | 30 | Timeout for transcript retrieval |
| `MAX_RETRIES` | No | 3 | Number of retry attempts for failures |
| `HOST` | No | 0.0.0.0 | Server host |
| `PORT` | No | 8000 | Server port |
| `APP_VERSION` | No | 1.0.0 | Application version |

## API Usage

### Get Transcript

```bash
# Using raw video ID
curl -X POST http://localhost:8000/api/v1/transcript \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"video_identifier": "dQw4w9WgXcQ"}'

# Using full YouTube URL
curl -X POST http://localhost:8000/api/v1/transcript \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"video_identifier": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Using short youtu.be URL
curl -X POST http://localhost:8000/api/v1/transcript \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"video_identifier": "https://youtu.be/dQw4w9WgXcQ"}'
```

### Success Response (200 OK)

```json
{
  "data": {
    "video_id": "dQw4w9WgXcQ",
    "language": "en",
    "is_generated": true,
    "segments": [
      {
        "text": "We're no strangers to love",
        "start": 0.0,
        "duration": 2.5
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

### Error Response (400/401/404/503)

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

### Health Check

```bash
curl http://localhost:8000/health
```

## Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html --cov-report=term

# Run specific test file
poetry run pytest tests/unit/test_video_id_parser.py

# Run with verbose output
poetry run pytest -v
```

## Development

### Code Quality

```bash
# Format code with black
poetry run black src/ tests/

# Lint with ruff
poetry run ruff check src/ tests/

# Type check with mypy
poetry run mypy src/

# Run all checks
poetry run black src/ tests/ && \
poetry run ruff check src/ tests/ && \
poetry run mypy src/
```

### Project Structure

```
yt-transcript/
├── src/
│   ├── api/              # API endpoints
│   │   ├── v1/
│   │   │   └── transcript.py
│   │   ├── dependencies.py
│   │   └── health.py
│   ├── middleware/       # Request/response middleware
│   ├── models/           # Pydantic models
│   ├── services/         # Business logic
│   ├── utils/            # Utilities (logger, exceptions)
│   ├── config.py         # Configuration
│   └── main.py           # FastAPI application
├── tests/
│   ├── contract/         # Contract tests
│   ├── integration/      # Integration tests
│   └── unit/             # Unit tests
├── pyproject.toml        # Poetry configuration
├── Dockerfile            # Docker image definition
└── docker-compose.yml    # Local development compose
```

## API Endpoints

- `POST /api/v1/transcript` - Retrieve video transcript (requires API key)
- `GET /health` - Health check endpoint (no auth required)
- `GET /` - Root endpoint with API information
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_VIDEO_ID` | 400 | Video ID format is invalid |
| `INVALID_API_KEY` | 401 | API key is missing or invalid |
| `VIDEO_NOT_FOUND` | 404 | Video doesn't exist on YouTube |
| `TRANSCRIPT_UNAVAILABLE` | 404 | Video exists but no transcript available |
| `SERVICE_UNAVAILABLE` | 503 | YouTube service temporarily unavailable |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

## Performance

- **Target Capacity**: 10+ requests/second
- **P95 Latency**: < 5 seconds
- **P50 Latency**: ~500ms
- **Timeout**: 30 seconds for transcript retrieval
- **Retry Logic**: 3 attempts with exponential backoff (1s, 2s, 4s)

## Production Deployment

### Resource Limits (Recommended)

```yaml
Resources:
  memory: 512Mi        # Soft limit
  memory_limit: 1Gi    # Hard limit
  cpu: 500m            # 0.5 CPU cores
```

### Kubernetes Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: yt-transcript-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: yt-transcript-api
  template:
    metadata:
      labels:
        app: yt-transcript-api
    spec:
      containers:
      - name: api
        image: yt-transcript-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: API_KEYS
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: api-keys
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 20
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
```

## License

[Your License Here]

## Contributing

[Contributing guidelines]

## Support

For issues and questions, please [open an issue](https://github.com/your-repo/issues).
