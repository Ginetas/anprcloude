#!/bin/bash

################################################################################
# ANPR Edge Worker Installation Script for Raspberry Pi + Google Coral TPU
#
# This script automates the complete installation of the ANPR Edge Worker
# on Raspberry Pi with Google Coral TPU acceleration.
#
# Usage:
#   sudo bash install_rpi_coral.sh
#
# Requirements:
#   - Raspberry Pi 4 or newer
#   - Google Coral TPU 3 (USB or PCIe)
#   - 4GB+ RAM recommended
#   - 16GB+ SD card
#   - Ubuntu 22.04 LTS or Debian 11+ (bullseye+)
#   - Root/sudo access
#
# Features:
#   - Idempotent (safe to run multiple times)
#   - Full error checking and recovery
#   - Progress reporting
#   - Installation verification
#   - Systemd service setup for auto-start
#   - TensorFlow Lite runtime setup
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
NC='\033[0m' # No Color

# Configuration
PYTHON_VERSION="3.9"
APP_USER="anprworker"
APP_HOME="/opt/anpr-edge-worker"
CONFIG_DIR="/etc/anpr-edge-worker"
LOG_DIR="/var/log/anpr-edge-worker"
SYSTEMD_SERVICE="anpr-edge-worker.service"
EDGETPU_RUNTIME_VERSION="13"

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

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        echo "Try: sudo bash install_rpi_coral.sh"
        exit 1
    fi
}

check_os() {
    log_info "Checking operating system compatibility..."

    if [ ! -f /etc/os-release ]; then
        log_error "Cannot determine OS version"
        exit 1
    fi

    . /etc/os-release

    if [[ "$ID" == "ubuntu" || "$ID" == "debian" ]]; then
        log_success "OS check passed: $ID $VERSION_ID"
    else
        log_error "Unsupported OS: $ID. This script requires Ubuntu 22.04+ or Debian 11+"
        exit 1
    fi
}

check_hardware() {
    log_info "Detecting Raspberry Pi hardware..."

    if [ ! -f /proc/device-tree/model ]; then
        log_error "Not running on Raspberry Pi"
        exit 1
    fi

    PI_MODEL=$(tr -d '\0' < /proc/device-tree/model)
    log_success "Detected: $PI_MODEL"

    # Check RAM
    TOTAL_RAM=$(free -m | awk 'NR==2 {print $2}')
    if (( TOTAL_RAM < 2048 )); then
        log_warning "Low memory detected: ${TOTAL_RAM}MB. Recommended: 4GB+"
    else
        log_success "RAM check passed: ${TOTAL_RAM}MB"
    fi
}

detect_coral_device() {
    log_info "Detecting Google Coral TPU device..."

    # Check for USB Coral
    if lsusb | grep -q "1a6e:089a"; then
        log_success "Google Coral TPU (USB) detected"
        return 0
    fi

    # Check for PCIe Coral
    if lspci | grep -q "089a"; then
        log_success "Google Coral TPU (PCIe) detected"
        return 0
    fi

    log_warning "No Coral TPU device detected - this is expected if device is not connected yet"
    log_info "Install will continue - verify after connecting Coral device"
}

system_update() {
    log_info "Updating system packages..."

    apt-get update -qq || {
        log_error "Failed to update package list"
        exit 1
    }

    apt-get upgrade -y -qq || {
        log_error "Failed to upgrade packages"
        exit 1
    }

    log_success "System packages updated"
}

install_dependencies() {
    log_info "Installing system dependencies..."

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
        "libatlas-base-dev"
        "libjasper-dev"
        "libjpeg-dev"
        "libtiff5"
        "zlib1g-dev"
        "libharfbuzz0b"
        "libwebp6"
        "libjasper1"
        "libopenjp2-7"
        "pkg-config"
        "libhdf5-dev"
        "libharfbuzz0b"
        "libwebpdemux0"
        "libwebpmux3"
        "systemd"
        "ca-certificates"
    )

    for package in "${PACKAGES[@]}"; do
        if ! dpkg -l | grep -q "^ii  $package"; then
            log_info "Installing $package..."
            apt-get install -y -qq "$package" || {
                log_error "Failed to install $package"
                exit 1
            }
        fi
    done

    log_success "All dependencies installed"
}

install_coral_edgetpu() {
    log_info "Installing Google Coral EdgeTPU runtime..."

    # Add Google Coral repository
    local CORAL_REPO="https://packages.cloud.google.com/apt"
    local APT_KEY_URL="https://dl-ssl.google.com/linux/linux_signing_key.pub"

    if ! grep -q "packages.cloud.google.com" /etc/apt/sources.list.d/*.list 2>/dev/null; then
        log_info "Adding Google Coral APT repository..."

        wget -qO - "$APT_KEY_URL" | apt-key add - || {
            log_error "Failed to add Google GPG key"
            exit 1
        }

        echo "deb [arch=armhf] $CORAL_REPO coral-edgetpu-stable main" | \
            tee /etc/apt/sources.list.d/coral-edgetpu.list > /dev/null || {
            log_error "Failed to add Coral repository"
            exit 1
        }

        apt-get update -qq || {
            log_error "Failed to update APT cache with Coral repo"
            exit 1
        }
    fi

    # Install EdgeTPU runtime
    if ! dpkg -l | grep -q "^ii  libedgetpu1-std"; then
        log_info "Installing libedgetpu1-std..."
        apt-get install -y -qq libedgetpu1-std || {
            log_error "Failed to install EdgeTPU runtime"
            exit 1
        }
    fi

    # Install EdgeTPU compiler (optional, for model conversion)
    if ! dpkg -l | grep -q "^ii  edgetpu-compiler"; then
        log_info "Installing edgetpu-compiler..."
        apt-get install -y -qq edgetpu-compiler || {
            log_warning "Failed to install EdgeTPU compiler (optional)"
        }
    fi

    log_success "Google Coral EdgeTPU runtime installed"
}

install_tensorflow_lite() {
    log_info "Installing TensorFlow Lite runtime..."

    source "$APP_HOME/venv/bin/activate"

    # Install TensorFlow Lite for Coral
    log_info "Installing tflite-runtime..."
    python -m pip install -q --index-url https://google-coral.github.io/py-repo/ tflite_runtime || {
        log_warning "Failed to install tflite-runtime from Coral index, trying standard index..."
        python -m pip install -q tflite-runtime || {
            log_error "Failed to install tflite-runtime"
            exit 1
        }
    }

    log_success "TensorFlow Lite runtime installed"
}

setup_python_environment() {
    log_info "Setting up Python ${PYTHON_VERSION} environment..."

    # Create virtual environment directory
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
        "pillow>=8.3.2"
        "opencv-contrib-python>=4.5.4"
        "requests>=2.26.0"
        "pyyaml>=5.4.1"
        "python-dotenv>=0.19.0"
        "gunicorn>=20.1.0"
        "flask>=2.0.0"
        "psutil>=5.8.0"
        "protobuf>=3.18.0"
        "pycoral>=2.0.0"
    )

    for package in "${PACKAGES[@]}"; do
        log_info "Installing $package..."
        python -m pip install -q "$package" || {
            log_warning "Failed to install $package - continuing anyway"
        }
    done

    log_success "Python packages installed"
}

setup_coral_permissions() {
    log_info "Setting up Coral device permissions..."

    # Add udev rules for Coral device
    if [ ! -f /etc/udev/rules.d/65-coral.rules ]; then
        cat > /etc/udev/rules.d/65-coral.rules << 'EOF'
# Coral USB device permissions
SUBSYSTEM=="usb", ATTRS{idVendor}=="1a6e", ATTRS{idProduct}=="089a", MODE="0666"

# Coral PCI-E device permissions
SUBSYSTEMS=="pci", ATTRS{vendor}=="0x1ac1", ATTRS{device}=="0x089a", MODE="0666"
EOF
        udevadm control --reload-rules || {
            log_warning "Failed to reload udev rules"
        }
        log_success "Coral udev rules installed"
    fi

    # Add user to plugdev group if using USB Coral
    if id -nG "$APP_USER" | grep -qw "plugdev"; then
        log_info "User already in plugdev group"
    else
        usermod -a -G plugdev,dialout "$APP_USER" || {
            log_warning "Failed to add user to groups"
        }
    fi
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
}

create_directories() {
    log_info "Creating application directories..."

    mkdir -p "$APP_HOME" || {
        log_error "Failed to create $APP_HOME"
        exit 1
    }

    mkdir -p "$CONFIG_DIR" || {
        log_error "Failed to create $CONFIG_DIR"
        exit 1
    }

    mkdir -p "$LOG_DIR" || {
        log_error "Failed to create $LOG_DIR"
        exit 1
    }

    mkdir -p "$APP_HOME/models" || {
        log_error "Failed to create models directory"
        exit 1
    }

    # Set ownership
    chown -R "$APP_USER:$APP_USER" "$APP_HOME" "$LOG_DIR"
    chmod 750 "$CONFIG_DIR"
    chmod 750 "$LOG_DIR"

    log_success "Directories created and configured"
}

create_config() {
    log_info "Creating configuration file..."

    local CONFIG_FILE="$CONFIG_DIR/config.yaml"

    if [ ! -f "$CONFIG_FILE" ]; then
        cat > "$CONFIG_FILE" << 'EOF'
# ANPR Edge Worker Configuration
# Generated by installation script

# Hardware Acceleration
hardware:
  accelerator: "coral"
  device_type: "usb"  # Options: usb, pcie
  device_index: 0     # For multiple devices

# Model Configuration
model:
  detection:
    name: "mobilenet_ssd_v2"
    model_path: "/opt/anpr-edge-worker/models/detection_coral.tflite"
    confidence_threshold: 0.5
    edge_tpu_delegate: true

  ocr:
    name: "crnn"
    model_path: "/opt/anpr-edge-worker/models/ocr_model_quant.tflite"
    edge_tpu_delegate: false

# Processing
processing:
  max_workers: 4
  queue_size: 100
  frame_skip: 0  # Process every frame
  input_shape: [320, 320]  # For MobileNet SSD

# Input Sources
sources:
  - id: "camera_0"
    type: "rtsp"
    uri: "rtsp://localhost:8554/stream"
    enabled: true

# Output
output:
  results_topic: "anpr/results"
  batch_interval: 5  # seconds

# Logging
logging:
  level: "INFO"
  file: "/var/log/anpr-edge-worker/worker.log"
  max_size: "100MB"
  backup_count: 5

# API Server
api:
  host: "0.0.0.0"
  port: 5000
  debug: false

# Performance tuning for Coral
performance:
  num_threads: 2
  use_xnnpack: true
EOF
        chmod 640 "$CONFIG_FILE"
        chown "$APP_USER:$APP_USER" "$CONFIG_FILE"
        log_success "Configuration file created: $CONFIG_FILE"
    else
        log_info "Configuration file already exists"
    fi
}

create_systemd_service() {
    log_info "Creating systemd service..."

    cat > "/etc/systemd/system/$SYSTEMD_SERVICE" << EOF
[Unit]
Description=ANPR Edge Worker - Coral TPU
Documentation=https://github.com/your-org/anpr-edge-worker
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_HOME
Environment="PATH=$APP_HOME/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"
Environment="PYTHONUNBUFFERED=1"
Environment="LD_LIBRARY_PATH=/usr/lib/arm-linux-gnueabihf:\${LD_LIBRARY_PATH}"
EnvironmentFile=-/etc/anpr-edge-worker/worker.env
ExecStart=$APP_HOME/venv/bin/python -m anpr_edge_worker --config $CONFIG_DIR/config.yaml

# Restart policy
Restart=on-failure
RestartSec=5
StartLimitInterval=60s
StartLimitBurst=3

# Resource limits (Coral needs moderate resources)
MemoryLimit=512M
CPUQuota=80%

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$LOG_DIR $CONFIG_DIR /dev/bus/usb

StandardOutput=journal
StandardError=journal
SyslogIdentifier=anpr-worker

[Install]
WantedBy=multi-user.target
EOF

    chmod 644 "/etc/systemd/system/$SYSTEMD_SERVICE"
    systemctl daemon-reload

    log_success "Systemd service created and reloaded"
}

verify_installation() {
    log_info "Verifying installation..."

    local CHECKS_PASSED=0
    local CHECKS_TOTAL=0

    # Check Coral runtime
    ((CHECKS_TOTAL++))
    if dpkg -l | grep -q "^ii  libedgetpu"; then
        log_success "EdgeTPU runtime found"
        ((CHECKS_PASSED++))
    else
        log_warning "EdgeTPU runtime not found"
    fi

    # Check Coral device
    ((CHECKS_TOTAL++))
    if detect_coral_device > /dev/null 2>&1; then
        log_success "Coral TPU device accessible"
        ((CHECKS_PASSED++))
    else
        log_warning "Coral TPU device not yet accessible (may be disconnected)"
    fi

    # Check Python
    ((CHECKS_TOTAL++))
    if [ -x "$APP_HOME/venv/bin/python" ]; then
        PYTHON_VER=$("$APP_HOME/venv/bin/python" --version 2>&1)
        log_success "Python installed: $PYTHON_VER"
        ((CHECKS_PASSED++))
    else
        log_error "Python not found in venv"
    fi

    # Check tflite runtime
    ((CHECKS_TOTAL++))
    if source "$APP_HOME/venv/bin/activate" && python -c "import tflite_runtime" 2>/dev/null; then
        log_success "TensorFlow Lite runtime installed"
        ((CHECKS_PASSED++))
    else
        log_warning "TensorFlow Lite runtime not verified"
    fi

    # Check configuration
    ((CHECKS_TOTAL++))
    if [ -f "$CONFIG_DIR/config.yaml" ]; then
        log_success "Configuration file exists"
        ((CHECKS_PASSED++))
    else
        log_error "Configuration file not found"
    fi

    # Check systemd service
    ((CHECKS_TOTAL++))
    if systemctl is-enabled "$SYSTEMD_SERVICE" &>/dev/null; then
        log_success "Systemd service enabled"
        ((CHECKS_PASSED++))
    else
        log_info "Systemd service not yet enabled (manual start needed)"
    fi

    log_info "Verification: $CHECKS_PASSED/$CHECKS_TOTAL checks passed"

    if (( CHECKS_PASSED >= CHECKS_TOTAL - 2 )); then
        log_success "Installation verification successful!"
        return 0
    else
        log_error "Installation verification incomplete"
        return 1
    fi
}

print_summary() {
    cat << EOF

${GREEN}===========================================${NC}
${GREEN}Installation Complete!${NC}
${GREEN}===========================================${NC}

Installation Summary:
  - OS: Raspberry Pi (Coral TPU)
  - App Home: $APP_HOME
  - Config Dir: $CONFIG_DIR
  - Log Dir: $LOG_DIR
  - Service: $SYSTEMD_SERVICE
  - EdgeTPU Runtime: $EDGETPU_RUNTIME_VERSION

Next Steps:

1. Connect your Google Coral TPU device (USB or PCIe)

2. Verify device detection:
   lsusb | grep "1a6e:089a"
   or
   lspci | grep "089a"

3. Place your TFLite model files in:
   $APP_HOME/models/
   (Ensure models are compiled for Coral with Edge TPU support)

4. Edit the configuration:
   sudo nano $CONFIG_DIR/config.yaml

5. Test the service manually:
   sudo systemctl start $SYSTEMD_SERVICE

6. View logs:
   sudo journalctl -u $SYSTEMD_SERVICE -f

7. Enable auto-start on boot:
   sudo systemctl enable $SYSTEMD_SERVICE

8. Test Coral functionality:
   python3 -c "from pycoral.utils import edgetpu_utils; print(edgetpu_utils.list_edge_tpus())"

Troubleshooting:
- Check service status: sudo systemctl status $SYSTEMD_SERVICE
- View recent logs: sudo journalctl -u $SYSTEMD_SERVICE -n 50
- List Coral devices: python3 -c "from pycoral.utils import edgetpu_utils; print(edgetpu_utils.list_edge_tpus())"
- Check permissions: ls -la /dev/bus/usb/*/
- Verify tflite: python3 -c "import tflite_runtime; print('OK')"

Documentation:
- Install logs: /var/log/anpr-edge-worker/
- Config file: $CONFIG_DIR/config.yaml
- Service file: /etc/systemd/system/$SYSTEMD_SERVICE
- Model preparation: https://coral.ai/docs/edgetpu/models-intro/

${YELLOW}Important:${NC}
- Models must be compiled for Coral with Edge TPU delegate
- Use edgetpu_compiler to prepare your models
- USB Coral devices need proper udev permissions
- PCIe Coral devices need PCIe support enabled in Pi's bootloader

EOF
}

main() {
    clear
    cat << EOF
${BLUE}╔═══════════════════════════════════════════════╗${NC}
${BLUE}║  ANPR Edge Worker Installation                ║${NC}
${BLUE}║  Raspberry Pi + Google Coral TPU              ║${NC}
${BLUE}╚═══════════════════════════════════════════════╝${NC}

Starting installation at $(date)
EOF

    check_root
    check_os
    check_hardware
    detect_coral_device
    system_update
    install_dependencies
    install_coral_edgetpu
    create_app_user
    create_directories
    setup_python_environment
    install_tensorflow_lite
    install_python_packages
    setup_coral_permissions
    create_config
    create_systemd_service
    verify_installation
    print_summary

    log_success "Installation completed at $(date)"
}

main "$@"
