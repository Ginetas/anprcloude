"""
Health Check Tests
Basic tests for application health endpoints.
"""

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test the root endpoint returns application info."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "running"


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test the health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "timestamp" in data
    assert "services" in data


@pytest.mark.asyncio
async def test_liveness_endpoint():
    """Test the Kubernetes liveness probe endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/liveness")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_readiness_endpoint():
    """Test the Kubernetes readiness probe endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/ready")

    # Response can be 200 or 503 depending on database availability
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data


@pytest.mark.asyncio
async def test_invalid_endpoint():
    """Test that invalid endpoints return 404."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/invalid-endpoint-123")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_cors_headers():
    """Test that CORS headers are properly set."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.options(
            "/",
            headers={"Origin": "http://localhost:3000"}
        )

    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers


@pytest.mark.asyncio
async def test_api_endpoints_exist():
    """Test that main API endpoints are registered."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test events endpoint
        response = await client.get("/api/v1/events")
        # Should return 200 or error (but not 404 which means route doesn't exist)
        assert response.status_code != 404

        # Test config endpoint
        response = await client.get("/api/v1/config/cameras")
        assert response.status_code != 404

        # Test exporters endpoint
        response = await client.get("/api/v1/exporters")
        assert response.status_code != 404
