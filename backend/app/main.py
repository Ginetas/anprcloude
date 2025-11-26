"""
Main FastAPI Application
Entry point for the ANPR Cloud Backend API.
"""

import sys
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.config import settings
from app.database import close_db, init_db, redis_manager
from app.routers import config, events, exporters

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format=settings.log_format,
    level=settings.log_level,
    colorize=True,
)

if settings.log_file:
    logger.add(
        settings.log_file,
        format=settings.log_format,
        level=settings.log_level,
        rotation="500 MB",
        retention="10 days",
        compression="zip",
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting ANPR Cloud Backend...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    try:
        # Initialize database connection
        await init_db()
        logger.success("Database connection established")

        # Initialize Redis connection
        await redis_manager.connect()
        logger.success("Redis connection established")

        # Create upload directory
        upload_path = Path(settings.upload_dir)
        upload_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Upload directory: {settings.upload_dir}")

        logger.success("Application startup complete")

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down ANPR Cloud Backend...")

    try:
        # Close database connection
        await close_db()
        logger.info("Database connection closed")

        # Close Redis connection
        await redis_manager.disconnect()
        logger.info("Redis connection closed")

        logger.success("Application shutdown complete")

    except Exception as e:
        logger.error(f"Shutdown error: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-ready ANPR (Automatic Number Plate Recognition) Cloud Backend API",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan,
)


# Middleware Configuration
# -------------------------

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Trusted Host (production only)
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure this properly in production
    )


# Exception Handlers
# ------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "path": str(request.url),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions."""
    logger.warning(f"ValueError: {exc}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": str(exc),
            "path": str(request.url),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# Request Logging Middleware
# ---------------------------

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests."""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


# Root Endpoints
# --------------

@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint.

    Returns:
        Application information
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs" if settings.debug else "disabled",
        "environment": settings.environment,
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status of all services
    """
    health_status = {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
        "services": {},
    }

    # Check database
    try:
        from app.database import async_engine
        async with async_engine.connect() as conn:
            await conn.execute("SELECT 1")
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["services"]["database"] = "unhealthy"
        health_status["status"] = "degraded"

    # Check Redis
    try:
        await redis_manager.client.ping()
        health_status["services"]["redis"] = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["services"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"

    return health_status


@app.get("/ready", tags=["health"])
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes.

    Returns:
        Ready status
    """
    try:
        # Quick database check
        from app.database import async_engine
        async with async_engine.connect() as conn:
            await conn.execute("SELECT 1")

        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready", "error": str(e)},
        )


@app.get("/liveness", tags=["health"])
async def liveness_check():
    """
    Liveness check endpoint for Kubernetes.

    Returns:
        Alive status
    """
    return {"status": "alive"}


# API Router Includes
# -------------------

# Include event routes
app.include_router(
    events.router,
    prefix=f"{settings.api_prefix}/events",
    tags=["events"],
)

# Include config routes
app.include_router(
    config.router,
    prefix=f"{settings.api_prefix}/config",
    tags=["config"],
)

# Include exporter routes
app.include_router(
    exporters.router,
    prefix=f"{settings.api_prefix}/exporters",
    tags=["exporters"],
)


# Metrics Endpoint (if enabled)
# ------------------------------

if settings.enable_metrics:
    from prometheus_client import Counter, Histogram, generate_latest

    # Define metrics
    request_count = Counter(
        "http_requests_total",
        "Total HTTP requests",
        ["method", "endpoint", "status"]
    )
    request_duration = Histogram(
        "http_request_duration_seconds",
        "HTTP request duration",
        ["method", "endpoint"]
    )

    @app.get("/metrics", tags=["monitoring"])
    async def metrics():
        """
        Prometheus metrics endpoint.

        Returns:
            Prometheus metrics
        """
        return generate_latest()


# Development utilities
# ---------------------

if settings.debug:
    @app.get("/debug/config", tags=["debug"])
    async def debug_config():
        """
        Debug endpoint to view configuration.
        Only available in debug mode.
        """
        return settings.model_dump_safe()


# Main entry point
# ----------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
