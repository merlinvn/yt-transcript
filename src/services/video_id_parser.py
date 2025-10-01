"""Video ID parser service.

Extracts YouTube video IDs from various input formats:
- Raw video ID (11 characters)
- Full YouTube URL (youtube.com/watch?v=...)
- Short YouTube URL (youtu.be/...)
"""

import re
from urllib.parse import urlparse, parse_qs
from src.utils.exceptions import InvalidVideoIdError


def extract_video_id(identifier: str) -> str:
    """Extract YouTube video ID from various formats.
    
    Args:
        identifier: Raw video ID, full URL, or short URL
        
    Returns:
        Extracted 11-character video ID
        
    Raises:
        InvalidVideoIdError: If format is invalid or ID can't be extracted
        
    Examples:
        >>> extract_video_id("dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_video_id("https://youtu.be/dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
    """
    if not identifier or not isinstance(identifier, str):
        raise InvalidVideoIdError(
            "Invalid YouTube video identifier format",
            "Video identifier must be a non-empty string",
        )

    identifier = identifier.strip()

    # Pattern 1: Raw video ID (11 characters, alphanumeric with - and _)
    if re.match(r"^[A-Za-z0-9_-]{11}$", identifier):
        return identifier

    # Pattern 2: Full YouTube URL (youtube.com/watch?v=...)
    if "youtube.com/watch" in identifier:
        try:
            parsed = urlparse(identifier)
            video_id = parse_qs(parsed.query).get("v", [None])[0]
            if video_id and re.match(r"^[A-Za-z0-9_-]{11}$", video_id):
                return video_id
        except Exception:
            pass

    # Pattern 3: Short YouTube URL (youtu.be/...)
    if "youtu.be/" in identifier:
        try:
            parsed = urlparse(identifier)
            # Get path after the slash
            video_id = parsed.path.lstrip("/").split("/")[0].split("?")[0]
            if video_id and re.match(r"^[A-Za-z0-9_-]{11}$", video_id):
                return video_id
        except Exception:
            pass

    # If we get here, format is invalid
    raise InvalidVideoIdError(
        "Invalid YouTube video identifier format",
        "Video identifier must be an 11-character ID, full YouTube URL, or short youtu.be URL",
    )
