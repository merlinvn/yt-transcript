# Multi-stage Dockerfile for YouTube Transcript API
# Stage 1: Builder - Export dependencies

FROM python:3.11-alpine AS builder

# Install poetry
RUN pip install --no-cache-dir poetry==1.7.0

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Export dependencies to requirements.txt
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


# Stage 2: Runtime - Minimal production image

FROM python:3.11-alpine

# Install runtime dependencies
RUN apk add --no-cache curl

# Create non-root user
RUN addgroup -S appuser && adduser -S appuser -G appuser

# Set working directory
WORKDIR /app

# Copy requirements from builder
COPY --from=builder /app/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
