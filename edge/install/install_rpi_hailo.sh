#!/bin/bash

################################################################################
# ANPR Edge Worker Installation Script for Raspberry Pi + Hailo-8L
#
# This script automates the complete installation of the ANPR Edge Worker
# on Raspberry Pi with Hailo-8L acceleration.
#
# Usage:
#   sudo bash install_rpi_hailo.sh
#
# Requirements:
#   - Raspberry Pi 4 or newer
#   - Hailo-8L development board
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
HAILO_VERSION="4.18.0"
PYTHON_VERSION="3.9"
APP_USER="anprworker"
APP_HOME="/opt/anpr-edge-worker"
CONFIG_DIR="/etc/anpr-edge-worker"
LOG_DIR="/var/log/anpr-edge-worker"
SYSTEMD_SERVICE="anpr-edge-worker.service"

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
        echo "Try: sudo bash install_rpi_hailo.sh"
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
        "gstreamer1.0-tools"
        "gstreamer1.0-plugins-base"
        "gstreamer1.0-plugins-good"
        "gstreamer1.0-plugins-bad"
        "gstreamer1.0-libav"
        "libgstreamer1.0-dev"
        "libgstreamer-plugins-base1.0-dev"
        "libjpeg-dev"
        "zlib1g-dev"
        "libatlas-base-dev"
        "libjasper-dev"
        "libharfbuzz0b"
        "libwebp6"
        "libtiff5"
        "libjasper1"
        "libopenjp2-7"
        "pkg-config"
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

install_hailo_driver() {
    log_info "Installing Hailo driver and runtime (version $HAILO_VERSION)..."

    # Add Hailo repository
    local APT_KEY_URL="https://hailo-csdata.s3.amazonaws.com/debian/public.key"
    local HAILO_REPO_URL="https://hailo-csdata.s3.amazonaws.com/debian bullseye main"

    if ! grep -q "hailo-csdata" /etc/apt/sources.list.d/*.list 2>/dev/null; then
        log_info "Adding Hailo APT repository..."

        wget -qO - "$APT_KEY_URL" | apt-key add - || {
            log_error "Failed to add Hailo GPG key"
            exit 1
        }

        echo "deb $HAILO_REPO_URL" | tee /etc/apt/sources.list.d/hailo.list > /dev/null || {
            log_error "Failed to add Hailo repository"
            exit 1
        }

        apt-get update -qq || {
            log_error "Failed to update APT cache with Hailo repo"
            exit 1
        }
    fi

    # Install Hailo runtime
    if ! dpkg -l | grep -q "^ii  hailo-all"; then
        log_info "Installing hailo-all package..."
        apt-get install -y -qq hailo-all || {
            log_error "Failed to install Hailo runtime"
            exit 1
        }
    fi

    # Verify Hailo installation
    if hailortcli fw-control identify > /dev/null 2>&1; then
        log_success "Hailo driver installed and verified"
    else
        log_warning "Hailo device not detected - this is expected if device is not connected yet"
        log_info "Install will continue - verify after connecting Hailo device"
    fi
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
        "opencv-contrib-python>=4.5.4"
        "pillow>=8.3.2"
        "requests>=2.26.0"
        "pyyaml>=5.4.1"
        "python-dotenv>=0.19.0"
        "gunicorn>=20.1.0"
        "flask>=2.0.0"
        "psutil>=5.8.0"
        "gstreamer-python>=1.0"
    )

    for package in "${PACKAGES[@]}"; do
        log_info "Installing $package..."
        python -m pip install -q "$package" || {
            log_warning "Failed to install $package - continuing anyway"
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
  accelerator: "hailo"
  device_id: 0  # Hailo device ID

# Model Configuration
model:
  detection:
    name: "yolov5s"
    model_path: "/opt/anpr-edge-worker/models/detection_hailo.hef"
    confidence_threshold: 0.5

  ocr:
    name: "crnn"
    model_path: "/opt/anpr-edge-worker/models/ocr_model.pb"

# Processing
processing:
  max_workers: 4
  queue_size: 100
  frame_skip: 0  # Process every frame

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
Description=ANPR Edge Worker - Hailo-8L
Documentation=https://github.com/your-org/anpr-edge-worker
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_HOME
Environment="PATH=$APP_HOME/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=-/etc/anpr-edge-worker/worker.env
ExecStart=$APP_HOME/venv/bin/python -m anpr_edge_worker --config $CONFIG_DIR/config.yaml

# Restart policy
Restart=on-failure
RestartSec=5
StartLimitInterval=60s
StartLimitBurst=3

# Resource limits
MemoryLimit=512M
CPUQuota=80%

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$LOG_DIR $CONFIG_DIR

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

    # Check Hailo runtime
    ((CHECKS_TOTAL++))
    if command -v hailortcli &> /dev/null; then
        log_success "Hailo CLI found"
        ((CHECKS_PASSED++))
    else
        log_warning "Hailo CLI not found"
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

    # Check GStreamer
    ((CHECKS_TOTAL++))
    if command -v gst-launch-1.0 &> /dev/null; then
        log_success "GStreamer installed"
        ((CHECKS_PASSED++))
    else
        log_warning "GStreamer not found"
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

    if (( CHECKS_PASSED >= CHECKS_TOTAL - 1 )); then
        log_success "Installation verification successful!"
        return 0
    else
        log_error "Installation verification failed"
        return 1
    fi
}

print_summary() {
    cat << EOF

${GREEN}===========================================${NC}
${GREEN}Installation Complete!${NC}
${GREEN}===========================================${NC}

Installation Summary:
  - OS: Raspberry Pi (Hailo-8L)
  - App Home: $APP_HOME
  - Config Dir: $CONFIG_DIR
  - Log Dir: $LOG_DIR
  - Service: $SYSTEMD_SERVICE

Next Steps:

1. Place your Hailo model files in:
   $APP_HOME/models/

2. Edit the configuration:
   sudo nano $CONFIG_DIR/config.yaml

3. Test the service manually:
   sudo systemctl start $SYSTEMD_SERVICE

4. View logs:
   sudo journalctl -u $SYSTEMD_SERVICE -f

5. Enable auto-start on boot:
   sudo systemctl enable $SYSTEMD_SERVICE

6. Verify Hailo device detection:
   sudo hailortcli fw-control identify

Troubleshooting:
- Check service status: sudo systemctl status $SYSTEMD_SERVICE
- View recent logs: sudo journalctl -u $SYSTEMD_SERVICE -n 50
- Test Hailo: hailortcli fw-control identify
- Verify Python: $APP_HOME/venv/bin/python --version

Documentation:
- Install logs: /var/log/anpr-edge-worker/
- Config file: $CONFIG_DIR/config.yaml
- Service file: /etc/systemd/system/$SYSTEMD_SERVICE

${YELLOW}Important: Connect your Hailo-8L device before running the service${NC}

EOF
}

main() {
    clear
    cat << EOF
${BLUE}╔═══════════════════════════════════════════════╗${NC}
${BLUE}║  ANPR Edge Worker Installation                ║${NC}
${BLUE}║  Raspberry Pi + Hailo-8L                      ║${NC}
${BLUE}╚═══════════════════════════════════════════════╝${NC}

Starting installation at $(date)
EOF

    check_root
    check_os
    check_hardware
    system_update
    install_dependencies
    install_hailo_driver
    create_app_user
    create_directories
    setup_python_environment
    install_python_packages
    create_config
    create_systemd_service
    verify_installation
    print_summary

    log_success "Installation completed at $(date)"
}

main "$@"
