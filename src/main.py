"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import health
from src.api.v1 import transcript
from src.config import settings
from src.middleware.logging_middleware import LoggingMiddleware
from src.middleware.request_id import RequestIDMiddleware
from src.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    ## start
    """Log application startup."""
    logger.info(
        "application_started",
        version=settings.app_version,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
    )
    yield

    ## end
    """Log application shutdown."""
    logger.info("application_shutdown")


# Create FastAPI application
app = FastAPI(
    title="YouTube Transcript API",
    description="FastAPI service for retrieving YouTube video transcripts",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# Add middleware (order matters - first added is outermost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)


# Include routers
app.include_router(health.router)
app.include_router(transcript.router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "YouTube Transcript API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }
