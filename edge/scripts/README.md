# Edge Worker Scripts

Utility scripts for ANPR Edge Worker setup and model conversion.

## Convert ONNX to HEF (Hailo-8L)

Convert fast-plate-ocr ONNX model to Hailo HEF format for hardware acceleration.

### Prerequisites

1. **Install Hailo SDK**:
   ```bash
   # Follow Hailo documentation for your platform
   # https://hailo.ai/developer-zone/documentation/

   # Verify installation
   python -c "from hailo_sdk_client import ClientRunner; print('OK')"
   ```

2. **Get fast-plate-ocr ONNX model**:
   ```bash
   # Option 1: Download pre-trained model
   wget https://github.com/ankandrew/fast-plate-ocr/releases/download/v0.1.3/model.onnx

   # Option 2: Export from fast-plate-ocr
   pip install fast-plate-ocr
   python -c "from fast_plate_ocr import export_onnx; export_onnx('model.onnx')"
   ```

3. **Prepare calibration dataset**:
   ```bash
   mkdir -p calibration_data

   # Add 100-500 license plate crop images
   # - Variety of lighting conditions
   # - Different angles and distances
   # - Representative of production data

   # Example structure:
   # calibration_data/
   #   ├── plate_001.jpg
   #   ├── plate_002.jpg
   #   └── ...
   ```

### Basic Usage

**Convert with INT8 quantization (recommended)**:
```bash
python convert_onnx_to_hef.py \
    --input model.onnx \
    --output fast-plate-ocr-hailo8l.hef \
    --calib-dataset ./calibration_data \
    --batch-size 1 \
    --target hailo8l \
    --precision int8
```

**Convert without quantization (faster conversion, lower runtime performance)**:
```bash
python convert_onnx_to_hef.py \
    --input model.onnx \
    --output fast-plate-ocr-hailo8l.hef \
    --precision mixed \
    --target hailo8l
```

### Parameters

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `--input`, `-i` | Path to input ONNX model | - | ✓ |
| `--output`, `-o` | Path to output HEF file | - | ✓ |
| `--calib-dataset`, `-c` | Path to calibration images | - | Only for INT8 |
| `--batch-size`, `-b` | Model batch size | 1 | ✗ |
| `--target`, `-t` | Target device (`hailo8`, `hailo8l`) | `hailo8l` | ✗ |
| `--precision`, `-p` | Precision (`int8`, `mixed`) | `int8` | ✗ |
| `--optimization-level` | Optimization level (0-4) | 2 | ✗ |

### Expected Output

```
2024-01-01 10:00:00 - INFO - Converting ONNX model: model.onnx
2024-01-01 10:00:00 - INFO - Target device: hailo8l
2024-01-01 10:00:00 - INFO - Precision: int8
2024-01-01 10:00:00 - INFO - Optimization level: 2
2024-01-01 10:00:01 - INFO - Step 1/5: Parsing ONNX model...
2024-01-01 10:00:05 - INFO - ✓ Model parsed successfully
2024-01-01 10:00:05 - INFO - Step 2/5: Optimizing model...
2024-01-01 10:00:10 - INFO - ✓ Model optimized
2024-01-01 10:00:10 - INFO - Step 3/5: Quantizing model to INT8...
2024-01-01 10:00:10 - INFO - Loading calibration data from: ./calibration_data
2024-01-01 10:01:30 - INFO - ✓ Model quantized to INT8
2024-01-01 10:01:30 - INFO - Step 4/5: Compiling model to HEF format...
2024-01-01 10:02:00 - INFO - ✓ Model compiled to HEF
2024-01-01 10:02:00 - INFO - Step 5/5: Saving HEF file to: fast-plate-ocr-hailo8l.hef
2024-01-01 10:02:01 - INFO - ✓ HEF file saved successfully
2024-01-01 10:02:01 - INFO -
==================================================
Conversion completed successfully!
Input:  model.onnx
Output: fast-plate-ocr-hailo8l.hef
Size:   2.34 MB
==================================================
```

### Using HEF Model in Edge Worker

Update your `config.yaml`:

```yaml
ocr:
  ensemble_method: "voting"
  min_agreement: 1

  models:
    # Fast Plate OCR with Hailo-8L
    - engine: "fast_plate_ocr"
      language: "en"
      model_path: "/path/to/fast-plate-ocr-hailo8l.hef"
      confidence_threshold: 0.7
      use_hailo: true
      enabled: true

    # Tesseract as fallback
    - engine: "tesseract"
      language: "eng"
      confidence_threshold: 0.5
      enabled: true
```

### Performance Comparison

| Configuration | Inference Time | Accuracy | Hardware |
|---------------|---------------|----------|----------|
| ONNX (CPU) | ~80-120ms | 95%+ | Raspberry Pi 4 |
| HEF (Hailo-8L) | ~8-15ms | 95%+ | Raspberry Pi 4 + Hailo-8L |
| HEF INT8 (Hailo-8L) | ~5-10ms | 94%+ | Raspberry Pi 4 + Hailo-8L |

**8-10x speedup with Hailo-8L!** 🚀

### Troubleshooting

#### Hailo SDK Not Found
```bash
pip install hailo-sdk-client
# Or follow: https://hailo.ai/developer-zone/documentation/
```

#### Calibration Dataset Missing
```
ERROR - --calib-dataset is required for INT8 precision
```

**Solution**: Provide calibration images:
```bash
python convert_onnx_to_hef.py \
    --input model.onnx \
    --output model.hef \
    --calib-dataset ./calibration_data  # Add this
```

#### Model Input Shape Issues
```
ERROR - Unexpected input shape
```

**Solution**: fast-plate-ocr expects shape `[batch, 64, 128, 3]` (H x W x C).
If your model has different shape, adjust preprocessing in `FastPlateOCR._preprocess_for_hailo()`.

#### Compilation Timeout
Large models may take 5-15 minutes to compile. Be patient!

### Advanced: Custom Calibration

For best results, use images representative of your specific use case:

```python
# extract_plates_for_calibration.py
import cv2
from pathlib import Path

def extract_plates(video_path, output_dir, max_images=500):
    """Extract plate crops from video for calibration"""
    cap = cv2.VideoCapture(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    count = 0
    while count < max_images:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect plate (use your detection model)
        plate_crop = detect_and_crop_plate(frame)

        if plate_crop is not None:
            # Resize to model input size
            resized = cv2.resize(plate_crop, (128, 64))

            # Save
            cv2.imwrite(output_dir / f"plate_{count:04d}.jpg", resized)
            count += 1

    cap.release()
    print(f"Extracted {count} plates to {output_dir}")

# Usage
extract_plates("camera_footage.mp4", "calibration_data", max_images=300)
```

### Resources

- **Hailo Documentation**: https://hailo.ai/developer-zone/documentation/
- **fast-plate-ocr GitHub**: https://github.com/ankandrew/fast-plate-ocr
- **ANPR Engine Docs**: [../README.md](../README.md)
- **Model Zoo**: Check for pre-converted HEF models in releases

---

**Questions?** Open an issue or check the documentation!
