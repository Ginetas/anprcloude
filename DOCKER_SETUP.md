# Docker Setup and Configuration Guide

This guide covers the complete Docker Compose setup for the ANPR License Plate Recognition System.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Services Overview](#services-overview)
3. [Environment Configuration](#environment-configuration)
4. [Running Environments](#running-environments)
5. [Database Management](#database-management)
6. [Monitoring](#monitoring)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites

- Docker (20.10+)
- Docker Compose (2.0+)
- Bash shell
- 10+ GB free disk space (for images and volumes)

### Initial Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd anprcloude

# 2. Create environment configuration
cp .env.example .env

# 3. Edit .env with your settings (optional for development)
nano .env

# 4. Run setup script (creates directories, builds images, starts services)
make setup

# 5. Verify services are running
make health
```

### Common Commands

```bash
# Start development environment
make dev

# View logs
make logs

# Run tests
make test

# Stop all services
make clean

# See all available commands
make help
```

## Services Overview

### Core Services

#### **PostgreSQL Database** (`postgres`)
- **Image**: `postgres:16-alpine`
- **Port**: 5432
- **Purpose**: Primary data store
- **Volume**: `postgres_data`
- **Health Check**: Every 10 seconds
- **Features**:
  - Automatic initialization with extensions
  - Audit logging support
  - Full-text search enabled
  - UUID generation support

#### **Redis Cache** (`redis`)
- **Image**: `redis:7-alpine`
- **Port**: 6379
- **Purpose**: Caching, sessions, real-time data
- **Volume**: `redis_data`
- **Health Check**: Every 10 seconds
- **Features**:
  - Persistence enabled (AOF)
  - LRU eviction policy
  - 256MB memory limit (configurable)

#### **MinIO Storage** (`minio`)
- **Image**: `minio/minio:latest`
- **Ports**: 9000 (API), 9001 (Console)
- **Purpose**: S3-compatible object storage
- **Volume**: `minio_data`
- **Health Check**: Every 30 seconds
- **Features**:
  - File uploads and storage
  - Bucket management
  - Web console for administration

#### **FastAPI Backend** (`backend`)
- **Build**: `./backend/Dockerfile`
- **Port**: 8000
- **Metrics Port**: 9090
- **Purpose**: REST API, business logic
- **Volume**: `uploads:/var/anpr/uploads`
- **Health Check**: Every 30 seconds
- **Dependencies**: PostgreSQL, Redis, MinIO
- **Features**:
  - Auto-reload in development
  - Prometheus metrics
  - API documentation at `/docs`

#### **Next.js Frontend** (`frontend`)
- **Build**: `./frontend/Dockerfile`
- **Port**: 3000
- **Purpose**: Web UI
- **Health Check**: Every 30 seconds
- **Dependencies**: Backend
- **Features**:
  - Server-side rendering
  - Static asset optimization

#### **Edge Worker** (`edge`)
- **Build**: `./edge/Dockerfile`
- **Purpose**: Video processing, license plate recognition
- **Metrics Port**: 9090
- **Dependencies**: Backend, Redis
- **Volume**: Model cache, processing queue

### Optional Management Services

#### **Adminer** (Database UI)
- **Port**: 8080
- **Usage**: `make adminer` or `docker-compose --profile tools up -d adminer`
- **URL**: http://localhost:8080

#### **Redis Commander** (Redis UI)
- **Port**: 8081
- **Usage**: `make redis-commander` or `docker-compose --profile tools up -d redis-commander`
- **URL**: http://localhost:8081

#### **Prometheus** (Metrics Collection)
- **Port**: 9091
- **Usage**: `make monitoring` or `docker-compose --profile tools up -d prometheus`
- **URL**: http://localhost:9091

#### **Grafana** (Metrics Visualization)
- **Port**: 3001
- **Usage**: `make monitoring` or `docker-compose --profile tools up -d grafana`
- **URL**: http://localhost:3001
- **Credentials**: admin / admin

## Environment Configuration

### Setting up .env

Copy the example and customize:

```bash
cp .env.example .env
```

### Key Environment Variables

#### PostgreSQL
```env
POSTGRES_SERVER=postgres          # Hostname (docker service name)
POSTGRES_PORT=5432               # Container port
POSTGRES_USER=anpr                # Database user
POSTGRES_PASSWORD=change_me        # Change in production!
POSTGRES_DB=anpr_db               # Database name
```

#### Redis
```env
REDIS_HOST=redis                  # Hostname (docker service name)
REDIS_PORT=6379                   # Container port
REDIS_PASSWORD=                    # Empty by default, set for production
REDIS_MAX_MEMORY=256mb             # Memory limit
```

#### MinIO
```env
MINIO_ENDPOINT=minio:9000         # Endpoint (docker service name)
MINIO_ROOT_USER=minioadmin        # Access key
MINIO_ROOT_PASSWORD=minioadmin    # Secret key (change in production!)
MINIO_BUCKET=anpr                 # Default bucket name
MINIO_USE_SSL=false               # Use SSL (set true for production)
```

#### Backend API
```env
BACKEND_PORT=8000                 # API port
BACKEND_METRICS_PORT=9090         # Metrics port
SECRET_KEY=your-secret             # JWT secret (MUST change in production)
CORS_ORIGINS=http://localhost:3000 # CORS allowed origins
```

#### Frontend
```env
FRONTEND_PORT=3000                # Frontend port
NEXT_PUBLIC_API_URL=http://localhost:8000  # Backend URL
```

### Environment-Specific Configurations

See `.env.example` for detailed examples of different environments:
- Development (local)
- Staging
- Production

## Running Environments

### Development

```bash
# Start with development settings
make dev

# Start with fresh builds
make dev-build

# Follow logs
make dev-logs

# Stop services
make dev-stop

# Remove containers
make dev-down
```

**Features**:
- Auto-reloading for code changes
- Verbose logging
- Development ports exposed
- Tools enabled by default

### Production

```bash
# Build and start production environment
make prod

# Rebuild images
make prod-build

# View logs
make prod-logs

# Graceful shutdown
make prod-stop

# Remove containers (WARNING: removes data)
make prod-down
```

**Features**:
- Optimized builds
- Resource limits
- Restart policies set to `always`
- Database optimization
- SSL/TLS ready
- Centralized logging

**Compose files used**:
- `docker-compose.yml` (base)
- `docker-compose.prod.yml` (production overrides)

### With Nginx Reverse Proxy

```bash
# Start with Nginx
docker-compose -f docker-compose.yml -f docker-compose.nginx.yml up -d

# Or using production setup
docker-compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.nginx.yml up -d
```

## Database Management

### Running Migrations

```bash
# Run pending migrations
make db-migrate

# Rollback last migration
make db-migrate-down

# Create new migration
make db-make-migration MESSAGE="Add users table"

# Fresh database (DESTRUCTIVE!)
make db-migrate-fresh
```

### Backup and Restore

```bash
# Create backup
make db-backup

# List available backups
ls -lh backups/

# Restore from backup
make db-restore
```

Backups are:
- Compressed with gzip
- Timestamped for easy identification
- Automatically cleaned up after 7 days (configurable)
- Stored in `./backups/` directory

### Direct Database Access

```bash
# Open PostgreSQL shell
make db-shell

# Or using psql directly
docker-compose exec postgres psql -U anpr -d anpr_db
```

## Monitoring

### Health Checks

```bash
# Check all service health
make health

# Check service status
make status
```

### Start Monitoring Stack

```bash
# Start Prometheus and Grafana
make monitoring

# Or individually
make adminer              # Database UI
make redis-commander      # Redis UI
```

### Accessing Monitoring Tools

| Service | URL | Purpose |
|---------|-----|---------|
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| ReDoc | http://localhost:8000/redoc | API reference documentation |
| Adminer | http://localhost:8080 | Database management |
| Redis Commander | http://localhost:8081 | Redis data browser |
| Prometheus | http://localhost:9091 | Metrics collection |
| Grafana | http://localhost:3001 | Metrics dashboards (admin/admin) |

### Viewing Logs

```bash
# All services
make logs

# Specific services
make logs-backend
make logs-frontend
make logs-db
make logs-redis
make logs-edge
```

## Production Deployment

### Pre-Deployment Checklist

- [ ] Update `.env` with production values
- [ ] Change all default passwords (PostgreSQL, Redis, MinIO, Grafana)
- [ ] Set strong `SECRET_KEY` for JWT
- [ ] Configure `CORS_ORIGINS` for your domain
- [ ] Set up SSL certificates
- [ ] Enable HTTPS with `USE_HTTPS=true`
- [ ] Configure email notifications (SMTP)
- [ ] Set up Slack webhooks if needed
- [ ] Configure backup retention policy
- [ ] Set resource limits in compose files

### SSL/TLS Setup

#### Using Let's Encrypt

```bash
# 1. Create certs directory
mkdir -p certs

# 2. Generate certificates (example with Certbot)
certbot certonly \
  --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com

# 3. Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem certs/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem certs/key.pem
sudo chown $(whoami):$(whoami) certs/*

# 4. Update docker-compose for Nginx
```

#### Using Self-Signed Certificates (for testing)

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -out certs/cert.pem \
  -keyout certs/key.pem \
  -days 365
```

### Deployment Steps

```bash
# 1. Pull latest code
git pull origin main

# 2. Update .env for production
nano .env

# 3. Build production images
make prod-build

# 4. Start services
make prod

# 5. Run migrations
make db-migrate

# 6. Verify health
make health

# 7. Check logs
make prod-logs
```

### Scaling Services

Modify `docker-compose.prod.yml` to add replicas:

```yaml
services:
  backend:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

### Monitoring in Production

```bash
# Set up monitoring stack
docker-compose --profile tools up -d

# Create Grafana dashboards
# Access: http://yourdomain.com:3001
```

## Troubleshooting

### Service Health Issues

#### Database Connection Failed

```bash
# Check PostgreSQL logs
make logs-db

# Verify database is running
docker-compose ps postgres

# Check connection
make db-shell
```

**Solutions**:
- Ensure `POSTGRES_PASSWORD` matches between services
- Check network connectivity: `docker network ls`
- Verify PostgreSQL is healthy: `make health`

#### Redis Connection Failed

```bash
# Check Redis logs
make logs-redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

**Solutions**:
- Ensure Redis password is set correctly
- Check memory usage: `docker-compose exec redis redis-cli info memory`
- Clear data if corrupted: `docker-compose exec redis redis-cli FLUSHALL`

#### Backend API Not Responding

```bash
# Check backend logs
make logs-backend

# Test endpoint
curl http://localhost:8000/health

# Check if migrations ran
docker-compose exec backend alembic current
```

**Solutions**:
- Run migrations: `make db-migrate`
- Check environment variables: `docker-compose config`
- Restart service: `docker-compose restart backend`

#### Frontend Not Loading

```bash
# Check frontend logs
make logs-frontend

# Test connectivity
curl http://localhost:3000

# Check API connectivity from frontend logs
```

**Solutions**:
- Ensure `NEXT_PUBLIC_API_URL` is set correctly
- Clear Next.js cache: `docker-compose exec frontend rm -rf .next`
- Rebuild image: `docker-compose build --no-cache frontend`

### Common Issues

#### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Stop specific container
docker-compose stop backend

# Or change port in .env
BACKEND_PORT=8001
```

#### Insufficient Disk Space

```bash
# Check Docker disk usage
docker system df

# Clean up unused images/volumes
docker system prune -a

# Remove old backups
rm -f backups/*
```

#### Memory Issues

```bash
# Check memory usage
docker stats

# Increase resource limits in docker-compose.yml
# or reduce Redis max memory
REDIS_MAX_MEMORY=128mb
```

#### Network Issues

```bash
# Check network status
docker network inspect anpr-network

# Reset network
docker-compose down
docker network prune
docker-compose up -d
```

### Debugging

#### Enable verbose logging

```bash
# In .env
LOG_LEVEL=DEBUG
DEBUG=true

# Restart services
docker-compose restart
```

#### Inspect container

```bash
# Open shell in container
docker-compose exec backend bash

# View environment variables
docker-compose config

# Check resource usage
docker stats
```

#### View detailed logs

```bash
# All logs with timestamps
docker-compose logs --timestamps

# Last 100 lines of backend logs
docker-compose logs --tail=100 backend

# Follow logs from specific time
docker-compose logs --since 2024-01-01T10:00:00 backend
```

## Security Best Practices

### .env Security

```bash
# Never commit .env to version control
echo ".env" >> .gitignore

# Use strong passwords (generate with)
openssl rand -base64 32

# Restrict .env permissions
chmod 600 .env
```

### Docker Security

```bash
# Run services as non-root
# Already configured in Dockerfiles

# Use read-only volumes where possible
docker-compose exec backend mount | grep ro

# Keep images updated
make pull-images
docker-compose build --no-cache
```

### Network Security

```bash
# Services are isolated on anpr-network
docker network inspect anpr-network

# Only expose necessary ports
# Modify docker-compose.yml for production

# Use Nginx with SSL for external access
docker-compose -f docker-compose.yml -f docker-compose.nginx.yml up -d
```

## Performance Tuning

### Database Performance

```yaml
# In docker-compose.prod.yml, PostgreSQL command includes:
- "-c shared_buffers=512MB"
- "-c effective_cache_size=1GB"
- "-c work_mem=128MB"
```

### Redis Performance

```env
# In .env
REDIS_MAX_MEMORY=512mb              # Adjust for your system
```

### Backend Performance

```yaml
# Resource limits in docker-compose.prod.yml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

### Frontend Optimization

- Next.js uses Image Optimization (enabled in .env)
- Static assets cached with long TTL
- Nginx compresses responses with gzip

## Maintenance

### Regular Tasks

```bash
# Weekly
make test              # Run tests
make security-check    # Security audit

# Daily
make db-backup         # Database backup
docker system df       # Check disk usage

# Monthly
docker image prune -a  # Clean up images
docker volume prune    # Clean up unused volumes
make pull-images       # Update base images
```

### Updating Services

```bash
# Pull latest images
make pull-images

# Rebuild with new versions
make build

# Test in development first
make dev

# Then deploy to production
make prod
```

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [MinIO Documentation](https://docs.min.io/)

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review logs: `make logs`
3. Check service health: `make health`
4. Open an issue on the repository

---

**Last Updated**: November 2024
