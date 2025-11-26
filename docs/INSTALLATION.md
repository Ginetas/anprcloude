# ANPR Engine - Installation Guide

Complete step-by-step installation instructions for all components of the ANPR Engine system.

---

## Table of Contents

1. [Backend Installation](#backend-installation)
2. [Frontend Installation](#frontend-installation)
3. [Edge Worker Installation](#edge-worker-installation)
4. [Docker Compose Setup](#docker-compose-setup)
5. [Production Deployment](#production-deployment)
6. [Troubleshooting](#troubleshooting)

---

## Backend Installation

### Prerequisites

- **Python**: 3.9 or higher
- **PostgreSQL**: 13 or higher
- **Git**
- **pip** (Python package manager)
- **2GB+ RAM**
- **10GB+ disk space** (depending on event storage)

### Step 1: Verify Python Installation

```bash
python --version
# or
python3 --version
```

Ensure you have Python 3.9+. If not, install from [python.org](https://www.python.org/downloads/).

### Step 2: Install PostgreSQL

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### On macOS (using Homebrew):
```bash
brew install postgresql@15
brew services start postgresql@15
```

#### On Windows:
Download and install from [postgresql.org](https://www.postgresql.org/download/windows/)

### Step 3: Create PostgreSQL Database and User

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Inside PostgreSQL prompt:
CREATE USER anpr_user WITH PASSWORD 'your_secure_password';
CREATE DATABASE anpr_db OWNER anpr_user;
GRANT ALL PRIVILEGES ON DATABASE anpr_db TO anpr_user;
ALTER USER anpr_user CREATEDB;
\q
```

Verify the connection:
```bash
psql -U anpr_user -d anpr_db -h localhost
```

### Step 4: Set Up Python Virtual Environment

```bash
# Navigate to backend directory
cd /home/user/anprcloude/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

You should see `(venv)` prefix in your terminal.

### Step 5: Install Backend Dependencies

```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install fastapi uvicorn sqlmodel psycopg2-binary python-dotenv pydantic
pip install aiofiles aioredis websockets
pip install pytest pytest-asyncio httpx
pip install sqlalchemy alembic

# Optional: For S3 storage support
pip install boto3

# Optional: For Redis caching
pip install redis aioredis
```

Or if a `requirements.txt` exists:
```bash
pip install -r requirements.txt
```

### Step 6: Configure Environment Variables

Create `.env` file in the backend directory:

```bash
cat > /home/user/anprcloude/backend/.env << 'EOF'
# Database
DATABASE_URL=postgresql://anpr_user:your_secure_password@localhost:5432/anpr_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
API_WORKERS=4

# Security
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# Redis (optional, for caching and WebSocket support)
REDIS_URL=redis://localhost:6379/0
ENABLE_REDIS=true

# File Storage
STORAGE_TYPE=local  # Options: local, s3
STORAGE_LOCAL_PATH=/tmp/anpr_events

# S3 Configuration (if using S3)
# S3_ENDPOINT=http://localhost:9000
# S3_ACCESS_KEY=minioadmin
# S3_SECRET_KEY=minioadmin
# S3_BUCKET=anpr-events
# S3_REGION=us-east-1

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Application
ENVIRONMENT=development  # Options: development, staging, production
DEBUG=true
EOF
```

### Step 7: Initialize Database

```bash
# Create migration directory (if using Alembic)
# This creates the database schema

cd /home/user/anprcloude/backend
python -m alembic upgrade head

# Or if using direct schema initialization
python -c "from app.database import init_db; init_db()"
```

### Step 8: Run Backend Server

```bash
# Using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or using the venv activation and reload during development
cd /home/user/anprcloude/backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Access the API:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000/api

### Step 9: Running Backend Tests

```bash
cd /home/user/anprcloude/backend
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

### Backend Troubleshooting

| Issue | Solution |
|-------|----------|
| PostgreSQL connection refused | Ensure PostgreSQL is running: `sudo systemctl status postgresql` |
| `ModuleNotFoundError: No module named 'fastapi'` | Activate venv: `source venv/bin/activate` and run `pip install -r requirements.txt` |
| Port 8000 already in use | Use different port: `uvicorn app.main:app --port 8001` |
| Database migration fails | Check PostgreSQL user permissions: `GRANT ALL PRIVILEGES ON DATABASE anpr_db TO anpr_user;` |
| JWT secret not set | Generate new secret: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |

---

## Frontend Installation

### Prerequisites

- **Node.js**: 18.0 or higher
- **npm** or **yarn** or **pnpm** (package manager)
- **Git**

### Step 1: Verify Node.js Installation

```bash
node --version
npm --version
```

Ensure Node.js 18+. If not, install from [nodejs.org](https://nodejs.org/).

### Step 2: Install Frontend Dependencies

```bash
cd /home/user/anprcloude/frontend

# Using npm
npm install

# Or using yarn
yarn install

# Or using pnpm
pnpm install
```

### Step 3: Configure Environment Variables

Create `.env.local` file in the frontend directory:

```bash
cat > /home/user/anprcloude/frontend/.env.local << 'EOF'
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_API_TIMEOUT=30000

# WebSocket Configuration
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_WS_RECONNECT_INTERVAL=3000

# Application
NEXT_PUBLIC_APP_NAME=ANPR Engine
NEXT_PUBLIC_APP_DESCRIPTION=Automatic Number Plate Recognition System
NEXT_PUBLIC_ENVIRONMENT=development

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_NOTIFICATIONS=true
NEXT_PUBLIC_ENABLE_DARK_MODE=true

# UI Configuration
NEXT_PUBLIC_ITEMS_PER_PAGE=20
NEXT_PUBLIC_REFRESH_INTERVAL=5000
EOF
```

### Step 4: Development Server

```bash
cd /home/user/anprcloude/frontend

# Start development server
npm run dev

# Or with yarn
yarn dev

# Or with pnpm
pnpm dev
```

Access the frontend:
- **Development**: http://localhost:3000

The development server supports hot-reload. Changes to files will automatically refresh the browser.

### Step 5: Production Build

```bash
cd /home/user/anprcloude/frontend

# Build the application
npm run build

# Start production server
npm start
```

Production build output is in the `.next` directory.

### Step 6: Running Frontend Tests

```bash
cd /home/user/anprcloude/frontend

# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test -- __tests__/components/dashboard.test.tsx
```

### Step 7: Code Formatting and Linting

```bash
cd /home/user/anprcloude/frontend

# Format code with Prettier
npm run format

# Check code style with ESLint
npm run lint

# Fix ESLint issues automatically
npm run lint -- --fix
```

### Step 8: Build Optimization (Optional)

```bash
cd /home/user/anprcloude/frontend

# Analyze bundle size
npm run analyze

# Generate build statistics
npm run build -- --analyze
```

### Frontend Troubleshooting

| Issue | Solution |
|-------|----------|
| `npm ERR! code ERESOLVE` | Clear cache: `npm cache clean --force` then `npm install` |
| Port 3000 already in use | Use different port: `npm run dev -- -p 3001` |
| WebSocket connection failed | Check backend is running and `NEXT_PUBLIC_WS_URL` is correct |
| Module not found errors | Delete `node_modules` and `.next`: `rm -rf node_modules .next` then `npm install` |
| Memory issues during build | Increase Node.js memory: `NODE_OPTIONS="--max-old-space-size=4096" npm run build` |

---

## Edge Worker Installation

The Edge Worker can run on different platforms. Choose the one that matches your hardware.

### Common Prerequisites for All Platforms

- **Python**: 3.9 or higher
- **pip** (Python package manager)
- **Git**
- **GStreamer**: 1.20 or higher (for RTSP streaming)

### Installing GStreamer

#### On Raspberry Pi / Ubuntu / Debian:
```bash
sudo apt update
sudo apt install -y gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad
sudo apt install -y gstreamer1.0-libav gstreamer1.0-tools
sudo apt install -y libgstreamer1.0-0 libgstreamer-plugins-base1.0-0
```

#### On macOS:
```bash
brew install gstreamer
```

#### On Windows:
Download and install from [gstreamer.freedesktop.org](https://gstreamer.freedesktop.org/download/)

---

### Option 1: Raspberry Pi + Hailo-8L NPU

The Hailo-8L is an excellent choice for Raspberry Pi with good performance and power efficiency.

#### Step 1: Verify Hailo-8L Hardware

```bash
# Check USB devices
lsusb | grep Hailo

# Expected output should show Hailo device
```

#### Step 2: Install Hailo Runtime

```bash
# Add Hailo repository (Raspberry Pi OS)
curl -fsSL https://raw.githubusercontent.com/hailo-ai/hailo-rpi5-examples/main/add-repo.sh | bash

# Install Hailo packages
sudo apt install -y hailo-all
```

Or download from [Hailo Developer Portal](https://hailo.ai/developer-zone/documentation/)

#### Step 3: Set Up Python Environment

```bash
cd /home/user/anprcloude/edge

# Create virtual environment
python -m venv venv_hailo

# Activate environment
source venv_hailo/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

#### Step 4: Install Dependencies for Hailo

```bash
# Core dependencies
pip install numpy opencv-python-headless
pip install pyyaml requests

# GStreamer bindings
pip install pygobject

# For Hailo
pip install hailort

# For video processing
pip install gstreamer-python

# For detection and OCR
pip install onnxruntime tensorflow-lite
pip install paddleocr

# For communication
pip install aiohttp websockets

# For testing
pip install pytest pytest-asyncio
```

Or use requirements file:
```bash
pip install -r requirements-hailo.txt
```

#### Step 5: Configure for Hailo

Create `config/config_hailo.yaml`:

```yaml
# Hailo Configuration
hardware:
  platform: hailo
  device_id: 0
  batch_size: 1
  npu_threads: 2

# Detection model optimized for Hailo
detection:
  model_path: models/yolov8s_hailo.hef
  input_size: [640, 640]
  confidence_threshold: 0.5
  iou_threshold: 0.4
  device: hailo

# OCR models
ocr:
  ensemble:
    - model: paddleocr_hailo
      weight: 0.5
    - model: tesseract
      weight: 0.5
  fallback_to_cpu: true

# Cameras
cameras:
  - id: cam-001
    name: "Main Entrance"
    rtsp_url: "rtsp://admin:password@192.168.1.100:554/stream1"
    fps: 10
    resolution: [1280, 720]
    hardware_acceleration: hailo

# Backend connectivity
backend:
  url: "http://backend:8000/api"
  ws_url: "ws://backend:8000/ws"
  retry_attempts: 5
  retry_delay: 5
```

#### Step 6: Run Edge Worker with Hailo

```bash
cd /home/user/anprcloude/edge
source venv_hailo/bin/activate

# Start the pipeline
python pipeline.py --config config/config_hailo.yaml

# Or with debug logging
python pipeline.py --config config/config_hailo.yaml --log-level DEBUG
```

#### Step 7: Verify Hailo Performance

```bash
# Check NPU utilization
hailortcli list-devices

# Benchmark model
python -c "from hailort import Device; d = Device(); print(d.info)"

# Monitor in separate terminal
watch -n 1 'hailortcli list-devices'
```

#### Hailo Troubleshooting

| Issue | Solution |
|-------|----------|
| `hailort module not found` | Reinstall: `pip install hailort --no-cache-dir` |
| Device not detected | Check USB: `lsusb` - ensure Hailo is listed |
| NPU out of memory | Reduce batch size or model resolution in config |
| High temperature warnings | Ensure proper cooling; reduce FPS or resolution |

---

### Option 2: Raspberry Pi + Google Coral TPU

The Coral TPU is widely compatible and well-supported on Raspberry Pi.

#### Step 1: Verify Coral TPU Hardware

```bash
# Check USB devices
lsusb | grep Google

# Expected output should show Coral device
```

#### Step 2: Install Coral Runtime and Dependencies

```bash
# Install Coral repository
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | \
  sudo tee /etc/apt/sources.list.d/coral-edgetpu.list

# Add repository key
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

# Update and install
sudo apt update
sudo apt install -y libedgetpu1-std python3-pycoral

# Or for high-frequency (requires cooling):
# sudo apt install -y libedgetpu1-max
# echo "CORAL_THROTTLE_EDGE_TPU=0" | sudo tee -a /etc/default/coral-edgetpu-accelerator.service
```

Or download from [Google Coral Download](https://coral.ai/docs/accelerator/get-started/)

#### Step 3: Set Up Python Environment

```bash
cd /home/user/anprcloude/edge

# Create virtual environment
python -m venv venv_coral

# Activate environment
source venv_coral/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

#### Step 4: Install Dependencies for Coral

```bash
# Core dependencies
pip install numpy opencv-python-headless
pip install pyyaml requests

# GStreamer bindings
pip install pygobject

# For Coral TPU
pip install pycoral

# For TensorFlow Lite
pip install tensorflow-lite

# For detection
pip install ultralytics  # YOLOv8

# For OCR
pip install paddleocr pytesseract

# For communication
pip install aiohttp websockets

# For testing
pip install pytest pytest-asyncio
```

Or use requirements file:
```bash
pip install -r requirements-coral.txt
```

#### Step 5: Download Pre-optimized Models

```bash
# Create models directory
mkdir -p /home/user/anprcloude/edge/models

cd /home/user/anprcloude/edge/models

# Download YOLOv8n optimized for Coral (if available)
# Example: vehicle detection model
wget https://coral.ai/examples/models/vehicle_detection_model.tflite

# Or export your own model:
# yolo export model=yolov8n.pt format=tflite int8
```

#### Step 6: Configure for Coral

Create `config/config_coral.yaml`:

```yaml
# Coral TPU Configuration
hardware:
  platform: coral
  accelerator: /dev/apex_0  # or /dev/apex_1 if multiple TPUs
  batch_size: 1
  use_edgetpu: true

# Detection model optimized for Coral
detection:
  model_path: models/yolov8n_coral.tflite
  input_size: [416, 416]
  confidence_threshold: 0.5
  iou_threshold: 0.4
  device: coral

# OCR ensemble
ocr:
  ensemble:
    - model: paddleocr
      weight: 0.6
    - model: tesseract
      weight: 0.4
  fallback_to_cpu: true

# Cameras
cameras:
  - id: cam-001
    name: "Main Gate"
    rtsp_url: "rtsp://admin:password@192.168.1.100:554/stream1"
    fps: 8
    resolution: [1280, 720]
    hardware_acceleration: coral

# Exporters
exporters:
  - type: rest
    url: "http://backend:8000/api/events/ingest"
    batch_size: 10
    max_retries: 5
    retry_delay: 5
```

#### Step 7: Run Edge Worker with Coral

```bash
cd /home/user/anprcloude/edge
source venv_coral/bin/activate

# Start the pipeline
python pipeline.py --config config/config_coral.yaml

# With verbose logging
python pipeline.py --config config/config_coral.yaml --verbose
```

#### Step 8: Monitor TPU Performance

```bash
# Check TPU availability
python -c "import pycoral; print('Coral TPU OK')"

# Monitor USB connection
watch -n 1 'lsusb | grep Google'

# Check thermal status
cat /sys/class/thermal/thermal_zone*/temp
```

#### Coral Troubleshooting

| Issue | Solution |
|-------|----------|
| `ImportError: No module named 'pycoral'` | Run: `pip install pycoral` |
| Device not found | Check USB: `lsusb \| grep Google` |
| Permission denied for /dev/apex_0 | Add user to group: `sudo usermod -a -G apex $USER` |
| Slow performance | Reduce input resolution or use quantized models |
| Device overheating | Reduce FPS or add active cooling (fan) |

---

### Option 3: Linux with NVIDIA GPU (CUDA)

For high-performance installations on x86_64 Linux with NVIDIA GPUs.

#### Step 1: Verify NVIDIA GPU

```bash
# Check GPU presence
lspci | grep -i nvidia

# Check NVIDIA drivers
nvidia-smi

# Expected output should show GPU information
```

If `nvidia-smi` command not found, install NVIDIA drivers.

#### Step 2: Install CUDA Toolkit

##### Ubuntu 22.04:
```bash
# Add NVIDIA repository
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600

sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/3bf863cc.pub
sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/ /"

# Install CUDA
sudo apt update
sudo apt install -y cuda-toolkit-12-4
sudo apt install -y cuda-drivers

# Add to PATH
echo 'export PATH=/usr/local/cuda-12.4/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.4/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

##### Or using CUDA installation script:
```bash
wget https://developer.download.nvidia.com/compute/cuda/12.4.0/local_installers/cuda_12.4.0_550.54.14_linux.run
sudo sh cuda_12.4.0_550.54.14_linux.run
```

##### macOS with Metal (Apple Silicon):
```bash
# Metal support is built into TensorFlow 2.13+
pip install tensorflow-macos tensorflow-metal
```

##### Verify CUDA installation:
```bash
nvcc --version
nvidia-smi
```

#### Step 3: Install cuDNN (NVIDIA Deep Neural Network Library)

```bash
# Download from https://developer.nvidia.com/cudnn
# Registration required

# Extract and install
tar -xzvf cudnn-linux-x86_64-8.x.x.x_cuda12-archive.tar.xz
sudo cp cudnn-*-archive/include/cudnn*.h /usr/local/cuda/include
sudo cp -P cudnn-*-archive/lib/libcudnn* /usr/local/cuda/lib64
sudo chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*
```

#### Step 4: Set Up Python Environment

```bash
cd /home/user/anprcloude/edge

# Create virtual environment
python -m venv venv_gpu

# Activate environment
source venv_gpu/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

#### Step 5: Install GPU-Enabled Dependencies

```bash
# Core dependencies
pip install numpy opencv-python

# GPU-accelerated TensorFlow
pip install tensorflow>=2.13

# Or PyTorch with CUDA support
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# GStreamer bindings
pip install pygobject

# Detection and tracking
pip install ultralytics  # YOLOv8
pip install opencv-contrib-python

# OCR
pip install paddleocr

# Communication
pip install aiohttp websockets

# Testing
pip install pytest pytest-asyncio

# Monitoring
pip install gputil psutil
```

#### Step 6: Verify GPU Support

```bash
# Check TensorFlow GPU
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

# Check PyTorch GPU (if using)
python -c "import torch; print(torch.cuda.is_available())"

# Check CUDA availability
python -c "import tensorflow as tf; print(tf.test.is_built_with_cuda())"
```

#### Step 7: Configure for GPU

Create `config/config_gpu.yaml`:

```yaml
# NVIDIA GPU Configuration
hardware:
  platform: linux
  device: gpu
  gpu_index: 0  # Use first GPU, or [0, 1] for multiple
  cuda_memory_fraction: 0.8  # Don't use all GPU memory
  cuda_device_order: FASTEST_FIRST

# Detection model with GPU acceleration
detection:
  model_path: models/yolov8m.pt  # Larger model safe with GPU
  input_size: [640, 640]
  confidence_threshold: 0.5
  iou_threshold: 0.4
  device: gpu  # or 'cuda'
  half_precision: true  # Use FP16 for speed

# OCR ensemble
ocr:
  ensemble:
    - model: paddleocr_gpu
      weight: 0.5
    - model: easyocr_gpu
      weight: 0.5
  device: gpu

# Cameras - can handle more concurrent streams
cameras:
  - id: cam-001
    name: "Camera 1"
    rtsp_url: "rtsp://admin:password@192.168.1.100:554/stream1"
    fps: 30
    resolution: [1920, 1080]
  - id: cam-002
    name: "Camera 2"
    rtsp_url: "rtsp://admin:password@192.168.1.101:554/stream1"
    fps: 30
    resolution: [1920, 1080]

# Exporters
exporters:
  - type: rest
    url: "http://backend:8000/api/events/ingest"
    batch_size: 20
    max_retries: 5
```

#### Step 8: Run Edge Worker with GPU

```bash
cd /home/user/anprcloude/edge
source venv_gpu/bin/activate

# Monitor GPU usage in another terminal
watch -n 1 nvidia-smi

# Start the pipeline
python pipeline.py --config config/config_gpu.yaml
```

#### Step 9: Monitor GPU Performance

```bash
# Real-time GPU monitoring
nvidia-smi dmon

# GPU memory usage
nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv

# Detailed stats
nvidia-smi --query-gpu=timestamp,name,utilization.gpu,utilization.memory,memory.used,memory.free,temperature.gpu --format=csv -l 1
```

#### GPU Troubleshooting

| Issue | Solution |
|-------|----------|
| CUDA not found | Install CUDA toolkit: follow Step 2 above |
| GPU memory full | Reduce batch size or model size in config |
| Driver crash on inference | Update drivers: `sudo apt install -y nvidia-driver-550` |
| TensorFlow not detecting GPU | Reinstall: `pip install --upgrade tensorflow[and-cuda]` |
| Out of memory errors | Reduce image resolution or use smaller model variants |

---

### Option 4: Linux with CPU Only

Fallback option for systems without specialized hardware (slower but works everywhere).

#### Step 1: Set Up Python Environment

```bash
cd /home/user/anprcloude/edge

# Create virtual environment
python -m venv venv_cpu

# Activate environment
source venv_cpu/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

#### Step 2: Install CPU Dependencies

```bash
# Core dependencies
pip install numpy opencv-python

# TensorFlow (CPU-only)
pip install tensorflow-cpu

# Or PyTorch CPU
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# GStreamer bindings
pip install pygobject

# Detection models
pip install ultralytics

# OCR
pip install paddleocr pytesseract

# Communication
pip install aiohttp websockets

# System monitoring
pip install psutil

# Testing
pip install pytest pytest-asyncio
```

#### Step 3: Configure for CPU

Create `config/config_cpu.yaml`:

```yaml
# CPU-only Configuration
hardware:
  platform: linux
  device: cpu
  num_threads: 4  # Adjust based on CPU cores
  enable_mkl: true  # If available

# Use smaller model for CPU
detection:
  model_path: models/yolov8n.pt  # Nano model for CPU
  input_size: [416, 416]  # Smaller input for CPU
  confidence_threshold: 0.5
  iou_threshold: 0.4
  device: cpu

# Lightweight OCR
ocr:
  ensemble:
    - model: paddleocr_lightweight
      weight: 0.7
    - model: tesseract
      weight: 0.3
  device: cpu

# Single or few cameras due to CPU limitations
cameras:
  - id: cam-001
    name: "Main Entrance"
    rtsp_url: "rtsp://admin:password@192.168.1.100:554/stream1"
    fps: 5  # Lower FPS on CPU
    resolution: [1280, 720]  # Lower resolution

# Exporters
exporters:
  - type: rest
    url: "http://backend:8000/api/events/ingest"
    batch_size: 5
    max_retries: 3
    retry_delay: 10
```

#### Step 4: Run Edge Worker with CPU

```bash
cd /home/user/anprcloude/edge
source venv_cpu/bin/activate

# Monitor system resources
watch -n 1 'ps aux | grep pipeline'

# Start the pipeline
python pipeline.py --config config/config_cpu.yaml

# Lower priority to avoid system freeze
nice -n 10 python pipeline.py --config config/config_cpu.yaml
```

#### Step 5: Performance Optimization for CPU

```bash
# Enable CPU optimizations
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=4

python pipeline.py --config config/config_cpu.yaml
```

#### CPU Troubleshooting

| Issue | Solution |
|-------|----------|
| System freezes during processing | Reduce FPS or resolution; use `nice` to lower priority |
| High CPU temperature | Ensure proper ventilation; reduce FPS |
| Out of memory | Reduce batch size; limit concurrent cameras |
| Slow inference | Use nano models (yolov8n); reduce resolution |

---

## Docker Compose Setup

All-in-one development environment using Docker.

### Prerequisites

- **Docker**: 20.10 or higher
- **Docker Compose**: 2.0 or higher
- **4GB+ RAM**
- **20GB+ free disk space**

### Step 1: Install Docker and Docker Compose

#### Ubuntu/Debian:
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

#### macOS (using Homebrew):
```bash
brew install docker docker-compose

# Start Docker daemon
open -a Docker
```

#### Windows:
Download and install from [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Step 2: Create Docker Compose Configuration

Create `docker-compose.yml` in the project root:

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: anpr-postgres
    environment:
      POSTGRES_USER: anpr_user
      POSTGRES_PASSWORD: anpr_password_dev
      POSTGRES_DB: anpr_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U anpr_user"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - anpr-network

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: anpr-redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - anpr-network

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: anpr-backend
    environment:
      DATABASE_URL: postgresql://anpr_user:anpr_password_dev@postgres:5432/anpr_db
      REDIS_URL: redis://redis:6379/0
      JWT_SECRET: dev-secret-key-change-in-prod
      CORS_ORIGINS: '["http://localhost:3000", "http://localhost:8000"]'
      ENVIRONMENT: development
      DEBUG: "true"
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - /app/venv
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - anpr-network

  # Frontend UI
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: anpr-frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/api
      NEXT_PUBLIC_WS_URL: ws://localhost:8000/ws
      NEXT_PUBLIC_ENVIRONMENT: development
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev
    networks:
      - anpr-network

  # Optional: MinIO for S3-compatible storage
  minio:
    image: minio/minio:latest
    container_name: anpr-minio
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
    command: minio server /data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3
    networks:
      - anpr-network

networks:
  anpr-network:
    driver: bridge

volumes:
  postgres_data:
  minio_data:
```

### Step 3: Create Dockerfiles for Backend and Frontend

**Backend Dockerfile** (`backend/Dockerfile`):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile** (`frontend/Dockerfile`):

```dockerfile
FROM node:18-alpine as builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build

FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm ci --only=production

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["npm", "start"]
```

### Step 4: Start All Services

```bash
# Navigate to project root
cd /home/user/anprcloude

# Create .env file for Docker Compose
cat > .env << 'EOF'
# Backend
DATABASE_URL=postgresql://anpr_user:anpr_password_dev@postgres:5432/anpr_db
REDIS_URL=redis://redis:6379/0
JWT_SECRET=dev-secret-key-change-in-prod
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
EOF

# Build images (first time only)
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Step 5: Verify Services

```bash
# Check service status
docker-compose ps

# Test API
curl http://localhost:8000/docs

# Check frontend
curl http://localhost:3000

# Check database connection
docker-compose exec postgres psql -U anpr_user -d anpr_db -c "SELECT 1"
```

### Step 6: Database Initialization

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Or initialize directly
docker-compose exec backend python -c "from app.database import init_db; init_db()"
```

### Docker Compose Management

```bash
# Stop services
docker-compose down

# Stop and remove data (careful!)
docker-compose down -v

# Rebuild services
docker-compose build --no-cache

# View resource usage
docker stats

# Access service shell
docker-compose exec backend bash
docker-compose exec frontend sh

# View service environment variables
docker-compose exec backend env

# Run one-off command
docker-compose run --rm backend pytest
```

### Docker Troubleshooting

| Issue | Solution |
|-------|----------|
| Ports already in use | Change ports in `docker-compose.yml` or stop conflicting services |
| Out of disk space | Clean up: `docker system prune -a` |
| Service won't start | Check logs: `docker-compose logs service_name` |
| Permission denied | Add user to docker group: `sudo usermod -aG docker $USER` |
| Network connectivity issues | Check networks: `docker network ls` and `docker network inspect` |

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Backend tests passing: `pytest`
- [ ] Frontend builds successfully: `npm run build`
- [ ] Environment variables configured securely
- [ ] Database backups configured
- [ ] SSL/TLS certificates obtained
- [ ] Domain DNS configured
- [ ] Firewall rules configured
- [ ] Monitoring and logging set up
- [ ] Backup and recovery procedures documented

### Backend Production Deployment

#### Step 1: Prepare Production Environment

```bash
# On production server
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y nginx supervisor

# Create application user
sudo useradd -m -s /bin/bash anpr
sudo su - anpr
```

#### Step 2: Deploy Backend Code

```bash
# Clone repository
git clone https://github.com/your-org/anpr-engine.git
cd anpr-engine/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install production dependencies
pip install --upgrade pip setuptools
pip install -r requirements.txt
pip install gunicorn

# Create production .env (never commit this!)
cat > .env << 'EOF'
DATABASE_URL=postgresql://anpr_user:SECURE_PASSWORD@localhost:5432/anpr_db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=GENERATE_WITH_secrets.token_urlsafe(32)
CORS_ORIGINS=["https://yourdomain.com"]
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
EOF

chmod 600 .env
```

#### Step 3: Configure Gunicorn

Create `gunicorn.conf.py`:

```python
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1024
timeout = 60
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
preload_app = True
daemon = False
errorlog = "-"
accesslog = "-"
loglevel = "info"
```

#### Step 4: Configure Nginx Reverse Proxy

Create `/etc/nginx/sites-available/anpr-backend`:

```nginx
upstream anpr_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL certificates (from Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Proxy settings
    client_max_body_size 100M;
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    location / {
        proxy_pass http://anpr_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://anpr_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 86400;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/anpr-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 5: Configure Supervisor

Create `/etc/supervisor/conf.d/anpr-backend.conf`:

```ini
[program:anpr-backend]
directory=/home/anpr/anpr-engine/backend
command=/home/anpr/anpr-engine/backend/venv/bin/gunicorn -c gunicorn.conf.py app.main:app
autostart=true
autorestart=true
stderr_logfile=/var/log/anpr-backend.err.log
stdout_logfile=/var/log/anpr-backend.out.log
environment=PATH="/home/anpr/anpr-engine/backend/venv/bin",PYTHONUNBUFFERED=1
user=anpr
```

Activate:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start anpr-backend
```

#### Step 6: Set Up PostgreSQL for Production

```bash
# Create backup directory
sudo mkdir -p /var/backups/postgresql
sudo chown postgres:postgres /var/backups/postgresql

# Create automated daily backups
sudo cat > /etc/cron.daily/pg-backup << 'EOF'
#!/bin/bash
pg_dump -U anpr_user anpr_db | gzip > /var/backups/postgresql/anpr_db_$(date +\%Y\%m\%d).sql.gz
find /var/backups/postgresql -name "*.sql.gz" -mtime +30 -delete
EOF
sudo chmod +x /etc/cron.daily/pg-backup
```

#### Step 7: Configure Logging

Create `/etc/rsyslog.d/anpr-backend.conf`:

```conf
:programname, isequal, "anpr-backend" /var/log/anpr/backend.log
& stop
```

Restart rsyslog:
```bash
sudo systemctl restart rsyslog
```

### Frontend Production Deployment

#### Step 1: Build for Production

```bash
cd /home/anpr/anpr-engine/frontend

# Install dependencies
npm ci

# Build
npm run build

# Verify build
npm run build && echo "Build successful"
```

#### Step 2: Configure Nginx for Frontend

Create `/etc/nginx/sites-available/anpr-frontend`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Root location
    location / {
        root /home/anpr/anpr-engine/frontend/.next/standalone/public;
        try_files $uri $uri/ /index.html;
        expires 0;
        add_header Cache-Control "public, max-age=0, must-revalidate";
    }

    # API proxy
    location /api {
        proxy_pass https://api.yourdomain.com;
        proxy_set_header Host api.yourdomain.com;
    }
}
```

#### Step 3: Configure PM2 for Next.js (Alternative to Supervisor)

```bash
npm install -g pm2

# Start Next.js with PM2
pm2 start npm --name "anpr-frontend" -- start

# Configure auto-startup
pm2 startup
pm2 save

# Monitor
pm2 monit
```

### Edge Worker Production Deployment

#### Step 1: Deploy on Raspberry Pi / Linux

```bash
# SSH into edge device
ssh user@edge-device-ip

# Clone and setup
git clone https://github.com/your-org/anpr-engine.git
cd anpr-engine/edge

# Setup venv (choose appropriate one: venv_hailo, venv_coral, etc.)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configuration
cp config/config_template.yaml config/config.yaml
# Edit configuration with actual backend URL and credentials
nano config/config.yaml
```

#### Step 2: Configure as SystemD Service

Create `/etc/systemd/system/anpr-edge.service`:

```ini
[Unit]
Description=ANPR Edge Worker
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/anpr-engine/edge
ExecStart=/home/pi/anpr-engine/edge/venv/bin/python pipeline.py --config config/config.yaml
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Activate:
```bash
sudo systemctl daemon-reload
sudo systemctl enable anpr-edge
sudo systemctl start anpr-edge
sudo systemctl status anpr-edge

# View logs
sudo journalctl -u anpr-edge -f
```

#### Step 3: Configure Remote Monitoring

```bash
# Install monitoring agent
pip install prometheus-client

# Export metrics from edge worker
# Add to config for Prometheus scraping at http://edge-device:9090/metrics
```

### SSL/TLS with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d api.yourdomain.com -d yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Test renewal
sudo certbot renew --dry-run
```

### Monitoring and Logging

#### Set Up ELK Stack (Elasticsearch, Logstash, Kibana)

```bash
# Install Elasticsearch
sudo apt install elasticsearch

# Install Kibana
sudo apt install kibana

# Configure Elasticsearch
sudo nano /etc/elasticsearch/elasticsearch.yml

# Start services
sudo systemctl start elasticsearch
sudo systemctl start kibana
```

#### Set Up Prometheus and Grafana

```bash
# Install Prometheus
sudo useradd -m -s /bin/false prometheus
cd /tmp && wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar xvf prometheus-2.40.0.linux-amd64.tar.gz

# Install Grafana
sudo apt install software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
sudo apt install grafana-server

# Start services
sudo systemctl start prometheus
sudo systemctl start grafana-server

# Access Grafana at http://localhost:3000 (default: admin/admin)
```

---

## Troubleshooting

### Common Issues

#### Backend Issues

| Issue | Solution |
|-------|----------|
| CORS errors | Check `CORS_ORIGINS` in `.env` matches frontend domain |
| WebSocket timeout | Increase timeout in proxy: `proxy_read_timeout 86400;` |
| Database connection pool exhausted | Increase `DATABASE_POOL_SIZE` in `.env` |
| Out of memory | Reduce `max_overflow` or add more RAM |

#### Frontend Issues

| Issue | Solution |
|-------|----------|
| API calls fail with CORS error | Backend CORS not configured for frontend domain |
| WebSocket reconnects constantly | Check `NEXT_PUBLIC_WS_URL` is correct |
| Build times very long | Increase Node.js memory: `NODE_OPTIONS="--max-old-space-size=4096" npm run build` |
| Page load slow | Enable caching in Nginx, compress responses |

#### Edge Worker Issues

| Issue | Solution |
|-------|----------|
| Can't connect to backend | Check network connectivity: `ping backend_url` |
| GPU/TPU not detected | Check device connection: `lsusb` (USB) or `nvidia-smi` (NVIDIA) |
| Poor recognition accuracy | Adjust model confidence thresholds in config |
| High latency to backend | Use batching; configure retry queue |

### Getting Help

1. **Check Logs**:
   ```bash
   # Backend
   docker-compose logs -f backend

   # Frontend
   docker-compose logs -f frontend

   # Edge
   sudo journalctl -u anpr-edge -f
   ```

2. **Debug Mode**:
   ```bash
   # Backend
   DEBUG=true LOG_LEVEL=DEBUG uvicorn app.main:app --reload

   # Edge
   python pipeline.py --config config.yaml --log-level DEBUG
   ```

3. **Health Checks**:
   ```bash
   # Backend API
   curl http://localhost:8000/health

   # Database
   psql -U anpr_user -d anpr_db -c "SELECT 1"

   # Redis
   redis-cli ping
   ```

---

## Next Steps

After installation:

1. **Configure Your Cameras**:
   - Add RTSP URLs in Edge Worker config
   - Test camera connectivity

2. **Set Up Zones**:
   - Define entry/exit zones in Web UI
   - Configure actions (REST/WebSocket/MQTT)

3. **Train Custom Models** (Optional):
   - Fine-tune detection models on your scenes
   - Improve OCR with custom character sets

4. **Enable Monitoring**:
   - Set up Prometheus/Grafana
   - Configure alerting

5. **Configure Backup**:
   - Set up database replication
   - Configure S3 backup for images

---

## Additional Resources

- **Official Documentation**: [docs/](../docs/)
- **API Reference**: [docs/API.md](API.md)
- **Architecture**: [docs/ARCHITECTURE.md](ARCHITECTURE.md)
- **Deployment**: [docs/DEPLOYMENT.md](DEPLOYMENT.md)
- **FastAPI**: https://fastapi.tiangolo.com/
- **Next.js**: https://nextjs.org/docs
- **Docker**: https://docs.docker.com/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Hailo**: https://hailo.ai/developer-zone/
- **Coral TPU**: https://coral.ai/docs/
- **NVIDIA CUDA**: https://docs.nvidia.com/cuda/

---

**Last Updated**: November 2024

For questions or issues, please open an issue on GitHub or contact support.
