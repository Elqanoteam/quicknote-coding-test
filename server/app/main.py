"""Main FastAPI application for the notes copilot."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .db import create_db_and_tables
from .routers import notes, tasks
from .schemas import HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Notes Copilot application...")

    # Validate settings
    try:
        settings.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise

    # Create database tables
    create_db_and_tables()
    logger.info("Database tables created")

    yield

    # Shutdown
    logger.info("Shutting down Notes Copilot application...")


# Create FastAPI app
app = FastAPI(
    title="Notes Copilot API",
    description="A minimal but polished notes copilot with AI-powered analysis and semantic search",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(notes.router, prefix=settings.API_PREFIX)
app.include_router(tasks.router, prefix=settings.API_PREFIX)


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Notes Copilot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
