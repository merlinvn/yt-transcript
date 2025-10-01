# Tasks: YouTube Transcript API Endpoint

**Feature**: YouTube Transcript API Endpoint  
**Branch**: `001-fastapi-endpoint-for`  
**Date**: 2025-10-01

**Input**: Design documents from `/specs/001-fastapi-endpoint-for/`  
**Prerequisites**: plan.md, research.md, data-model.md, contracts/

---

## Task Execution Rules

**Format**: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Tasks are numbered sequentially (T001, T002, etc.)
- Include exact file paths in descriptions
- Follow TDD: Tests before implementation

**Execution Order**:
1. Complete all Setup tasks (Phase 3.1)
2. Complete all Tests First tasks (Phase 3.2) - MUST COMPLETE BEFORE 3.3
3. Complete Core Development tasks (Phase 3.3)
4. Complete Integration tasks (Phase 3.4)
5. Complete Polish & Validation tasks (Phase 3.5)

**Parallel Execution**:
- Tasks marked [P] can run simultaneously
- Tasks without [P] must run sequentially within their phase
- Different files = can be parallel
- Same file or dependencies = sequential

---

## Phase 3.1: Project Setup & Configuration

### Setup Tasks

- [ ] **T001**: Initialize Python project structure
  - Create `src/` directory with `__init__.py`
  - Create subdirectories: `models/`, `services/`, `api/`, `middleware/`, `utils/`
  - Create `tests/` directory with subdirectories: `contract/`, `integration/`, `unit/`
  - Add `__init__.py` to all directories
  - **Files**: Project structure at repository root

- [ ] **T002**: Configure Poetry and dependencies
  - Initialize `pyproject.toml` with Poetry
  - Set Python version to ^3.11
  - Add production dependencies:
    * fastapi = "^0.104.0"
    * uvicorn = {extras = ["standard"], version = "^0.24.0"}
    * youtube-transcript-api = "^0.6.1"
    * pydantic = "^2.5.0"
    * pydantic-settings = "^2.1.0"
    * structlog = "^23.2.0"
    * python-dotenv = "^1.0.0"
  - Add dev dependencies:
    * pytest = "^7.4.0"
    * pytest-asyncio = "^0.21.0"
    * pytest-cov = "^4.1.0"
    * pytest-mock = "^3.12.0"
    * httpx = "^0.25.0"
    * black = "^23.11.0"
    * ruff = "^0.1.5"
    * mypy = "^1.7.0"
  - Run `poetry lock`
  - **Files**: `pyproject.toml`, `poetry.lock`

- [ ] **T003**: Configure development tools and linting
  - Create `pyproject.toml` sections for black, ruff, mypy
  - Configure ruff: select = ["E", "F", "I"], line-length = 100
  - Configure black: line-length = 100
  - Configure mypy: strict = true, python_version = "3.11"
  - Create `.env.example` with API_KEYS, LOG_LEVEL, TIMEOUT_SECONDS
  - Create `.gitignore` for Python (venv, __pycache__, .env, etc.)
  - **Files**: `pyproject.toml`, `.env.example`, `.gitignore`

- [ ] **T004**: Create pytest configuration
  - Add pytest configuration to `pyproject.toml`
  - Configure asyncio_mode = "auto"
  - Set testpaths = ["tests"]
  - Configure coverage: source = ["src"], branch = true, minimum 80%
  - Create `tests/conftest.py` with shared fixtures
  - **Files**: `pyproject.toml`, `tests/conftest.py`

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

### Contract Tests (Parallel - Different Files)

- [ ] **T005 [P]**: Create contract test for transcript endpoint
  - File: `tests/contract/test_transcript_contract.py`
  - Import pytest, httpx.AsyncClient
  - Implement 10 test cases from `contracts/get-transcript.md`:
    * TC-001: Valid raw video ID (expect 200)
    * TC-002: Valid full YouTube URL (expect 200)
    * TC-003: Valid short YouTube URL (expect 200)
    * TC-004: Invalid video ID format (expect 400)
    * TC-005: Missing API key (expect 401)
    * TC-006: Invalid API key (expect 401)
    * TC-007: Non-existent video (expect 404)
    * TC-008: Video without transcript (expect 404)
    * TC-009: Concurrent requests (expect all 200)
    * TC-010: Response contains request_id (expect in metadata)
  - Use mocked youtube-transcript-api
  - Assert response schemas match contract
  - **Tests MUST FAIL initially** (no implementation yet)
  - **Files**: `tests/contract/test_transcript_contract.py`

- [ ] **T006 [P]**: Create contract test for health endpoint
  - File: `tests/contract/test_health_contract.py`
  - Import pytest, httpx.AsyncClient
  - Implement 5 test cases from `contracts/health-check.md`:
    * TC-H01: Service healthy (expect 200, status="healthy")
    * TC-H02: Service degraded (expect 200, status="degraded")
    * TC-H03: Service unhealthy (expect 503, status="unhealthy")
    * TC-H04: Response time < 2 seconds
    * TC-H05: No authentication required (no X-API-Key)
  - Mock library import failures for degraded/unhealthy scenarios
  - **Tests MUST FAIL initially** (no implementation yet)
  - **Files**: `tests/contract/test_health_contract.py`

### Integration Test Stubs (Parallel - Different Files)

- [ ] **T007 [P]**: Create integration test for scenario 1-3 (happy paths)
  - File: `tests/integration/test_transcript_happy_paths.py`
  - Import pytest, httpx.AsyncClient
  - Implement tests from `quickstart.md` Scenarios 1-3:
    * Test raw video ID retrieves transcript
    * Test full YouTube URL works
    * Test short youtu.be URL works
  - Use mocked youtube-transcript-api responses
  - Assert complete data structure (video_id, segments, metadata)
  - **Tests MUST FAIL initially**
  - **Files**: `tests/integration/test_transcript_happy_paths.py`

- [ ] **T008 [P]**: Create integration test for scenarios 4-7 (error handling)
  - File: `tests/integration/test_error_handling.py`
  - Import pytest, httpx.AsyncClient
  - Implement tests from `quickstart.md` Scenarios 4-7:
    * Test invalid format returns 400 with INVALID_VIDEO_ID
    * Test missing API key returns 401
    * Test non-existent video returns 404 with VIDEO_NOT_FOUND
    * Test no transcript returns 404 with TRANSCRIPT_UNAVAILABLE
  - Mock appropriate exceptions from youtube-transcript-api
  - Assert error codes, messages, and details
  - **Tests MUST FAIL initially**
  - **Files**: `tests/integration/test_error_handling.py`

- [ ] **T009 [P]**: Create integration test for authentication
  - File: `tests/integration/test_authentication.py`
  - Import pytest, httpx.AsyncClient
  - Test API key validation:
    * Valid API key allows access
    * Invalid API key returns 401
    * Missing API key returns 401
    * Multiple valid API keys work
  - Test API key hashing in logs (don't log plaintext)
  - **Tests MUST FAIL initially**
  - **Files**: `tests/integration/test_authentication.py`

- [ ] **T010 [P]**: Create integration test for concurrent requests
  - File: `tests/integration/test_concurrent.py`
  - Import pytest, httpx.AsyncClient, asyncio
  - Implement test from `quickstart.md` Scenario 9:
    * Send 10 concurrent requests
    * Assert all complete successfully
    * Assert unique request_ids
    * Assert no race conditions
  - **Tests MUST FAIL initially**
  - **Files**: `tests/integration/test_concurrent.py`

---

## Phase 3.3: Core Development

### Configuration & Models (Parallel - Different Files)

- [ ] **T011 [P]**: Create application configuration
  - File: `src/config.py`
  - Import pydantic_settings.BaseSettings
  - Create Settings class:
    * api_keys: str (comma-separated)
    * log_level: str = "INFO"
    * timeout_seconds: int = 30
    * max_retries: int = 3
    * host: str = "0.0.0.0"
    * port: int = 8000
    * app_version: str = "1.0.0"
  - Configure env_file = ".env"
  - Add settings instance: `settings = Settings()`
  - **Files**: `src/config.py`

- [ ] **T012 [P]**: Create request/response models
  - File: `src/models/request.py`
  - Import pydantic.BaseModel
  - Create VideoIdentifierInput model (per data-model.md):
    * video_identifier: str (with field validation)
  - Create APIRequest model:
    * request_id: str (UUID)
    * video_identifier: str
    * api_key_hash: str
    * timestamp: datetime
    * user_agent: Optional[str]
    * client_ip: Optional[str]
  - Add type hints for all fields
  - **Files**: `src/models/request.py`

- [ ] **T013 [P]**: Create response models
  - File: `src/models/response.py`
  - Import pydantic.BaseModel, Generic, TypeVar
  - Create ErrorDetail model (per data-model.md):
    * code: str
    * message: str
    * details: Optional[str]
  - Create ResponseMetadata model:
    * request_id: str
    * timestamp: datetime
    * duration_ms: int
    * version: str
  - Create APIResponse[T] generic model:
    * data: Optional[T]
    * error: Optional[ErrorDetail]
    * metadata: ResponseMetadata
  - Add validator: exactly one of data/error must be non-null
  - **Files**: `src/models/response.py`

- [ ] **T014 [P]**: Create transcript models
  - File: `src/models/transcript.py`
  - Import pydantic.BaseModel
  - Create TranscriptSegment model (per data-model.md):
    * text: str (non-empty)
    * start: float (>= 0)
    * duration: float (> 0)
  - Create Transcript model:
    * video_id: str (11 characters)
    * language: str (ISO 639-1 code)
    * is_generated: bool
    * segments: List[TranscriptSegment] (non-empty)
    * total_duration: float
    * segment_count: int
    * retrieved_at: datetime
  - Add field validators per data-model.md
  - **Files**: `src/models/transcript.py`

- [ ] **T015 [P]**: Create health status model
  - File: `src/models/health.py`
  - Import pydantic.BaseModel
  - Create HealthStatus model (per data-model.md):
    * status: Literal["healthy", "degraded", "unhealthy"]
    * timestamp: datetime
    * checks: Dict[str, bool]
    * version: str
  - **Files**: `src/models/health.py`

### Service Layer (Sequential - Has Dependencies)

- [ ] **T016**: Create custom exceptions
  - File: `src/utils/exceptions.py`
  - Define custom exception classes:
    * InvalidVideoIdError(ValueError)
    * VideoNotFoundError(Exception)
    * TranscriptUnavailableError(Exception)
    * ServiceUnavailableError(Exception)
    * TimeoutError(Exception)
  - Each exception should accept message and optional details
  - **Files**: `src/utils/exceptions.py`

- [ ] **T017**: Implement video ID parser service
  - File: `src/services/video_id_parser.py`
  - Import re, urllib.parse
  - Implement extract_video_id(identifier: str) -> str function:
    * Pattern 1: Raw video ID (11 chars, alphanumeric/-/_)
    * Pattern 2: Full URL (youtube.com/watch?v=...)
    * Pattern 3: Short URL (youtu.be/...)
    * Raise InvalidVideoIdError for invalid formats
  - Follow implementation from research.md Section 3
  - Add comprehensive docstrings with examples
  - **Files**: `src/services/video_id_parser.py`

- [ ] **T018**: Implement transcript service
  - File: `src/services/transcript_service.py`
  - Import youtube_transcript_api, asyncio
  - Import models: Transcript, TranscriptSegment
  - Import config: settings
  - Implement async get_transcript(video_id: str) -> Transcript:
    * Use asyncio.to_thread() to wrap sync youtube-transcript-api call
    * Apply timeout (settings.timeout_seconds)
    * Implement retry logic with exponential backoff (settings.max_retries)
    * Map youtube-transcript-api exceptions to custom exceptions
    * Build Transcript model from response
    * Always return default language
  - Follow implementation from research.md Sections 2, 6
  - **Files**: `src/services/transcript_service.py`

- [ ] **T019**: Implement authentication service
  - File: `src/services/auth_service.py`
  - Import hashlib, os, config.settings
  - Parse VALID_API_KEYS from settings.api_keys (split by comma)
  - Implement validate_api_key(api_key: str) -> bool
  - Implement hash_api_key(api_key: str) -> str (SHA256)
  - Follow implementation from research.md Section 4
  - **Files**: `src/services/auth_service.py`

### Utilities (Parallel - Different Files)

- [ ] **T020 [P]**: Configure structured logging
  - File: `src/utils/logger.py`
  - Import structlog, config.settings
  - Configure structlog processors:
    * Add timestamp
    * Add log level
    * Format as JSON
  - Create get_logger(name: str) function
  - Set log level from settings.log_level
  - Follow configuration from research.md Section 7
  - **Files**: `src/utils/logger.py`

---

## Phase 3.4: API Integration & Middleware

### Middleware (Parallel - Different Files)

- [ ] **T021 [P]**: Create request ID middleware
  - File: `src/middleware/request_id.py`
  - Import starlette.middleware, uuid
  - Create RequestIDMiddleware class:
    * Generate UUID for each request
    * Add to request state
    * Add to response headers (X-Request-ID)
  - Follow pattern from research.md
  - **Files**: `src/middleware/request_id.py`

- [ ] **T022 [P]**: Create logging middleware
  - File: `src/middleware/logging_middleware.py`
  - Import structlog, time, starlette.middleware
  - Create LoggingMiddleware class:
    * Log request start (method, path, request_id)
    * Log request end (status, duration_ms, request_id)
    * Log errors with full context
  - Use structured logger from utils.logger
  - **Files**: `src/middleware/logging_middleware.py`

### API Dependencies (Sequential)

- [ ] **T023**: Create FastAPI dependencies
  - File: `src/api/dependencies.py`
  - Import fastapi, services.auth_service
  - Create verify_api_key dependency:
    * Extract X-API-Key header
    * Validate using auth_service
    * Raise HTTPException(401) if invalid
    * Return api_key_hash for logging
  - Create get_request_id dependency:
    * Extract request_id from request.state
    * Return request_id
  - Follow implementation from research.md Section 4
  - **Files**: `src/api/dependencies.py`

### API Endpoints (Sequential - Shared Dependencies)

- [ ] **T024**: Implement health check endpoint
  - File: `src/api/health.py`
  - Import fastapi, models.health, datetime
  - Create router = APIRouter()
  - Implement GET /health:
    * Check API is running (always true)
    * Try importing youtube_transcript_api (catch ImportError)
    * Build HealthStatus response
    * Return 200 if healthy/degraded, 503 if unhealthy
  - Follow contract from contracts/health-check.md
  - No authentication required
  - **Files**: `src/api/health.py`

- [ ] **T025**: Implement transcript endpoint
  - File: `src/api/v1/transcript.py`
  - Create `src/api/v1/__init__.py` first
  - Import fastapi, models, services, dependencies
  - Create router = APIRouter(prefix="/api/v1")
  - Implement POST /api/v1/transcript:
    * Dependency: verify_api_key
    * Request body: VideoIdentifierInput
    * Extract video_id using video_id_parser
    * Get transcript using transcript_service
    * Build APIResponse with data/error/metadata
    * Handle all exceptions → appropriate HTTP status codes
    * Track request timing for metadata
  - Follow contract from contracts/get-transcript.md
  - Map exceptions per research.md Section 5
  - **Files**: `src/api/v1/__init__.py`, `src/api/v1/transcript.py`

### Main Application (Sequential - Depends on All Above)

- [ ] **T026**: Create FastAPI application
  - File: `src/main.py`
  - Import FastAPI, middleware, routers, config.settings
  - Create app = FastAPI():
    * title="YouTube Transcript API"
    * version=settings.app_version
    * docs_url="/docs"
    * redoc_url="/redoc"
  - Add middleware:
    * RequestIDMiddleware
    * LoggingMiddleware
    * CORSMiddleware (if needed)
  - Include routers:
    * app.include_router(health.router)
    * app.include_router(transcript.router)
  - Add startup/shutdown event handlers
  - Log startup with config summary
  - **Files**: `src/main.py`

---

## Phase 3.5: Polish & Validation

### Unit Tests (Parallel - Different Files)

- [ ] **T027 [P]**: Create unit tests for video ID parser
  - File: `tests/unit/test_video_id_parser.py`
  - Import pytest, services.video_id_parser
  - Test extract_video_id function:
    * Valid raw ID: "dQw4w9WgXcQ" → "dQw4w9WgXcQ"
    * Valid full URL: "https://youtube.com/watch?v=dQw4w9WgXcQ" → "dQw4w9WgXcQ"
    * Valid short URL: "https://youtu.be/dQw4w9WgXcQ" → "dQw4w9WgXcQ"
    * Invalid format: "invalid!!!" → raises InvalidVideoIdError
    * Edge cases: special characters, empty string
  - Aim for 100% coverage of parser logic
  - **Files**: `tests/unit/test_video_id_parser.py`

- [ ] **T028 [P]**: Create unit tests for models
  - File: `tests/unit/test_models.py`
  - Import pytest, all models
  - Test Pydantic validation for each model:
    * TranscriptSegment: empty text fails, negative start fails
    * Transcript: empty segments fails, invalid video_id fails
    * APIResponse: both data and error fails validation
    * ErrorDetail: empty code fails
  - Test model serialization (to_dict, from_dict)
  - **Files**: `tests/unit/test_models.py`

- [ ] **T029 [P]**: Create unit tests for transcript service
  - File: `tests/unit/test_transcript_service.py`
  - Import pytest, pytest_mock, services.transcript_service
  - Mock youtube_transcript_api
  - Test get_transcript function:
    * Success case: returns Transcript model
    * Video not found: raises VideoNotFoundError
    * Transcript unavailable: raises TranscriptUnavailableError
    * Timeout: raises TimeoutError
    * Retry logic: 3 attempts with backoff
  - Verify async/await behavior
  - **Files**: `tests/unit/test_transcript_service.py`

### Containerization (Sequential)

- [ ] **T030**: Create Dockerfile
  - File: `Dockerfile`
  - Multi-stage build:
    * Stage 1: Builder with Poetry
      - FROM python:3.11-alpine AS builder
      - Install poetry
      - Copy pyproject.toml, poetry.lock
      - Export to requirements.txt
    * Stage 2: Runtime
      - FROM python:3.11-alpine
      - Create non-root user (appuser)
      - Copy requirements.txt
      - Install dependencies
      - Copy src/
      - Switch to appuser
      - HEALTHCHECK using /health endpoint
      - CMD: uvicorn src.main:app --host 0.0.0.0 --port 8000
  - **Resource Limits** (example for production deployment):
    ```yaml
    Resources:
      memory: 512Mi          # Soft limit for normal operation
      memory_limit: 1Gi      # Hard limit to prevent OOM
      cpu: 500m              # 0.5 CPU cores (500 millicores)
    ```
  - Follow Dockerfile from research.md Section 9
  - **Files**: `Dockerfile`

- [ ] **T031**: Create Docker ignore and compose files
  - File: `.dockerignore`
  - Exclude: tests/, .git/, .env, __pycache__/, *.pyc, .venv/
  - Create `docker-compose.yml` for local development:
    * Service: api
    * Build from Dockerfile
    * Environment variables from .env
    * Port mapping: 8000:8000
    * Volume for development (optional)
  - **Note**: docker-compose.yml is for local development only.
    Production deployments should use orchestration-specific
    configurations (Kubernetes manifests, ECS task definitions,
    Docker Swarm compose, etc.) with proper secrets management.
  - **Files**: `.dockerignore`, `docker-compose.yml`

### Documentation & Validation (Sequential)

- [ ] **T032**: Create README.md
  - File: `README.md`
  - Sections:
    * Project overview
    * Features
    * Prerequisites (Python 3.11+, Poetry, Docker)
    * Quick start (Poetry, Docker)
    * Configuration (environment variables)
    * API documentation (/docs)
    * Testing (pytest commands)
    * Development (linting, formatting)
  - Include examples from quickstart.md
  - **Files**: `README.md`

- [ ] **T033**: Run full test suite and coverage report
  - Execute: `poetry run pytest --cov=src --cov-report=html --cov-report=term`
  - Verify all tests pass
  - Verify coverage >= 80% (constitutional requirement)
  - Generate coverage report
  - Fix any failing tests
  - **Validation**: All tests pass, coverage >= 80%

- [ ] **T034**: Run linting and formatting
  - Execute: `poetry run black src/ tests/`
  - Execute: `poetry run ruff check src/ tests/`
  - Execute: `poetry run mypy src/`
  - Fix any linting errors
  - Ensure all type hints pass mypy strict mode
  - **Validation**: No linting errors, mypy passes

- [ ] **T035**: Build and test Docker image
  - Execute: `docker build -t yt-transcript-api:latest .`
  - Verify image builds successfully
  - Check image size (should be ~50-80 MB)
  - Run container: `docker run -e API_KEYS=test-key -p 8000:8000 yt-transcript-api`
  - Test health endpoint: `curl http://localhost:8000/health`
  - Test API endpoint with valid API key
  - Verify container runs as non-root user
  - **Validation**: Container builds, runs, health check passes

---

## Dependency Graph

```
Phase 3.1 (Setup)
  T001 → T002 → T003 → T004
  (sequential: each builds on previous)

Phase 3.2 (Tests)
  T005 [P] ┐
  T006 [P] ├─ All parallel (different files)
  T007 [P] │
  T008 [P] │
  T009 [P] │
  T010 [P] ┘

Phase 3.3 (Core)
  T011 [P] ┐
  T012 [P] │
  T013 [P] ├─ Models & config parallel
  T014 [P] │
  T015 [P] ┘
        ↓
  T016 → T017 → T018 → T019
  (sequential: services have dependencies)
        ↓
  T020 [P] (can run parallel with above)

Phase 3.4 (API)
  T021 [P] ┐
  T022 [P] ┘ middleware parallel
        ↓
  T023 → T024 → T025 → T026
  (sequential: endpoints depend on dependencies)

Phase 3.5 (Polish)
  T027 [P] ┐
  T028 [P] ├─ Unit tests parallel
  T029 [P] ┘
        ↓
  T030 → T031 → T032 → T033 → T034 → T035
  (sequential: validation builds on previous)
```

---

## Task Summary

**Total Tasks**: 35

**By Phase**:
- Phase 3.1 Setup: 4 tasks (sequential)
- Phase 3.2 Tests: 6 tasks (all parallel)
- Phase 3.3 Core: 10 tasks (5 parallel models, 4 sequential services, 1 parallel util)
- Phase 3.4 API: 6 tasks (2 parallel middleware, 4 sequential endpoints)
- Phase 3.5 Polish: 9 tasks (3 parallel unit tests, 6 sequential validation)

**Parallel Tasks**: 16 tasks marked [P]  
**Sequential Tasks**: 19 tasks

**Estimated Effort**:
- Setup: 2-3 hours
- Tests: 4-5 hours (can parallelize)
- Core: 6-8 hours
- API: 3-4 hours
- Polish: 3-4 hours
- **Total**: 18-24 hours of development time

---

## Execution Instructions

### Sequential Execution
```bash
# Execute tasks in order T001 → T035
# Wait for each phase to complete before starting next
```

### Parallel Execution Example
```bash
# Phase 3.2: Can run all 6 test tasks simultaneously
T005 & T006 & T007 & T008 & T009 & T010

# Phase 3.3: Can run 5 model tasks simultaneously
T011 & T012 & T013 & T014 & T015
```

### Validation Checkpoints
- After Phase 3.2: All tests should fail (red phase of TDD)
- After Phase 3.3: Core functionality tests should pass
- After Phase 3.4: All contract and integration tests should pass
- After Phase 3.5: 100% test suite passes, coverage >= 80%

---

## Constitutional Compliance Checklist

- [x] TDD Approach: Phase 3.2 (Tests) MUST complete before Phase 3.3 (Core)
- [x] Type Hints: All functions require type annotations (mypy strict)
- [x] Testing: Minimum 80% coverage (T033 validates)
- [x] Code Quality: black formatting, ruff linting (T034 validates)
- [x] Containerization: Docker with health checks (T030, T031, T035)
- [x] Documentation: OpenAPI automatic, README manual (T032)
- [x] Observability: Structured logging in all services
- [x] Security: API key auth, non-root container user

---

**Ready for Implementation**: Execute tasks T001-T035 in dependency order following TDD principles ✅
