"""
Configuration Routes
API endpoints for managing cameras, zones, models, and sensor settings.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Camera, ModelConfig, SensorSettings, Zone
from app.schemas import (
    CameraCreate,
    CameraRead,
    CameraUpdate,
    ModelConfigCreate,
    ModelConfigRead,
    ModelConfigUpdate,
    SensorSettingsCreate,
    SensorSettingsRead,
    SensorSettingsUpdate,
    ZoneCreate,
    ZoneRead,
    ZoneUpdate,
)

router = APIRouter()


# Camera Endpoints
# ----------------

@router.post("/cameras", response_model=CameraRead, status_code=status.HTTP_201_CREATED)
async def create_camera(
    camera: CameraCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new camera configuration.

    Args:
        camera: Camera data
        session: Database session

    Returns:
        Created camera
    """
    try:
        db_camera = Camera(**camera.model_dump())
        session.add(db_camera)
        await session.commit()
        await session.refresh(db_camera)

        logger.info(f"Camera created: {db_camera.id} - {db_camera.name}")
        return db_camera

    except Exception as e:
        logger.error(f"Failed to create camera: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create camera: {str(e)}"
        )


@router.get("/cameras", response_model=List[CameraRead])
async def get_cameras(
    enabled: bool = None,
    session: AsyncSession = Depends(get_session),
):
    """
    Get all cameras.

    Args:
        enabled: Filter by enabled status (optional)
        session: Database session

    Returns:
        List of cameras
    """
    try:
        query = select(Camera).order_by(Camera.id)

        if enabled is not None:
            query = query.where(Camera.enabled == enabled)

        result = await session.execute(query)
        cameras = result.scalars().all()

        return cameras

    except Exception as e:
        logger.error(f"Failed to retrieve cameras: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve cameras: {str(e)}"
        )


@router.get("/cameras/{camera_id}", response_model=CameraRead)
async def get_camera(
    camera_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Get a specific camera by ID.

    Args:
        camera_id: Camera identifier
        session: Database session

    Returns:
        Camera details
    """
    camera = await session.get(Camera, camera_id)

    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with id {camera_id} not found"
        )

    return camera


@router.put("/cameras/{camera_id}", response_model=CameraRead)
async def update_camera(
    camera_id: int,
    camera_update: CameraUpdate,
    session: AsyncSession = Depends(get_session),
):
    """
    Update a camera configuration.

    Args:
        camera_id: Camera identifier
        camera_update: Updated camera data
        session: Database session

    Returns:
        Updated camera
    """
    try:
        camera = await session.get(Camera, camera_id)

        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Camera with id {camera_id} not found"
            )

        # Update fields
        update_data = camera_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(camera, field, value)

        await session.commit()
        await session.refresh(camera)

        logger.info(f"Camera updated: {camera.id} - {camera.name}")
        return camera

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update camera: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update camera: {str(e)}"
        )


@router.delete("/cameras/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(
    camera_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a camera.

    Args:
        camera_id: Camera identifier
        session: Database session
    """
    try:
        camera = await session.get(Camera, camera_id)

        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Camera with id {camera_id} not found"
            )

        await session.delete(camera)
        await session.commit()

        logger.info(f"Camera deleted: {camera_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete camera: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete camera: {str(e)}"
        )


# Zone Endpoints
# --------------

@router.post("/zones", response_model=ZoneRead, status_code=status.HTTP_201_CREATED)
async def create_zone(
    zone: ZoneCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new zone configuration.

    Args:
        zone: Zone data
        session: Database session

    Returns:
        Created zone
    """
    try:
        # Verify camera exists
        camera = await session.get(Camera, zone.camera_id)
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Camera with id {zone.camera_id} not found"
            )

        db_zone = Zone(**zone.model_dump())
        session.add(db_zone)
        await session.commit()
        await session.refresh(db_zone)

        logger.info(f"Zone created: {db_zone.id} - {db_zone.name}")
        return db_zone

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create zone: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create zone: {str(e)}"
        )


@router.get("/zones", response_model=List[ZoneRead])
async def get_zones(
    camera_id: int = None,
    enabled: bool = None,
    session: AsyncSession = Depends(get_session),
):
    """
    Get all zones.

    Args:
        camera_id: Filter by camera ID (optional)
        enabled: Filter by enabled status (optional)
        session: Database session

    Returns:
        List of zones
    """
    try:
        query = select(Zone).order_by(Zone.id)

        if camera_id is not None:
            query = query.where(Zone.camera_id == camera_id)

        if enabled is not None:
            query = query.where(Zone.enabled == enabled)

        result = await session.execute(query)
        zones = result.scalars().all()

        return zones

    except Exception as e:
        logger.error(f"Failed to retrieve zones: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve zones: {str(e)}"
        )


@router.get("/zones/{zone_id}", response_model=ZoneRead)
async def get_zone(
    zone_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Get a specific zone by ID.

    Args:
        zone_id: Zone identifier
        session: Database session

    Returns:
        Zone details
    """
    zone = await session.get(Zone, zone_id)

    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone with id {zone_id} not found"
        )

    return zone


@router.put("/zones/{zone_id}", response_model=ZoneRead)
async def update_zone(
    zone_id: int,
    zone_update: ZoneUpdate,
    session: AsyncSession = Depends(get_session),
):
    """
    Update a zone configuration.

    Args:
        zone_id: Zone identifier
        zone_update: Updated zone data
        session: Database session

    Returns:
        Updated zone
    """
    try:
        zone = await session.get(Zone, zone_id)

        if not zone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Zone with id {zone_id} not found"
            )

        # Update fields
        update_data = zone_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(zone, field, value)

        await session.commit()
        await session.refresh(zone)

        logger.info(f"Zone updated: {zone.id} - {zone.name}")
        return zone

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update zone: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update zone: {str(e)}"
        )


@router.delete("/zones/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_zone(
    zone_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a zone.

    Args:
        zone_id: Zone identifier
        session: Database session
    """
    try:
        zone = await session.get(Zone, zone_id)

        if not zone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Zone with id {zone_id} not found"
            )

        await session.delete(zone)
        await session.commit()

        logger.info(f"Zone deleted: {zone_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete zone: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete zone: {str(e)}"
        )


# Model Config Endpoints
# ----------------------

@router.post("/models", response_model=ModelConfigRead, status_code=status.HTTP_201_CREATED)
async def create_model_config(
    model_config: ModelConfigCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new model configuration.

    Args:
        model_config: Model config data
        session: Database session

    Returns:
        Created model config
    """
    try:
        db_model = ModelConfig(**model_config.model_dump())
        session.add(db_model)
        await session.commit()
        await session.refresh(db_model)

        logger.info(f"Model config created: {db_model.id} - {db_model.name}")
        return db_model

    except Exception as e:
        logger.error(f"Failed to create model config: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create model config: {str(e)}"
        )


@router.get("/models", response_model=List[ModelConfigRead])
async def get_model_configs(
    type: str = None,
    enabled: bool = None,
    session: AsyncSession = Depends(get_session),
):
    """
    Get all model configurations.

    Args:
        type: Filter by model type (optional)
        enabled: Filter by enabled status (optional)
        session: Database session

    Returns:
        List of model configs
    """
    try:
        query = select(ModelConfig).order_by(ModelConfig.id)

        if type:
            query = query.where(ModelConfig.type == type)

        if enabled is not None:
            query = query.where(ModelConfig.enabled == enabled)

        result = await session.execute(query)
        models = result.scalars().all()

        return models

    except Exception as e:
        logger.error(f"Failed to retrieve model configs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve model configs: {str(e)}"
        )


@router.get("/models/{model_id}", response_model=ModelConfigRead)
async def get_model_config(
    model_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Get a specific model configuration by ID.

    Args:
        model_id: Model config identifier
        session: Database session

    Returns:
        Model config details
    """
    model = await session.get(ModelConfig, model_id)

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model config with id {model_id} not found"
        )

    return model


@router.put("/models/{model_id}", response_model=ModelConfigRead)
async def update_model_config(
    model_id: int,
    model_update: ModelConfigUpdate,
    session: AsyncSession = Depends(get_session),
):
    """
    Update a model configuration.

    Args:
        model_id: Model config identifier
        model_update: Updated model config data
        session: Database session

    Returns:
        Updated model config
    """
    try:
        model = await session.get(ModelConfig, model_id)

        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model config with id {model_id} not found"
            )

        # Update fields
        update_data = model_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(model, field, value)

        await session.commit()
        await session.refresh(model)

        logger.info(f"Model config updated: {model.id} - {model.name}")
        return model

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update model config: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update model config: {str(e)}"
        )


@router.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model_config(
    model_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a model configuration.

    Args:
        model_id: Model config identifier
        session: Database session
    """
    try:
        model = await session.get(ModelConfig, model_id)

        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model config with id {model_id} not found"
            )

        await session.delete(model)
        await session.commit()

        logger.info(f"Model config deleted: {model_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete model config: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete model config: {str(e)}"
        )


# Sensor Settings Endpoints
# --------------------------

@router.post("/sensors", response_model=SensorSettingsRead, status_code=status.HTTP_201_CREATED)
async def create_sensor_settings(
    sensor_settings: SensorSettingsCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create new sensor settings.

    Args:
        sensor_settings: Sensor settings data
        session: Database session

    Returns:
        Created sensor settings
    """
    try:
        # Verify camera exists
        camera = await session.get(Camera, sensor_settings.camera_id)
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Camera with id {sensor_settings.camera_id} not found"
            )

        # Verify zone exists if provided
        if sensor_settings.zone_id:
            zone = await session.get(Zone, sensor_settings.zone_id)
            if not zone:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Zone with id {sensor_settings.zone_id} not found"
                )

        db_settings = SensorSettings(**sensor_settings.model_dump())
        session.add(db_settings)
        await session.commit()
        await session.refresh(db_settings)

        logger.info(f"Sensor settings created: {db_settings.id} - {db_settings.name}")
        return db_settings

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create sensor settings: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create sensor settings: {str(e)}"
        )


@router.get("/sensors", response_model=List[SensorSettingsRead])
async def get_sensor_settings(
    camera_id: int = None,
    type: str = None,
    enabled: bool = None,
    session: AsyncSession = Depends(get_session),
):
    """
    Get all sensor settings.

    Args:
        camera_id: Filter by camera ID (optional)
        type: Filter by sensor type (optional)
        enabled: Filter by enabled status (optional)
        session: Database session

    Returns:
        List of sensor settings
    """
    try:
        query = select(SensorSettings).order_by(SensorSettings.id)

        if camera_id is not None:
            query = query.where(SensorSettings.camera_id == camera_id)

        if type:
            query = query.where(SensorSettings.type == type)

        if enabled is not None:
            query = query.where(SensorSettings.enabled == enabled)

        result = await session.execute(query)
        settings = result.scalars().all()

        return settings

    except Exception as e:
        logger.error(f"Failed to retrieve sensor settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sensor settings: {str(e)}"
        )


@router.get("/sensors/{settings_id}", response_model=SensorSettingsRead)
async def get_sensor_setting(
    settings_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Get specific sensor settings by ID.

    Args:
        settings_id: Sensor settings identifier
        session: Database session

    Returns:
        Sensor settings details
    """
    settings = await session.get(SensorSettings, settings_id)

    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor settings with id {settings_id} not found"
        )

    return settings


@router.put("/sensors/{settings_id}", response_model=SensorSettingsRead)
async def update_sensor_settings(
    settings_id: int,
    settings_update: SensorSettingsUpdate,
    session: AsyncSession = Depends(get_session),
):
    """
    Update sensor settings.

    Args:
        settings_id: Sensor settings identifier
        settings_update: Updated sensor settings data
        session: Database session

    Returns:
        Updated sensor settings
    """
    try:
        settings = await session.get(SensorSettings, settings_id)

        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sensor settings with id {settings_id} not found"
            )

        # Update fields
        update_data = settings_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(settings, field, value)

        await session.commit()
        await session.refresh(settings)

        logger.info(f"Sensor settings updated: {settings.id} - {settings.name}")
        return settings

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update sensor settings: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update sensor settings: {str(e)}"
        )


@router.delete("/sensors/{settings_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sensor_settings(
    settings_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Delete sensor settings.

    Args:
        settings_id: Sensor settings identifier
        session: Database session
    """
    try:
        settings = await session.get(SensorSettings, settings_id)

        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sensor settings with id {settings_id} not found"
            )

        await session.delete(settings)
        await session.commit()

        logger.info(f"Sensor settings deleted: {settings_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete sensor settings: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete sensor settings: {str(e)}"
        )
