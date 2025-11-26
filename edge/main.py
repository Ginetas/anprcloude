"""
ANPR Edge Worker - Main Entry Point
Coordinates video processing, detection, OCR, and event export
"""

import argparse
import sys
import signal
from pathlib import Path
from typing import Dict, Any
import uuid
from datetime import datetime
import cv2
import numpy as np
from loguru import logger

from edge import __version__
from edge.config import load_config, EdgeWorkerConfig
from edge.pipeline import PipelineManager
from edge.detection import Detector
from edge.detection.tracker import CentroidTracker
from edge.ocr.ensemble import OCREnsemble
from edge.exporters.dispatcher import EventDispatcher, DetectionEvent


class EdgeWorker:
    """
    Main edge worker class that coordinates all components
    """

    def __init__(self, config: EdgeWorkerConfig):
        """
        Initialize edge worker

        Args:
            config: Edge worker configuration
        """
        self.config = config
        self.running = False

        # Initialize components
        logger.info(f"Initializing Edge Worker: {config.worker_id}")
        logger.info(f"Version: {__version__}")

        # Detection
        logger.info("Loading detection model...")
        self.detector = Detector(
            model_config=config.detection_model,
            hardware_config=config.hardware,
        )

        # OCR
        logger.info("Loading OCR models...")
        self.ocr_ensemble = OCREnsemble(config=config.ocr)

        # Tracking
        logger.info("Initializing object tracker...")
        self.tracker = CentroidTracker(config=config.tracking)

        # Event dispatcher
        logger.info("Initializing event exporters...")
        self.dispatcher = EventDispatcher(
            configs=config.exporters,
            queue_path=config.exporters[0].queue_path if config.exporters else None,
        )

        # Pipeline manager
        logger.info("Initializing pipeline manager...")
        self.pipeline_manager = PipelineManager(
            pipeline_config=config.pipeline,
            hardware_config=config.hardware,
        )

        # Add cameras
        for camera_config in config.cameras:
            if camera_config.enabled:
                self.pipeline_manager.add_camera(
                    camera_config=camera_config,
                    frame_callback=self.process_frame,
                )

        # Statistics
        self.stats = {
            "frames_processed": 0,
            "vehicles_detected": 0,
            "plates_detected": 0,
            "plates_recognized": 0,
            "events_exported": 0,
        }

        # Create image save directory
        if config.save_images and config.image_save_path:
            Path(config.image_save_path).mkdir(parents=True, exist_ok=True)

        logger.info("Edge worker initialized successfully")

    def process_frame(self, frame: np.ndarray, metadata: Dict[str, Any]):
        """
        Process a single frame from camera

        Args:
            frame: Video frame (RGB format)
            metadata: Frame metadata (camera_id, timestamp, etc.)
        """
        try:
            self.stats["frames_processed"] += 1
            camera_id = metadata["camera_id"]

            # Convert RGB to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Detect vehicles and plates
            vehicles, plates = self.detector.detect_vehicles_and_plates(frame_bgr)

            self.stats["vehicles_detected"] += len(vehicles)
            self.stats["plates_detected"] += len(plates)

            # Update tracker with vehicle detections
            tracked_objects = self.tracker.update(
                detections=vehicles,
                timestamp=datetime.fromisoformat(metadata["timestamp"].replace("Z", "+00:00")),
            )

            # Process each detected plate
            for plate_detection in plates:
                # Extract plate image
                plate_img = self.detector.extract_plate_image(frame_bgr, plate_detection)
                if plate_img is None:
                    continue

                # Run OCR
                ocr_result = self.ocr_ensemble.recognize_with_post_processing(plate_img)
                if ocr_result is None:
                    continue

                plate_text = ocr_result.text
                confidence = ocr_result.confidence

                logger.info(
                    f"[{camera_id}] Plate detected: {plate_text} "
                    f"(confidence: {confidence:.2f})"
                )

                # Check cooldown
                if self.tracker.is_in_cooldown(plate_text):
                    logger.debug(f"Plate {plate_text} is in cooldown, skipping")
                    continue

                # Find associated vehicle (closest centroid)
                vehicle_detection = self._find_closest_vehicle(
                    plate_detection, vehicles
                )

                # Create detection event
                event = self._create_event(
                    camera_id=camera_id,
                    camera_name=metadata.get("camera_name", "Unknown"),
                    timestamp=metadata["timestamp"],
                    plate_text=plate_text,
                    confidence=confidence,
                    plate_detection=plate_detection,
                    vehicle_detection=vehicle_detection,
                    frame=frame_bgr,
                )

                # Dispatch event
                self.dispatcher.dispatch(event)
                self.stats["events_exported"] += 1
                self.stats["plates_recognized"] += 1

                # Add to cooldown
                self.tracker.add_to_cooldown(plate_text)

                logger.info(
                    f"[{camera_id}] Event exported: {event.event_id} - {plate_text}"
                )

            # Periodic cleanup
            if self.stats["frames_processed"] % 100 == 0:
                self.tracker.cleanup_cooldown()
                self._log_stats()

        except Exception as e:
            logger.error(f"Error processing frame: {e}", exc_info=True)

    def _find_closest_vehicle(self, plate_detection, vehicles):
        """
        Find closest vehicle to plate detection

        Args:
            plate_detection: Plate detection result
            vehicles: List of vehicle detections

        Returns:
            Closest vehicle detection or None
        """
        if not vehicles:
            return None

        plate_cx = (plate_detection.bbox[0] + plate_detection.bbox[2]) / 2
        plate_cy = (plate_detection.bbox[1] + plate_detection.bbox[3]) / 2

        min_dist = float('inf')
        closest_vehicle = None

        for vehicle in vehicles:
            vehicle_cx = (vehicle.bbox[0] + vehicle.bbox[2]) / 2
            vehicle_cy = (vehicle.bbox[1] + vehicle.bbox[3]) / 2

            dist = ((plate_cx - vehicle_cx) ** 2 + (plate_cy - vehicle_cy) ** 2) ** 0.5

            if dist < min_dist:
                min_dist = dist
                closest_vehicle = vehicle

        return closest_vehicle

    def _create_event(
        self,
        camera_id: str,
        camera_name: str,
        timestamp: str,
        plate_text: str,
        confidence: float,
        plate_detection,
        vehicle_detection,
        frame: np.ndarray,
    ) -> DetectionEvent:
        """
        Create detection event

        Args:
            camera_id: Camera identifier
            camera_name: Camera name
            timestamp: Event timestamp
            plate_text: Recognized plate text
            confidence: Recognition confidence
            plate_detection: Plate detection result
            vehicle_detection: Vehicle detection result
            frame: Video frame

        Returns:
            DetectionEvent instance
        """
        event_id = str(uuid.uuid4())

        # Save image if enabled
        image_path = None
        if self.config.save_images and self.config.image_save_path:
            image_filename = f"{event_id}_{plate_text}.jpg"
            image_path = str(Path(self.config.image_save_path) / image_filename)

            try:
                # Draw bounding boxes
                annotated = frame.copy()
                if vehicle_detection:
                    x1, y1, x2, y2 = vehicle_detection.bbox
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)

                x1, y1, x2, y2 = plate_detection.bbox
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(
                    annotated, plate_text, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2
                )

                cv2.imwrite(image_path, annotated)
            except Exception as e:
                logger.error(f"Failed to save image: {e}")
                image_path = None

        event = DetectionEvent(
            event_id=event_id,
            worker_id=self.config.worker_id,
            camera_id=camera_id,
            camera_name=camera_name,
            timestamp=timestamp,
            plate_text=plate_text,
            confidence=confidence,
            vehicle_bbox=vehicle_detection.bbox if vehicle_detection else None,
            plate_bbox=plate_detection.bbox,
            image_path=image_path,
            metadata={
                "vehicle_confidence": vehicle_detection.confidence if vehicle_detection else None,
                "plate_confidence": plate_detection.confidence,
            },
        )

        return event

    def _log_stats(self):
        """Log statistics"""
        logger.info(
            f"Stats: Frames={self.stats['frames_processed']}, "
            f"Vehicles={self.stats['vehicles_detected']}, "
            f"Plates={self.stats['plates_detected']}, "
            f"Recognized={self.stats['plates_recognized']}, "
            f"Events={self.stats['events_exported']}"
        )

    def start(self):
        """Start edge worker"""
        logger.info("Starting edge worker...")
        self.running = True

        # Start pipelines
        self.pipeline_manager.start_all()

        logger.info(f"Edge worker {self.config.worker_id} is running")
        logger.info("Press Ctrl+C to stop")

        try:
            # Keep main thread alive
            signal.pause()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
            self.stop()

    def stop(self):
        """Stop edge worker"""
        logger.info("Stopping edge worker...")
        self.running = False

        # Stop pipelines
        self.pipeline_manager.stop_all()

        # Stop dispatcher
        self.dispatcher.stop()

        # Log final stats
        self._log_stats()

        logger.info("Edge worker stopped")


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="ANPR Edge Worker - License Plate Recognition System"
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Configuration file path (default: config.yaml)",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (overrides config)",
    )

    parser.add_argument(
        "--cameras",
        type=str,
        help="Separate cameras configuration file",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test configuration without starting",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"ANPR Edge Worker v{__version__}",
    )

    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()

    # Load configuration
    try:
        config = load_config(args.config)

        # Override log level if specified
        if args.log_level:
            config.log_level = args.log_level

        # Configure logging
        logger.remove()
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=config.log_level,
        )

        logger.info(f"Configuration loaded from {args.config}")

    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)

    # Dry run mode
    if args.dry_run:
        logger.info("Dry run mode - configuration is valid")
        logger.info(f"Worker ID: {config.worker_id}")
        logger.info(f"Cameras: {len(config.cameras)}")
        logger.info(f"Hardware: {config.hardware.type}")
        logger.info(f"Detection model: {config.detection_model.type}")
        logger.info(f"OCR engines: {len(config.ocr.models)}")
        logger.info(f"Exporters: {len(config.exporters)}")
        sys.exit(0)

    # Create and start edge worker
    try:
        worker = EdgeWorker(config)

        # Setup signal handlers
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}")
            worker.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start worker
        worker.start()

    except Exception as e:
        logger.error(f"Edge worker failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
