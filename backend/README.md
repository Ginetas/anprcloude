# ANPR Cloud Backend

Production-ready FastAPI backend for the Automatic Number Plate Recognition (ANPR) Cloud system.

## Features

- **FastAPI Framework**: Modern, fast, async-first web framework
- **SQLModel ORM**: Type-safe database models with Pydantic validation
- **PostgreSQL Database**: Reliable, scalable relational database
- **Redis Cache**: Fast caching and pub/sub for real-time features
- **WebSocket Support**: Real-time event streaming to clients
- **File Upload**: Handle frame and crop image uploads
- **Comprehensive API**: Full CRUD operations for all entities
- **Database Migrations**: Alembic for version-controlled schema changes
- **Production-Ready**: Docker support, health checks, logging, metrics
- **Type Safety**: Full typing with mypy support
- **Testing**: Pytest with async support

## Architecture

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection and session
│   ├── models.py            # SQLModel database models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── routers/             # API route handlers
│   │   ├── __init__.py
│   │   ├── events.py        # Event endpoints and WebSocket
│   │   ├── config.py        # Configuration endpoints
│   │   └── exporters.py     # Exporter endpoints
│   └── services/            # Business logic layer
│       ├── __init__.py
│       └── event_service.py # Event processing logic
├── tests/                   # Test suite
│   ├── __init__.py
│   └── test_health.py       # Health check tests
├── alembic/                 # Database migrations
│   ├── versions/            # Migration scripts
│   ├── env.py               # Alembic environment
│   └── script.py.mako       # Migration template
├── requirements.txt         # Python dependencies
├── Dockerfile              # Production Docker image
├── alembic.ini             # Alembic configuration
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Database Models

### Camera
- Camera configuration and metadata
- RTSP stream URL, FPS, resolution
- Location and zone association

### Zone
- Detection zone configuration
- GeoJSON geometry for zone boundaries
- Zone types: detection, exclusion, parking

### ModelConfig
- AI model configuration
- Model weights path and version
- Type-specific parameters

### SensorSettings
- Edge sensor configuration
- Camera and zone associations
- Sensor-specific settings

### ExporterConfig
- Data exporter configuration
- Support for webhook, MQTT, Kafka
- Retry policies and authentication

### PlateEvent
- License plate detection events
- OCR results with confidence scores
- Vehicle information and TPMS data
- Image URLs (frame and crop)
- Export tracking

## API Endpoints

### Health & Monitoring

```
GET  /                  # Application info
GET  /health            # Health check with service status
GET  /ready             # Kubernetes readiness probe
GET  /liveness          # Kubernetes liveness probe
GET  /metrics           # Prometheus metrics (if enabled)
```

### Events

```
POST   /api/v1/events/ingest     # Ingest new plate event (with file upload)
GET    /api/v1/events            # List events with filtering
GET    /api/v1/events/{id}       # Get specific event
GET    /api/v1/events/stats      # Event statistics
WS     /api/v1/events/stream     # WebSocket real-time stream
```

### Configuration

```
# Cameras
POST   /api/v1/config/cameras              # Create camera
GET    /api/v1/config/cameras              # List cameras
GET    /api/v1/config/cameras/{id}         # Get camera
PUT    /api/v1/config/cameras/{id}         # Update camera
DELETE /api/v1/config/cameras/{id}         # Delete camera

# Zones
POST   /api/v1/config/zones                # Create zone
GET    /api/v1/config/zones                # List zones
GET    /api/v1/config/zones/{id}           # Get zone
PUT    /api/v1/config/zones/{id}           # Update zone
DELETE /api/v1/config/zones/{id}           # Delete zone

# Models
POST   /api/v1/config/models               # Create model config
GET    /api/v1/config/models               # List model configs
GET    /api/v1/config/models/{id}          # Get model config
PUT    /api/v1/config/models/{id}          # Update model config
DELETE /api/v1/config/models/{id}          # Delete model config

# Sensors
POST   /api/v1/config/sensors              # Create sensor settings
GET    /api/v1/config/sensors              # List sensor settings
GET    /api/v1/config/sensors/{id}         # Get sensor settings
PUT    /api/v1/config/sensors/{id}         # Update sensor settings
DELETE /api/v1/config/sensors/{id}         # Delete sensor settings
```

### Exporters

```
POST   /api/v1/exporters                   # Create exporter
GET    /api/v1/exporters                   # List exporters
GET    /api/v1/exporters/{id}              # Get exporter
PUT    /api/v1/exporters/{id}              # Update exporter
DELETE /api/v1/exporters/{id}              # Delete exporter
POST   /api/v1/exporters/{id}/test         # Test exporter
POST   /api/v1/exporters/{id}/enable       # Enable exporter
POST   /api/v1/exporters/{id}/disable      # Disable exporter
```

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+

### Installation

1. **Clone the repository**

```bash
cd backend
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment**

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**

```bash
# Create database
createdb anpr_db

# Run migrations
alembic upgrade head
```

6. **Start the application**

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Docker Deployment

### Build Image

```bash
docker build -t anpr-backend:latest .
```

### Run Container

```bash
docker run -d \
  --name anpr-backend \
  -p 8000:8000 \
  -p 9090:9090 \
  -e POSTGRES_SERVER=host.docker.internal \
  -e REDIS_HOST=host.docker.internal \
  -v /var/anpr/uploads:/var/anpr/uploads \
  anpr-backend:latest
```

### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
      - "9090:9090"
    environment:
      - POSTGRES_SERVER=postgres
      - REDIS_HOST=redis
    volumes:
      - uploads:/var/anpr/uploads
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:16
    environment:
      - POSTGRES_USER=anpr
      - POSTGRES_PASSWORD=anpr_password
      - POSTGRES_DB=anpr_db
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
  uploads:
```

## Database Migrations

### Create Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new table"

# Create empty migration
alembic revision -m "Custom migration"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>
```

### Migration History

```bash
# View history
alembic history --verbose

# Current revision
alembic current
```

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_health.py

# Run with verbose output
pytest -v
```

### Test Structure

```python
# Example test
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_camera():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/config/cameras",
            json={
                "name": "Test Camera",
                "rtsp_url": "rtsp://example.com/stream",
                "enabled": True
            }
        )
    assert response.status_code == 201
```

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

**Key Settings:**

- `DEBUG`: Enable debug mode and API docs
- `POSTGRES_SERVER`: Database host
- `REDIS_HOST`: Redis host
- `UPLOAD_DIR`: File upload directory
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)

### Production Considerations

1. **Security**
   - Change `SECRET_KEY` to a secure random string
   - Update `POSTGRES_PASSWORD` and `REDIS_PASSWORD`
   - Restrict `CORS_ORIGINS` to your frontend domain
   - Disable debug mode (`DEBUG=false`)

2. **Performance**
   - Adjust `DB_POOL_SIZE` based on load
   - Configure Redis for persistence if needed
   - Use CDN for uploaded images
   - Enable Prometheus metrics for monitoring

3. **Reliability**
   - Set up database backups
   - Configure log rotation
   - Monitor health endpoints
   - Use load balancer for multiple instances

## Development

### Code Style

```bash
# Format code
black app/

# Sort imports
isort app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Adding New Endpoints

1. **Create schema in `schemas.py`**

```python
class NewItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
```

2. **Create model in `models.py`**

```python
class NewItem(TimestampMixin, table=True):
    __tablename__ = "new_items"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
```

3. **Add routes in appropriate router**

```python
@router.post("/items", response_model=NewItemRead)
async def create_item(
    item: NewItemCreate,
    session: AsyncSession = Depends(get_session)
):
    # Implementation
    pass
```

4. **Create migration**

```bash
alembic revision --autogenerate -m "Add new_items table"
alembic upgrade head
```

## Monitoring

### Health Checks

- `/health` - Overall health status
- `/ready` - Kubernetes readiness
- `/liveness` - Kubernetes liveness

### Prometheus Metrics

When `ENABLE_METRICS=true`:

- HTTP request count
- Request duration histogram
- Custom application metrics

### Logging

Structured logging with Loguru:

```python
from loguru import logger

logger.info("Event created", event_id=event.id)
logger.error("Failed to process", error=str(e))
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Test connection
psql -h localhost -U anpr -d anpr_db

# Check logs
docker logs anpr-backend
```

### Redis Connection Issues

```bash
# Check Redis is running
redis-cli ping

# Test connection
redis-cli -h localhost -p 6379
```

### File Upload Issues

```bash
# Check upload directory permissions
ls -la /var/anpr/uploads

# Create directory if missing
mkdir -p /var/anpr/uploads
chown -R anpr:anpr /var/anpr/uploads
```

## Support

For issues and questions:
- Check the main project README
- Review API documentation at `/docs` (when DEBUG=true)
- Check logs for error details

## License

See LICENSE file in the project root.
