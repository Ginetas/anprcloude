from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any


class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int


class PlateEventBase(BaseModel):
    camera_id: int
    plate_text: str
    confidence: float
    detection_confidence: Optional[float] = None
    ocr_confidence: Optional[float] = None
    bbox: Optional[BoundingBox] = None
    timestamp: datetime
    image_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PlateEventCreate(PlateEventBase):
    pass


class PlateEvent(PlateEventBase):
    id: int
    processed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlateEventWithCamera(PlateEvent):
    camera_name: str
    camera_location: Optional[str] = None
