"""
Configuration Management
Loads and validates configuration from YAML files using Pydantic models
"""

from typing import Dict, List, Optional, Literal, Any
from pathlib import Path
from pydantic import BaseModel, Field, validator, field_validator
import yaml
from loguru import logger


class CameraConfig(BaseModel):
    """Configuration for a single camera"""

    id: str = Field(..., description="Unique camera identifier")
    name: str = Field(..., description="Human-readable camera name")
    rtsp_url: str = Field(..., description="RTSP stream URL")
    location: Optional[str] = Field(None, description="Physical location")
    zones: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Detection zones")
    enabled: bool = Field(True, description="Whether camera is enabled")
    fps: int = Field(10, ge=1, le=30, description="Frames per second to process")
    resolution: Optional[str] = Field(None, description="Resolution override (e.g., '1920x1080')")

    @field_validator('rtsp_url')
    @classmethod
    def validate_rtsp_url(cls, v):
        """Validate RTSP URL format"""
        if not v.startswith(('rtsp://', 'rtmp://', 'http://', 'https://', 'file://')):
            raise ValueError(f"Invalid stream URL: {v}")
        return v


class HardwareAccelerationConfig(BaseModel):
    """Hardware acceleration configuration"""

    type: Literal["cpu", "gpu", "coral", "hailo", "npu"] = Field("cpu", description="Hardware accelerator type")
    device_id: Optional[str] = Field(None, description="Device identifier (e.g., /dev/apex_0)")
    use_cuda: bool = Field(False, description="Enable CUDA acceleration")
    cuda_device: int = Field(0, description="CUDA device ID")
    num_threads: int = Field(4, ge=1, description="Number of threads for CPU inference")


class DetectionModelConfig(BaseModel):
    """Object detection model configuration"""

    type: Literal["yolov5", "yolov8", "ssd", "fasterrcnn"] = Field("yolov8", description="Model architecture")
    weights_path: str = Field(..., description="Path to model weights")
    framework: Literal["pytorch", "tensorflow", "onnx", "tflite"] = Field("pytorch", description="Framework")
    confidence_threshold: float = Field(0.5, ge=0.0, le=1.0, description="Detection confidence threshold")
    nms_threshold: float = Field(0.4, ge=0.0, le=1.0, description="Non-maximum suppression threshold")
    input_size: int = Field(640, description="Model input size")
    classes: List[str] = Field(default_factory=lambda: ["vehicle", "license_plate"], description="Detection classes")


class OCRModelConfig(BaseModel):
    """OCR model configuration"""

    engine: Literal["paddleocr", "easyocr", "tesseract"] = Field(..., description="OCR engine")
    language: str = Field("en", description="OCR language")
    weights_path: Optional[str] = Field(None, description="Custom weights path")
    confidence_threshold: float = Field(0.5, ge=0.0, le=1.0, description="OCR confidence threshold")
    enabled: bool = Field(True, description="Whether this OCR engine is enabled")


class OCRConfig(BaseModel):
    """OCR ensemble configuration"""

    models: List[OCRModelConfig] = Field(..., description="List of OCR models to use")
    ensemble_method: Literal["voting", "weighted", "best"] = Field("voting", description="Ensemble method")
    min_agreement: int = Field(2, ge=1, description="Minimum models that must agree")
    plate_format_regex: Optional[str] = Field(
        r"^[A-Z]{3}\d{3}$",
        description="Lithuanian plate format validation regex"
    )


class ExporterConfig(BaseModel):
    """Event exporter configuration"""

    type: Literal["rest", "websocket", "mqtt"] = Field(..., description="Exporter type")
    enabled: bool = Field(True, description="Whether exporter is enabled")
    endpoint: str = Field(..., description="Backend endpoint URL")
    retry_enabled: bool = Field(True, description="Enable retry on failure")
    retry_max_attempts: int = Field(5, ge=1, description="Maximum retry attempts")
    retry_backoff: float = Field(2.0, ge=1.0, description="Retry backoff multiplier")
    timeout: int = Field(30, ge=1, description="Request timeout in seconds")
    batch_size: int = Field(10, ge=1, description="Event batch size")
    queue_path: Optional[str] = Field("/var/lib/anpr/queue", description="Disk queue path")


class PipelineConfig(BaseModel):
    """GStreamer pipeline configuration"""

    buffer_size: int = Field(100, ge=1, description="Pipeline buffer size")
    drop_on_latency: bool = Field(True, description="Drop frames on latency")
    sync: bool = Field(False, description="Sync to clock")
    latency: int = Field(0, ge=0, description="Pipeline latency in ms")
    use_hw_decoder: bool = Field(True, description="Use hardware video decoder if available")


class TrackingConfig(BaseModel):
    """Object tracking configuration"""

    max_disappeared: int = Field(50, ge=1, description="Max frames before object is deregistered")
    max_distance: float = Field(50.0, ge=0.0, description="Max distance for object matching")
    cooldown_seconds: int = Field(300, ge=0, description="Cooldown before re-detecting same plate")


class EdgeWorkerConfig(BaseModel):
    """Main edge worker configuration"""

    worker_id: str = Field(..., description="Unique worker identifier")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field("INFO", description="Logging level")

    cameras: List[CameraConfig] = Field(..., description="Camera configurations")
    hardware: HardwareAccelerationConfig = Field(default_factory=HardwareAccelerationConfig)
    detection_model: DetectionModelConfig = Field(..., description="Detection model config")
    ocr: OCRConfig = Field(..., description="OCR configuration")
    exporters: List[ExporterConfig] = Field(..., description="Event exporters")
    pipeline: PipelineConfig = Field(default_factory=PipelineConfig)
    tracking: TrackingConfig = Field(default_factory=TrackingConfig)

    image_save_path: Optional[str] = Field("/var/lib/anpr/images", description="Path to save images")
    save_images: bool = Field(True, description="Whether to save detection images")

    metrics_enabled: bool = Field(True, description="Enable Prometheus metrics")
    metrics_port: int = Field(9090, ge=1024, le=65535, description="Prometheus metrics port")


def load_config(config_path: str | Path) -> EdgeWorkerConfig:
    """
    Load configuration from YAML file

    Args:
        config_path: Path to configuration YAML file

    Returns:
        Validated EdgeWorkerConfig instance

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    logger.info(f"Loading configuration from {config_path}")

    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)

    try:
        config = EdgeWorkerConfig(**config_data)
        logger.info(f"Configuration loaded successfully for worker {config.worker_id}")
        logger.debug(f"Loaded {len(config.cameras)} camera(s)")
        logger.debug(f"Hardware acceleration: {config.hardware.type}")
        logger.debug(f"Detection model: {config.detection_model.type}")
        logger.debug(f"OCR models: {len(config.ocr.models)}")
        return config
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise ValueError(f"Invalid configuration: {e}")


def load_cameras_config(cameras_path: str | Path) -> List[CameraConfig]:
    """
    Load cameras configuration from separate YAML file

    Args:
        cameras_path: Path to cameras YAML file

    Returns:
        List of validated CameraConfig instances
    """
    cameras_path = Path(cameras_path)

    if not cameras_path.exists():
        raise FileNotFoundError(f"Cameras configuration file not found: {cameras_path}")

    logger.info(f"Loading cameras configuration from {cameras_path}")

    with open(cameras_path, 'r') as f:
        cameras_data = yaml.safe_load(f)

    cameras = []
    for camera_data in cameras_data.get('cameras', []):
        try:
            camera = CameraConfig(**camera_data)
            cameras.append(camera)
            logger.debug(f"Loaded camera: {camera.name} ({camera.id})")
        except Exception as e:
            logger.error(f"Failed to load camera config: {e}")
            raise

    logger.info(f"Loaded {len(cameras)} camera configuration(s)")
    return cameras
