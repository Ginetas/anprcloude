from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class CameraBase(BaseModel):
    name: str
    rtsp_url: str
    location: Optional[str] = None
    zone_id: Optional[int] = None
    enabled: bool = True
    fps: int = 15
    resolution_width: int = 1920
    resolution_height: int = 1080


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    rtsp_url: Optional[str] = None
    location: Optional[str] = None
    zone_id: Optional[int] = None
    enabled: Optional[bool] = None
    fps: Optional[int] = None
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None


class Camera(CameraBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
