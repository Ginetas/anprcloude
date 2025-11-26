from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...models import Exporter
from ...schemas import Exporter as ExporterSchema, ExporterCreate, ExporterUpdate

router = APIRouter()


@router.get("/", response_model=List[ExporterSchema])
def list_exporters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all exporters"""
    exporters = db.query(Exporter).offset(skip).limit(limit).all()
    return exporters


@router.get("/{exporter_id}", response_model=ExporterSchema)
def get_exporter(exporter_id: int, db: Session = Depends(get_db)):
    """Get a specific exporter by ID"""
    exporter = db.query(Exporter).filter(Exporter.id == exporter_id).first()
    if not exporter:
        raise HTTPException(status_code=404, detail="Exporter not found")
    return exporter


@router.post("/", response_model=ExporterSchema)
def create_exporter(exporter: ExporterCreate, db: Session = Depends(get_db)):
    """Create a new exporter"""
    db_exporter = Exporter(**exporter.model_dump())
    db.add(db_exporter)
    db.commit()
    db.refresh(db_exporter)
    return db_exporter


@router.put("/{exporter_id}", response_model=ExporterSchema)
def update_exporter(exporter_id: int, exporter: ExporterUpdate, db: Session = Depends(get_db)):
    """Update an exporter"""
    db_exporter = db.query(Exporter).filter(Exporter.id == exporter_id).first()
    if not db_exporter:
        raise HTTPException(status_code=404, detail="Exporter not found")

    update_data = exporter.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_exporter, key, value)

    db.commit()
    db.refresh(db_exporter)
    return db_exporter


@router.delete("/{exporter_id}")
def delete_exporter(exporter_id: int, db: Session = Depends(get_db)):
    """Delete an exporter"""
    db_exporter = db.query(Exporter).filter(Exporter.id == exporter_id).first()
    if not db_exporter:
        raise HTTPException(status_code=404, detail="Exporter not found")

    db.delete(db_exporter)
    db.commit()
    return {"message": "Exporter deleted successfully"}
