from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from ...core.database import get_db
from ...models import PlateEvent, Camera
from ...schemas import PlateEvent as PlateEventSchema, PlateEventCreate

router = APIRouter()


@router.get("/", response_model=List[PlateEventSchema])
def list_plate_events(
    skip: int = 0,
    limit: int = 100,
    camera_id: Optional[int] = None,
    plate_text: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List plate events with optional filters"""
    query = db.query(PlateEvent)

    if camera_id:
        query = query.filter(PlateEvent.camera_id == camera_id)

    if plate_text:
        query = query.filter(PlateEvent.plate_text.ilike(f"%{plate_text}%"))

    events = query.order_by(desc(PlateEvent.timestamp)).offset(skip).limit(limit).all()
    return events


@router.get("/{event_id}", response_model=PlateEventSchema)
def get_plate_event(event_id: int, db: Session = Depends(get_db)):
    """Get a specific plate event by ID"""
    event = db.query(PlateEvent).filter(PlateEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Plate event not found")
    return event


@router.post("/ingest", response_model=PlateEventSchema)
async def ingest_plate_event(event: PlateEventCreate, db: Session = Depends(get_db)):
    """Ingest a plate event from the edge worker"""
    # Verify camera exists
    camera = db.query(Camera).filter(Camera.id == event.camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    # Convert BoundingBox to dict if present
    event_data = event.model_dump()
    if event_data.get("bbox"):
        event_data["bbox"] = event_data["bbox"]

    # Create plate event
    db_event = PlateEvent(**event_data)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # TODO: Trigger websocket broadcast
    # TODO: Trigger exporter integrations

    return db_event


@router.delete("/{event_id}")
def delete_plate_event(event_id: int, db: Session = Depends(get_db)):
    """Delete a plate event"""
    db_event = db.query(PlateEvent).filter(PlateEvent.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Plate event not found")

    db.delete(db_event)
    db.commit()
    return {"message": "Plate event deleted successfully"}
