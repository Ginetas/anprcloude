# ANPR Edge Worker Installation Scripts

This directory contains automated installation scripts for deploying the ANPR Edge Worker on various platforms. Each script is idempotent, production-ready, and includes comprehensive error handling.

## Available Installation Scripts

### 1. Raspberry Pi + Hailo-8L (`install_rpi_hailo.sh`)

**Best for:** Edge deployment with specialized AI accelerator
- **Hardware:** Raspberry Pi 4/5 + Hailo-8L accelerator
- **Performance:** High throughput with low power consumption
- **File Size:** ~14KB

#### Features:
- Hailo driver and runtime installation
- GStreamer integration for video processing
- Python 3.9+ with optimized environment
- Automatic device detection and verification
- Systemd service for auto-start

#### Quick Start:
```bash
sudo bash install_rpi_hailo.sh
```

#### Post-Installation:
1. Connect your Hailo-8L device
2. Verify connection: `hailortcli fw-control identify`
3. Configure: `sudo nano /etc/anpr-edge-worker/config.yaml`
4. Start service: `sudo systemctl start anpr-edge-worker.service`
5. Check status: `sudo systemctl status anpr-edge-worker.service`

#### System Requirements:
- Raspberry Pi 4 or newer
- 4GB+ RAM (recommended)
- 16GB+ SD card
- Ubuntu 22.04 LTS or Debian 11+
- Root/sudo access

---

### 2. Raspberry Pi + Google Coral TPU (`install_rpi_coral.sh`)

**Best for:** TensorFlow Lite models with Google's accelerator
- **Hardware:** Raspberry Pi 4/5 + Coral TPU (USB or PCIe)
- **Performance:** Excellent for vision models compiled for Coral
- **File Size:** ~18KB

#### Features:
- EdgeTPU runtime and compiler installation
- TensorFlow Lite support
- PyCoral Python bindings
- USB and PCIe device support
- Automatic permission configuration
- Device detection and verification

#### Quick Start:
```bash
sudo bash install_rpi_coral.sh
```

#### Post-Installation:
1. Connect your Coral TPU device (USB or PCIe)
2. Verify connection: `lsusb | grep 1a6e:089a` (USB) or `lspci | grep 089a` (PCIe)
3. Check device list:
   ```bash
   python3 -c "from pycoral.utils import edgetpu_utils; print(edgetpu_utils.list_edge_tpus())"
   ```
4. Configure: `sudo nano /etc/anpr-edge-worker/config.yaml`
5. Start service: `sudo systemctl start anpr-edge-worker.service`

#### System Requirements:
- Raspberry Pi 4 or newer
- 4GB+ RAM (recommended)
- 16GB+ SD card
- Ubuntu 22.04 LTS or Debian 11+
- Google Coral TPU device
- Root/sudo access

#### Model Preparation:
Models must be compiled for Coral with Edge TPU support:
```bash
edgetpu_compiler -s your_model.tflite
```

---

### 3. Linux with GPU/CPU Support (`install_linux.sh`)

**Best for:** Flexible deployments with automatic hardware detection
- **Hardware:** Linux (Ubuntu/Debian/RHEL/CentOS) with optional NVIDIA GPU
- **Performance:** Full PyTorch, TensorFlow, CUDA support
- **File Size:** ~24KB

#### Features:
- Automatic NVIDIA GPU detection
- CUDA Toolkit installation (versions 11.x, 12.x)
- cuDNN support for deep learning
- CPU-only fallback mode
- Advanced driver detection
- Multi-platform support (Ubuntu, Debian, RHEL, CentOS, Fedora)
- Resource limit configuration
- GPU group permissions

#### Quick Start:
```bash
# Automatic GPU detection
sudo bash install_linux.sh

# CPU-only mode
sudo bash install_linux.sh --skip-gpu

# Force specific CUDA version
sudo bash install_linux.sh --force-cuda-version 11.8
```

#### Post-Installation:
1. Copy your models to: `/opt/anpr-edge-worker/models/`
2. Configure: `sudo nano /etc/anpr-edge-worker/config.yaml`
3. Test the service: `sudo systemctl start anpr-edge-worker.service`
4. Check logs: `sudo journalctl -u anpr-edge-worker.service -f`

#### System Requirements:
- Ubuntu 20.04+, Debian 11+, or RHEL/CentOS 7+
- 4GB+ RAM (8GB+ recommended for GPU)
- 20GB+ disk space
- Optional: NVIDIA GPU (CUDA Compute Capability 3.5+)
- Root/sudo access

#### GPU Support:
Supports NVIDIA GPUs with:
- CUDA Toolkit 11.x, 12.x
- cuDNN library
- Automatic driver installation (Ubuntu)
- Environment configuration for TensorFlow/PyTorch

#### Command-Line Arguments:
```bash
--skip-gpu              Disable GPU detection (CPU-only)
--force-cuda-version    Specify CUDA version (e.g., 11.8, 12.0)
```

---

## Installation Workflow

### General Steps (All Platforms):
1. **Download script** for your platform
2. **Run as root** with sudo
3. **Verify installation** (automatic)
4. **Configure application** (edit config.yaml)
5. **Prepare models** (place in /opt/anpr-edge-worker/models/)
6. **Start service** (systemctl start)

### Example Installation Sequence:

#### Raspberry Pi + Hailo:
```bash
# Download script
wget https://your-repo/install_rpi_hailo.sh

# Install
sudo bash install_rpi_hailo.sh

# Verify Hailo device
hailortcli fw-control identify

# Configure
sudo nano /etc/anpr-edge-worker/config.yaml

# Start service
sudo systemctl start anpr-edge-worker.service
sudo systemctl enable anpr-edge-worker.service
```

#### Linux with GPU:
```bash
# Download script
wget https://your-repo/install_linux.sh

# Install with GPU support
sudo bash install_linux.sh

# Check GPU
nvidia-smi

# Configure
sudo nano /etc/anpr-edge-worker/config.yaml

# Start service
sudo systemctl start anpr-edge-worker.service
sudo systemctl enable anpr-edge-worker.service
```

---

## Installation Directory Structure

After installation, the following structure is created:

```
/opt/anpr-edge-worker/
├── venv/                           # Python virtual environment
│   ├── bin/
│   │   ├── python                 # Python interpreter
│   │   └── pip                    # Package manager
│   ├── lib/
│   └── ...
├── models/                         # Place your model files here
├── data/                           # Data directory
└── ...

/etc/anpr-edge-worker/
├── config.yaml                    # Main configuration file
├── cuda.env                       # CUDA environment (GPU systems)
└── worker.env                     # Worker environment variables

/var/log/anpr-edge-worker/
├── worker.log                     # Application logs
└── ...

/etc/systemd/system/
└── anpr-edge-worker.service       # Systemd service definition
```

---

## Configuration

### Main Configuration File
Located at: `/etc/anpr-edge-worker/config.yaml`

#### Essential Settings:
```yaml
hardware:
  accelerator: "hailo"  # or "coral", "nvidia_gpu", "cpu"
  device_id: 0

model:
  detection:
    model_path: "/opt/anpr-edge-worker/models/detection_model.hef"
    confidence_threshold: 0.5

sources:
  - id: "camera_0"
    type: "rtsp"
    uri: "rtsp://192.168.1.100:554/stream"
    enabled: true
```

### Environment Variables
Create optional `/etc/anpr-edge-worker/worker.env`:
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=5000

# Logging
LOG_LEVEL=INFO

# MQTT (if using MQTT output)
MQTT_BROKER=mqtt.example.com
MQTT_PORT=1883
```

---

## Service Management

### SystemD Commands:

```bash
# Check status
sudo systemctl status anpr-edge-worker.service

# Start service
sudo systemctl start anpr-edge-worker.service

# Stop service
sudo systemctl stop anpr-edge-worker.service

# Restart service
sudo systemctl restart anpr-edge-worker.service

# Enable auto-start on boot
sudo systemctl enable anpr-edge-worker.service

# Disable auto-start
sudo systemctl disable anpr-edge-worker.service

# View real-time logs
sudo journalctl -u anpr-edge-worker.service -f

# View last 50 log lines
sudo journalctl -u anpr-edge-worker.service -n 50

# View logs since boot
sudo journalctl -u anpr-edge-worker.service -b
```

---

## Verification and Troubleshooting

### Post-Installation Verification

#### Raspberry Pi + Hailo:
```bash
# Verify Hailo device
hailortcli fw-control identify

# Check Python and packages
/opt/anpr-edge-worker/venv/bin/python --version
source /opt/anpr-edge-worker/venv/bin/activate
python -c "from hailo_platform import Device; d = Device(); print(d.get_device_info())"

# Verify GStreamer
gst-launch-1.0 --version
```

#### Raspberry Pi + Coral:
```bash
# List Coral devices
python3 -c "from pycoral.utils import edgetpu_utils; print(edgetpu_utils.list_edge_tpus())"

# Check device permissions
ls -la /dev/bus/usb/*/

# Verify TFLite
python3 -c "import tflite_runtime; print('TFLite OK')"
```

#### Linux + GPU:
```bash
# Check GPU
nvidia-smi

# Verify CUDA
nvcc --version

# Check cuDNN
ls -la /usr/local/cuda/lib64/libcudnn*

# Verify PyTorch GPU
python3 -c "import torch; print(torch.cuda.is_available())"
```

### Common Issues

#### Issue: Service fails to start
**Solution:**
```bash
# Check logs
sudo journalctl -u anpr-edge-worker.service -n 100

# Check file permissions
ls -la /opt/anpr-edge-worker/
ls -la /etc/anpr-edge-worker/

# Verify Python
/opt/anpr-edge-worker/venv/bin/python --version
```

#### Issue: Device not detected
**Solution:**

For Hailo:
```bash
# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Check device connection
lsusb | grep 1a6e

# Re-run device detection
hailortcli fw-control identify
```

For Coral:
```bash
# Check USB device
lsusb | grep 1a6e:089a

# Check PCIe device
lspci | grep 089a

# Verify permissions
groups $USER
# Should include: video, render, dialout
```

#### Issue: GPU not detected
**Solution:**
```bash
# Check NVIDIA driver
nvidia-smi

# Reinstall driver (Ubuntu)
sudo ubuntu-drivers autoinstall
sudo reboot

# Force CUDA version
sudo bash install_linux.sh --force-cuda-version 12.0
```

#### Issue: Out of memory
**Solution:**
```bash
# Check available memory
free -h

# Adjust service memory limit in systemd file
sudo systemctl edit anpr-edge-worker.service
# Add: MemoryMax=2G

# Adjust Python heap
export PYTHONUNBUFFERED=1
```

---

## Performance Tuning

### Hailo-8L:
```yaml
hardware:
  accelerator: "hailo"
processing:
  max_workers: 4
  batch_size: 8
```

### Coral TPU:
```yaml
hardware:
  accelerator: "coral"
performance:
  num_threads: 2
  use_xnnpack: true
```

### GPU (NVIDIA):
```yaml
hardware:
  accelerator: "nvidia_gpu"
performance:
  use_fp16: true
  use_tensor_cores: true
  num_cuda_streams: 4
```

---

## Model Preparation

### For Hailo-8L:
1. Export your model to ONNX format
2. Use Hailo's model compiler
3. Place `.hef` file in `/opt/anpr-edge-worker/models/`

### For Google Coral:
1. Convert to TensorFlow Lite format
2. Compile with EdgeTPU compiler:
   ```bash
   edgetpu_compiler your_model.tflite
   ```
3. Place compiled model in `/opt/anpr-edge-worker/models/`

### For GPU/CPU:
1. Export from PyTorch or TensorFlow
2. Place model in `/opt/anpr-edge-worker/models/`
3. Update config.yaml with path

---

## Uninstallation

To completely remove the installation:

```bash
# Stop and disable service
sudo systemctl stop anpr-edge-worker.service
sudo systemctl disable anpr-edge-worker.service

# Remove service file
sudo rm /etc/systemd/system/anpr-edge-worker.service
sudo systemctl daemon-reload

# Remove application
sudo rm -rf /opt/anpr-edge-worker/

# Remove configuration
sudo rm -rf /etc/anpr-edge-worker/

# Remove logs
sudo rm -rf /var/log/anpr-edge-worker/

# Remove user
sudo userdel -r anprworker
```

---

## Updating Installation

All scripts are idempotent and safe to run multiple times. To update:

```bash
# Run the installation script again
sudo bash install_rpi_hailo.sh

# Check for dependency updates
sudo apt-get update
sudo apt-get upgrade

# Restart service
sudo systemctl restart anpr-edge-worker.service
```

---

## Support and Documentation

- **Configuration Guide:** See `/etc/anpr-edge-worker/config.yaml`
- **Service Logs:** `sudo journalctl -u anpr-edge-worker.service`
- **System Status:** `sudo systemctl status anpr-edge-worker.service`
- **Hardware Info:** Device-specific commands listed above

## Security Considerations

- Scripts create non-root user (`anprworker`) for service
- Configuration files use restricted permissions (640)
- Systemd service uses security hardening directives
- Device access requires appropriate group membership
- Environment files kept separate for sensitive data

## License

These installation scripts are part of the ANPR project.
