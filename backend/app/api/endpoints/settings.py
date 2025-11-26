"""
Settings API Endpoints
Provides comprehensive settings management with CRUD operations, validation, import/export, and history tracking.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from ...core.database import get_db
from ...models import Settings, SettingsHistory
from ...schemas import (
    SettingsCreate,
    SettingsRead,
    SettingsUpdate,
    SettingValueUpdate,
    SettingsBulkUpdate,
    SettingsExportResponse,
    SettingsImportRequest,
    SettingsImportResponse,
    SettingsValidationRequest,
    SettingsValidationResponse,
    SettingsRecommendationsResponse,
    SettingsHistoryRead,
    SettingsRollbackRequest,
    SettingsCategoryResponse,
)

router = APIRouter()


# Helper function to record settings change in history
def _record_history(
    db: Session,
    setting_key: str,
    old_value: Any,
    new_value: Any,
    changed_by: str = "system",
    reason: Optional[str] = None
):
    """Record a settings change in the history table."""
    history_entry = SettingsHistory(
        setting_key=setting_key,
        old_value=old_value,
        new_value=new_value,
        changed_by=changed_by,
        reason=reason,
    )
    db.add(history_entry)


@router.get("/", response_model=List[SettingsRead])
def get_all_settings(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in key or description"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all settings with optional filtering.

    Args:
        category: Filter settings by category
        search: Search term for key or description
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of settings matching the criteria
    """
    query = select(Settings)

    # Apply filters
    if category:
        query = query.where(Settings.category == category)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Settings.key.ilike(search_pattern)) |
            (Settings.description.ilike(search_pattern))
        )

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = db.execute(query)
    settings = result.scalars().all()

    return settings


@router.get("/categories", response_model=List[SettingsCategoryResponse])
def get_settings_by_category(db: Session = Depends(get_db)):
    """
    Get all settings grouped by category.

    Returns:
        Settings grouped by category
    """
    result = db.execute(select(Settings))
    all_settings = result.scalars().all()

    # Group by category
    categories_dict = {}
    for setting in all_settings:
        if setting.category not in categories_dict:
            categories_dict[setting.category] = []
        categories_dict[setting.category].append(setting)

    # Format response
    response = [
        SettingsCategoryResponse(
            category=cat,
            settings=settings_list,
            count=len(settings_list)
        )
        for cat, settings_list in categories_dict.items()
    ]

    return response


@router.get("/{setting_id}", response_model=SettingsRead)
def get_setting_by_id(setting_id: int, db: Session = Depends(get_db)):
    """
    Get a specific setting by ID.

    Args:
        setting_id: Setting database ID
        db: Database session

    Returns:
        The requested setting

    Raises:
        HTTPException: If setting not found
    """
    result = db.execute(select(Settings).where(Settings.id == setting_id))
    setting = result.scalar_one_or_none()

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting with id {setting_id} not found"
        )

    return setting


@router.get("/key/{setting_key}", response_model=SettingsRead)
def get_setting_by_key(setting_key: str, db: Session = Depends(get_db)):
    """
    Get a specific setting by key.

    Args:
        setting_key: Setting key (e.g., 'system.worker_id')
        db: Database session

    Returns:
        The requested setting

    Raises:
        HTTPException: If setting not found
    """
    result = db.execute(select(Settings).where(Settings.key == setting_key))
    setting = result.scalar_one_or_none()

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting with key '{setting_key}' not found"
        )

    return setting


@router.post("/", response_model=SettingsRead, status_code=status.HTTP_201_CREATED)
def create_setting(setting: SettingsCreate, db: Session = Depends(get_db)):
    """
    Create a new setting.

    Args:
        setting: Setting data
        db: Database session

    Returns:
        The created setting

    Raises:
        HTTPException: If setting with same key already exists
    """
    # Check if setting with same key exists
    result = db.execute(select(Settings).where(Settings.key == setting.key))
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Setting with key '{setting.key}' already exists"
        )

    # Create new setting
    db_setting = Settings(**setting.model_dump())
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)

    # Record in history
    _record_history(
        db=db,
        setting_key=db_setting.key,
        old_value=None,
        new_value=db_setting.value,
        changed_by="system",
        reason="Setting created"
    )
    db.commit()

    return db_setting


@router.put("/{setting_id}", response_model=SettingsRead)
def update_setting(
    setting_id: int,
    setting_update: SettingsUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a setting (full update).

    Args:
        setting_id: Setting database ID
        setting_update: Updated setting data
        db: Database session

    Returns:
        The updated setting

    Raises:
        HTTPException: If setting not found
    """
    result = db.execute(select(Settings).where(Settings.id == setting_id))
    db_setting = result.scalar_one_or_none()

    if not db_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting with id {setting_id} not found"
        )

    # Store old value for history
    old_value = db_setting.value

    # Update fields
    update_data = setting_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_setting, key, value)

    db_setting.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_setting)

    # Record in history if value changed
    if 'value' in update_data and old_value != db_setting.value:
        _record_history(
            db=db,
            setting_key=db_setting.key,
            old_value=old_value,
            new_value=db_setting.value,
            changed_by="system",
            reason="Setting updated"
        )
        db.commit()

    return db_setting


@router.patch("/{setting_id}/value", response_model=SettingsRead)
def update_setting_value(
    setting_id: int,
    value_update: SettingValueUpdate,
    db: Session = Depends(get_db)
):
    """
    Update only a setting's value (optimized for frequent updates).

    Args:
        setting_id: Setting database ID
        value_update: New value and metadata
        db: Database session

    Returns:
        The updated setting

    Raises:
        HTTPException: If setting not found
    """
    result = db.execute(select(Settings).where(Settings.id == setting_id))
    db_setting = result.scalar_one_or_none()

    if not db_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting with id {setting_id} not found"
        )

    # Store old value
    old_value = db_setting.value

    # Update value
    db_setting.value = value_update.value
    db_setting.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_setting)

    # Record in history
    _record_history(
        db=db,
        setting_key=db_setting.key,
        old_value=old_value,
        new_value=db_setting.value,
        changed_by=value_update.changed_by,
        reason=value_update.reason
    )
    db.commit()

    return db_setting


@router.post("/bulk-update", response_model=Dict[str, Any])
def bulk_update_settings(
    bulk_update: SettingsBulkUpdate,
    db: Session = Depends(get_db)
):
    """
    Update multiple settings at once.

    Args:
        bulk_update: Bulk update request with list of settings
        db: Database session

    Returns:
        Summary of updated settings
    """
    updated_count = 0
    errors = []

    for setting_data in bulk_update.settings:
        try:
            setting_key = setting_data.get('key')
            new_value = setting_data.get('value')

            if not setting_key or new_value is None:
                errors.append(f"Invalid setting data: {setting_data}")
                continue

            # Find setting by key
            result = db.execute(select(Settings).where(Settings.key == setting_key))
            db_setting = result.scalar_one_or_none()

            if not db_setting:
                errors.append(f"Setting with key '{setting_key}' not found")
                continue

            # Store old value
            old_value = db_setting.value

            # Update value
            db_setting.value = new_value
            db_setting.updated_at = datetime.utcnow()

            # Record in history
            _record_history(
                db=db,
                setting_key=db_setting.key,
                old_value=old_value,
                new_value=new_value,
                changed_by=bulk_update.changed_by,
                reason=bulk_update.reason or "Bulk update"
            )

            updated_count += 1

        except Exception as e:
            errors.append(f"Error updating {setting_data.get('key', 'unknown')}: {str(e)}")

    db.commit()

    return {
        "success": True,
        "updated_count": updated_count,
        "total_count": len(bulk_update.settings),
        "errors": errors
    }


@router.delete("/{setting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_setting(setting_id: int, db: Session = Depends(get_db)):
    """
    Delete a setting.

    Args:
        setting_id: Setting database ID
        db: Database session

    Raises:
        HTTPException: If setting not found
    """
    result = db.execute(select(Settings).where(Settings.id == setting_id))
    db_setting = result.scalar_one_or_none()

    if not db_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting with id {setting_id} not found"
        )

    # Record deletion in history
    _record_history(
        db=db,
        setting_key=db_setting.key,
        old_value=db_setting.value,
        new_value=None,
        changed_by="system",
        reason="Setting deleted"
    )

    db.delete(db_setting)
    db.commit()

    return None


@router.post("/export", response_model=SettingsExportResponse)
def export_settings(
    format: str = Query("json", description="Export format (json, yaml, env)"),
    category: Optional[str] = Query(None, description="Export specific category"),
    exclude_sensitive: bool = Query(True, description="Exclude sensitive settings"),
    db: Session = Depends(get_db)
):
    """
    Export settings in various formats.

    Args:
        format: Export format (json, yaml, env)
        category: Optional category filter
        exclude_sensitive: Whether to exclude sensitive settings
        db: Database session

    Returns:
        Exported settings data
    """
    query = select(Settings)

    if category:
        query = query.where(Settings.category == category)

    if exclude_sensitive:
        query = query.where(Settings.is_sensitive == False)

    result = db.execute(query)
    settings = result.scalars().all()

    # Format data based on requested format
    if format == "json":
        data = {
            setting.key: setting.value
            for setting in settings
        }
    elif format == "yaml":
        # YAML format (as dict, will be converted to YAML string by client)
        data = {
            setting.key: {
                "value": setting.value,
                "description": setting.description,
                "default": setting.default_value
            }
            for setting in settings
        }
    elif format == "env":
        # ENV format (as list of KEY=VALUE strings)
        data = [
            f"{setting.key.upper().replace('.', '_')}={setting.value}"
            for setting in settings
        ]
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported export format: {format}"
        )

    return SettingsExportResponse(
        format=format,
        data=data,
        exported_at=datetime.utcnow()
    )


@router.post("/import", response_model=SettingsImportResponse)
def import_settings(
    import_request: SettingsImportRequest,
    db: Session = Depends(get_db)
):
    """
    Import settings from various formats.

    Args:
        import_request: Import request with data and options
        db: Database session

    Returns:
        Import result summary
    """
    imported_count = 0
    skipped_count = 0
    errors = []

    try:
        # Parse data based on format
        if import_request.format == "json":
            settings_data = import_request.data
            if not isinstance(settings_data, dict):
                raise ValueError("JSON format expects a dictionary")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported import format: {import_request.format}"
            )

        # Import each setting
        for key, value in settings_data.items():
            try:
                # Check if setting exists
                result = db.execute(select(Settings).where(Settings.key == key))
                existing_setting = result.scalar_one_or_none()

                if existing_setting:
                    if import_request.overwrite_existing:
                        # Update existing setting
                        old_value = existing_setting.value
                        existing_setting.value = value
                        existing_setting.updated_at = datetime.utcnow()

                        _record_history(
                            db=db,
                            setting_key=key,
                            old_value=old_value,
                            new_value=value,
                            changed_by=import_request.changed_by,
                            reason="Imported from file"
                        )

                        imported_count += 1
                    else:
                        skipped_count += 1
                else:
                    # Create new setting
                    # For imports, we need to determine category from key
                    category = key.split('.')[0] if '.' in key else 'general'

                    new_setting = Settings(
                        key=key,
                        value=value,
                        category=category,
                        description=f"Imported setting: {key}",
                        value_type="string"  # Default type
                    )
                    db.add(new_setting)

                    _record_history(
                        db=db,
                        setting_key=key,
                        old_value=None,
                        new_value=value,
                        changed_by=import_request.changed_by,
                        reason="Imported from file"
                    )

                    imported_count += 1

            except Exception as e:
                errors.append(f"Error importing '{key}': {str(e)}")

        db.commit()

        return SettingsImportResponse(
            success=True,
            imported_count=imported_count,
            skipped_count=skipped_count,
            errors=errors,
            message=f"Successfully imported {imported_count} settings"
        )

    except Exception as e:
        db.rollback()
        return SettingsImportResponse(
            success=False,
            imported_count=0,
            skipped_count=0,
            errors=[str(e)],
            message="Import failed"
        )


@router.post("/validate", response_model=SettingsValidationResponse)
def validate_setting(
    validation_request: SettingsValidationRequest,
    db: Session = Depends(get_db)
):
    """
    Validate a setting value against its rules.

    Args:
        validation_request: Validation request with key and value
        db: Database session

    Returns:
        Validation result
    """
    # Get setting definition
    result = db.execute(select(Settings).where(Settings.key == validation_request.key))
    setting = result.scalar_one_or_none()

    if not setting:
        return SettingsValidationResponse(
            valid=False,
            errors=[f"Setting '{validation_request.key}' not found"],
            warnings=[],
            message="Validation failed"
        )

    errors = []
    warnings = []

    # Validate value type
    value = validation_request.value
    expected_type = setting.value_type

    # Type validation
    if expected_type == "int" and not isinstance(value, int):
        errors.append(f"Expected integer, got {type(value).__name__}")
    elif expected_type == "float" and not isinstance(value, (int, float)):
        errors.append(f"Expected float, got {type(value).__name__}")
    elif expected_type == "bool" and not isinstance(value, bool):
        errors.append(f"Expected boolean, got {type(value).__name__}")
    elif expected_type == "string" and not isinstance(value, str):
        errors.append(f"Expected string, got {type(value).__name__}")

    # Apply validation rules
    rules = setting.validation_rules

    if "min" in rules and isinstance(value, (int, float)):
        if value < rules["min"]:
            errors.append(f"Value {value} is below minimum {rules['min']}")

    if "max" in rules and isinstance(value, (int, float)):
        if value > rules["max"]:
            errors.append(f"Value {value} exceeds maximum {rules['max']}")

    if "enum" in rules and value not in rules["enum"]:
        errors.append(f"Value must be one of: {', '.join(map(str, rules['enum']))}")

    # Check if restart required
    if setting.requires_restart:
        warnings.append("Changing this setting requires a system restart")

    valid = len(errors) == 0
    message = "Validation passed" if valid else "Validation failed"

    return SettingsValidationResponse(
        valid=valid,
        errors=errors,
        warnings=warnings,
        message=message
    )


@router.get("/recommendations/get", response_model=SettingsRecommendationsResponse)
def get_recommendations(db: Session = Depends(get_db)):
    """
    Get intelligent settings recommendations.

    Returns:
        List of recommendations
    """
    # This is a placeholder - actual implementation would analyze current settings
    # and system state to provide intelligent recommendations

    recommendations = [
        {
            "setting_key": "hardware.type",
            "current_value": "cpu",
            "recommended_value": "gpu",
            "reason": "GPU detected, using GPU acceleration can improve performance",
            "impact": "high",
            "category": "hardware"
        },
        {
            "setting_key": "camera.fps",
            "current_value": 30,
            "recommended_value": 15,
            "reason": "Lower FPS can reduce CPU usage without significant accuracy loss",
            "impact": "medium",
            "category": "camera"
        }
    ]

    categories = {}
    for rec in recommendations:
        cat = rec.get("category", "general")
        categories[cat] = categories.get(cat, 0) + 1

    return SettingsRecommendationsResponse(
        recommendations=recommendations,
        total_count=len(recommendations),
        categories=categories
    )


@router.get("/history", response_model=List[SettingsHistoryRead])
def get_settings_history(
    setting_key: Optional[str] = Query(None, description="Filter by setting key"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get settings change history.

    Args:
        setting_key: Optional filter by setting key
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of history entries
    """
    query = select(SettingsHistory).order_by(SettingsHistory.created_at.desc())

    if setting_key:
        query = query.where(SettingsHistory.setting_key == setting_key)

    query = query.offset(skip).limit(limit)

    result = db.execute(query)
    history = result.scalars().all()

    return history


@router.post("/rollback", response_model=SettingsRead)
def rollback_setting(
    rollback_request: SettingsRollbackRequest,
    db: Session = Depends(get_db)
):
    """
    Rollback a setting to a previous value from history.

    Args:
        rollback_request: Rollback request with history ID
        db: Database session

    Returns:
        The rolled back setting

    Raises:
        HTTPException: If history entry not found
    """
    if not rollback_request.history_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="history_id is required for rollback"
        )

    # Get history entry
    result = db.execute(
        select(SettingsHistory).where(SettingsHistory.id == rollback_request.history_id)
    )
    history_entry = result.scalar_one_or_none()

    if not history_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History entry {rollback_request.history_id} not found"
        )

    # Get current setting
    result = db.execute(
        select(Settings).where(Settings.key == history_entry.setting_key)
    )
    setting = result.scalar_one_or_none()

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting '{history_entry.setting_key}' not found"
        )

    # Rollback to old value
    current_value = setting.value
    setting.value = history_entry.old_value
    setting.updated_at = datetime.utcnow()

    # Record rollback in history
    _record_history(
        db=db,
        setting_key=setting.key,
        old_value=current_value,
        new_value=history_entry.old_value,
        changed_by=rollback_request.changed_by,
        reason=f"Rolled back to history entry {rollback_request.history_id}"
    )

    db.commit()
    db.refresh(setting)

    return setting
