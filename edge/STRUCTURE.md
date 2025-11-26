# Edge Worker Project Structure

Complete directory structure and file descriptions for the ANPR Edge Worker.

## Directory Tree

```
edge/
├── config/                         # Configuration files
│   ├── cameras.example.yaml        # Example camera configuration
│   ├── config.example.yaml         # Example main configuration
│   └── models.example.yaml         # Example model configurations
│
├── detection/                      # Detection module
│   ├── __init__.py                 # Module initialization
│   ├── detector.py                 # Vehicle and plate detection
│   └── tracker.py                  # Object tracking with centroid matching
│
├── exporters/                      # Event export module
│   ├── __init__.py                 # Module initialization
│   └── dispatcher.py               # Event dispatchers (REST/WebSocket/MQTT)
│
├── ocr/                            # OCR module
│   ├── __init__.py                 # Module initialization
│   ├── models.py                   # OCR engine wrappers
│   └── ensemble.py                 # OCR ensemble and consensus
│
├── tests/                          # Unit tests
│   ├── __init__.py                 # Tests initialization
│   └── test_detection.py           # Detection tests
│
├── models/                         # Model weights directory
│   └── .gitkeep                    # Keep empty directory in git
│
├── __init__.py                     # Package initialization
├── config.py                       # Configuration management
├── pipeline.py                     # GStreamer video pipeline
├── main.py                         # Main entry point
│
├── requirements.txt                # Python dependencies
├── setup.py                        # Package setup
├── pyproject.toml                  # Tool configurations
├── pytest.ini                      # Pytest configuration
│
├── Dockerfile                      # Docker image definition
├── docker-compose.yaml             # Docker Compose configuration
├── .dockerignore                   # Docker ignore patterns
├── .gitignore                      # Git ignore patterns
│
├── Makefile                        # Common development tasks
├── README.md                       # Full documentation
├── QUICKSTART.md                   # Quick start guide
└── STRUCTURE.md                    # This file
```

## File Descriptions

### Core Application Files

**`__init__.py`**
- Package initialization
- Logging configuration
- Version information

**`config.py`**
- Pydantic models for configuration validation
- YAML configuration loading
- Configuration schemas for all components

**`pipeline.py`**
- GStreamer pipeline implementation
- RTSP stream handling
- Hardware-accelerated video decoding
- Frame extraction and callback management
- Multi-camera pipeline manager

**`main.py`**
- Main application entry point
- EdgeWorker coordinator class
- Frame processing orchestration
- Signal handling and lifecycle management

### Detection Module

**`detection/__init__.py`**
- Module exports

**`detection/detector.py`**
- BaseDetector abstract class
- YOLOv8Detector implementation
- YOLOv5Detector implementation
- ONNXDetector implementation
- Unified Detector interface
- Bounding box extraction

**`detection/tracker.py`**
- CentroidTracker for object tracking
- TrackedObject data class
- Zone crossing detection
- Cooldown management
- Object lifecycle handling

### OCR Module

**`ocr/__init__.py`**
- Module exports

**`ocr/models.py`**
- BaseOCR abstract class
- PaddleOCR wrapper
- EasyOCR wrapper
- TesseractOCR wrapper
- OCR engine factory function
- Image preprocessing utilities

**`ocr/ensemble.py`**
- OCREnsemble class
- Character-level voting consensus
- Confidence-weighted consensus
- Best result selection
- Plate format validation
- Post-processing and error correction

### Exporters Module

**`exporters/__init__.py`**
- Module exports

**`exporters/dispatcher.py`**
- DetectionEvent data class
- BaseExporter abstract class
- RESTExporter with retry logic
- WebSocketExporter for real-time streaming
- MQTTExporter for IoT deployments
- EventDispatcher with disk-backed retry queue
- Async event processing

### Configuration Files

**`config/config.example.yaml`**
- Main configuration template
- Worker settings
- Hardware acceleration config
- Detection model config
- OCR ensemble config
- Exporter settings
- Pipeline parameters
- Tracking settings

**`config/cameras.example.yaml`**
- Camera configuration examples
- Multiple camera setups
- Zone definitions
- RTSP URL formats

**`config/models.example.yaml`**
- Model configuration examples for different hardware
- GPU, CPU, Coral TPU, Hailo NPU setups
- OCR configuration variants
- Performance tuning examples

### Testing Files

**`tests/__init__.py`**
- Test package initialization

**`tests/test_detection.py`**
- Unit tests for detection module
- Tracker tests
- Integration test helpers
- Test fixtures

**`pytest.ini`**
- Pytest configuration
- Test discovery patterns
- Coverage settings
- Test markers

### Build and Deployment Files

**`requirements.txt`**
- Python package dependencies
- Core libraries (OpenCV, NumPy, etc.)
- Deep learning frameworks (PyTorch, TensorFlow)
- OCR libraries (PaddleOCR, EasyOCR, Tesseract)
- Web clients (requests, websocket-client)
- Configuration (Pydantic)
- Utilities (loguru, diskcache, etc.)

**`setup.py`**
- Python package setup
- Package metadata
- Dependencies
- Entry points
- Package data

**`pyproject.toml`**
- Modern Python project configuration
- Black formatter settings
- isort settings
- mypy type checker settings
- flake8 linter settings
- Coverage settings

**`Dockerfile`**
- Multi-stage Docker build
- System dependencies installation
- Python environment setup
- Non-root user configuration
- Health check
- Labels and metadata

**`docker-compose.yaml`**
- Docker Compose service definitions
- Volume mappings
- Environment variables
- Resource limits
- Optional Prometheus and Grafana services
- Logging configuration

**`.dockerignore`**
- Files to exclude from Docker build
- Python cache files
- Virtual environments
- Test files
- Documentation

**`.gitignore`**
- Files to exclude from git
- Python cache files
- Virtual environments
- Local configuration files
- Model weights
- Data directories

**`Makefile`**
- Common development tasks
- Installation commands
- Test commands
- Docker commands
- Code quality commands
- Running commands

### Documentation Files

**`README.md`**
- Comprehensive documentation
- Architecture overview
- Installation instructions
- Configuration guide
- Usage examples
- Performance tuning
- Troubleshooting

**`QUICKSTART.md`**
- Quick setup guide
- Minimal configuration
- Common issues
- Quick command reference

**`STRUCTURE.md`**
- This file
- Project structure documentation
- File descriptions

## Module Dependencies

```
main.py
├── config.py
├── pipeline.py
│   └── config.py
├── detection/
│   ├── detector.py
│   │   └── config.py
│   └── tracker.py
│       └── config.py
├── ocr/
│   ├── models.py
│   │   └── config.py
│   └── ensemble.py
│       └── models.py
└── exporters/
    └── dispatcher.py
        └── config.py
```

## Configuration Flow

```
config.yaml
    ↓
config.py (load_config)
    ↓
EdgeWorkerConfig (Pydantic validation)
    ↓
┌───────────────┬─────────────────┬──────────────┬────────────────┐
│               │                 │              │                │
PipelineConfig  DetectionConfig   OCRConfig     ExporterConfig
│               │                 │              │                │
PipelineManager Detector          OCREnsemble    EventDispatcher
```

## Data Flow

```
RTSP Stream
    ↓
GStreamerPipeline (pipeline.py)
    ↓
Frame Callback
    ↓
Detector (detection/detector.py)
    ↓
CentroidTracker (detection/tracker.py)
    ↓
OCREnsemble (ocr/ensemble.py)
    ↓
DetectionEvent
    ↓
EventDispatcher (exporters/dispatcher.py)
    ↓
Backend API / WebSocket / MQTT
```

## Key Design Patterns

1. **Abstract Base Classes**: BaseDetector, BaseOCR, BaseExporter
2. **Factory Pattern**: create_ocr_engine()
3. **Strategy Pattern**: Different OCR engines, detection models, exporters
4. **Observer Pattern**: Frame callbacks, event dispatching
5. **Singleton Pattern**: PipelineManager, EventDispatcher
6. **Data Classes**: DetectionResult, TrackedObject, DetectionEvent
7. **Configuration as Code**: Pydantic models for type-safe configuration

## Extension Points

1. **New Detection Models**: Extend BaseDetector
2. **New OCR Engines**: Extend BaseOCR
3. **New Exporters**: Extend BaseExporter
4. **Custom Tracking**: Extend CentroidTracker
5. **Custom Preprocessing**: Override preprocess methods
6. **Custom Consensus**: Modify OCREnsemble methods

## Performance Considerations

1. **Pipeline**: Async frame processing with queues
2. **Detection**: Batch processing support
3. **OCR**: Parallel execution of multiple engines
4. **Export**: Async dispatch with retry queue
5. **Tracking**: Efficient centroid matching
6. **Memory**: Frame dropping on buffer overflow

## Security Considerations

1. **Configuration**: Sensitive data (passwords) should use environment variables
2. **Docker**: Non-root user execution
3. **Network**: HTTPS/WSS for production exporters
4. **File System**: Restricted permissions on queue and image directories
5. **Logging**: Sensitive data filtering in logs

## Monitoring and Observability

1. **Logging**: Structured logging with loguru
2. **Metrics**: Prometheus metrics endpoint
3. **Health Checks**: Docker health check endpoint
4. **Statistics**: Per-component statistics methods
5. **Error Tracking**: Comprehensive exception handling and logging

## Testing Strategy

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **Mock Tests**: Mock external dependencies (models, cameras)
4. **Fixtures**: Reusable test data and configurations
5. **Coverage**: Aim for >80% code coverage

## Development Workflow

1. **Local Development**: Use Makefile commands
2. **Code Quality**: Black formatter, flake8 linter, mypy type checker
3. **Testing**: pytest with coverage
4. **Docker Testing**: docker-compose for integration testing
5. **CI/CD**: Automated testing and building

## Deployment Options

1. **Bare Metal**: systemd service
2. **Docker**: Single container
3. **Docker Compose**: Multi-container with monitoring
4. **Kubernetes**: Scalable edge deployment
5. **Docker Swarm**: Distributed edge deployment

---

For more information, see [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md).
