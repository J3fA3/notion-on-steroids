"""
Lotus FastAPI Application Entry Point.
"""
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.base import Base, engine

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Startup:
        - Create database tables
        - Initialize connections

    Shutdown:
        - Close connections
        - Cleanup resources
    """
    logger.info("Starting Lotus backend application...")

    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

    logger.info("Lotus backend ready to serve requests")

    yield

    # Shutdown
    logger.info("Shutting down Lotus backend...")


# Create FastAPI app
app = FastAPI(
    title="Lotus API",
    description="Personal AI Task Companion - Backend API",
    version="0.1.0",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Health Check Endpoints
# ============================================


@app.get("/")
async def root():
    """
    Root endpoint - API information.

    Returns:
        dict: API name, version, and status
    """
    return {
        "name": "Lotus API",
        "version": "0.1.0",
        "status": "running",
        "message": "Personal AI Task Companion Backend",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and deployment.

    Returns:
        dict: Health status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected",
        "version": "0.1.0",
    }


# ============================================
# API Routes
# ============================================
from app.api import tasks

app.include_router(tasks.router, prefix="/api", tags=["tasks"])

# TODO: Add more routers as we build them
# from app.api import auth, integrations
# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
# app.include_router(integrations.router, prefix="/api/integrations", tags=["integrations"])


# ============================================
# Error Handlers
# ============================================


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.

    Args:
        request: The incoming request
        exc: The exception that was raised

    Returns:
        JSONResponse with error details
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {
        "error": "Internal server error",
        "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
