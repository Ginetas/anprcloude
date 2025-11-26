"""
Event Routes
API endpoints for plate event management and real-time streaming.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_redis, get_session
from app.models import Camera, PlateEvent, Zone
from app.schemas import (
    EventIngestResponse,
    EventStatsResponse,
    PlateEventCreate,
    PlateEventFilter,
    PlateEventRead,
)
from app.services.event_service import EventService

router = APIRouter()


@router.post("/ingest", response_model=EventIngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_event(
    camera_id: int = Form(...),
    plate_text: str = Form(...),
    confidence: float = Form(...),
    zone_id: Optional[int] = Form(None),
    vehicle_info: Optional[str] = Form(None),
    tpms_status: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None),
    frame_image: Optional[UploadFile] = File(None),
    crop_image: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(get_session),
):
    """
    Ingest a new plate detection event.

    Supports file uploads for frame and crop images.

    Args:
        camera_id: Source camera identifier
        plate_text: Recognized license plate text
        confidence: Recognition confidence (0.0-1.0)
        zone_id: Detection zone identifier (optional)
        vehicle_info: Vehicle information as JSON string (optional)
        tpms_status: TPMS data as JSON string (optional)
        metadata: Additional metadata as JSON string (optional)
        frame_image: Full frame image file (optional)
        crop_image: Plate crop image file (optional)
        session: Database session

    Returns:
        EventIngestResponse with event_id and status
    """
    try:
        # Validate camera exists
        camera = await session.get(Camera, camera_id)
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Camera with id {camera_id} not found"
            )

        # Validate zone if provided
        if zone_id:
            zone = await session.get(Zone, zone_id)
            if not zone:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Zone with id {zone_id} not found"
                )

        # Use service to handle event creation
        event_service = EventService(session)
        event = await event_service.create_event(
            camera_id=camera_id,
            plate_text=plate_text,
            confidence=confidence,
            zone_id=zone_id,
            vehicle_info=vehicle_info,
            tpms_status=tpms_status,
            metadata=metadata,
            frame_image=frame_image,
            crop_image=crop_image,
        )

        logger.info(f"Event ingested: {event.event_id} - Plate: {plate_text}")

        return EventIngestResponse(
            success=True,
            event_id=event.event_id,
            message="Event ingested successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Event ingest failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest event: {str(e)}"
        )


@router.get("", response_model=List[PlateEventRead])
async def get_events(
    camera_id: Optional[int] = Query(None, description="Filter by camera ID"),
    zone_id: Optional[int] = Query(None, description="Filter by zone ID"),
    plate_text: Optional[str] = Query(None, description="Filter by plate text (partial match)"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum confidence"),
    start_date: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO format)"),
    exported: Optional[bool] = Query(None, description="Filter by export status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    session: AsyncSession = Depends(get_session),
):
    """
    Get plate events with optional filtering.

    Args:
        camera_id: Filter by camera
        zone_id: Filter by zone
        plate_text: Filter by plate text (partial match)
        min_confidence: Minimum confidence threshold
        start_date: Start date filter
        end_date: End date filter
        exported: Filter by export status
        limit: Maximum results to return
        offset: Pagination offset
        session: Database session

    Returns:
        List of plate events
    """
    try:
        # Build query
        query = select(PlateEvent).order_by(PlateEvent.timestamp.desc())

        # Apply filters
        if camera_id:
            query = query.where(PlateEvent.camera_id == camera_id)

        if zone_id:
            query = query.where(PlateEvent.zone_id == zone_id)

        if plate_text:
            query = query.where(PlateEvent.plate_text.ilike(f"%{plate_text}%"))

        if min_confidence is not None:
            query = query.where(PlateEvent.confidence >= min_confidence)

        if start_date:
            query = query.where(PlateEvent.timestamp >= start_date)

        if end_date:
            query = query.where(PlateEvent.timestamp <= end_date)

        if exported is not None:
            query = query.where(PlateEvent.exported == exported)

        # Apply pagination
        query = query.limit(limit).offset(offset)

        # Execute query
        result = await session.execute(query)
        events = result.scalars().all()

        return events

    except Exception as e:
        logger.error(f"Failed to retrieve events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve events: {str(e)}"
        )


@router.get("/{event_id}", response_model=PlateEventRead)
async def get_event(
    event_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """
    Get a specific plate event by ID.

    Args:
        event_id: Event UUID
        session: Database session

    Returns:
        Plate event details
    """
    try:
        query = select(PlateEvent).where(PlateEvent.event_id == event_id)
        result = await session.execute(query)
        event = result.scalar_one_or_none()

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with id {event_id} not found"
            )

        return event

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve event: {str(e)}"
        )


@router.get("/stats", response_model=EventStatsResponse)
async def get_event_stats(
    camera_id: Optional[int] = Query(None, description="Filter by camera ID"),
    zone_id: Optional[int] = Query(None, description="Filter by zone ID"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    session: AsyncSession = Depends(get_session),
):
    """
    Get event statistics.

    Args:
        camera_id: Filter by camera
        zone_id: Filter by zone
        start_date: Start date filter
        end_date: End date filter
        session: Database session

    Returns:
        Event statistics
    """
    try:
        # Base query
        query = select(PlateEvent)

        # Apply filters
        if camera_id:
            query = query.where(PlateEvent.camera_id == camera_id)

        if zone_id:
            query = query.where(PlateEvent.zone_id == zone_id)

        if start_date:
            query = query.where(PlateEvent.timestamp >= start_date)

        if end_date:
            query = query.where(PlateEvent.timestamp <= end_date)

        # Get total events
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(total_query)
        total_events = total_result.scalar()

        # Get unique plates
        unique_query = select(func.count(func.distinct(PlateEvent.plate_text))).select_from(query.subquery())
        unique_result = await session.execute(unique_query)
        unique_plates = unique_result.scalar()

        # Get average confidence
        avg_query = select(func.avg(PlateEvent.confidence)).select_from(query.subquery())
        avg_result = await session.execute(avg_query)
        avg_confidence = avg_result.scalar() or 0.0

        # Get events by camera
        camera_query = select(
            PlateEvent.camera_id,
            func.count(PlateEvent.id)
        ).group_by(PlateEvent.camera_id)

        if start_date:
            camera_query = camera_query.where(PlateEvent.timestamp >= start_date)
        if end_date:
            camera_query = camera_query.where(PlateEvent.timestamp <= end_date)

        camera_result = await session.execute(camera_query)
        events_by_camera = {str(cam_id): count for cam_id, count in camera_result.all()}

        # Get events by zone
        zone_query = select(
            PlateEvent.zone_id,
            func.count(PlateEvent.id)
        ).where(PlateEvent.zone_id.isnot(None)).group_by(PlateEvent.zone_id)

        if start_date:
            zone_query = zone_query.where(PlateEvent.timestamp >= start_date)
        if end_date:
            zone_query = zone_query.where(PlateEvent.timestamp <= end_date)

        zone_result = await session.execute(zone_query)
        events_by_zone = {str(zone_id): count for zone_id, count in zone_result.all()}

        # Get events by hour (last 24 hours)
        hour_query = select(
            func.extract('hour', PlateEvent.timestamp).label('hour'),
            func.count(PlateEvent.id)
        ).group_by('hour').order_by('hour')

        if start_date:
            hour_query = hour_query.where(PlateEvent.timestamp >= start_date)
        if end_date:
            hour_query = hour_query.where(PlateEvent.timestamp <= end_date)

        hour_result = await session.execute(hour_query)
        events_by_hour = {str(int(hour)): count for hour, count in hour_result.all()}

        # Get recent events
        recent_query = query.order_by(PlateEvent.timestamp.desc()).limit(10)
        recent_result = await session.execute(recent_query)
        recent_events = recent_result.scalars().all()

        return EventStatsResponse(
            total_events=total_events or 0,
            unique_plates=unique_plates or 0,
            avg_confidence=float(avg_confidence),
            events_by_camera=events_by_camera,
            events_by_zone=events_by_zone,
            events_by_hour=events_by_hour,
            recent_events=recent_events,
        )

    except Exception as e:
        logger.error(f"Failed to retrieve event stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve event stats: {str(e)}"
        )


# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time event streaming."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        """Broadcast message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to send message to client: {e}")


# Global connection manager
manager = ConnectionManager()


@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time event streaming.

    Clients can connect to receive live plate detection events.
    """
    await manager.connect(websocket)

    try:
        while True:
            # Keep connection alive and wait for messages
            data = await websocket.receive_text()

            # Handle ping/pong for keep-alive
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
