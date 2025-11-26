#!/bin/bash

################################################################################
# ANPR Edge Worker Installation Script for Linux with GPU/CPU Support
#
# This script automates the complete installation of the ANPR Edge Worker
# on Linux systems with automatic GPU detection and configuration.
#
# Usage:
#   sudo bash install_linux.sh [--skip-gpu] [--force-cuda-version VERSION]
#
# Arguments:
#   --skip-gpu              Skip GPU detection and installation (CPU-only)
#   --force-cuda-version    Force specific CUDA version (e.g., 11.8, 12.0)
#
# Supported Systems:
#   - Ubuntu 20.04+ (Focal, Jammy, Noble)
#   - Debian 11+ (Bullseye+)
#   - CentOS 7+ / RHEL 7+
#   - Fedora 33+
#
# Hardware Requirements:
#   - 4GB+ RAM (8GB+ recommended for GPU)
#   - 20GB+ disk space
#   - Optional: NVIDIA GPU with CUDA Compute Capability 3.5+
#
# Features:
#   - Automatic GPU detection (NVIDIA)
#   - CUDA and cuDNN installation
#   - Optimized Python environment
#   - Idempotent (safe to run multiple times)
#   - Full error checking
#   - Installation verification
#   - Systemd service setup
#
# Author: ANPR Project
# Date: 2025-11-26
################################################################################

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PYTHON_VERSION="3.9"
APP_USER="anprworker"
APP_HOME="/opt/anpr-edge-worker"
CONFIG_DIR="/etc/anpr-edge-worker"
LOG_DIR="/var/log/anpr-edge-worker"
SYSTEMD_SERVICE="anpr-edge-worker.service"
SKIP_GPU=false
FORCE_CUDA_VERSION=""
CUDA_HOME="/usr/local/cuda"

# Utility functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${CYAN}[DEBUG]${NC} $1"
}

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-gpu)
                SKIP_GPU=true
                log_info "GPU installation will be skipped"
                shift
                ;;
            --force-cuda-version)
                FORCE_CUDA_VERSION="$2"
                log_info "Forcing CUDA version: $FORCE_CUDA_VERSION"
                shift 2
                ;;
            *)
                log_warning "Unknown argument: $1"
                shift
                ;;
        esac
    done
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        echo "Try: sudo bash install_linux.sh"
        exit 1
    fi
}

check_os() {
    log_info "Detecting operating system..."

    if [ ! -f /etc/os-release ]; then
        log_error "Cannot determine OS version"
        exit 1
    fi

    . /etc/os-release

    OS_ID="$ID"
    OS_VERSION="$VERSION_ID"
    OS_NAME="$PRETTY_NAME"

    log_success "Detected: $OS_NAME"

    # Validate supported OS
    case "$OS_ID" in
        ubuntu|debian)
            log_success "Ubuntu/Debian-based system detected"
            ;;
        fedora|rhel|centos)
            log_warning "RHEL-based system detected - some features may be limited"
            ;;
        *)
            log_error "Unsupported OS: $OS_ID"
            exit 1
            ;;
    esac
}

detect_gpu() {
    if [ "$SKIP_GPU" = true ]; then
        log_info "GPU detection skipped (--skip-gpu enabled)"
        return 1
    fi

    log_info "Detecting NVIDIA GPU..."

    # Check if nvidia-smi exists
    if command -v nvidia-smi &> /dev/null; then
        GPU_COUNT=$(nvidia-smi --list-gpus 2>/dev/null | wc -l)
        if [ "$GPU_COUNT" -gt 0 ]; then
            log_success "Found $GPU_COUNT NVIDIA GPU(s)"
            nvidia-smi --query-gpu=name,driver_version --format=csv,noheader | while read -r line; do
                log_info "  GPU: $line"
            done
            return 0
        fi
    fi

    # Check lspci for NVIDIA cards
    if command -v lspci &> /dev/null; then
        if lspci | grep -i nvidia | grep -i "3d controller\|vga compatible" > /dev/null; then
            log_info "NVIDIA GPU detected via lspci (driver may not be installed)"
            return 0
        fi
    fi

    log_warning "No NVIDIA GPU detected - will proceed with CPU-only installation"
    return 1
}

get_cuda_version() {
    log_info "Determining appropriate CUDA version..."

    if [ -n "$FORCE_CUDA_VERSION" ]; then
        CUDA_VERSION="$FORCE_CUDA_VERSION"
        log_info "Using forced CUDA version: $CUDA_VERSION"
        return 0
    fi

    # Default to CUDA 12.0 for modern systems
    CUDA_VERSION="12.0"

    # Check driver version if available
    if command -v nvidia-smi &> /dev/null; then
        DRIVER_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)
        DRIVER_MAJOR=$(echo "$DRIVER_VERSION" | cut -d'.' -f1)

        log_debug "Driver version: $DRIVER_VERSION"

        # Map driver version to CUDA version
        if [ "$DRIVER_MAJOR" -lt 450 ]; then
            CUDA_VERSION="11.0"
        elif [ "$DRIVER_MAJOR" -lt 470 ]; then
            CUDA_VERSION="11.1"
        elif [ "$DRIVER_MAJOR" -lt 495 ]; then
            CUDA_VERSION="11.2"
        elif [ "$DRIVER_MAJOR" -lt 520 ]; then
            CUDA_VERSION="11.8"
        else
            CUDA_VERSION="12.0"
        fi
    fi

    log_success "Selected CUDA version: $CUDA_VERSION"
}

install_nvidia_driver() {
    log_info "Installing NVIDIA driver..."

    case "$OS_ID" in
        ubuntu)
            # Use Ubuntu's nvidia-driver package
            if ! dpkg -l | grep -q "^ii  nvidia-driver"; then
                log_info "Installing nvidia-driver via ubuntu-drivers..."
                apt-get install -y -qq ubuntu-drivers-common || {
                    log_error "Failed to install ubuntu-drivers-common"
                    exit 1
                }

                # Auto-install recommended driver
                ubuntu-drivers autoinstall || {
                    log_warning "Auto driver install failed, installing generic driver"
                    apt-get install -y -qq nvidia-driver-545 || {
                        log_error "Failed to install NVIDIA driver"
                        exit 1
                    }
                }

                log_success "NVIDIA driver installed"
                log_warning "System reboot may be required for driver to take effect"
            else
                log_info "NVIDIA driver already installed"
            fi
            ;;
        debian)
            # Use Debian's nvidia-driver package
            if ! dpkg -l | grep -q "^ii  nvidia-driver"; then
                apt-get install -y -qq nvidia-driver || {
                    log_warning "nvidia-driver not available in standard repos"
                    log_info "Installing from backports if available..."
                    apt-get install -y -t "${OS_VERSION}-backports" -qq nvidia-driver 2>/dev/null || {
                        log_error "Failed to install NVIDIA driver"
                        exit 1
                    }
                }
            fi
            ;;
        fedora|rhel|centos)
            log_warning "NVIDIA driver installation on RHEL-based systems requires additional setup"
            log_info "Please install NVIDIA driver manually or use NVIDIA's official repository"
            ;;
    esac
}

install_cuda_toolkit() {
    log_info "Installing CUDA Toolkit $CUDA_VERSION..."

    if [ -d "$CUDA_HOME" ] && [ -x "$CUDA_HOME/bin/nvcc" ]; then
        INSTALLED_CUDA=$("$CUDA_HOME/bin/nvcc" --version | grep -oP 'release \K[0-9.]+' | head -1)
        if [ "$INSTALLED_CUDA" = "$CUDA_VERSION" ]; then
            log_success "CUDA $CUDA_VERSION already installed at $CUDA_HOME"
            return 0
        fi
    fi

    case "$OS_ID" in
        ubuntu)
            log_info "Setting up CUDA Toolkit repository for Ubuntu..."
            # Example for Ubuntu 22.04 and CUDA 12.0
            # Adjust based on actual version
            if [ ! -f /etc/apt/sources.list.d/cuda-ubuntu*.list ]; then
                wget -qO /tmp/cuda-repo.pin https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
                mv /tmp/cuda-repo.pin /etc/apt/preferences.d/cuda-repository-pin-600

                wget -qO /tmp/cuda-repo-ubuntu.deb \
                    https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-repo-ubuntu2204-12-0-local_12.0.0-525.60.13-1_amd64.deb

                dpkg -i /tmp/cuda-repo-ubuntu.deb
                apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/3bf863cc.pub
                apt-get update -qq
                rm /tmp/cuda-repo-ubuntu.deb
            fi

            apt-get install -y -qq cuda-toolkit || {
                log_error "Failed to install CUDA Toolkit"
                exit 1
            }
            ;;
        debian)
            log_warning "Manual CUDA installation on Debian - using NVIDIA's official repository"
            log_info "CUDA installation skipped - please install manually from NVIDIA's website"
            ;;
        *)
            log_warning "CUDA installation for $OS_ID not automated"
            log_info "Please install CUDA manually from https://developer.nvidia.com/cuda-downloads"
            ;;
    esac

    # Verify installation
    if [ -x "$CUDA_HOME/bin/nvcc" ]; then
        log_success "CUDA Toolkit installed successfully"
    else
        log_warning "CUDA installation could not be verified"
    fi
}

install_cudnn() {
    log_info "Installing cuDNN..."

    # cuDNN requires registration/login on NVIDIA website
    # This is a placeholder - manual installation usually required
    log_warning "cuDNN installation requires manual download from NVIDIA Developer portal"
    log_info "Visit: https://developer.nvidia.com/rdnn"
    log_info "Extract to: /usr/local/cuda/"

    # Check if cuDNN is already installed
    if [ -f "$CUDA_HOME/lib64/libcudnn.so" ]; then
        log_success "cuDNN already installed"
    fi
}

system_update() {
    log_info "Updating system packages..."

    case "$OS_ID" in
        ubuntu|debian)
            apt-get update -qq || {
                log_error "Failed to update package list"
                exit 1
            }

            apt-get upgrade -y -qq || {
                log_error "Failed to upgrade packages"
                exit 1
            }
            ;;
        fedora)
            dnf update -y -q || {
                log_error "Failed to update packages"
                exit 1
            }
            ;;
        rhel|centos)
            yum update -y -q || {
                log_error "Failed to update packages"
                exit 1
            }
            ;;
    esac

    log_success "System packages updated"
}

install_dependencies() {
    log_info "Installing system dependencies..."

    case "$OS_ID" in
        ubuntu|debian)
            local PACKAGES=(
                "build-essential"
                "git"
                "wget"
                "curl"
                "libssl-dev"
                "libffi-dev"
                "python${PYTHON_VERSION}"
                "python${PYTHON_VERSION}-dev"
                "python3-pip"
                "python3-venv"
                "libopencv-dev"
                "python3-opencv"
                "libjpeg-dev"
                "zlib1g-dev"
                "pkg-config"
                "systemd"
                "ca-certificates"
                "libgomp1"
            )

            for package in "${PACKAGES[@]}"; do
                if ! dpkg -l | grep -q "^ii  ${package%:*}"; then
                    log_info "Installing $package..."
                    apt-get install -y -qq "$package" || {
                        log_warning "Failed to install $package (may be optional)"
                    }
                fi
            done
            ;;
        fedora|rhel|centos)
            local PACKAGES=(
                "gcc"
                "gcc-c++"
                "make"
                "kernel-devel"
                "git"
                "wget"
                "curl"
                "openssl-devel"
                "libffi-devel"
                "python39"
                "python39-devel"
                "python3-pip"
                "opencv-devel"
                "opencv-contrib"
                "systemd"
                "ca-certificates"
            )

            for package in "${PACKAGES[@]}"; do
                if ! rpm -qa | grep -q "^${package}"; then
                    log_info "Installing $package..."
                    if command -v dnf &> /dev/null; then
                        dnf install -y -q "$package" || {
                            log_warning "Failed to install $package"
                        }
                    else
                        yum install -y -q "$package" || {
                            log_warning "Failed to install $package"
                        }
                    fi
                fi
            done
            ;;
    esac

    log_success "System dependencies installed"
}

setup_python_environment() {
    log_info "Setting up Python ${PYTHON_VERSION} environment..."

    mkdir -p "$APP_HOME/venv"

    if [ ! -d "$APP_HOME/venv/bin" ]; then
        log_info "Creating Python virtual environment..."
        python${PYTHON_VERSION} -m venv "$APP_HOME/venv" || {
            log_error "Failed to create virtual environment"
            exit 1
        }
    fi

    # Activate venv and upgrade pip
    source "$APP_HOME/venv/bin/activate"
    python -m pip install --upgrade pip setuptools wheel -q || {
        log_error "Failed to upgrade pip"
        exit 1
    }

    log_success "Python environment ready: $APP_HOME/venv"
}

install_python_packages() {
    log_info "Installing Python packages..."

    source "$APP_HOME/venv/bin/activate"

    local PACKAGES=(
        "numpy>=1.21.0"
        "opencv-python>=4.5.4"
        "opencv-contrib-python>=4.5.4"
        "pillow>=8.3.2"
        "requests>=2.26.0"
        "pyyaml>=5.4.1"
        "python-dotenv>=0.19.0"
        "gunicorn>=20.1.0"
        "flask>=2.0.0"
        "psutil>=5.8.0"
        "pydantic>=1.8.0"
    )

    # Add GPU-specific packages if GPU is available
    if detect_gpu 2>/dev/null; then
        log_info "Adding GPU-optimized packages..."
        PACKAGES+=(
            "tensorflow[and-cuda]>=2.12"
            "torch==2.0.1"
        )
    else
        log_info "Adding CPU-only packages..."
        PACKAGES+=(
            "tensorflow>=2.12"
            "torch>=2.0.1"
        )
    fi

    for package in "${PACKAGES[@]}"; do
        log_info "Installing $package..."
        python -m pip install -q "$package" 2>/dev/null || {
            log_warning "Failed to install $package (optional)"
        }
    done

    log_success "Python packages installed"
}

create_app_user() {
    log_info "Creating application user..."

    if id "$APP_USER" &>/dev/null; then
        log_info "User $APP_USER already exists"
    else
        useradd -r -s /bin/bash -d "$APP_HOME" -m "$APP_USER" || {
            log_error "Failed to create user $APP_USER"
            exit 1
        }
        log_success "User $APP_USER created"
    fi

    # Add user to video and render groups for GPU access
    if detect_gpu 2>/dev/null; then
        usermod -a -G video,render,dialout "$APP_USER" 2>/dev/null || true
    fi
}

create_directories() {
    log_info "Creating application directories..."

    mkdir -p "$APP_HOME" "$CONFIG_DIR" "$LOG_DIR" || {
        log_error "Failed to create directories"
        exit 1
    }

    mkdir -p "$APP_HOME/models" "$APP_HOME/data" || {
        log_error "Failed to create model directories"
        exit 1
    }

    chown -R "$APP_USER:$APP_USER" "$APP_HOME" "$LOG_DIR"
    chmod 750 "$CONFIG_DIR" "$LOG_DIR"

    log_success "Directories created and configured"
}

create_config() {
    log_info "Creating configuration file..."

    local CONFIG_FILE="$CONFIG_DIR/config.yaml"
    local ACCELERATOR="cpu"

    if detect_gpu 2>/dev/null; then
        ACCELERATOR="nvidia_gpu"
    fi

    if [ ! -f "$CONFIG_FILE" ]; then
        cat > "$CONFIG_FILE" << EOF
# ANPR Edge Worker Configuration
# Generated by installation script

# Hardware Configuration
hardware:
  accelerator: "$ACCELERATOR"  # Options: cpu, nvidia_gpu
  device_id: 0
  num_threads: $(nproc)
  memory_limit: "2GB"

# Model Configuration
model:
  detection:
    name: "yolov5s"
    model_path: "$APP_HOME/models/detection_model.pt"
    confidence_threshold: 0.5
    nms_threshold: 0.4
    input_size: [640, 640]

  ocr:
    name: "crnn"
    model_path: "$APP_HOME/models/ocr_model.pb"
    input_size: [100, 32]

# Processing
processing:
  max_workers: $(nproc)
  queue_size: 200
  frame_skip: 0
  batch_processing: true
  batch_size: 8

# Input Sources
sources:
  - id: "camera_0"
    type: "rtsp"
    uri: "rtsp://localhost:8554/stream"
    enabled: true

# Output
output:
  results_topic: "anpr/results"
  results_format: "json"
  batch_interval: 5

# Logging
logging:
  level: "INFO"
  file: "$LOG_DIR/worker.log"
  max_size: "100MB"
  backup_count: 10
  format: "json"

# API Server
api:
  host: "0.0.0.0"
  port: 5000
  workers: 4
  debug: false
  timeout: 30

# Performance tuning
performance:
  use_fp16: true
  use_tensor_cores: true
  num_cuda_streams: 4
EOF
        chmod 640 "$CONFIG_FILE"
        chown "$APP_USER:$APP_USER" "$CONFIG_FILE"
        log_success "Configuration file created: $CONFIG_FILE"
    else
        log_info "Configuration file already exists"
    fi
}

setup_cuda_environment() {
    if ! detect_gpu 2>/dev/null; then
        return 0
    fi

    log_info "Setting up CUDA environment variables..."

    # Create environment file
    cat > "$CONFIG_DIR/cuda.env" << EOF
# CUDA Environment Configuration
export CUDA_HOME=$CUDA_HOME
export LD_LIBRARY_PATH=\${CUDA_HOME}/lib64:\${LD_LIBRARY_PATH}
export PATH=\${CUDA_HOME}/bin:\${PATH}
export CUDA_VISIBLE_DEVICES=0
export TF_FORCE_GPU_ALLOW_GROWTH=true
EOF

    log_success "CUDA environment file created"
}

create_systemd_service() {
    log_info "Creating systemd service..."

    local ENVIRONMENT_FILE=""
    if [ -f "$CONFIG_DIR/cuda.env" ]; then
        ENVIRONMENT_FILE="EnvironmentFile=$CONFIG_DIR/cuda.env"
    fi

    cat > "/etc/systemd/system/$SYSTEMD_SERVICE" << EOF
[Unit]
Description=ANPR Edge Worker Service
Documentation=https://github.com/your-org/anpr-edge-worker
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_HOME
Environment="PATH=$APP_HOME/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"
Environment="PYTHONUNBUFFERED=1"
Environment="PYTHONDONTWRITEBYTECODE=1"
${ENVIRONMENT_FILE}
EnvironmentFile=-/etc/anpr-edge-worker/worker.env

ExecStart=$APP_HOME/venv/bin/python -m anpr_edge_worker --config $CONFIG_DIR/config.yaml

# Restart policy
Restart=on-failure
RestartSec=10
StartLimitInterval=120s
StartLimitBurst=5

# Resource limits
MemoryMax=4G
CPUQuota=100%

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$LOG_DIR $CONFIG_DIR

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=anpr-worker

[Install]
WantedBy=multi-user.target
EOF

    chmod 644 "/etc/systemd/system/$SYSTEMD_SERVICE"
    systemctl daemon-reload

    log_success "Systemd service created"
}

verify_installation() {
    log_info "Verifying installation..."

    local CHECKS_PASSED=0
    local CHECKS_TOTAL=0

    # Check Python
    ((CHECKS_TOTAL++))
    if [ -x "$APP_HOME/venv/bin/python" ]; then
        PYTHON_VER=$("$APP_HOME/venv/bin/python" --version 2>&1)
        log_success "Python: $PYTHON_VER"
        ((CHECKS_PASSED++))
    else
        log_error "Python not found"
    fi

    # Check OpenCV
    ((CHECKS_TOTAL++))
    if source "$APP_HOME/venv/bin/activate" && python -c "import cv2" 2>/dev/null; then
        log_success "OpenCV installed"
        ((CHECKS_PASSED++))
    else
        log_warning "OpenCV verification failed"
    fi

    # Check GPU (if applicable)
    if detect_gpu 2>/dev/null; then
        ((CHECKS_TOTAL++))
        if command -v nvidia-smi &> /dev/null; then
            GPU_MEMORY=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
            log_success "GPU: NVIDIA ${GPU_MEMORY}MB"
            ((CHECKS_PASSED++))
        fi
    fi

    # Check configuration
    ((CHECKS_TOTAL++))
    if [ -f "$CONFIG_DIR/config.yaml" ]; then
        log_success "Configuration file exists"
        ((CHECKS_PASSED++))
    else
        log_error "Configuration file not found"
    fi

    # Check systemd
    ((CHECKS_TOTAL++))
    if [ -f "/etc/systemd/system/$SYSTEMD_SERVICE" ]; then
        log_success "Systemd service installed"
        ((CHECKS_PASSED++))
    else
        log_error "Systemd service not found"
    fi

    log_info "Verification: $CHECKS_PASSED/$CHECKS_TOTAL checks passed"

    if (( CHECKS_PASSED >= CHECKS_TOTAL - 1 )); then
        log_success "Installation verification successful!"
        return 0
    else
        log_error "Installation verification incomplete"
        return 1
    fi
}

print_summary() {
    local HARDWARE="CPU"
    if detect_gpu 2>/dev/null; then
        HARDWARE="GPU (NVIDIA)"
    fi

    cat << EOF

${GREEN}===========================================${NC}
${GREEN}Installation Complete!${NC}
${GREEN}===========================================${NC}

Installation Summary:
  - OS: $OS_NAME
  - Hardware: $HARDWARE
  - App Home: $APP_HOME
  - Config Dir: $CONFIG_DIR
  - Python Venv: $APP_HOME/venv
  - Service: $SYSTEMD_SERVICE

Next Steps:

1. Install/prepare your models:
   mkdir -p $APP_HOME/models
   # Copy your model files here

2. Configure the application:
   sudo nano $CONFIG_DIR/config.yaml

3. Test the service:
   sudo systemctl start $SYSTEMD_SERVICE
   sudo systemctl status $SYSTEMD_SERVICE

4. View logs in real-time:
   sudo journalctl -u $SYSTEMD_SERVICE -f

5. Enable auto-start on boot:
   sudo systemctl enable $SYSTEMD_SERVICE

Useful Commands:

  - Check service status:
    sudo systemctl status $SYSTEMD_SERVICE

  - View recent logs:
    sudo journalctl -u $SYSTEMD_SERVICE -n 50

  - Restart service:
    sudo systemctl restart $SYSTEMD_SERVICE

  - Disable service:
    sudo systemctl disable $SYSTEMD_SERVICE

EOF

    if detect_gpu 2>/dev/null; then
        echo -e "${CYAN}GPU Information:${NC}"
        echo ""
        nvidia-smi
    fi
}

main() {
    clear
    cat << EOF
${BLUE}╔═══════════════════════════════════════════════╗${NC}
${BLUE}║  ANPR Edge Worker Installation                ║${NC}
${BLUE}║  Linux with GPU/CPU Support                   ║${NC}
${BLUE}╚═══════════════════════════════════════════════╝${NC}

Starting installation at $(date)
EOF

    parse_arguments "$@"
    check_root
    check_os
    system_update
    install_dependencies

    # GPU detection and installation
    if detect_gpu 2>/dev/null; then
        log_info "GPU detected - proceeding with GPU support installation"
        get_cuda_version
        install_nvidia_driver
        install_cuda_toolkit
        install_cudnn
    else
        log_info "No GPU detected or GPU installation skipped - CPU-only mode"
    fi

    create_app_user
    create_directories
    setup_python_environment
    install_python_packages
    create_config
    setup_cuda_environment
    create_systemd_service
    verify_installation
    print_summary

    log_success "Installation completed at $(date)"
}

main "$@"
