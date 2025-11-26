# Quick Start Guide

Get the ANPR Edge Worker up and running in 5 minutes.

## Prerequisites

- Ubuntu 20.04+ or Debian 11+ (or compatible Linux distribution)
- Python 3.8+
- 4GB+ RAM (8GB+ recommended)
- Camera with RTSP stream or test video file

## Quick Setup

### 1. Install System Dependencies

```bash
make install-system-deps
```

Or manually:

```bash
sudo apt-get update
sudo apt-get install -y \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-rtsp \
    python3-gi \
    tesseract-ocr \
    libopencv-dev
```

### 2. Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
make install
```

### 3. Setup Configuration

```bash
# Create config files from examples
make setup-config

# Edit configuration
nano config/config.yaml
```

**Minimum required changes:**

```yaml
# config/config.yaml
worker_id: "edge_worker_001"

# Update camera RTSP URL
cameras:
  - id: "cam_01"
    name: "Test Camera"
    rtsp_url: "rtsp://admin:password@192.168.1.100:554/stream1"
    enabled: true

# Update model path (download YOLOv8 first)
detection_model:
  weights_path: "/path/to/yolov8n.pt"

# Update backend endpoint
exporters:
  - type: "rest"
    endpoint: "http://backend.local:8000/api/v1/events"
```

### 4. Download Models

#### Detection Model (YOLOv8)

```bash
# Install ultralytics if not already installed
pip install ultralytics

# Download pre-trained model
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# Move to models directory
mv yolov8n.pt models/

# Or train custom model for vehicles and license plates
# See README.md for training instructions
```

#### OCR Models

OCR models (PaddleOCR, EasyOCR) will be downloaded automatically on first run.

### 5. Test Configuration

```bash
# Dry run to validate configuration
make run-dry
```

Expected output:
```
Configuration loaded from config.yaml
Worker ID: edge_worker_001
Cameras: 1
Hardware: cpu
Detection model: yolov8
OCR engines: 3
Exporters: 1
```

### 6. Run Edge Worker

```bash
# Start worker
make run

# Or with debug logging
make run-debug
```

Expected output:
```
2024-01-15 10:30:45 | INFO | Initializing Edge Worker: edge_worker_001
2024-01-15 10:30:46 | INFO | Loading detection model...
2024-01-15 10:30:48 | INFO | Loading OCR models...
2024-01-15 10:30:52 | INFO | Pipeline started for camera Test Camera
2024-01-15 10:30:53 | INFO | Edge worker is running
```

## Docker Quick Start

### 1. Build Image

```bash
make docker-build
```

### 2. Setup Configuration

```bash
# Create config files
make setup-config

# Edit config.yaml and cameras.yaml
nano config/config.yaml
```

### 3. Run Container

```bash
# Start container
make docker-run

# View logs
make docker-logs

# Stop container
make docker-stop
```

## Testing with Sample Video

If you don't have a live RTSP stream, use a video file:

```yaml
cameras:
  - id: "cam_test"
    name: "Test Video"
    rtsp_url: "file:///path/to/test/video.mp4"
    enabled: true
    fps: 10
```

Download sample video:
```bash
# Example: Download sample traffic video
wget https://example.com/sample-traffic.mp4 -O test-video.mp4

# Update config to use file
rtsp_url: "file:///home/user/anpr-edge/test-video.mp4"
```

## Verify Installation

### 1. Check GStreamer

```bash
# List GStreamer plugins
gst-inspect-1.0 | grep rtsp

# Test RTSP stream
gst-launch-1.0 rtspsrc location=rtsp://your-camera-url ! fakesink
```

### 2. Check Python Dependencies

```bash
python -c "import cv2, torch, paddleocr, easyocr; print('OK')"
```

### 3. Run Tests

```bash
make test
```

## Common Issues

### Issue: "No module named 'gi'"

**Solution:**
```bash
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gstreamer-1.0
```

### Issue: "Failed to load detection model"

**Solution:**
1. Download YOLOv8 model: `python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"`
2. Update `detection_model.weights_path` in config

### Issue: "RTSP connection timeout"

**Solution:**
1. Verify camera URL: `gst-launch-1.0 rtspsrc location=rtsp://... ! fakesink`
2. Check network connectivity
3. Verify camera credentials
4. Check firewall rules

### Issue: "OCR models downloading slowly"

**Solution:**
OCR models are large and downloaded on first run. Be patient or download manually:

```bash
# PaddleOCR models (downloaded automatically)
# EasyOCR models
python -c "import easyocr; reader = easyocr.Reader(['en'])"
```

## Next Steps

1. **Fine-tune Detection Model**: Train on your specific vehicles and plates
2. **Optimize OCR**: Adjust confidence thresholds and ensemble settings
3. **Setup Monitoring**: Enable Prometheus metrics and Grafana dashboards
4. **Production Deployment**: Use systemd service or Docker Swarm/Kubernetes
5. **Multiple Cameras**: Add more cameras to configuration

## Getting Help

- Read full documentation: [README.md](README.md)
- Check logs: `tail -f logs/edge.log`
- Enable debug mode: `--log-level DEBUG`
- Report issues: GitHub Issues

## Quick Commands Reference

```bash
# Installation
make install              # Install dependencies
make dev-install          # Install with dev tools
make setup-config         # Create config files

# Running
make run                  # Run edge worker
make run-debug            # Run with debug logging
make run-dry              # Test configuration

# Testing
make test                 # Run tests
make test-cov             # Run tests with coverage

# Code quality
make lint                 # Run linters
make format               # Format code

# Docker
make docker-build         # Build image
make docker-run           # Start container
make docker-stop          # Stop container
make docker-logs          # View logs

# Cleanup
make clean                # Clean temporary files
```

## Performance Tips

1. **CPU Mode**: Use YOLOv8n (nano) model, reduce FPS to 5-8
2. **GPU Mode**: Enable CUDA, use YOLOv8s/m model
3. **Edge TPU**: Use TFLite model compiled for Coral
4. **Multi-Camera**: 1 camera per 2 CPU cores or 4-8 cameras per GPU

Happy license plate detecting!
