from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...models import Zone
from ...schemas import Zone as ZoneSchema, ZoneCreate, ZoneUpdate

router = APIRouter()


@router.get("/", response_model=List[ZoneSchema])
def list_zones(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all zones"""
    zones = db.query(Zone).offset(skip).limit(limit).all()
    return zones


@router.get("/{zone_id}", response_model=ZoneSchema)
def get_zone(zone_id: int, db: Session = Depends(get_db)):
    """Get a specific zone by ID"""
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone


@router.post("/", response_model=ZoneSchema)
def create_zone(zone: ZoneCreate, db: Session = Depends(get_db)):
    """Create a new zone"""
    db_zone = Zone(**zone.model_dump())
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    return db_zone


@router.put("/{zone_id}", response_model=ZoneSchema)
def update_zone(zone_id: int, zone: ZoneUpdate, db: Session = Depends(get_db)):
    """Update a zone"""
    db_zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not db_zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    update_data = zone.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_zone, key, value)

    db.commit()
    db.refresh(db_zone)
    return db_zone


@router.delete("/{zone_id}")
def delete_zone(zone_id: int, db: Session = Depends(get_db)):
    """Delete a zone"""
    db_zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not db_zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    db.delete(db_zone)
    db.commit()
    return {"message": "Zone deleted successfully"}
