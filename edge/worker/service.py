"""
Main edge worker service.
Manages multiple GStreamer pipelines and coordinates plate event processing.
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import threading

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from gstreamer.pipeline import ANPRPipeline
from worker.backend_client import BackendClient
from worker.models import PlateEvent, CameraConfig, WorkerConfig, BoundingBox

logger = logging.getLogger(__name__)


class EdgeWorkerService:
    """
    Main edge worker service.

    Responsibilities:
    - Fetch camera configurations from backend
    - Create and manage GStreamer pipelines for each camera
    - Process plate detection results
    - Send plate events to backend
    - Handle reconnection and error recovery
    """

    def __init__(self, config: WorkerConfig):
        """
        Initialize edge worker service.

        Args:
            config: Worker configuration
        """
        self.config = config
        self.backend_client = BackendClient(config.backend_url)
        self.pipelines: Dict[int, ANPRPipeline] = {}
        self.pipeline_threads: Dict[int, threading.Thread] = {}
        self.running = False
        self.event_queue = asyncio.Queue()

        # Setup logging
        logging.basicConfig(
            level=getattr(logging, config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def _on_plate_detected(self, camera_id: int, metadata: dict):
        """
        Callback for plate detection results from GStreamer pipeline.

        Args:
            camera_id: Camera ID
            metadata: Detection metadata from Hailo
        """
        try:
            # Extract plate information from Hailo metadata
            # This structure depends on the post-processing plugin output
            plate_text = metadata.get('plate_text', '')
            detection_conf = metadata.get('detection_confidence', 0.0)
            ocr_conf = metadata.get('ocr_confidence', 0.0)
            bbox_data = metadata.get('bbox', {})

            # Calculate overall confidence (average of detection and OCR)
            confidence = (detection_conf + ocr_conf) / 2.0

            # Create bounding box
            bbox = None
            if bbox_data:
                bbox = BoundingBox(
                    x=bbox_data.get('x', 0),
                    y=bbox_data.get('y', 0),
                    width=bbox_data.get('width', 0),
                    height=bbox_data.get('height', 0)
                )

            # Create plate event
            event = PlateEvent(
                camera_id=camera_id,
                plate_text=plate_text,
                confidence=confidence,
                detection_confidence=detection_conf,
                ocr_confidence=ocr_conf,
                bbox=bbox,
                timestamp=datetime.utcnow(),
                metadata=metadata
            )

            # Add to queue for async processing
            asyncio.run_coroutine_threadsafe(
                self.event_queue.put(event),
                self.loop
            )

            logger.debug(
                f"Plate detected: {plate_text} "
                f"(camera {camera_id}, conf: {confidence:.2f})"
            )

        except Exception as e:
            logger.error(f"Error processing plate detection: {e}")

    async def _event_processor(self):
        """Process plate events from queue and send to backend"""
        while self.running:
            try:
                # Get event from queue with timeout
                event = await asyncio.wait_for(
                    self.event_queue.get(),
                    timeout=1.0
                )

                # Send to backend
                await self.backend_client.ingest_plate_event(event)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in event processor: {e}")

    def _start_pipeline(self, camera: CameraConfig):
        """
        Start GStreamer pipeline for a camera.

        Args:
            camera: Camera configuration
        """
        try:
            logger.info(f"Starting pipeline for camera {camera.id} ({camera.name})")

            # Create pipeline
            pipeline = ANPRPipeline(
                camera_id=camera.id,
                rtsp_url=camera.rtsp_url,
                detection_model_path=self.config.detection_model_path,
                ocr_model_path=self.config.ocr_model_path,
                target_width=self.config.target_width,
                target_height=self.config.target_height,
                detection_threshold=self.config.detection_threshold,
                result_callback=self._on_plate_detected
            )

            # Start pipeline
            if pipeline.start():
                self.pipelines[camera.id] = pipeline

                # Run pipeline in separate thread
                thread = threading.Thread(
                    target=pipeline.run,
                    daemon=True
                )
                thread.start()
                self.pipeline_threads[camera.id] = thread

                logger.info(f"Pipeline started for camera {camera.id}")
            else:
                logger.error(f"Failed to start pipeline for camera {camera.id}")

        except Exception as e:
            logger.error(f"Error starting pipeline for camera {camera.id}: {e}")

    def _stop_pipeline(self, camera_id: int):
        """
        Stop GStreamer pipeline for a camera.

        Args:
            camera_id: Camera ID
        """
        if camera_id in self.pipelines:
            logger.info(f"Stopping pipeline for camera {camera_id}")
            self.pipelines[camera_id].stop()

            # Wait for thread to finish
            if camera_id in self.pipeline_threads:
                self.pipeline_threads[camera_id].join(timeout=5.0)
                del self.pipeline_threads[camera_id]

            del self.pipelines[camera_id]

    async def _sync_cameras(self):
        """Synchronize camera configurations with backend"""
        try:
            # Fetch cameras from backend
            cameras = await self.backend_client.get_cameras()
            logger.info(f"Fetched {len(cameras)} enabled cameras from backend")

            # Get current camera IDs
            current_ids = set(self.pipelines.keys())
            new_ids = {cam.id for cam in cameras}

            # Stop removed cameras
            for cam_id in current_ids - new_ids:
                self._stop_pipeline(cam_id)

            # Start new cameras (up to max limit)
            cameras_to_add = [
                cam for cam in cameras
                if cam.id not in current_ids
            ][:self.config.max_cameras - len(self.pipelines)]

            for camera in cameras_to_add:
                self._start_pipeline(camera)

        except Exception as e:
            logger.error(f"Error syncing cameras: {e}")

    async def run(self):
        """Run the edge worker service"""
        self.running = True
        self.loop = asyncio.get_running_loop()

        logger.info("Edge worker service starting...")

        # Wait for backend to be available
        while self.running:
            if await self.backend_client.health_check():
                logger.info("Backend is healthy")
                break
            logger.warning("Waiting for backend to be available...")
            await asyncio.sleep(5)

        # Start event processor
        event_processor_task = asyncio.create_task(self._event_processor())

        # Main loop
        try:
            while self.running:
                # Sync cameras
                await self._sync_cameras()

                # Wait before next sync
                await asyncio.sleep(self.config.reconnect_interval)

        except Exception as e:
            logger.error(f"Error in main loop: {e}")

        finally:
            # Cleanup
            logger.info("Shutting down edge worker service...")

            # Stop all pipelines
            for camera_id in list(self.pipelines.keys()):
                self._stop_pipeline(camera_id)

            # Cancel event processor
            event_processor_task.cancel()

            # Close backend client
            await self.backend_client.close()

            logger.info("Edge worker service stopped")


async def main():
    """Main entry point"""
    # Load configuration from environment or config file
    config = WorkerConfig(
        backend_url="http://localhost:8000",
        detection_model_path="/opt/hailo/models/yolov8n-plate.hef",
        ocr_model_path="/opt/hailo/models/plate-ocr.hef"
    )

    # Create and run service
    service = EdgeWorkerService(config)
    await service.run()


if __name__ == "__main__":
    asyncio.run(main())
