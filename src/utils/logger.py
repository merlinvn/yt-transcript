"""Structured logging configuration using structlog."""

import structlog
from src.config import settings


def configure_logging() -> None:
    """Configure structlog for JSON-formatted structured logging."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(structlog.stdlib, settings.log_level.upper(), structlog.stdlib.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a logger instance for the given name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


# Configure on module import
configure_logging()
