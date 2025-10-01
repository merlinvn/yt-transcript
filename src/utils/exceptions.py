"""Custom exception classes for the application."""


class InvalidVideoIdError(ValueError):
    """Raised when video ID format is invalid."""

    def __init__(self, message: str = "Invalid YouTube video identifier format", details: str | None = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class VideoNotFoundError(Exception):
    """Raised when video doesn't exist or can't be found."""

    def __init__(self, message: str = "Video not found", details: str | None = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class TranscriptUnavailableError(Exception):
    """Raised when video exists but transcript is not available."""

    def __init__(self, message: str = "Transcript unavailable", details: str | None = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class ServiceUnavailableError(Exception):
    """Raised when external service (YouTube) is temporarily unavailable."""

    def __init__(self, message: str = "Service temporarily unavailable", details: str | None = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class TranscriptTimeoutError(Exception):
    """Raised when transcript retrieval exceeds timeout."""

    def __init__(self, message: str = "Request timeout", details: str | None = None):
        self.message = message
        self.details = details
        super().__init__(self.message)
