# ANPR Edge Worker Dockerfile
# Multi-stage build for optimized image size

# Stage 1: Base image with system dependencies
FROM python:3.10-slim-bullseye as base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # GStreamer
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-rtsp \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gstreamer-1.0 \
    # OpenCV dependencies
    libopencv-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # Tesseract OCR
    tesseract-ocr \
    libtesseract-dev \
    # Build tools (for some Python packages)
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Builder image for Python dependencies
FROM base as builder

WORKDIR /build

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 3: Final runtime image
FROM base

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash anpr

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/anpr/.local

# Copy application code
COPY --chown=anpr:anpr . /app

# Create necessary directories
RUN mkdir -p /var/lib/anpr/images /var/lib/anpr/queue /var/lib/anpr/models \
    && chown -R anpr:anpr /var/lib/anpr

# Switch to non-root user
USER anpr

# Add local bin to PATH
ENV PATH=/home/anpr/.local/bin:$PATH
ENV PYTHONPATH=/app:$PYTHONPATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:9090/metrics', timeout=5)"

# Default command
CMD ["python", "-m", "edge.main", "--config", "/config/config.yaml"]

# Metadata
LABEL maintainer="ANPR Team <team@anpr.local>"
LABEL description="ANPR Edge Worker - License Plate Recognition System"
LABEL version="0.1.0"
