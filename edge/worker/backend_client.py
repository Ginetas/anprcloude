"""
Backend communication client for edge worker.
Handles HTTP requests to FastAPI backend and retry logic.
"""

import httpx
import logging
from typing import List, Optional
from datetime import datetime
import asyncio
from .models import PlateEvent, CameraConfig

logger = logging.getLogger(__name__)


class BackendClient:
    """Client for communicating with the ANPR backend API"""

    def __init__(self, backend_url: str, timeout: float = 10.0):
        """
        Initialize backend client.

        Args:
            backend_url: Base URL of the backend API
            timeout: Request timeout in seconds
        """
        self.backend_url = backend_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def health_check(self) -> bool:
        """
        Check if backend is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            response = await self.client.get(f"{self.backend_url}/healthz")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False

    async def get_cameras(self) -> List[CameraConfig]:
        """
        Fetch list of enabled cameras from backend.

        Returns:
            List of camera configurations
        """
        try:
            response = await self.client.get(f"{self.backend_url}/api/cameras")
            response.raise_for_status()

            cameras_data = response.json()
            cameras = [CameraConfig(**cam) for cam in cameras_data]

            # Filter only enabled cameras
            return [cam for cam in cameras if cam.enabled]

        except Exception as e:
            logger.error(f"Failed to fetch cameras: {e}")
            return []

    async def ingest_plate_event(
        self,
        event: PlateEvent,
        max_retries: int = 3
    ) -> bool:
        """
        Send plate event to backend with retry logic.

        Args:
            event: PlateEvent to send
            max_retries: Maximum number of retry attempts

        Returns:
            True if successful, False otherwise
        """
        retry_delays = [1, 2, 5]  # Exponential backoff (seconds)

        for attempt in range(max_retries):
            try:
                # Convert event to JSON-serializable dict
                event_data = event.model_dump(mode='json')

                response = await self.client.post(
                    f"{self.backend_url}/api/plate-events/ingest",
                    json=event_data
                )
                response.raise_for_status()

                logger.info(
                    f"Plate event ingested: {event.plate_text} "
                    f"(camera {event.camera_id}, conf: {event.confidence:.2f})"
                )
                return True

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    logger.error(
                        f"Camera {event.camera_id} not found in backend. "
                        "Skipping event."
                    )
                    return False
                else:
                    logger.warning(
                        f"HTTP error ingesting event (attempt {attempt + 1}/{max_retries}): "
                        f"{e.response.status_code}"
                    )

            except Exception as e:
                logger.warning(
                    f"Failed to ingest event (attempt {attempt + 1}/{max_retries}): {e}"
                )

            # Wait before retry
            if attempt < max_retries - 1:
                delay = retry_delays[min(attempt, len(retry_delays) - 1)]
                await asyncio.sleep(delay)

        logger.error(
            f"Failed to ingest plate event after {max_retries} attempts: "
            f"{event.plate_text}"
        )
        return False

    async def batch_ingest_events(
        self,
        events: List[PlateEvent]
    ) -> int:
        """
        Ingest multiple plate events concurrently.

        Args:
            events: List of plate events to send

        Returns:
            Number of successfully ingested events
        """
        if not events:
            return 0

        tasks = [self.ingest_plate_event(event) for event in events]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        success_count = sum(1 for r in results if r is True)
        logger.info(
            f"Batch ingest: {success_count}/{len(events)} events successful"
        )

        return success_count
