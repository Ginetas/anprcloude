from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...models import Camera
from ...schemas import Camera as CameraSchema, CameraCreate, CameraUpdate

router = APIRouter()


@router.get("/", response_model=List[CameraSchema])
def list_cameras(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all cameras"""
    cameras = db.query(Camera).offset(skip).limit(limit).all()
    return cameras


@router.get("/{camera_id}", response_model=CameraSchema)
def get_camera(camera_id: int, db: Session = Depends(get_db)):
    """Get a specific camera by ID"""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.post("/", response_model=CameraSchema)
def create_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    """Create a new camera"""
    db_camera = Camera(**camera.model_dump())
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera


@router.put("/{camera_id}", response_model=CameraSchema)
def update_camera(camera_id: int, camera: CameraUpdate, db: Session = Depends(get_db)):
    """Update a camera"""
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not db_camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    update_data = camera.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_camera, key, value)

    db.commit()
    db.refresh(db_camera)
    return db_camera


@router.delete("/{camera_id}")
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    """Delete a camera"""
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not db_camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    db.delete(db_camera)
    db.commit()
    return {"message": "Camera deleted successfully"}
