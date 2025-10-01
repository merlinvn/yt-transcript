# API Contract: Health Check Endpoint

**Endpoint**: `GET /health`  
**Purpose**: Verify service availability and health status  
**Authentication**: Not required (public endpoint)

## Request

### HTTP Method
```
GET
```

### Headers
```
None required
```

### Query Parameters
None

## Response

### Success Response (200 OK)

**Status Code**: `200 OK`

**Response Body**:
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

**Response Schema**:
```typescript
{
  status: "healthy" | "degraded" | "unhealthy",
  timestamp: string,                    // ISO 8601 timestamp
  checks: {
    api: boolean,                       // API service is running
    youtube_transcript_library: boolean // Library can be imported
  },
  version: string                       // Application version
}
```

### Degraded Response (200 OK)

**Status Code**: `200 OK`  
**Note**: Still returns 200 even if degraded, for compatibility with basic health checks

**Response Body**:
```json
{
  "status": "degraded",
  "timestamp": "2025-10-01T12:34:56Z",
  "checks": {
    "api": true,
    "youtube_transcript_library": false
  },
  "version": "1.0.0"
}
```

### Unhealthy Response (503 Service Unavailable)

**Status Code**: `503 Service Unavailable`

**Response Body**:
```json
{
  "status": "unhealthy",
  "timestamp": "2025-10-01T12:34:56Z",
  "checks": {
    "api": false,
    "youtube_transcript_library": false
  },
  "version": "1.0.0"
}
```

## Test Cases

### TC-H01: Service Healthy
**Given**: All systems operational  
**When**: GET /health  
**Then**: Returns 200 OK with status "healthy"

### TC-H02: Service Degraded
**Given**: Some dependency unavailable (e.g., library import fails)  
**When**: GET /health  
**Then**: Returns 200 OK with status "degraded" and specific check failures

### TC-H03: Service Unhealthy
**Given**: Critical failure (API not responding)  
**When**: GET /health  
**Then**: Returns 503 Service Unavailable with status "unhealthy"

### TC-H04: Health Check Performance
**Given**: Normal operation  
**When**: GET /health  
**Then**: Responds within 2 seconds

### TC-H05: No Authentication Required
**Given**: No API key provided  
**When**: GET /health  
**Then**: Returns successful response (no 401 error)

## Purpose

The health check endpoint is used for:
- **Container Health Checks**: Docker HEALTHCHECK directive
- **Kubernetes Probes**: Readiness and liveness probes
- **Load Balancer Health**: AWS ELB, nginx upstream health
- **Monitoring Systems**: Uptime monitoring, alerting

## Container Integration

### Docker HEALTHCHECK
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### Kubernetes Readiness Probe
```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 2
  failureThreshold: 3
```

### Kubernetes Liveness Probe
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 20
  timeoutSeconds: 2
  failureThreshold: 3
```

## Performance Requirements

- **Response Time**: < 2 seconds
- **No External Calls**: Should not call YouTube API
- **Lightweight Checks**: Only verify critical dependencies

## Versioning

- Endpoint path does NOT include /api/v1/ prefix (top-level for simplicity)
- Version number included in response body
