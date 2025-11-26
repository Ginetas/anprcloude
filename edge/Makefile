# ANPR Edge Worker - Makefile

.PHONY: help install dev-install test lint format clean docker-build docker-run docker-stop

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
BLACK := $(PYTHON) -m black
FLAKE8 := $(PYTHON) -m flake8
MYPY := $(PYTHON) -m mypy

# Default target
help:
	@echo "ANPR Edge Worker - Available targets:"
	@echo "  install        - Install production dependencies"
	@echo "  dev-install    - Install development dependencies"
	@echo "  test           - Run tests"
	@echo "  test-cov       - Run tests with coverage"
	@echo "  lint           - Run linting (flake8, mypy)"
	@echo "  format         - Format code (black)"
	@echo "  format-check   - Check code formatting"
	@echo "  clean          - Clean temporary files"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-run     - Run Docker container"
	@echo "  docker-stop    - Stop Docker container"
	@echo "  run            - Run edge worker locally"
	@echo "  run-debug      - Run edge worker in debug mode"

# Installation
install:
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

dev-install: install
	$(PIP) install -r requirements.txt
	$(PIP) install -e ".[dev]"

# Testing
test:
	$(PYTEST) tests/ -v

test-cov:
	$(PYTEST) tests/ -v --cov=edge --cov-report=html --cov-report=term

test-watch:
	$(PYTEST) tests/ -v --watch

# Code quality
lint:
	$(FLAKE8) edge/ tests/
	$(MYPY) edge/

format:
	$(BLACK) edge/ tests/

format-check:
	$(BLACK) --check edge/ tests/

# Cleaning
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/

# Docker
docker-build:
	docker build -t anpr-edge:latest .

docker-build-no-cache:
	docker build --no-cache -t anpr-edge:latest .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f edge-worker

docker-shell:
	docker-compose exec edge-worker /bin/bash

# Local execution
run:
	$(PYTHON) -m edge.main --config config/config.yaml

run-debug:
	$(PYTHON) -m edge.main --config config/config.yaml --log-level DEBUG

run-dry:
	$(PYTHON) -m edge.main --config config/config.yaml --dry-run

# Configuration
setup-config:
	@if [ ! -f config/config.yaml ]; then \
		cp config/config.example.yaml config/config.yaml; \
		echo "Created config/config.yaml from example"; \
	fi
	@if [ ! -f config/cameras.yaml ]; then \
		cp config/cameras.example.yaml config/cameras.yaml; \
		echo "Created config/cameras.yaml from example"; \
	fi

# System dependencies (Ubuntu/Debian)
install-system-deps:
	@echo "Installing system dependencies (requires sudo)..."
	sudo apt-get update
	sudo apt-get install -y \
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
		tesseract-ocr \
		libtesseract-dev \
		libopencv-dev

# Development workflow
dev: dev-install setup-config
	@echo "Development environment ready!"
	@echo "Run 'make run-debug' to start the edge worker"

# CI workflow
ci: format-check lint test
	@echo "CI checks passed!"
