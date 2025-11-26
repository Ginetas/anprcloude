# Makefile for ANPR Backend

.PHONY: help install dev test lint format clean docker-build docker-up docker-down migrate

# Default target
help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make dev          - Run development server"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean temporary files"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make migrate      - Run database migrations"

# Install dependencies
install:
	pip install --upgrade pip
	pip install -r requirements.txt

# Run development server
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	pytest -v

# Run tests with coverage
test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

# Run linters
lint:
	flake8 app/
	mypy app/

# Format code
format:
	black app/ tests/
	isort app/ tests/

# Type checking
type-check:
	mypy app/

# Clean temporary files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf dist/
	rm -rf build/

# Docker commands
docker-build:
	docker build -t anpr-backend:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f backend

docker-rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

# Database migrations
migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(message)"

migrate-down:
	alembic downgrade -1

migrate-history:
	alembic history --verbose

# Database commands
db-shell:
	psql -h localhost -U anpr -d anpr_db

db-create:
	createdb -h localhost -U anpr anpr_db

db-drop:
	dropdb -h localhost -U anpr anpr_db

db-reset: db-drop db-create migrate

# Redis commands
redis-cli:
	redis-cli -h localhost -p 6379

redis-flush:
	redis-cli -h localhost -p 6379 FLUSHALL

# Development utilities
shell:
	python -c "from app.database import *; from app.models import *; import asyncio"

# Production commands
prod:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Check code quality
quality: format lint test

# Full reset (dangerous - use with caution)
reset: clean docker-down
	rm -rf uploads/
	rm -rf alembic/versions/*.py
	git checkout alembic/versions/.gitkeep
