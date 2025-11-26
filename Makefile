.PHONY: help setup dev prod test clean logs db-migrate db-backup db-restore \
        build build-backend build-frontend build-edge push-images pull-images \
        lint format type-check security-check docs health status \
        install-dev install-prod backend-shell frontend-shell db-shell \
        migrations migrate-up migrate-down migrate-fresh

.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Environment detection
ENVIRONMENT ?= development
ENV_FILE := .env

# Docker Compose flags
DC := docker-compose
DC_PROD := docker-compose -f docker-compose.yml -f docker-compose.prod.yml
DC_DEV := docker-compose -f docker-compose.yml

# Check if .env exists
ifeq (,$(wildcard $(ENV_FILE)))
    $(info $(YELLOW)Warning: .env file not found. Run 'make setup' to create it.$(NC))
endif

help: ## Show this help message
	@echo "$(BLUE)ANPR License Plate Recognition System - Make Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Setup & Installation:$(NC)"
	@grep -E '^\s*[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		grep -E "(setup|install|build)" | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@grep -E '^\s*[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		grep -E "(dev|shell|lint|format|test)" | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Production:$(NC)"
	@grep -E '^\s*[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		grep -E "(prod|migrate|backup|restore)" | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Monitoring & Status:$(NC)"
	@grep -E '^\s*[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		grep -E "(logs|status|health|docs)" | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Cleanup:$(NC)"
	@grep -E '^\s*[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		grep -E "clean" | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'

# ==============================================================================
# SETUP & INSTALLATION
# ==============================================================================

setup: ## Initial project setup - create .env from example and install dependencies
	@echo "$(GREEN)Setting up ANPR project...$(NC)"
	@if [ ! -f $(ENV_FILE) ]; then \
		echo "$(YELLOW)Creating $(ENV_FILE) from .env.example$(NC)"; \
		cp .env.example $(ENV_FILE); \
		echo "$(YELLOW)Please update $(ENV_FILE) with your configuration$(NC)"; \
	else \
		echo "$(BLUE)$(ENV_FILE) already exists$(NC)"; \
	fi
	@bash ./scripts/setup-dev.sh

install-dev: ## Install development dependencies
	@echo "$(GREEN)Installing development dependencies...$(NC)"
	@cd backend && pip install -r requirements.txt -r requirements-dev.txt
	@cd ../edge && pip install -r requirements.txt
	@cd ../frontend && npm install

install-prod: ## Install production dependencies
	@echo "$(GREEN)Installing production dependencies...$(NC)"
	@cd backend && pip install -r requirements.txt
	@cd ../edge && pip install -r requirements.txt
	@cd ../frontend && npm ci

build: build-backend build-frontend build-edge ## Build all Docker images

build-backend: ## Build backend Docker image
	@echo "$(GREEN)Building backend Docker image...$(NC)"
	@$(DC) build backend

build-frontend: ## Build frontend Docker image
	@echo "$(GREEN)Building frontend Docker image...$(NC)"
	@$(DC) build frontend

build-edge: ## Build edge worker Docker image
	@echo "$(GREEN)Building edge worker Docker image...$(NC)"
	@$(DC) build edge

# ==============================================================================
# DEVELOPMENT
# ==============================================================================

dev: ## Start development environment with all services
	@echo "$(GREEN)Starting development environment...$(NC)"
	@$(DC_DEV) up -d
	@echo "$(GREEN)Services starting, checking health...$(NC)"
	@sleep 5
	@make health

dev-build: ## Start development with fresh builds
	@echo "$(GREEN)Building and starting development environment...$(NC)"
	@$(DC_DEV) up -d --build
	@echo "$(GREEN)Services started, checking health...$(NC)"
	@sleep 5
	@make health

dev-logs: ## Show development logs (follow mode)
	@$(DC_DEV) logs -f

dev-stop: ## Stop development environment
	@echo "$(GREEN)Stopping development environment...$(NC)"
	@$(DC_DEV) stop

dev-down: ## Stop and remove development containers
	@echo "$(RED)Removing development containers...$(NC)"
	@$(DC_DEV) down

# ==============================================================================
# PRODUCTION
# ==============================================================================

prod: ## Build and start production environment
	@echo "$(GREEN)Starting production environment...$(NC)"
	@$(DC_PROD) up -d
	@echo "$(GREEN)Services started. Run 'make health' to check status$(NC)"

prod-build: ## Build production images with optimizations
	@echo "$(GREEN)Building production images...$(NC)"
	@$(DC_PROD) build --no-cache
	@echo "$(GREEN)Build complete$(NC)"

prod-logs: ## Show production logs
	@$(DC_PROD) logs -f

prod-stop: ## Stop production environment gracefully
	@echo "$(YELLOW)Stopping production services...$(NC)"
	@$(DC_PROD) stop --timeout=30

prod-down: ## Stop and remove production containers (WARNING: removes data)
	@echo "$(RED)WARNING: This will stop and remove production containers!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(DC_PROD) down; \
		echo "$(RED)Production environment removed$(NC)"; \
	fi

# ==============================================================================
# TESTING
# ==============================================================================

test: test-backend test-frontend test-edge ## Run all tests

test-backend: ## Run backend tests
	@echo "$(GREEN)Running backend tests...$(NC)"
	@cd backend && pytest tests/ -v --cov=app --cov-report=html

test-frontend: ## Run frontend tests
	@echo "$(GREEN)Running frontend tests...$(NC)"
	@cd frontend && npm test -- --passWithNoTests

test-edge: ## Run edge worker tests
	@echo "$(GREEN)Running edge tests...$(NC)"
	@cd edge && pytest tests/ -v --cov=edge --cov-report=html

test-coverage: ## Generate coverage reports for all services
	@echo "$(GREEN)Generating coverage reports...$(NC)"
	@cd backend && pytest tests/ --cov=app --cov-report=html --cov-report=term
	@cd ../edge && pytest tests/ --cov=edge --cov-report=html --cov-report=term
	@echo "$(GREEN)Coverage reports generated in htmlcov/ directories$(NC)"

# ==============================================================================
# CODE QUALITY
# ==============================================================================

lint: lint-backend lint-frontend lint-edge ## Run linters on all services

lint-backend: ## Lint backend code
	@echo "$(GREEN)Linting backend...$(NC)"
	@cd backend && flake8 app/ --max-line-length=120 && echo "$(GREEN)Backend lint passed$(NC)"

lint-frontend: ## Lint frontend code
	@echo "$(GREEN)Linting frontend...$(NC)"
	@cd frontend && npm run lint

lint-edge: ## Lint edge code
	@echo "$(GREEN)Linting edge...$(NC)"
	@cd edge && flake8 edge/ --max-line-length=120

format: ## Format code (Black, isort, Prettier)
	@echo "$(GREEN)Formatting code...$(NC)"
	@cd backend && black app/ && isort app/ && echo "$(GREEN)Backend formatted$(NC)"
	@cd ../edge && black edge/ && isort edge/ && echo "$(GREEN)Edge formatted$(NC)"
	@cd ../frontend && npm run format && echo "$(GREEN)Frontend formatted$(NC)"

type-check: ## Run type checking
	@echo "$(GREEN)Running type checks...$(NC)"
	@cd backend && mypy app/ --ignore-missing-imports && echo "$(GREEN)Backend type check passed$(NC)"

security-check: ## Run security checks (bandit, npm audit)
	@echo "$(GREEN)Running security checks...$(NC)"
	@cd backend && bandit -r app/ && echo "$(GREEN)Backend security check passed$(NC)"
	@cd ../frontend && npm audit && echo "$(GREEN)Frontend security check passed$(NC)"

# ==============================================================================
# DATABASE MIGRATIONS
# ==============================================================================

db-migrate: ## Run database migrations (Alembic)
	@echo "$(GREEN)Running database migrations...$(NC)"
	@$(DC) exec -T backend alembic upgrade head
	@echo "$(GREEN)Migrations complete$(NC)"

db-migrate-down: ## Rollback last migration
	@echo "$(YELLOW)Rolling back last migration...$(NC)"
	@$(DC) exec -T backend alembic downgrade -1

db-migrate-fresh: ## Create fresh database schema (destructive!)
	@echo "$(RED)WARNING: This will destroy all data in the database!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(DC) exec -T backend alembic downgrade base; \
		$(DC) exec -T backend alembic upgrade head; \
		echo "$(GREEN)Database reset complete$(NC)"; \
	fi

db-make-migration: ## Create new migration (requires MESSAGE="description")
	@if [ -z "$(MESSAGE)" ]; then \
		echo "$(RED)Error: MESSAGE not provided. Usage: make db-make-migration MESSAGE=\"description\"$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Creating migration: $(MESSAGE)$(NC)"
	@$(DC) exec -T backend alembic revision --autogenerate -m "$(MESSAGE)"

# ==============================================================================
# DATABASE BACKUP & RESTORE
# ==============================================================================

db-backup: ## Create database backup
	@echo "$(GREEN)Creating database backup...$(NC)"
	@bash ./scripts/backup-db.sh
	@echo "$(GREEN)Backup complete$(NC)"

db-restore: ## Restore database from backup
	@echo "$(YELLOW)Restoring database from backup...$(NC)"
	@read -p "Enter backup filename: " backup_file; \
	if [ -f "backups/$$backup_file" ]; then \
		$(DC) exec -T postgres psql -U $(POSTGRES_USER) < backups/$$backup_file; \
		echo "$(GREEN)Restore complete$(NC)"; \
	else \
		echo "$(RED)Backup file not found: $$backup_file$(NC)"; \
	fi

db-shell: ## Open PostgreSQL shell
	@$(DC) exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

# ==============================================================================
# SHELLS & INTERACTIVE
# ==============================================================================

backend-shell: ## Open backend Python shell
	@$(DC) exec backend python -m ipython

frontend-shell: ## Open frontend Node shell
	@$(DC) exec frontend npm run dev

edge-shell: ## Open edge worker Python shell
	@$(DC) exec edge python -m ipython

# ==============================================================================
# HEALTH & STATUS
# ==============================================================================

health: ## Check health of all services
	@echo "$(GREEN)Checking service health...$(NC)"
	@echo ""
	@echo "$(BLUE)Database$(NC) (PostgreSQL)"
	@$(DC) exec -T postgres pg_isready -U $(POSTGRES_USER) && echo "$(GREEN)Healthy$(NC)" || echo "$(RED)Unhealthy$(NC)"
	@echo ""
	@echo "$(BLUE)Cache$(NC) (Redis)"
	@$(DC) exec -T redis redis-cli ping && echo "$(GREEN)Healthy$(NC)" || echo "$(RED)Unhealthy$(NC)"
	@echo ""
	@echo "$(BLUE)Backend$(NC) (FastAPI)"
	@curl -s http://localhost:8000/health > /dev/null && echo "$(GREEN)Healthy$(NC)" || echo "$(RED)Unhealthy$(NC)"
	@echo ""
	@echo "$(BLUE)Frontend$(NC) (Next.js)"
	@curl -s http://localhost:3000 > /dev/null && echo "$(GREEN)Healthy$(NC)" || echo "$(RED)Unhealthy$(NC)"
	@echo ""

status: ## Show status of all services
	@echo "$(GREEN)Service Status:$(NC)"
	@$(DC) ps

logs: ## Show combined logs from all services
	@$(DC) logs -f

logs-backend: ## Show backend logs only
	@$(DC) logs -f backend

logs-frontend: ## Show frontend logs only
	@$(DC) logs -f frontend

logs-db: ## Show database logs only
	@$(DC) logs -f postgres

logs-redis: ## Show Redis logs only
	@$(DC) logs -f redis

logs-edge: ## Show edge worker logs only
	@$(DC) logs -f edge

# ==============================================================================
# MONITORING & ADMIN TOOLS
# ==============================================================================

monitoring: ## Start monitoring services (Prometheus, Grafana)
	@echo "$(GREEN)Starting monitoring services...$(NC)"
	@$(DC) --profile tools up -d prometheus grafana
	@echo "$(GREEN)Prometheus: http://localhost:9091$(NC)"
	@echo "$(GREEN)Grafana: http://localhost:3001 (admin/admin)$(NC)"

adminer: ## Start Adminer database UI
	@echo "$(GREEN)Starting Adminer...$(NC)"
	@$(DC) --profile tools up -d adminer
	@echo "$(GREEN)Adminer: http://localhost:8080$(NC)"

redis-commander: ## Start Redis Commander UI
	@echo "$(GREEN)Starting Redis Commander...$(NC)"
	@$(DC) --profile tools up -d redis-commander
	@echo "$(GREEN)Redis Commander: http://localhost:8081$(NC)"

# ==============================================================================
# DOCUMENTATION
# ==============================================================================

docs: ## Generate API documentation
	@echo "$(GREEN)Generating documentation...$(NC)"
	@$(DC) exec -T backend python -m mkdocs build
	@echo "$(GREEN)Documentation available at http://localhost:8000/docs$(NC)"

docs-serve: ## Serve API docs locally
	@echo "$(GREEN)Serving API documentation...$(NC)"
	@open http://localhost:8000/docs || xdg-open http://localhost:8000/docs || echo "Visit http://localhost:8000/docs"

# ==============================================================================
# CLEANUP
# ==============================================================================

clean: ## Remove containers and volumes (keeps data)
	@echo "$(YELLOW)Cleaning up Docker environment...$(NC)"
	@$(DC) down
	@echo "$(GREEN)Cleanup complete$(NC)"

clean-all: ## Remove containers, volumes, and all data (DESTRUCTIVE)
	@echo "$(RED)WARNING: This will remove all containers, volumes, and data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(DC) down -v; \
		echo "$(RED)All containers and volumes removed$(NC)"; \
	fi

clean-cache: ## Clear all cache directories
	@echo "$(YELLOW)Clearing cache...$(NC)"
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null
	@find . -type d -name .next -exec rm -rf {} + 2>/dev/null
	@find . -type d -name dist -exec rm -rf {} + 2>/dev/null
	@echo "$(GREEN)Cache cleared$(NC)"

clean-deps: ## Remove all dependencies (venv, node_modules)
	@echo "$(RED)Removing dependencies...$(NC)"
	@rm -rf backend/venv edge/venv frontend/node_modules
	@echo "$(GREEN)Dependencies removed$(NC)"

# ==============================================================================
# UTILITIES
# ==============================================================================

env-check: ## Verify .env configuration
	@echo "$(GREEN)Checking environment configuration...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(RED)Error: .env file not found$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Environment variables set:$(NC)"
	@grep -v '^#' .env | grep -v '^$$' | wc -l | xargs echo "Total variables:"

pull-images: ## Pull latest base images
	@echo "$(GREEN)Pulling latest base images...$(NC)"
	@docker pull postgres:16-alpine
	@docker pull redis:7-alpine
	@docker pull minio/minio:latest
	@docker pull node:20-alpine
	@docker pull python:3.11-slim
	@echo "$(GREEN)Images updated$(NC)"

version: ## Show version information
	@echo "$(BLUE)ANPR License Plate Recognition System$(NC)"
	@echo "Version: 0.1.0"
	@echo ""
	@echo "$(BLUE)Components:$(NC)"
	@echo "  Backend: FastAPI 0.109.2"
	@echo "  Frontend: Next.js"
	@echo "  Database: PostgreSQL 16"
	@echo "  Cache: Redis 7"
	@echo "  Storage: MinIO"
