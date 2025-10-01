# Implementation Plan: YouTube Transcript API Endpoint

**Branch**: `001-fastapi-endpoint-for` | **Date**: 2025-10-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-fastapi-endpoint-for/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary

Build a FastAPI-based REST API service that retrieves YouTube video transcripts. The service accepts video identifiers in three formats (raw ID, full URL, short URL), validates and extracts the video ID, retrieves transcripts using the `youtube-transcript-api` library, and returns structured JSON responses. API key authentication via X-API-Key header secures all transcript requests. The service is containerized, stateless, and designed for 10 req/s capacity with P95 latency under 5 seconds.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI 0.104+, uvicorn 0.24+ (with standard extras), youtube-transcript-api 0.6.1, pydantic 2.5+, structlog 23.2+  
**Storage**: N/A (stateless service, no data persistence)  
**Testing**: pytest 7.4+, pytest-asyncio, pytest-cov, pytest-mock, httpx (for async endpoint testing)  
**Target Platform**: Linux container (Docker) with Alpine base, deployable to any container orchestration platform  
**Project Type**: single (backend API service only)  
**Performance Goals**: 10 requests/second minimum, P95 latency < 5 seconds, P50 ~500ms  
**Constraints**: 30-second timeout for transcript retrieval, stateless design for horizontal scaling, non-root container user  
**Scale/Scope**: Low-volume service (10 req/s), 2 REST endpoints (transcript, health), API key authentication, structured JSON logging

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. API-First Architecture ✅ PASS
- **Requirement**: RESTful API with OpenAPI documentation, proper HTTP semantics, consistent JSON responses
- **Compliance**: FastAPI provides automatic OpenAPI/Swagger docs at /docs, standardized response structure with data/error/metadata fields, proper status codes (200, 400, 401, 404, 503)
- **Evidence**: Contracts defined in contracts/, response format documented in data-model.md

### II. Input Flexibility ✅ PASS
- **Requirement**: Accept YouTube video IDs in multiple formats (full URL, short URL, raw ID) with robust parsing
- **Compliance**: Custom regex-based parser supports all three formats per FR-001, clear validation errors per FR-002
- **Evidence**: Parser implementation detailed in research.md Section 3, test cases in contracts/get-transcript.md

### III. Container-First Deployment ✅ PASS
- **Requirement**: Fully containerized with Docker, optimized image, pinned dependencies, env vars, non-root user, health check
- **Compliance**: Multi-stage Dockerfile with Alpine base, Poetry for pinned deps, environment variable config, non-root appuser, /health endpoint
- **Evidence**: Dockerfile structure in research.md Section 9, health check contract in contracts/health-check.md, config in research.md Section 13

### IV. Test-Driven Development ✅ PASS
- **Requirement**: TDD mandatory - write tests first, see them fail, implement, refactor
- **Compliance**: Phase 3.2 (Tests First) must complete before Phase 3.3 (Core Development), contract tests per endpoint, integration tests per user story
- **Evidence**: Test strategy in research.md Section 10, test cases in contracts/, quickstart.md provides integration scenarios

### V. Observability & Reliability ✅ PASS
- **Requirement**: Structured JSON logging, request ID tracking, metrics, graceful error handling, retry logic
- **Compliance**: structlog for JSON logs per FR-011, request_id in all responses, exponential backoff retry per NFR-004, descriptive error messages per FR-006
- **Evidence**: Logging strategy in research.md Section 7, error handling in research.md Section 5, ResponseMetadata in data-model.md

### Python & FastAPI Requirements ✅ PASS
- **Requirement**: Python 3.11+, FastAPI with async, type hints, black/ruff, 80% coverage, poetry/pip-tools
- **Compliance**: Python 3.11+ specified, async FastAPI endpoints, Pydantic models provide type safety, poetry for deps, pytest-cov for coverage tracking
- **Evidence**: Dependencies in research.md Section 11, async implementation in research.md Section 12

### API Design Standards ✅ PASS
- **Requirement**: RESTful naming, consistent JSON structure (data/error/metadata), proper HTTP status codes, Pydantic validation, auto-generated docs
- **Compliance**: POST /api/v1/transcript follows REST, standardized response format in data-model.md Section 5, all required status codes mapped in research.md Section 5
- **Evidence**: APIResponse model in data-model.md, contracts in contracts/

### Security & Privacy ✅ PASS
- **Requirement**: Input validation, rate limiting, no hardcoded secrets, explicit CORS, pass-through service
- **Compliance**: Pydantic validation per FR-002, API key via env vars per research.md Section 13, stateless pass-through per NFR-005, API key authentication per FR-012/013/014
- **Evidence**: Authentication in research.md Section 4, validation in data-model.md, no data persistence per data-model.md state management

### Performance Standards ✅ PASS
- **Requirement**: Meet performance targets, configurable timeouts, consider caching, define resource limits
- **Compliance**: P95 < 5s per NFR-001, 30s timeout per NFR-003, 10 req/s capacity per NFR-002, container resource limits per NFR-006
- **Evidence**: Performance estimates in research.md, timeout in research.md Section 6, Docker resource limits in research.md Section 9

**GATE RESULT**: ✅ ALL CONSTITUTIONAL REQUIREMENTS MET - Proceed to Phase 0

## Project Structure

### Documentation (this feature)
```
specs/001-fastapi-endpoint-for/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (complete)
├── data-model.md        # Phase 1 output (complete)
├── quickstart.md        # Phase 1 output (complete)
├── contracts/           # Phase 1 output (complete)
│   ├── get-transcript.md    # POST /api/v1/transcript contract
│   └── health-check.md      # GET /health contract
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Single project structure (backend API service only)
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization, startup/shutdown
│   ├── config.py                  # Settings with pydantic-settings (env vars)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py             # VideoIdentifierInput, APIRequest
│   │   ├── response.py            # APIResponse, ErrorDetail, ResponseMetadata
│   │   ├── transcript.py          # Transcript, TranscriptSegment
│   │   └── health.py              # HealthStatus
│   ├── services/
│   │   ├── __init__.py
│   │   ├── video_id_parser.py    # extract_video_id() logic
│   │   ├── transcript_service.py  # get_transcript() with retry logic
│   │   └── auth_service.py        # API key validation
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py        # FastAPI dependencies (auth, request ID)
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   └── transcript.py      # POST /api/v1/transcript endpoint
│   │   └── health.py              # GET /health endpoint
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── request_id.py          # Request ID generation/tracking
│   │   └── logging_middleware.py  # Structured logging setup
│   └── utils/
│       ├── __init__.py
│       ├── logger.py              # structlog configuration
│       └── exceptions.py          # Custom exception classes
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures (mock API keys, test client)
│   ├── contract/
│   │   ├── __init__.py
│   │   ├── test_transcript_contract.py    # Contract tests for transcript endpoint
│   │   └── test_health_contract.py        # Contract tests for health endpoint
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_transcript_flow.py        # End-to-end scenarios from quickstart
│   │   ├── test_authentication.py         # API key auth scenarios
│   │   └── test_error_handling.py         # Error scenario validations
│   └── unit/
│       ├── __init__.py
│       ├── test_video_id_parser.py        # URL parsing logic
│       ├── test_transcript_service.py     # Service layer mocked
│       └── test_models.py                 # Pydantic model validation
├── pyproject.toml             # Poetry dependencies and project metadata
├── poetry.lock                # Locked dependency versions
├── Dockerfile                 # Multi-stage build with Alpine
├── .dockerignore              # Exclude tests, .git, etc.
├── .env.example               # Example environment variables
├── README.md                  # Project overview, setup instructions
└── .github/ (or .specify/)
    └── copilot-instructions.md # Agent-specific guidance (Phase 1 output)
```

**Structure Decision**: Single project structure selected because:
- Backend-only API service (no frontend or mobile components)
- Simple, flat structure appropriate for microservice
- All code under `src/` for clean package imports
- Tests mirror `src/` structure for discoverability
- FastAPI convention: routers in `api/`, models separate, services for business logic

## Phase 0: Outline & Research ✅ COMPLETE

**Status**: All technical decisions made and documented

**Research Tasks Completed**:
1. ✅ Core technology stack selection (Python 3.11+, FastAPI)
2. ✅ YouTube transcript retrieval approach (youtube-transcript-api package)
3. ✅ URL parsing and video ID extraction strategy (regex-based custom parser)
4. ✅ API key authentication mechanism (custom middleware with env vars)
5. ✅ Error handling and response structure (standardized JSON with data/error/metadata)
6. ✅ Timeout and retry logic (30s timeout, 3 retries with exponential backoff)
7. ✅ Logging and observability approach (structlog with JSON formatting)
8. ✅ Health check implementation (simple endpoint with dependency checks)
9. ✅ Containerization strategy (multi-stage Docker with Alpine)
10. ✅ Testing strategy (pytest with TDD, contract → integration → unit)
11. ✅ Dependency management (Poetry with lock file)
12. ✅ Performance optimization (async endpoints, connection handling)
13. ✅ Configuration management (pydantic-settings with env vars)

**Output**: research.md complete with 13 technical decisions, rationales, alternatives, risk assessment, and performance estimates

**Unknowns Resolved**: All NEEDS CLARIFICATION markers from spec resolved during /clarify phase

## Phase 1: Design & Contracts ✅ COMPLETE
*Prerequisites: research.md complete*

**1. Data Model** ✅ COMPLETE
- Extracted 8 entities from feature spec
- Documented in data-model.md with Pydantic model specifications:
  - VideoIdentifier (input parsing)
  - TranscriptSegment (timestamped text)
  - Transcript (complete video transcript)
  - APIRequest (request tracking)
  - APIResponse (standardized response)
  - ErrorDetail (structured errors)
  - ResponseMetadata (tracking and metrics)
  - HealthStatus (health check response)
- Defined validation rules, relationships, data flow
- State management strategy: stateless (no persistence)

**2. API Contracts** ✅ COMPLETE
- Generated 2 contract files in contracts/:
  - get-transcript.md: POST /api/v1/transcript
    * Request/response schemas
    * Success (200) and error responses (400, 401, 404, 503, 500)
    * 10 test cases (TC-001 through TC-010)
  - health-check.md: GET /health
    * Health status responses (healthy, degraded, unhealthy)
    * Container integration (Docker HEALTHCHECK, K8s probes)
    * 5 test cases (TC-H01 through TC-H05)
- All contracts follow RESTful conventions and constitutional requirements

**3. Integration Scenarios** ✅ COMPLETE
- Generated quickstart.md with 10 complete integration scenarios:
  - Scenario 1-3: Happy paths (raw ID, full URL, short URL)
  - Scenario 4-7: Error handling (invalid format, auth, not found, no transcript)
  - Scenario 8: Health check
  - Scenario 9: Concurrent requests
  - Scenario 10: API documentation access
- Each scenario includes: curl commands, expected responses, validation points
- Added environment setup, troubleshooting, performance benchmarking

**4. Agent Context** ⏭️ DEFERRED
- Agent-specific guidance file update deferred until repository structure exists
- Will run after initial project scaffolding: `.specify/scripts/bash/update-agent-context.sh copilot`

**Output**: data-model.md (8 entities), contracts/ (2 files, 15 test cases), quickstart.md (10 scenarios)

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:

1. **Load Base Template**: Use `.specify/templates/tasks-template.md` as foundation

2. **Generate from Design Artifacts**:
   - **From contracts/ (2 files)**:
     * contracts/get-transcript.md → T00X: Contract test for POST /api/v1/transcript [P]
     * contracts/health-check.md → T00Y: Contract test for GET /health [P]
   
   - **From data-model.md (8 entities)**:
     * VideoIdentifier → T00Z: Create VideoIdentifier models [P]
     * TranscriptSegment → T0XX: Create TranscriptSegment model [P]
     * Transcript → T0XX: Create Transcript model [P]
     * APIRequest → T0XX: Create APIRequest model [P]
     * APIResponse → T0XX: Create APIResponse model [P]
     * ErrorDetail → T0XX: Create ErrorDetail model [P]
     * ResponseMetadata → T0XX: Create ResponseMetadata model [P]
     * HealthStatus → T0XX: Create HealthStatus model [P]
   
   - **From quickstart.md (10 scenarios)**:
     * Scenario 1-10 → 10 integration test tasks [P]
   
   - **From research.md decisions**:
     * Setup: Project init, Poetry config, dependencies
     * Services: video_id_parser, transcript_service, auth_service
     * API: endpoints, middleware, dependencies
     * Integration: logging, error handling, configuration
     * Polish: Docker, documentation, performance validation

3. **Task Ordering Rules**:
   - **Phase 3.1 Setup**: Project structure, dependencies, tooling (sequential)
   - **Phase 3.2 Tests**: Contract tests [P], integration test stubs [P] (must complete before 3.3)
   - **Phase 3.3 Core**: Models [P], services (parsers before transcript service), middleware
   - **Phase 3.4 Integration**: API endpoints, auth wiring, logging setup
   - **Phase 3.5 Polish**: Unit tests [P], Docker, docs, validation

4. **Parallel Execution Markers [P]**:
   - Different model files → [P]
   - Different contract test files → [P]
   - Different integration test files → [P]
   - Same file or dependencies → sequential (no [P])

**Estimated Task Count**: 30-35 tasks
- Setup: 3-4 tasks
- Tests: 12-15 tasks (2 contract + 10 integration + unit)
- Core: 8-10 tasks (models + services)
- Integration: 4-5 tasks (endpoints + wiring)
- Polish: 3-4 tasks (Docker + docs + validation)

**IMPORTANT**: The /tasks command will execute this strategy to create tasks.md. The /plan command STOPS here.

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

**No Violations**: All constitutional requirements are met. No complexity deviations to document.


## Progress Tracking

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) ✅
- [x] Phase 1: Design complete (/plan command) ✅
- [x] Phase 2: Task planning approach documented (/plan command) ✅
- [ ] Phase 3: Tasks generated (/tasks command) ⏭️ NEXT STEP
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS ✅
- [x] Post-Design Constitution Check: PASS ✅
- [x] All NEEDS CLARIFICATION resolved ✅
- [x] Complexity deviations documented: N/A (none) ✅

**Artifacts Generated**:
- [x] research.md (13 technical decisions, risk assessment)
- [x] data-model.md (8 entities with Pydantic schemas)
- [x] contracts/get-transcript.md (10 test cases)
- [x] contracts/health-check.md (5 test cases)
- [x] quickstart.md (10 integration scenarios)
- [x] plan.md (this file)
- [ ] Agent context file (deferred until project structure exists)
- [ ] tasks.md (next command: /tasks)

---

**STATUS**: ✅ PLAN COMPLETE - Ready for `/tasks` command

*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
