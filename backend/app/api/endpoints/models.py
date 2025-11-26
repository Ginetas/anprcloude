from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...models import Model
from ...schemas import Model as ModelSchema, ModelCreate, ModelUpdate

router = APIRouter()


@router.get("/", response_model=List[ModelSchema])
def list_models(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all AI models"""
    models = db.query(Model).offset(skip).limit(limit).all()
    return models


@router.get("/{model_id}", response_model=ModelSchema)
def get_model(model_id: int, db: Session = Depends(get_db)):
    """Get a specific model by ID"""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.post("/", response_model=ModelSchema)
def create_model(model: ModelCreate, db: Session = Depends(get_db)):
    """Create a new model"""
    db_model = Model(**model.model_dump())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


@router.put("/{model_id}", response_model=ModelSchema)
def update_model(model_id: int, model: ModelUpdate, db: Session = Depends(get_db)):
    """Update a model"""
    db_model = db.query(Model).filter(Model.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")

    update_data = model.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_model, key, value)

    db.commit()
    db.refresh(db_model)
    return db_model


@router.delete("/{model_id}")
def delete_model(model_id: int, db: Session = Depends(get_db)):
    """Delete a model"""
    db_model = db.query(Model).filter(Model.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")

    db.delete(db_model)
    db.commit()
    return {"message": "Model deleted successfully"}
