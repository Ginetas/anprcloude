"""
Exporter Routes
API endpoints for managing data exporters and testing export functionality.
"""

import json
import time
from typing import List

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import ExporterConfig
from app.schemas import (
    ExporterConfigCreate,
    ExporterConfigRead,
    ExporterConfigUpdate,
    ExporterTestRequest,
    ExporterTestResponse,
)

router = APIRouter()


@router.post("", response_model=ExporterConfigRead, status_code=status.HTTP_201_CREATED)
async def create_exporter(
    exporter: ExporterConfigCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new exporter configuration.

    Args:
        exporter: Exporter config data
        session: Database session

    Returns:
        Created exporter config
    """
    try:
        db_exporter = ExporterConfig(**exporter.model_dump())
        session.add(db_exporter)
        await session.commit()
        await session.refresh(db_exporter)

        logger.info(f"Exporter created: {db_exporter.id} - {db_exporter.name}")
        return db_exporter

    except Exception as e:
        logger.error(f"Failed to create exporter: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create exporter: {str(e)}"
        )


@router.get("", response_model=List[ExporterConfigRead])
async def get_exporters(
    type: str = None,
    enabled: bool = None,
    session: AsyncSession = Depends(get_session),
):
    """
    Get all exporter configurations.

    Args:
        type: Filter by exporter type (optional)
        enabled: Filter by enabled status (optional)
        session: Database session

    Returns:
        List of exporter configs
    """
    try:
        query = select(ExporterConfig).order_by(ExporterConfig.id)

        if type:
            query = query.where(ExporterConfig.type == type)

        if enabled is not None:
            query = query.where(ExporterConfig.enabled == enabled)

        result = await session.execute(query)
        exporters = result.scalars().all()

        return exporters

    except Exception as e:
        logger.error(f"Failed to retrieve exporters: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve exporters: {str(e)}"
        )


@router.get("/{exporter_id}", response_model=ExporterConfigRead)
async def get_exporter(
    exporter_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Get a specific exporter configuration by ID.

    Args:
        exporter_id: Exporter config identifier
        session: Database session

    Returns:
        Exporter config details
    """
    exporter = await session.get(ExporterConfig, exporter_id)

    if not exporter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exporter with id {exporter_id} not found"
        )

    return exporter


@router.put("/{exporter_id}", response_model=ExporterConfigRead)
async def update_exporter(
    exporter_id: int,
    exporter_update: ExporterConfigUpdate,
    session: AsyncSession = Depends(get_session),
):
    """
    Update an exporter configuration.

    Args:
        exporter_id: Exporter config identifier
        exporter_update: Updated exporter config data
        session: Database session

    Returns:
        Updated exporter config
    """
    try:
        exporter = await session.get(ExporterConfig, exporter_id)

        if not exporter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exporter with id {exporter_id} not found"
            )

        # Update fields
        update_data = exporter_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(exporter, field, value)

        await session.commit()
        await session.refresh(exporter)

        logger.info(f"Exporter updated: {exporter.id} - {exporter.name}")
        return exporter

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update exporter: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update exporter: {str(e)}"
        )


@router.delete("/{exporter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exporter(
    exporter_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Delete an exporter configuration.

    Args:
        exporter_id: Exporter config identifier
        session: Database session
    """
    try:
        exporter = await session.get(ExporterConfig, exporter_id)

        if not exporter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exporter with id {exporter_id} not found"
            )

        await session.delete(exporter)
        await session.commit()

        logger.info(f"Exporter deleted: {exporter_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete exporter: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete exporter: {str(e)}"
        )


@router.post("/{exporter_id}/test", response_model=ExporterTestResponse)
async def test_exporter(
    exporter_id: int,
    test_request: ExporterTestRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Test an exporter configuration by sending a sample event.

    Args:
        exporter_id: Exporter config identifier
        test_request: Test request with optional sample event data
        session: Database session

    Returns:
        Test result with status and response time
    """
    # Get exporter config
    exporter = await session.get(ExporterConfig, exporter_id)

    if not exporter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exporter with id {exporter_id} not found"
        )

    # Prepare sample event
    sample_event = test_request.sample_event or {
        "event_id": "00000000-0000-0000-0000-000000000000",
        "timestamp": "2025-01-01T00:00:00Z",
        "camera_id": 1,
        "zone_id": 1,
        "plate_text": "ABC123",
        "confidence": 0.95,
        "vehicle_info": {
            "type": "car",
            "color": "blue"
        },
        "metadata": {
            "test": True
        }
    }

    # Test based on exporter type
    if exporter.type == "webhook":
        return await _test_webhook_exporter(exporter, sample_event)
    elif exporter.type == "mqtt":
        return ExporterTestResponse(
            success=False,
            response_time=0.0,
            message="MQTT exporter testing not yet implemented",
            error="Not implemented"
        )
    elif exporter.type == "kafka":
        return ExporterTestResponse(
            success=False,
            response_time=0.0,
            message="Kafka exporter testing not yet implemented",
            error="Not implemented"
        )
    else:
        return ExporterTestResponse(
            success=False,
            response_time=0.0,
            message=f"Unknown exporter type: {exporter.type}",
            error="Invalid exporter type"
        )


async def _test_webhook_exporter(
    exporter: ExporterConfig,
    sample_event: dict
) -> ExporterTestResponse:
    """
    Test a webhook exporter.

    Args:
        exporter: Exporter configuration
        sample_event: Sample event data to send

    Returns:
        Test response with results
    """
    start_time = time.time()

    try:
        # Prepare headers
        headers = exporter.headers.copy() if exporter.headers else {}
        headers.setdefault("Content-Type", "application/json")

        # Add authentication if configured
        if exporter.auth:
            auth_type = exporter.auth.get("type", "none")

            if auth_type == "bearer":
                token = exporter.auth.get("token")
                if token:
                    headers["Authorization"] = f"Bearer {token}"

            elif auth_type == "api_key":
                key_name = exporter.auth.get("key_name", "X-API-Key")
                key_value = exporter.auth.get("key_value")
                if key_value:
                    headers[key_name] = key_value

            elif auth_type == "basic":
                username = exporter.auth.get("username")
                password = exporter.auth.get("password")
                if username and password:
                    import base64
                    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                    headers["Authorization"] = f"Basic {credentials}"

        # Get timeout from retry config
        timeout = exporter.retry_config.get("timeout", 30)

        # Send test request
        async with httpx.AsyncClient() as client:
            response = await client.post(
                exporter.url,
                json=sample_event,
                headers=headers,
                timeout=timeout,
            )

        response_time = time.time() - start_time

        # Check response
        if response.status_code in [200, 201, 202, 204]:
            return ExporterTestResponse(
                success=True,
                status_code=response.status_code,
                response_time=response_time,
                message=f"Test successful. Response: {response.text[:200]}"
            )
        else:
            return ExporterTestResponse(
                success=False,
                status_code=response.status_code,
                response_time=response_time,
                message="Test failed with non-2xx status code",
                error=f"Status {response.status_code}: {response.text[:200]}"
            )

    except httpx.TimeoutException as e:
        response_time = time.time() - start_time
        logger.error(f"Exporter test timeout: {e}")
        return ExporterTestResponse(
            success=False,
            response_time=response_time,
            message="Test failed due to timeout",
            error=str(e)
        )

    except httpx.HTTPError as e:
        response_time = time.time() - start_time
        logger.error(f"Exporter test HTTP error: {e}")
        return ExporterTestResponse(
            success=False,
            response_time=response_time,
            message="Test failed due to HTTP error",
            error=str(e)
        )

    except Exception as e:
        response_time = time.time() - start_time
        logger.error(f"Exporter test error: {e}")
        return ExporterTestResponse(
            success=False,
            response_time=response_time,
            message="Test failed due to unexpected error",
            error=str(e)
        )


@router.post("/{exporter_id}/enable", response_model=ExporterConfigRead)
async def enable_exporter(
    exporter_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Enable an exporter.

    Args:
        exporter_id: Exporter config identifier
        session: Database session

    Returns:
        Updated exporter config
    """
    try:
        exporter = await session.get(ExporterConfig, exporter_id)

        if not exporter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exporter with id {exporter_id} not found"
            )

        exporter.enabled = True
        await session.commit()
        await session.refresh(exporter)

        logger.info(f"Exporter enabled: {exporter.id} - {exporter.name}")
        return exporter

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to enable exporter: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable exporter: {str(e)}"
        )


@router.post("/{exporter_id}/disable", response_model=ExporterConfigRead)
async def disable_exporter(
    exporter_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Disable an exporter.

    Args:
        exporter_id: Exporter config identifier
        session: Database session

    Returns:
        Updated exporter config
    """
    try:
        exporter = await session.get(ExporterConfig, exporter_id)

        if not exporter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exporter with id {exporter_id} not found"
            )

        exporter.enabled = False
        await session.commit()
        await session.refresh(exporter)

        logger.info(f"Exporter disabled: {exporter.id} - {exporter.name}")
        return exporter

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to disable exporter: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disable exporter: {str(e)}"
        )
