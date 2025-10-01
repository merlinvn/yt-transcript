"""Request ID middleware for tracking requests across the lifecycle."""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to generate and track request IDs."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Generate UUID for request and add to state and response headers.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler in chain
            
        Returns:
            Response with X-Request-ID header
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Add to request state for access in handlers
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
