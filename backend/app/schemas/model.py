from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ModelBase(BaseModel):
    name: str
    model_type: str  # "detection" or "ocr"
    file_path: str
    version: Optional[str] = None
    enabled: bool = True
    confidence_threshold: float = 0.5
    description: Optional[str] = None


class ModelCreate(ModelBase):
    pass


class ModelUpdate(BaseModel):
    name: Optional[str] = None
    model_type: Optional[str] = None
    file_path: Optional[str] = None
    version: Optional[str] = None
    enabled: Optional[bool] = None
    confidence_threshold: Optional[float] = None
    description: Optional[str] = None


class Model(ModelBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
