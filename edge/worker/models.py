"""
Data models for edge worker.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class BoundingBox(BaseModel):
    """Bounding box for detected plate"""
    x: int
    y: int
    width: int
    height: int


class PlateEvent(BaseModel):
    """
    Plate detection event sent from edge to backend.

    This matches the backend's PlateEventCreate schema.
    """
    camera_id: int
    plate_text: str
    confidence: float
    detection_confidence: Optional[float] = None
    ocr_confidence: Optional[float] = None
    bbox: Optional[BoundingBox] = None
    timestamp: datetime
    image_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CameraConfig(BaseModel):
    """Camera configuration from backend"""
    id: int
    name: str
    rtsp_url: str
    location: Optional[str] = None
    zone_id: Optional[int] = None
    enabled: bool = True
    fps: int = 15
    resolution_width: int = 1920
    resolution_height: int = 1080


class WorkerConfig(BaseModel):
    """Edge worker configuration"""
    backend_url: str = Field(default="http://localhost:8000")
    detection_model_path: str = Field(default="/opt/hailo/models/yolov8n-plate.hef")
    ocr_model_path: str = Field(default="/opt/hailo/models/plate-ocr.hef")
    target_width: int = Field(default=640)
    target_height: int = Field(default=480)
    detection_threshold: float = Field(default=0.5)
    save_plate_images: bool = Field(default=False)
    plate_images_dir: str = Field(default="/tmp/plates")
    max_cameras: int = Field(default=4)
    reconnect_interval: int = Field(default=30)
    log_level: str = Field(default="INFO")
