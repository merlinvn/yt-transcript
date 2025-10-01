"""Logging middleware for structured request/response logging."""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from src.utils.logger import get_logger


logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured logging of requests and responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Log request start, end, and errors with full context.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler in chain
            
        Returns:
            Response
        """
        # Extract request ID (added by RequestIDMiddleware)
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Log request start
        logger.info(
            "request_started",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
        )
        
        # Track duration
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log successful response
            logger.info(
                "request_completed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )
            
            return response
            
        except Exception as exc:
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log error
            logger.error(
                "request_failed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms,
                error=str(exc),
                error_type=type(exc).__name__,
            )
            
            # Re-raise to be handled by FastAPI
            raise
