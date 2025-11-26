"""
Database Models
SQLModel models for all database entities.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlmodel import Column, Field, JSON, Relationship, SQLModel


# Base Models with common fields
class TimestampMixin(SQLModel):
    """Mixin for timestamp fields."""

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Record creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Record last update timestamp",
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )


# Camera Model
class Camera(TimestampMixin, table=True):
    """
    Camera configuration and metadata.

    Attributes:
        id: Unique camera identifier
        name: Human-readable camera name
        rtsp_url: RTSP stream URL
        enabled: Whether camera is active
        zone_id: Associated zone identifier
        fps: Frames per second for processing
        resolution: Camera resolution (e.g., "1920x1080")
        location: Physical location description
        metadata: Additional camera metadata
    """

    __tablename__ = "cameras"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255, description="Camera name")
    rtsp_url: str = Field(max_length=512, description="RTSP stream URL")
    enabled: bool = Field(default=True, description="Camera enabled status")
    zone_id: Optional[int] = Field(default=None, foreign_key="zones.id", description="Associated zone")
    fps: int = Field(default=10, ge=1, le=60, description="Processing FPS")
    resolution: str = Field(default="1920x1080", max_length=50, description="Camera resolution")
    location: Optional[str] = Field(default=None, max_length=255, description="Physical location")
    metadata: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="Additional metadata")

    # Relationships
    zones: List["Zone"] = Relationship(back_populates="camera")
    sensor_settings: List["SensorSettings"] = Relationship(back_populates="camera")
    plate_events: List["PlateEvent"] = Relationship(back_populates="camera")


# Zone Model
class Zone(TimestampMixin, table=True):
    """
    Detection zone configuration.

    Attributes:
        id: Unique zone identifier
        name: Human-readable zone name
        camera_id: Parent camera identifier
        type: Zone type (detection, exclusion, etc.)
        geometry: Zone geometry as GeoJSON
        enabled: Whether zone is active
        priority: Zone priority for overlapping zones
        metadata: Additional zone metadata
    """

    __tablename__ = "zones"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255, description="Zone name")
    camera_id: int = Field(foreign_key="cameras.id", description="Parent camera")
    type: str = Field(
        default="detection",
        max_length=50,
        description="Zone type (detection, exclusion, parking, etc.)"
    )
    geometry: Dict[str, Any] = Field(
        sa_column=Column(JSON),
        description="Zone geometry as GeoJSON (polygon coordinates)"
    )
    enabled: bool = Field(default=True, description="Zone enabled status")
    priority: int = Field(default=0, description="Zone priority (higher = more important)")
    metadata: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="Additional metadata")

    # Relationships
    camera: Optional[Camera] = Relationship(back_populates="zones")
    sensor_settings: List["SensorSettings"] = Relationship(back_populates="zone")
    plate_events: List["PlateEvent"] = Relationship(back_populates="zone")


# Model Configuration
class ModelConfig(TimestampMixin, table=True):
    """
    AI Model configuration and versioning.

    Attributes:
        id: Unique model config identifier
        name: Human-readable model name
        type: Model type (yolo, paddleocr, etc.)
        weights_path: Path to model weights file
        version: Model version string
        parameters: Model-specific parameters as JSON
        enabled: Whether model is active
        is_default: Whether this is the default model for its type
    """

    __tablename__ = "model_configs"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255, description="Model name")
    type: str = Field(
        index=True,
        max_length=50,
        description="Model type (plate_detector, ocr, vehicle_classifier, etc.)"
    )
    weights_path: str = Field(max_length=512, description="Path to model weights")
    version: str = Field(max_length=50, description="Model version")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Model parameters (confidence, NMS threshold, etc.)"
    )
    enabled: bool = Field(default=True, description="Model enabled status")
    is_default: bool = Field(default=False, description="Default model for this type")
    description: Optional[str] = Field(default=None, max_length=512, description="Model description")


# Sensor Settings
class SensorSettings(TimestampMixin, table=True):
    """
    Edge sensor configuration settings.

    Attributes:
        id: Unique settings identifier
        name: Human-readable settings name
        type: Sensor type (anpr, vehicle_count, parking, etc.)
        camera_id: Associated camera
        zone_id: Associated zone
        config: Sensor-specific configuration as JSON
        enabled: Whether settings are active
    """

    __tablename__ = "sensor_settings"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255, description="Settings name")
    type: str = Field(
        index=True,
        max_length=50,
        description="Sensor type (anpr, vehicle_count, parking_occupancy, etc.)"
    )
    camera_id: int = Field(foreign_key="cameras.id", description="Associated camera")
    zone_id: Optional[int] = Field(default=None, foreign_key="zones.id", description="Associated zone")
    config: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Sensor configuration (thresholds, processing options, etc.)"
    )
    enabled: bool = Field(default=True, description="Settings enabled status")
    description: Optional[str] = Field(default=None, max_length=512, description="Settings description")

    # Relationships
    camera: Optional[Camera] = Relationship(back_populates="sensor_settings")
    zone: Optional[Zone] = Relationship(back_populates="sensor_settings")


# Exporter Configuration
class ExporterConfig(TimestampMixin, table=True):
    """
    Data exporter configuration.

    Attributes:
        id: Unique exporter identifier
        name: Human-readable exporter name
        type: Exporter type (webhook, mqtt, kafka, database, etc.)
        url: Target URL or connection string
        headers: HTTP headers for webhook exporters
        auth: Authentication configuration
        retry_config: Retry policy configuration
        enabled: Whether exporter is active
    """

    __tablename__ = "exporter_configs"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255, description="Exporter name")
    type: str = Field(
        index=True,
        max_length=50,
        description="Exporter type (webhook, mqtt, kafka, database, syslog, etc.)"
    )
    url: str = Field(max_length=512, description="Target URL or connection string")
    headers: Dict[str, str] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="HTTP headers (for webhook exporters)"
    )
    auth: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Authentication config (API keys, tokens, credentials)"
    )
    retry_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "max_attempts": 3,
            "retry_delay": 5,
            "backoff_factor": 2,
            "timeout": 30
        },
        sa_column=Column(JSON),
        description="Retry policy configuration"
    )
    enabled: bool = Field(default=True, description="Exporter enabled status")
    description: Optional[str] = Field(default=None, max_length=512, description="Exporter description")
    filter_config: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Event filtering configuration"
    )


# Plate Event
class PlateEvent(TimestampMixin, table=True):
    """
    License plate detection event.

    Attributes:
        id: Database primary key
        event_id: Unique event identifier (UUID)
        timestamp: Event detection timestamp
        camera_id: Source camera identifier
        zone_id: Detection zone identifier
        plate_text: Recognized plate text
        confidence: Recognition confidence score
        raw_candidates: All OCR candidates with scores
        frame_url: URL to full frame image
        crop_url: URL to plate crop image
        vehicle_info: Detected vehicle information
        tpms_status: Tire pressure monitoring status
        metadata: Additional event metadata
        exported: Whether event has been exported
        export_attempts: Number of export attempts
        last_export_at: Last export attempt timestamp
    """

    __tablename__ = "plate_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: UUID = Field(
        default_factory=uuid4,
        unique=True,
        index=True,
        description="Unique event identifier"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Event detection timestamp"
    )
    camera_id: int = Field(
        foreign_key="cameras.id",
        index=True,
        description="Source camera"
    )
    zone_id: Optional[int] = Field(
        default=None,
        foreign_key="zones.id",
        index=True,
        description="Detection zone"
    )

    # Plate Recognition Data
    plate_text: str = Field(
        index=True,
        max_length=20,
        description="Recognized license plate text"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Recognition confidence score"
    )
    raw_candidates: List[Dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="All OCR candidates with confidence scores"
    )

    # Image URLs
    frame_url: Optional[str] = Field(
        default=None,
        max_length=512,
        description="URL to full frame image"
    )
    crop_url: Optional[str] = Field(
        default=None,
        max_length=512,
        description="URL to plate crop image"
    )

    # Vehicle Information
    vehicle_info: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Vehicle classification (type, color, make, model, etc.)"
    )

    # TPMS Data (Tire Pressure Monitoring)
    tpms_status: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="TPMS sensor data if available"
    )

    # Additional Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Additional event metadata (speed, direction, etc.)"
    )

    # Export Tracking
    exported: bool = Field(
        default=False,
        index=True,
        description="Export status"
    )
    export_attempts: int = Field(
        default=0,
        description="Number of export attempts"
    )
    last_export_at: Optional[datetime] = Field(
        default=None,
        description="Last export attempt timestamp"
    )

    # Relationships
    camera: Optional[Camera] = Relationship(back_populates="plate_events")
    zone: Optional[Zone] = Relationship(back_populates="plate_events")


# Event Statistics (for analytics)
class EventStatistics(SQLModel, table=True):
    """
    Aggregated event statistics for analytics.

    Attributes:
        id: Primary key
        date: Statistics date
        camera_id: Camera identifier
        zone_id: Zone identifier
        total_events: Total events count
        unique_plates: Unique plates count
        avg_confidence: Average confidence score
        hourly_distribution: Events by hour
    """

    __tablename__ = "event_statistics"

    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime = Field(index=True, description="Statistics date")
    camera_id: Optional[int] = Field(
        default=None,
        foreign_key="cameras.id",
        index=True,
        description="Camera (null for all cameras)"
    )
    zone_id: Optional[int] = Field(
        default=None,
        foreign_key="zones.id",
        index=True,
        description="Zone (null for all zones)"
    )
    total_events: int = Field(default=0, description="Total events count")
    unique_plates: int = Field(default=0, description="Unique plates count")
    avg_confidence: float = Field(default=0.0, description="Average confidence score")
    hourly_distribution: Dict[str, int] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Events count by hour"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Settings Model
class Settings(TimestampMixin, table=True):
    """
    System settings and configuration.

    Stores all configurable settings for the ANPR system including:
    - System settings (worker_id, log_level, etc.)
    - Hardware settings (GPU, NPU, CPU configuration)
    - Camera, zone, model, OCR, pipeline settings
    - Storage, monitoring, security, notification settings

    Attributes:
        id: Primary key
        key: Setting key/name (unique)
        value: Setting value (stored as JSON)
        category: Setting category (system, hardware, camera, etc.)
        description: Human-readable description
        default_value: Default value for this setting
        value_type: Expected value type (string, int, float, bool, json)
        validation_rules: Validation rules as JSON
        is_sensitive: Whether this setting contains sensitive data
        requires_restart: Whether changing this setting requires restart
        metadata: Additional metadata
    """

    __tablename__ = "settings"

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(
        unique=True,
        index=True,
        max_length=255,
        description="Setting key/name (e.g., 'system.worker_id', 'hardware.type')"
    )
    value: Any = Field(
        sa_column=Column(JSON),
        description="Setting value (can be any JSON-serializable type)"
    )
    category: str = Field(
        index=True,
        max_length=100,
        description="Setting category (system, hardware, camera, detection, ocr, etc.)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=512,
        description="Human-readable description of this setting"
    )
    default_value: Any = Field(
        default=None,
        sa_column=Column(JSON),
        description="Default value for this setting"
    )
    value_type: str = Field(
        default="string",
        max_length=50,
        description="Expected value type (string, int, float, bool, array, object)"
    )
    validation_rules: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Validation rules (min, max, pattern, enum, etc.)"
    )
    is_sensitive: bool = Field(
        default=False,
        description="Whether this setting contains sensitive data (passwords, keys)"
    )
    requires_restart: bool = Field(
        default=False,
        description="Whether changing this setting requires system restart"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Additional metadata (help text, examples, related settings, etc.)"
    )


# Settings History Model
class SettingsHistory(TimestampMixin, table=True):
    """
    Audit log for settings changes.

    Tracks all changes to settings for rollback and audit purposes.

    Attributes:
        id: Primary key
        setting_key: The setting that was changed
        old_value: Previous value
        new_value: New value
        changed_by: User/system that made the change
        reason: Optional reason for the change
        metadata: Additional metadata
    """

    __tablename__ = "settings_history"

    id: Optional[int] = Field(default=None, primary_key=True)
    setting_key: str = Field(
        index=True,
        max_length=255,
        description="Setting key that was changed"
    )
    old_value: Any = Field(
        default=None,
        sa_column=Column(JSON),
        description="Previous value"
    )
    new_value: Any = Field(
        sa_column=Column(JSON),
        description="New value"
    )
    changed_by: Optional[str] = Field(
        default="system",
        max_length=255,
        description="User or system that made the change"
    )
    reason: Optional[str] = Field(
        default=None,
        max_length=512,
        description="Reason for the change"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Additional metadata"
    )
