# GStreamer Pipeline with Hailo Integration

This directory contains the GStreamer pipeline implementation for hardware-accelerated ANPR.

## Architecture

```
RTSP Stream
    ↓
rtspsrc (GStreamer element)
    ↓
h264parse + v4l2h264dec (Raspberry Pi hardware decode)
    ↓
videoscale + videoconvert (resize to 640x480, format conversion)
    ↓
hailonet (YOLO detection model on Hailo)
    ↓
hailofilter (post-process detections)
    ↓
hailocropper (crop plate regions)
    ↓
hailonet (OCR model on Hailo)
    ↓
hailofilter (post-process OCR results)
    ↓
Results → Python callback → Edge Worker
```

## Required Hailo Post-Processing Plugins

The pipeline requires three custom C++ plugins for Hailo post-processing:

### 1. `libplate_detection.so` - Detection Post-Processing
- Parses YOLO output tensors
- Filters detections by confidence threshold
- Applies NMS (Non-Maximum Suppression)
- Outputs bounding boxes for license plates

### 2. `libplate_crop.so` - Plate Cropping
- Extracts plate regions from detections
- Resizes plates to OCR model input size
- Passes cropped images to next stage

### 3. `libplate_ocr.so` - OCR Post-Processing
- Parses OCR model output (CTC)
- Decodes character sequences
- Applies confidence filtering
- Outputs plate text + confidence

## Building the Plugins

```bash
cd edge/gstreamer/hailo-postprocess
mkdir build && cd build
cmake ..
make
sudo make install
```

## Pipeline Configuration

The pipeline can be configured via environment variables or the worker config file:

- `DETECTION_MODEL_PATH`: Path to detection .hef file
- `OCR_MODEL_PATH`: Path to OCR .hef file
- `TARGET_WIDTH`: Inference width (default: 640)
- `TARGET_HEIGHT`: Inference height (default: 480)
- `DETECTION_THRESHOLD`: Detection confidence (default: 0.5)

## Hardware Requirements

- Raspberry Pi 4/5 with V4L2 H.264 hardware decoder
- Hailo-8 or Hailo-8L AI accelerator
- Hailo SDK 4.17.0+
- GStreamer 1.20+
- GStreamer Hailo plugin

## Testing the Pipeline

```bash
# Test with a single camera
python3 -m edge.gstreamer.pipeline \
    --rtsp-url rtsp://camera-ip:554/stream \
    --detection-model models/yolov8n-plate.hef \
    --ocr-model models/plate-ocr.hef
```
