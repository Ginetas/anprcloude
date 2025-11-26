# ANPR Edge Worker

Edge computing component for the ANPR (Automatic Number Plate Recognition) system. Processes video streams in real-time to detect vehicles, recognize license plates, and export events to the central backend.

## Features

- **Multi-Camera Support**: Process multiple RTSP streams simultaneously
- **Hardware Acceleration**: Support for GPU (CUDA), Edge TPU (Coral), Hailo NPU, and CPU
- **Multiple Detection Models**: YOLOv5, YOLOv8, SSD, Faster R-CNN with PyTorch, TensorFlow, ONNX, and TFLite
- **OCR Ensemble**: Combine PaddleOCR, EasyOCR, and Tesseract with voting/consensus
- **Object Tracking**: Centroid-based tracking with zone crossing detection
- **Event Export**: REST API, WebSocket, and MQTT exporters with retry queue
- **Robust Pipeline**: GStreamer-based video processing with hardware decoding
- **Configurable**: YAML-based configuration with Pydantic validation

## Architecture

```
┌─────────────┐
│ RTSP Camera │
└──────┬──────┘
       │
       v
┌─────────────────┐
│ GStreamer       │  - Hardware-accelerated decoding
│ Pipeline        │  - Frame extraction
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Detection       │  - YOLOv8/v5, SSD, etc.
│ (Vehicle/Plate) │  - GPU/TPU/CPU
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Object Tracking │  - Centroid matching
│                 │  - Zone crossing
└────────┬────────┘
         │
         v
┌─────────────────┐
│ OCR Ensemble    │  - PaddleOCR
│                 │  - EasyOCR
│                 │  - Tesseract
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Event Dispatcher│  - REST API
│                 │  - WebSocket
│                 │  - MQTT
└─────────────────┘
```

## Installation

### System Dependencies

#### Ubuntu/Debian
```bash
# GStreamer
sudo apt-get install -y \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-rtsp \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev

# Python GObject
sudo apt-get install -y \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gstreamer-1.0

# Tesseract OCR
sudo apt-get install -y tesseract-ocr libtesseract-dev

# OpenCV dependencies
sudo apt-get install -y libopencv-dev python3-opencv
```

#### Hardware-Specific

**NVIDIA GPU:**
```bash
# Install CUDA and cuDNN
# Follow: https://developer.nvidia.com/cuda-downloads

# Install GStreamer NVDEC plugin
sudo apt-get install -y gstreamer1.0-plugins-nvidia
```

**Google Coral Edge TPU:**
```bash
# Install Edge TPU runtime
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get install -y libedgetpu1-std python3-pycoral
```

**Intel/AMD (VA-API):**
```bash
sudo apt-get install -y gstreamer1.0-vaapi
```

### Python Package Installation

```bash
# Clone repository
git clone https://github.com/your-org/anpr-edge-worker.git
cd anpr-edge-worker/edge

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Configuration

### 1. Main Configuration

Copy and edit the main configuration file:

```bash
cp config/config.example.yaml config/config.yaml
nano config/config.yaml
```

Key configuration sections:

- **worker_id**: Unique identifier for this edge worker
- **hardware**: Hardware acceleration settings
- **detection_model**: Model type, weights, and parameters
- **ocr**: OCR engines and ensemble configuration
- **exporters**: Backend export settings
- **pipeline**: GStreamer pipeline settings
- **tracking**: Object tracking parameters

### 2. Camera Configuration

Define cameras in the main config or separate file:

```bash
cp config/cameras.example.yaml config/cameras.yaml
nano config/cameras.yaml
```

Example camera configuration:

```yaml
cameras:
  - id: "cam_entrance_01"
    name: "Main Entrance Camera"
    rtsp_url: "rtsp://admin:password@192.168.1.100:554/stream1"
    location: "Main Gate"
    enabled: true
    fps: 10
    resolution: "1920x1080"
    zones:
      - name: "entry_zone"
        polygon: [[100, 100], [500, 100], [500, 400], [100, 400]]
```

### 3. Model Configuration

Download or train models and update paths in config:

```yaml
detection_model:
  type: "yolov8"
  weights_path: "/path/to/models/yolov8n.pt"
  framework: "pytorch"
  confidence_threshold: 0.5
```

## Usage

### Basic Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Run edge worker
python -m edge.main --config config/config.yaml
```

### Command Line Options

```bash
python -m edge.main --help

Options:
  --config PATH          Configuration file path (default: config.yaml)
  --log-level LEVEL     Logging level: DEBUG, INFO, WARNING, ERROR
  --cameras PATH        Separate cameras configuration file
  --dry-run            Test configuration without starting
```

### Running as Service

Create systemd service file `/etc/systemd/system/anpr-edge.service`:

```ini
[Unit]
Description=ANPR Edge Worker
After=network.target

[Service]
Type=simple
User=anpr
WorkingDirectory=/opt/anpr-edge
ExecStart=/opt/anpr-edge/venv/bin/python -m edge.main --config /etc/anpr/config.yaml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable anpr-edge
sudo systemctl start anpr-edge
sudo systemctl status anpr-edge
```

### Docker Deployment

```bash
# Build image
docker build -t anpr-edge:latest .

# Run container
docker run -d \
  --name anpr-edge \
  --restart unless-stopped \
  --network host \
  -v /path/to/config:/config \
  -v /path/to/models:/models \
  -v /path/to/images:/var/lib/anpr/images \
  -v /path/to/queue:/var/lib/anpr/queue \
  anpr-edge:latest
```

## Model Training

### Vehicle and License Plate Detection

Train custom YOLOv8 model:

```bash
# Prepare dataset (YOLO format)
# - images/
# - labels/
# - data.yaml

# Train
yolo detect train \
  data=data.yaml \
  model=yolov8n.pt \
  epochs=100 \
  imgsz=640 \
  batch=16

# Export
yolo export model=runs/detect/train/weights/best.pt format=onnx
```

### OCR Fine-Tuning

PaddleOCR fine-tuning for license plates:

```python
# Follow PaddleOCR documentation
# https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_en/finetune_en.md
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_detection.py -v

# Run with coverage
pytest tests/ --cov=edge --cov-report=html
```

## Performance Tuning

### Hardware Acceleration

**GPU (NVIDIA):**
- Set `hardware.use_cuda: true`
- Use `pipeline.use_hw_decoder: true` for NVDEC
- Select appropriate model size (n/s/m/l)

**Edge TPU (Coral):**
- Use TFLite models compiled for Edge TPU
- Set `hardware.type: "coral"`
- Process multiple cameras per TPU

**CPU Optimization:**
- Use smaller models (YOLOv8n)
- Reduce input size (416 instead of 640)
- Lower FPS (5-8 instead of 10+)
- Increase `hardware.num_threads`

### Pipeline Optimization

- **Buffer Management**: Adjust `pipeline.buffer_size`
- **Frame Dropping**: Enable `pipeline.drop_on_latency`
- **Resolution**: Reduce camera resolution if needed
- **FPS**: Lower FPS for CPU-constrained systems

## Monitoring

### Prometheus Metrics

Metrics available at `http://localhost:9090/metrics`:

- `anpr_frames_processed_total` - Total frames processed
- `anpr_detections_total` - Total detections
- `anpr_ocr_success_total` - Successful OCR recognitions
- `anpr_events_exported_total` - Events exported
- `anpr_pipeline_latency_seconds` - Processing latency

### Logging

Logs are output to stderr with structured format:

```
2024-01-15 10:30:45.123 | INFO     | edge.pipeline:start:234 - Pipeline started for camera Main Entrance
2024-01-15 10:30:46.456 | INFO     | edge.detection:detect:89 - Detected vehicle with confidence 0.95
2024-01-15 10:30:46.789 | INFO     | edge.ocr:recognize:123 - OCR result: ABC123 (0.92)
```

## Troubleshooting

### Common Issues

**1. GStreamer pipeline errors**
```bash
# Check GStreamer plugins
gst-inspect-1.0 | grep rtsp
gst-inspect-1.0 | grep h264

# Test RTSP stream
gst-launch-1.0 rtspsrc location=rtsp://... ! fakesink
```

**2. CUDA out of memory**
- Reduce batch size
- Use smaller model
- Lower input resolution

**3. OCR poor accuracy**
- Check image preprocessing
- Adjust confidence thresholds
- Add more OCR engines to ensemble
- Improve lighting conditions

**4. Event export failures**
- Check network connectivity
- Verify backend endpoint
- Check retry queue: `/var/lib/anpr/queue`
- Review logs for detailed errors

### Debug Mode

Enable debug logging:

```bash
python -m edge.main --config config.yaml --log-level DEBUG
```

## Development

### Code Structure

```
edge/
├── __init__.py           # Package initialization
├── config.py             # Configuration models
├── pipeline.py           # GStreamer pipeline
├── detection/            # Detection module
│   ├── detector.py       # Model inference
│   └── tracker.py        # Object tracking
├── ocr/                  # OCR module
│   ├── models.py         # OCR engines
│   └── ensemble.py       # Consensus algorithm
├── exporters/            # Export module
│   └── dispatcher.py     # Event exporters
├── config/               # Configuration files
└── tests/                # Unit tests
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run linting: `black . && flake8`
5. Submit pull request

## License

MIT License - See LICENSE file for details

## Support

- Documentation: https://docs.anpr.local
- Issues: https://github.com/your-org/anpr-edge-worker/issues
- Email: support@anpr.local

## Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- [GStreamer](https://gstreamer.freedesktop.org/)
