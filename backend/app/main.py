from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import engine, Base
from .api.endpoints import cameras, zones, models, exporters, plate_events, websocket

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cameras.router, prefix="/api/cameras", tags=["cameras"])
app.include_router(zones.router, prefix="/api/zones", tags=["zones"])
app.include_router(models.router, prefix="/api/models", tags=["models"])
app.include_router(exporters.router, prefix="/api/exporters", tags=["exporters"])
app.include_router(plate_events.router, prefix="/api/plate-events", tags=["plate-events"])
app.include_router(websocket.router, prefix="/api", tags=["websocket"])


@app.get("/")
async def root():
    return {"message": f"{settings.APP_NAME} v{settings.APP_VERSION}"}


@app.get("/healthz")
async def health_check():
    return {"status": "healthy"}
