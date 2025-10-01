"""Authentication service for API key validation."""

import hashlib
from src.config import settings


# Parse valid API keys from settings (comma-separated)
VALID_API_KEYS = set(key.strip() for key in settings.api_keys.split(",") if key.strip())


def validate_api_key(api_key: str) -> bool:
    """Validate if provided API key is valid.
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if valid, False otherwise
    """
    return api_key in VALID_API_KEYS


def hash_api_key(api_key: str) -> str:
    """Hash API key for logging (never log plaintext keys).
    
    Args:
        api_key: API key to hash
        
    Returns:
        SHA256 hash of the API key (first 16 characters)
    """
    return hashlib.sha256(api_key.encode()).hexdigest()[:16]
