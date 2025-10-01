"""FastAPI dependencies for authentication and request tracking."""

from typing import Optional
from fastapi import Header, HTTPException, Request
from src.services.auth_service import validate_api_key, hash_api_key


async def verify_api_key(x_api_key: Optional[str] = Header(None, description="API key for authentication")) -> str:
    """Verify API key from X-API-Key header.
    
    Args:
        x_api_key: API key from request header (optional to allow custom 401 error)
        
    Returns:
        Hashed API key for logging (never log plaintext)
        
    Raises:
        HTTPException: 401 if API key is invalid or missing
    """
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail={
                "data": None,
                "error": {
                    "code": "INVALID_API_KEY",
                    "message": "Invalid or missing API key",
                    "details": "Provide a valid API key in the X-API-Key header",
                },
                "metadata": {
                    "request_id": "auth-error",
                    "timestamp": None,
                    "duration_ms": 0,
                    "version": "1.0.0",
                },
            },
        )
    
    if not validate_api_key(x_api_key):
        raise HTTPException(
            status_code=401,
            detail={
                "data": None,
                "error": {
                    "code": "INVALID_API_KEY",
                    "message": "Invalid or missing API key",
                    "details": "Provide a valid API key in the X-API-Key header",
                },
                "metadata": {
                    "request_id": "auth-error",
                    "timestamp": None,
                    "duration_ms": 0,
                    "version": "1.0.0",
                },
            },
        )
    
    # Return hashed key for logging
    return hash_api_key(x_api_key)


async def get_request_id(request: Request) -> str:
    """Extract request ID from request state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Request ID (UUID)
    """
    return getattr(request.state, "request_id", "unknown")
