"""
API Schemas
Pydantic schemas for request/response validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator


# Base Schemas
class TimestampSchema(BaseModel):
    """Base schema with timestamps."""

    created_at: datetime
    updated_at: datetime


# Camera Schemas
class CameraBase(BaseModel):
    """Base camera schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Camera name")
    rtsp_url: str = Field(..., min_length=1, max_length=512, description="RTSP stream URL")
    enabled: bool = Field(default=True, description="Camera enabled status")
    zone_id: Optional[int] = Field(default=None, description="Associated zone")
    fps: int = Field(default=10, ge=1, le=60, description="Processing FPS")
    resolution: str = Field(default="1920x1080", description="Camera resolution")
    location: Optional[str] = Field(default=None, max_length=255, description="Physical location")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class CameraCreate(CameraBase):
    """Schema for creating a camera."""

    pass


class CameraUpdate(BaseModel):
    """Schema for updating a camera."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    rtsp_url: Optional[str] = Field(None, min_length=1, max_length=512)
    enabled: Optional[bool] = None
    zone_id: Optional[int] = None
    fps: Optional[int] = Field(None, ge=1, le=60)
    resolution: Optional[str] = None
    location: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CameraRead(CameraBase, TimestampSchema):
    """Schema for reading a camera."""

    id: int

    class Config:
        from_attributes = True


# Zone Schemas
class ZoneBase(BaseModel):
    """Base zone schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Zone name")
    camera_id: int = Field(..., description="Parent camera ID")
    type: str = Field(default="detection", max_length=50, description="Zone type")
    geometry: Dict[str, Any] = Field(..., description="Zone geometry as GeoJSON")
    enabled: bool = Field(default=True, description="Zone enabled status")
    priority: int = Field(default=0, description="Zone priority")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("geometry")
    @classmethod
    def validate_geometry(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate GeoJSON geometry."""
        if "type" not in v:
            raise ValueError("Geometry must have a 'type' field")
        if "coordinates" not in v:
            raise ValueError("Geometry must have a 'coordinates' field")
        return v


class ZoneCreate(ZoneBase):
    """Schema for creating a zone."""

    pass


class ZoneUpdate(BaseModel):
    """Schema for updating a zone."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    camera_id: Optional[int] = None
    type: Optional[str] = None
    geometry: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None
    priority: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class ZoneRead(ZoneBase, TimestampSchema):
    """Schema for reading a zone."""

    id: int

    class Config:
        from_attributes = True


# Model Config Schemas
class ModelConfigBase(BaseModel):
    """Base model config schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Model name")
    type: str = Field(..., max_length=50, description="Model type")
    weights_path: str = Field(..., max_length=512, description="Path to model weights")
    version: str = Field(..., max_length=50, description="Model version")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model parameters")
    enabled: bool = Field(default=True, description="Model enabled status")
    is_default: bool = Field(default=False, description="Default model for this type")
    description: Optional[str] = Field(None, max_length=512, description="Model description")


class ModelConfigCreate(ModelConfigBase):
    """Schema for creating a model config."""

    pass


class ModelConfigUpdate(BaseModel):
    """Schema for updating a model config."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = None
    weights_path: Optional[str] = None
    version: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None
    is_default: Optional[bool] = None
    description: Optional[str] = None


class ModelConfigRead(ModelConfigBase, TimestampSchema):
    """Schema for reading a model config."""

    id: int

    class Config:
        from_attributes = True


# Sensor Settings Schemas
class SensorSettingsBase(BaseModel):
    """Base sensor settings schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Settings name")
    type: str = Field(..., max_length=50, description="Sensor type")
    camera_id: int = Field(..., description="Associated camera")
    zone_id: Optional[int] = Field(None, description="Associated zone")
    config: Dict[str, Any] = Field(default_factory=dict, description="Sensor configuration")
    enabled: bool = Field(default=True, description="Settings enabled status")
    description: Optional[str] = Field(None, max_length=512, description="Settings description")


class SensorSettingsCreate(SensorSettingsBase):
    """Schema for creating sensor settings."""

    pass


class SensorSettingsUpdate(BaseModel):
    """Schema for updating sensor settings."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = None
    camera_id: Optional[int] = None
    zone_id: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None
    description: Optional[str] = None


class SensorSettingsRead(SensorSettingsBase, TimestampSchema):
    """Schema for reading sensor settings."""

    id: int

    class Config:
        from_attributes = True


# Exporter Config Schemas
class ExporterConfigBase(BaseModel):
    """Base exporter config schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Exporter name")
    type: str = Field(..., max_length=50, description="Exporter type")
    url: str = Field(..., max_length=512, description="Target URL")
    headers: Dict[str, str] = Field(default_factory=dict, description="HTTP headers")
    auth: Dict[str, Any] = Field(default_factory=dict, description="Authentication config")
    retry_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "max_attempts": 3,
            "retry_delay": 5,
            "backoff_factor": 2,
            "timeout": 30
        },
        description="Retry configuration"
    )
    enabled: bool = Field(default=True, description="Exporter enabled status")
    description: Optional[str] = Field(None, max_length=512, description="Exporter description")
    filter_config: Dict[str, Any] = Field(default_factory=dict, description="Event filtering")


class ExporterConfigCreate(ExporterConfigBase):
    """Schema for creating an exporter config."""

    pass


class ExporterConfigUpdate(BaseModel):
    """Schema for updating an exporter config."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = None
    url: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    auth: Optional[Dict[str, Any]] = None
    retry_config: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None
    description: Optional[str] = None
    filter_config: Optional[Dict[str, Any]] = None


class ExporterConfigRead(ExporterConfigBase, TimestampSchema):
    """Schema for reading an exporter config."""

    id: int

    class Config:
        from_attributes = True


# Plate Event Schemas
class PlateEventBase(BaseModel):
    """Base plate event schema."""

    camera_id: int = Field(..., description="Source camera ID")
    zone_id: Optional[int] = Field(None, description="Detection zone ID")
    plate_text: str = Field(..., min_length=1, max_length=20, description="Recognized plate text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Recognition confidence")
    raw_candidates: List[Dict[str, Any]] = Field(default_factory=list, description="OCR candidates")
    frame_url: Optional[str] = Field(None, max_length=512, description="Full frame image URL")
    crop_url: Optional[str] = Field(None, max_length=512, description="Plate crop image URL")
    vehicle_info: Dict[str, Any] = Field(default_factory=dict, description="Vehicle information")
    tpms_status: Dict[str, Any] = Field(default_factory=dict, description="TPMS data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PlateEventCreate(PlateEventBase):
    """Schema for creating a plate event."""

    timestamp: Optional[datetime] = Field(None, description="Event timestamp (defaults to now)")


class PlateEventRead(PlateEventBase, TimestampSchema):
    """Schema for reading a plate event."""

    id: int
    event_id: UUID
    timestamp: datetime
    exported: bool
    export_attempts: int
    last_export_at: Optional[datetime]

    class Config:
        from_attributes = True


class PlateEventFilter(BaseModel):
    """Schema for filtering plate events."""

    camera_id: Optional[int] = None
    zone_id: Optional[int] = None
    plate_text: Optional[str] = None
    min_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    exported: Optional[bool] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


# Event Statistics Schemas
class EventStatsResponse(BaseModel):
    """Schema for event statistics response."""

    total_events: int
    unique_plates: int
    avg_confidence: float
    events_by_camera: Dict[str, int]
    events_by_zone: Dict[str, int]
    events_by_hour: Dict[str, int]
    recent_events: List[PlateEventRead]


class EventIngestResponse(BaseModel):
    """Schema for event ingest response."""

    success: bool
    event_id: UUID
    message: str


# Health Check Schema
class HealthCheckResponse(BaseModel):
    """Schema for health check response."""

    status: str
    version: str
    database: str
    redis: str
    timestamp: datetime


# Exporter Test Schema
class ExporterTestRequest(BaseModel):
    """Schema for testing an exporter."""

    sample_event: Optional[Dict[str, Any]] = None


class ExporterTestResponse(BaseModel):
    """Schema for exporter test response."""

    success: bool
    status_code: Optional[int] = None
    response_time: float
    message: str
    error: Optional[str] = None


# Pagination Schema
class PaginatedResponse(BaseModel):
    """Generic paginated response schema."""

    items: List[Any]
    total: int
    limit: int
    offset: int
    has_more: bool
