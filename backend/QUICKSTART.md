# Quick Start Guide

Get the ANPR Cloud Backend up and running in 5 minutes.

## Option 1: Docker Compose (Recommended)

The easiest way to get started is using Docker Compose:

```bash
# 1. Start all services (PostgreSQL, Redis, Backend)
docker-compose up -d

# 2. Check service status
docker-compose ps

# 3. View logs
docker-compose logs -f backend

# 4. Run migrations
docker-compose exec backend alembic upgrade head

# 5. Access the API
open http://localhost:8000
```

**Optional: Start with database management tools**

```bash
# Start with Adminer (database UI) and Redis Commander
docker-compose --profile tools up -d

# Access Adminer at http://localhost:8080
# Access Redis Commander at http://localhost:8081
```

## Option 2: Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+

### Setup Steps

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your database credentials

# 4. Create database
createdb anpr_db

# 5. Run migrations
alembic upgrade head

# 6. Start the server
uvicorn app.main:app --reload
```

## Quick Test

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Create a camera
curl -X POST http://localhost:8000/api/v1/config/cameras \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Front Entrance",
    "rtsp_url": "rtsp://192.168.1.100/stream",
    "enabled": true,
    "fps": 10,
    "resolution": "1920x1080"
  }'

# List cameras
curl http://localhost:8000/api/v1/config/cameras

# Ingest a plate event
curl -X POST http://localhost:8000/api/v1/events/ingest \
  -F "camera_id=1" \
  -F "plate_text=ABC123" \
  -F "confidence=0.95"

# Get events
curl http://localhost:8000/api/v1/events

# Get statistics
curl http://localhost:8000/api/v1/events/stats
```

### API Documentation

When debug mode is enabled, access interactive API docs:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## WebSocket Test

Connect to the WebSocket endpoint for real-time events:

```javascript
// JavaScript example
const ws = new WebSocket('ws://localhost:8000/api/v1/events/stream');

ws.onopen = () => {
  console.log('Connected to event stream');
};

ws.onmessage = (event) => {
  console.log('Event received:', JSON.parse(event.data));
};
```

```python
# Python example
import asyncio
import websockets

async def listen():
    async with websockets.connect('ws://localhost:8000/api/v1/events/stream') as websocket:
        while True:
            message = await websocket.recv()
            print(f"Event: {message}")

asyncio.run(listen())
```

## Common Commands

### Docker

```bash
# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# View logs
docker-compose logs -f backend

# Execute commands in container
docker-compose exec backend alembic upgrade head
docker-compose exec backend pytest
```

### Database

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# View history
alembic history
```

### Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Format code
black app/ tests/
isort app/ tests/

# Lint
flake8 app/
mypy app/
```

## Using Makefile

If you have `make` installed:

```bash
make help           # Show all commands
make install        # Install dependencies
make dev            # Run development server
make test           # Run tests
make docker-up      # Start Docker services
make migrate        # Run migrations
```

## Next Steps

1. **Configure Cameras**: Add your RTSP camera streams
2. **Setup Zones**: Define detection zones for each camera
3. **Configure Models**: Set up AI model paths and parameters
4. **Add Exporters**: Configure webhooks or other export destinations
5. **Test Events**: Send test events and verify processing

## Troubleshooting

### Port Already in Use

```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or change the port in .env
API_PORT=8001
```

### Database Connection Error

```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Test connection
psql -h localhost -U anpr -d anpr_db

# Check Docker logs
docker-compose logs postgres
```

### Redis Connection Error

```bash
# Check Redis is running
redis-cli ping

# Test connection
redis-cli -h localhost -p 6379 ping
```

### Permission Errors

```bash
# Fix upload directory permissions
sudo mkdir -p /var/anpr/uploads
sudo chown -R $USER:$USER /var/anpr/uploads
```

## Production Deployment

For production deployment:

1. Update `.env` with secure credentials
2. Set `DEBUG=false`
3. Configure proper `CORS_ORIGINS`
4. Set up SSL/TLS termination
5. Use a reverse proxy (nginx, traefik)
6. Configure backups for database
7. Set up monitoring and alerting
8. Use container orchestration (Kubernetes, Docker Swarm)

See [README.md](README.md) for detailed production deployment guide.

## Support

- Check the logs: `docker-compose logs -f backend`
- Review API docs: http://localhost:8000/docs
- See main README for detailed documentation
