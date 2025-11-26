"""
Event Service
Business logic for handling plate detection events.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import UploadFile
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import PlateEvent


class EventService:
    """Service for managing plate detection events."""

    def __init__(self, session: AsyncSession):
        """
        Initialize event service.

        Args:
            session: Database session
        """
        self.session = session

    async def create_event(
        self,
        camera_id: int,
        plate_text: str,
        confidence: float,
        zone_id: Optional[int] = None,
        vehicle_info: Optional[str] = None,
        tpms_status: Optional[str] = None,
        metadata: Optional[str] = None,
        frame_image: Optional[UploadFile] = None,
        crop_image: Optional[UploadFile] = None,
    ) -> PlateEvent:
        """
        Create a new plate detection event.

        Args:
            camera_id: Source camera ID
            plate_text: Recognized plate text
            confidence: Recognition confidence
            zone_id: Detection zone ID (optional)
            vehicle_info: Vehicle information as JSON string (optional)
            tpms_status: TPMS data as JSON string (optional)
            metadata: Additional metadata as JSON string (optional)
            frame_image: Full frame image file (optional)
            crop_image: Plate crop image file (optional)

        Returns:
            Created plate event

        Raises:
            ValueError: If validation fails
        """
        # Validate confidence
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")

        # Validate and parse JSON fields
        vehicle_info_dict = self._parse_json_field(vehicle_info, "vehicle_info")
        tpms_status_dict = self._parse_json_field(tpms_status, "tpms_status")
        metadata_dict = self._parse_json_field(metadata, "metadata")

        # Handle file uploads
        frame_url = None
        crop_url = None

        if frame_image:
            frame_url = await self._save_uploaded_file(
                frame_image,
                prefix="frame",
                camera_id=camera_id
            )

        if crop_image:
            crop_url = await self._save_uploaded_file(
                crop_image,
                prefix="crop",
                camera_id=camera_id
            )

        # Create event
        event = PlateEvent(
            camera_id=camera_id,
            plate_text=plate_text.upper(),  # Normalize to uppercase
            confidence=confidence,
            zone_id=zone_id,
            vehicle_info=vehicle_info_dict,
            tpms_status=tpms_status_dict,
            metadata=metadata_dict,
            frame_url=frame_url,
            crop_url=crop_url,
            timestamp=datetime.utcnow(),
        )

        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)

        logger.info(
            f"Event created: {event.event_id} - "
            f"Camera: {camera_id}, Plate: {plate_text}, "
            f"Confidence: {confidence:.2f}"
        )

        return event

    async def get_event_by_id(self, event_id: uuid.UUID) -> Optional[PlateEvent]:
        """
        Get an event by its UUID.

        Args:
            event_id: Event UUID

        Returns:
            Plate event or None if not found
        """
        return await self.session.get(PlateEvent, event_id)

    async def mark_as_exported(
        self,
        event: PlateEvent,
        success: bool = True
    ) -> PlateEvent:
        """
        Mark an event as exported.

        Args:
            event: Plate event to update
            success: Whether export was successful

        Returns:
            Updated plate event
        """
        event.exported = success
        event.export_attempts += 1
        event.last_export_at = datetime.utcnow()

        await self.session.flush()
        await self.session.refresh(event)

        logger.info(f"Event {event.event_id} marked as exported: {success}")

        return event

    async def get_events_for_export(
        self,
        limit: int = 100
    ) -> List[PlateEvent]:
        """
        Get events that need to be exported.

        Args:
            limit: Maximum number of events to retrieve

        Returns:
            List of plate events
        """
        from sqlalchemy import select

        query = (
            select(PlateEvent)
            .where(PlateEvent.exported == False)
            .order_by(PlateEvent.timestamp)
            .limit(limit)
        )

        result = await self.session.execute(query)
        events = result.scalars().all()

        logger.info(f"Found {len(events)} events for export")

        return events

    async def validate_event_data(
        self,
        plate_text: str,
        confidence: float,
        vehicle_info: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Validate event data.

        Args:
            plate_text: Plate text to validate
            confidence: Confidence score
            vehicle_info: Optional vehicle information

        Returns:
            True if valid, False otherwise

        Raises:
            ValueError: If validation fails with details
        """
        # Validate plate text
        if not plate_text or len(plate_text.strip()) == 0:
            raise ValueError("Plate text cannot be empty")

        if len(plate_text) > 20:
            raise ValueError("Plate text too long (max 20 characters)")

        # Validate confidence
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")

        # Validate vehicle info if provided
        if vehicle_info:
            valid_vehicle_types = [
                "car", "truck", "bus", "motorcycle",
                "van", "suv", "unknown"
            ]
            if "type" in vehicle_info:
                if vehicle_info["type"] not in valid_vehicle_types:
                    raise ValueError(
                        f"Invalid vehicle type. "
                        f"Must be one of: {', '.join(valid_vehicle_types)}"
                    )

        return True

    def _parse_json_field(
        self,
        json_string: Optional[str],
        field_name: str
    ) -> Dict[str, Any]:
        """
        Parse a JSON string field.

        Args:
            json_string: JSON string to parse
            field_name: Field name for error messages

        Returns:
            Parsed dictionary

        Raises:
            ValueError: If JSON is invalid
        """
        if not json_string:
            return {}

        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {field_name}: {str(e)}")

    async def _save_uploaded_file(
        self,
        file: UploadFile,
        prefix: str,
        camera_id: int
    ) -> str:
        """
        Save an uploaded file to disk.

        Args:
            file: Uploaded file
            prefix: Filename prefix (frame or crop)
            camera_id: Camera ID for organizing files

        Returns:
            Relative URL to the saved file

        Raises:
            ValueError: If file validation fails
        """
        # Validate file type
        if file.content_type not in settings.allowed_image_types:
            raise ValueError(
                f"Invalid file type: {file.content_type}. "
                f"Allowed types: {', '.join(settings.allowed_image_types)}"
            )

        # Validate file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to start

        if file_size > settings.max_upload_size:
            raise ValueError(
                f"File too large: {file_size} bytes. "
                f"Maximum size: {settings.max_upload_size} bytes"
            )

        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        ext = Path(file.filename).suffix if file.filename else ".jpg"
        filename = f"{prefix}_{camera_id}_{timestamp}_{unique_id}{ext}"

        # Create directory structure: upload_dir/camera_id/YYYY-MM-DD/
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        upload_path = Path(settings.upload_dir) / str(camera_id) / date_str
        upload_path.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = upload_path / filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"File saved: {file_path}")

        # Return relative URL
        return f"/uploads/{camera_id}/{date_str}/{filename}"

    async def cleanup_old_events(self, days: int = 90) -> int:
        """
        Delete events older than specified days.

        Args:
            days: Number of days to retain

        Returns:
            Number of deleted events
        """
        from sqlalchemy import delete
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        query = delete(PlateEvent).where(PlateEvent.timestamp < cutoff_date)
        result = await self.session.execute(query)
        await self.session.commit()

        deleted_count = result.rowcount
        logger.info(f"Deleted {deleted_count} events older than {days} days")

        return deleted_count

    async def get_event_statistics(
        self,
        camera_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get event statistics.

        Args:
            camera_id: Filter by camera (optional)
            start_date: Start date filter (optional)
            end_date: End date filter (optional)

        Returns:
            Dictionary with statistics
        """
        from sqlalchemy import func, select

        # Base query
        query = select(PlateEvent)

        # Apply filters
        if camera_id:
            query = query.where(PlateEvent.camera_id == camera_id)

        if start_date:
            query = query.where(PlateEvent.timestamp >= start_date)

        if end_date:
            query = query.where(PlateEvent.timestamp <= end_date)

        # Get counts
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(total_query)
        total = total_result.scalar()

        # Get unique plates
        unique_query = select(
            func.count(func.distinct(PlateEvent.plate_text))
        ).select_from(query.subquery())
        unique_result = await self.session.execute(unique_query)
        unique = unique_result.scalar()

        # Get average confidence
        avg_query = select(
            func.avg(PlateEvent.confidence)
        ).select_from(query.subquery())
        avg_result = await self.session.execute(avg_query)
        avg_confidence = avg_result.scalar() or 0.0

        return {
            "total_events": total or 0,
            "unique_plates": unique or 0,
            "avg_confidence": float(avg_confidence),
        }
