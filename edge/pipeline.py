"""
GStreamer Video Pipeline
Handles RTSP stream ingestion, frame extraction, and hardware acceleration
"""

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

import threading
import numpy as np
import cv2
from typing import Callable, Optional, Dict, Any
from queue import Queue, Full
from loguru import logger
from datetime import datetime

from edge.config import CameraConfig, PipelineConfig, HardwareAccelerationConfig


# Initialize GStreamer
Gst.init(None)


class GStreamerPipeline:
    """
    GStreamer pipeline for processing RTSP video streams

    Handles:
    - RTSP stream connection
    - Hardware-accelerated decoding
    - Frame extraction and conversion
    - Multi-threaded frame processing
    """

    def __init__(
        self,
        camera_config: CameraConfig,
        pipeline_config: PipelineConfig,
        hardware_config: HardwareAccelerationConfig,
        frame_callback: Callable[[np.ndarray, Dict[str, Any]], None],
        max_queue_size: int = 100,
    ):
        """
        Initialize GStreamer pipeline

        Args:
            camera_config: Camera configuration
            pipeline_config: Pipeline configuration
            hardware_config: Hardware acceleration configuration
            frame_callback: Callback function for processing frames
            max_queue_size: Maximum frame queue size
        """
        self.camera_config = camera_config
        self.pipeline_config = pipeline_config
        self.hardware_config = hardware_config
        self.frame_callback = frame_callback
        self.max_queue_size = max_queue_size

        self.pipeline: Optional[Gst.Pipeline] = None
        self.loop: Optional[GLib.MainLoop] = None
        self.thread: Optional[threading.Thread] = None
        self.frame_queue: Queue = Queue(maxsize=max_queue_size)
        self.running = False
        self.frame_count = 0
        self.last_frame_time = None

        logger.info(f"Initialized pipeline for camera: {camera_config.name} ({camera_config.id})")

    def _build_pipeline(self) -> str:
        """
        Build GStreamer pipeline string based on configuration

        Returns:
            GStreamer pipeline string
        """
        rtsp_url = self.camera_config.rtsp_url
        fps = self.camera_config.fps

        # Base RTSP source
        pipeline_parts = [
            f"rtspsrc location={rtsp_url}",
            f"latency={self.pipeline_config.latency}",
            f"drop-on-latency={str(self.pipeline_config.drop_on_latency).lower()}",
            "protocols=tcp",
            "!",
        ]

        # RTP depayload
        pipeline_parts.extend([
            "rtph264depay",
            "!",
        ])

        # Video decoder - hardware accelerated if available
        if self.pipeline_config.use_hw_decoder:
            if self.hardware_config.type == "gpu" and self.hardware_config.use_cuda:
                # NVIDIA GPU decoding
                pipeline_parts.extend(["nvh264dec", "!"])
            elif self.hardware_config.type == "cpu":
                # Check for VA-API (Intel/AMD)
                pipeline_parts.extend(["vaapih264dec", "!", "vaapipostproc", "!"])
            else:
                # Fallback to software decoder
                pipeline_parts.extend(["avdec_h264", "!"])
        else:
            # Software decoder
            pipeline_parts.extend(["avdec_h264", "!"])

        # Video rate limiting
        pipeline_parts.extend([
            f"videorate",
            "!",
            f"video/x-raw,framerate={fps}/1",
            "!",
        ])

        # Convert to RGB for processing
        pipeline_parts.extend([
            "videoconvert",
            "!",
            "video/x-raw,format=RGB",
            "!",
        ])

        # Resolution scaling if specified
        if self.camera_config.resolution:
            width, height = self.camera_config.resolution.split('x')
            pipeline_parts.extend([
                "videoscale",
                "!",
                f"video/x-raw,width={width},height={height}",
                "!",
            ])

        # App sink for frame extraction
        pipeline_parts.extend([
            "appsink name=sink",
            "emit-signals=true",
            f"sync={str(self.pipeline_config.sync).lower()}",
            "max-buffers=1",
            "drop=true",
        ])

        pipeline_str = " ".join(pipeline_parts)
        logger.debug(f"Pipeline string: {pipeline_str}")
        return pipeline_str

    def _on_new_sample(self, sink: Gst.Element) -> Gst.FlowReturn:
        """
        Callback for new frame from appsink

        Args:
            sink: GStreamer appsink element

        Returns:
            Flow return status
        """
        sample = sink.emit("pull-sample")
        if sample is None:
            return Gst.FlowReturn.ERROR

        try:
            # Extract buffer from sample
            buffer = sample.get_buffer()
            caps = sample.get_caps()

            # Get frame dimensions
            structure = caps.get_structure(0)
            width = structure.get_value("width")
            height = structure.get_value("height")

            # Extract frame data
            success, map_info = buffer.map(Gst.MapFlags.READ)
            if not success:
                logger.warning("Failed to map buffer")
                return Gst.FlowReturn.ERROR

            # Convert to numpy array
            frame_data = np.ndarray(
                shape=(height, width, 3),
                dtype=np.uint8,
                buffer=map_info.data
            )

            # Copy frame (GStreamer will reuse the buffer)
            frame = frame_data.copy()
            buffer.unmap(map_info)

            # Frame metadata
            metadata = {
                "camera_id": self.camera_config.id,
                "camera_name": self.camera_config.name,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "frame_number": self.frame_count,
                "width": width,
                "height": height,
            }

            self.frame_count += 1
            self.last_frame_time = datetime.utcnow()

            # Add to processing queue (non-blocking)
            try:
                self.frame_queue.put_nowait((frame, metadata))
            except Full:
                logger.warning(f"Frame queue full for camera {self.camera_config.id}, dropping frame")

            return Gst.FlowReturn.OK

        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return Gst.FlowReturn.ERROR

    def _on_bus_message(self, bus: Gst.Bus, message: Gst.Message) -> bool:
        """
        Handle GStreamer bus messages

        Args:
            bus: GStreamer bus
            message: Bus message

        Returns:
            True to continue receiving messages
        """
        msg_type = message.type

        if msg_type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            logger.error(f"Pipeline error: {err} - {debug}")
            self.stop()
            return False

        elif msg_type == Gst.MessageType.WARNING:
            err, debug = message.parse_warning()
            logger.warning(f"Pipeline warning: {err} - {debug}")

        elif msg_type == Gst.MessageType.EOS:
            logger.info(f"End of stream for camera {self.camera_config.id}")
            self.stop()
            return False

        elif msg_type == Gst.MessageType.STATE_CHANGED:
            if message.src == self.pipeline:
                old_state, new_state, pending = message.parse_state_changed()
                logger.debug(
                    f"Pipeline state changed: {old_state.value_nick} -> {new_state.value_nick}"
                )

        return True

    def _process_frames(self):
        """
        Process frames from queue in separate thread
        """
        logger.info(f"Frame processing thread started for camera {self.camera_config.id}")

        while self.running:
            try:
                # Get frame with timeout
                frame, metadata = self.frame_queue.get(timeout=1.0)

                # Call frame callback
                try:
                    self.frame_callback(frame, metadata)
                except Exception as e:
                    logger.error(f"Error in frame callback: {e}")

            except:
                # Queue timeout, continue
                continue

        logger.info(f"Frame processing thread stopped for camera {self.camera_config.id}")

    def start(self):
        """
        Start the GStreamer pipeline
        """
        if self.running:
            logger.warning(f"Pipeline already running for camera {self.camera_config.id}")
            return

        try:
            # Build pipeline
            pipeline_str = self._build_pipeline()
            self.pipeline = Gst.parse_launch(pipeline_str)

            # Get appsink element
            sink = self.pipeline.get_by_name("sink")
            if not sink:
                raise RuntimeError("Failed to get appsink element")

            # Connect new-sample callback
            sink.connect("new-sample", self._on_new_sample)

            # Setup bus watch
            bus = self.pipeline.get_bus()
            bus.add_signal_watch()
            bus.connect("message", self._on_bus_message)

            # Start frame processing thread
            self.running = True
            self.thread = threading.Thread(target=self._process_frames, daemon=True)
            self.thread.start()

            # Start pipeline
            ret = self.pipeline.set_state(Gst.State.PLAYING)
            if ret == Gst.StateChangeReturn.FAILURE:
                raise RuntimeError("Failed to start pipeline")

            logger.info(f"Pipeline started for camera {self.camera_config.name}")

        except Exception as e:
            logger.error(f"Failed to start pipeline: {e}")
            self.running = False
            raise

    def stop(self):
        """
        Stop the GStreamer pipeline
        """
        if not self.running:
            return

        logger.info(f"Stopping pipeline for camera {self.camera_config.id}")

        self.running = False

        # Stop pipeline
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)

        # Wait for processing thread
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5.0)

        logger.info(f"Pipeline stopped for camera {self.camera_config.id}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get pipeline statistics

        Returns:
            Dictionary of statistics
        """
        return {
            "camera_id": self.camera_config.id,
            "camera_name": self.camera_config.name,
            "running": self.running,
            "frame_count": self.frame_count,
            "queue_size": self.frame_queue.qsize(),
            "last_frame_time": self.last_frame_time.isoformat() + "Z" if self.last_frame_time else None,
        }


class PipelineManager:
    """
    Manages multiple GStreamer pipelines for multiple cameras
    """

    def __init__(
        self,
        pipeline_config: PipelineConfig,
        hardware_config: HardwareAccelerationConfig,
    ):
        """
        Initialize pipeline manager

        Args:
            pipeline_config: Pipeline configuration
            hardware_config: Hardware acceleration configuration
        """
        self.pipeline_config = pipeline_config
        self.hardware_config = hardware_config
        self.pipelines: Dict[str, GStreamerPipeline] = {}

        logger.info("Pipeline manager initialized")

    def add_camera(
        self,
        camera_config: CameraConfig,
        frame_callback: Callable[[np.ndarray, Dict[str, Any]], None],
    ):
        """
        Add a camera pipeline

        Args:
            camera_config: Camera configuration
            frame_callback: Frame processing callback
        """
        if camera_config.id in self.pipelines:
            logger.warning(f"Camera {camera_config.id} already exists")
            return

        if not camera_config.enabled:
            logger.info(f"Camera {camera_config.id} is disabled, skipping")
            return

        pipeline = GStreamerPipeline(
            camera_config=camera_config,
            pipeline_config=self.pipeline_config,
            hardware_config=self.hardware_config,
            frame_callback=frame_callback,
        )

        self.pipelines[camera_config.id] = pipeline
        logger.info(f"Added camera pipeline: {camera_config.name} ({camera_config.id})")

    def start_all(self):
        """
        Start all camera pipelines
        """
        logger.info(f"Starting {len(self.pipelines)} camera pipeline(s)")

        for camera_id, pipeline in self.pipelines.items():
            try:
                pipeline.start()
            except Exception as e:
                logger.error(f"Failed to start pipeline for camera {camera_id}: {e}")

    def stop_all(self):
        """
        Stop all camera pipelines
        """
        logger.info("Stopping all camera pipelines")

        for camera_id, pipeline in self.pipelines.items():
            try:
                pipeline.stop()
            except Exception as e:
                logger.error(f"Failed to stop pipeline for camera {camera_id}: {e}")

    def get_pipeline(self, camera_id: str) -> Optional[GStreamerPipeline]:
        """
        Get pipeline by camera ID

        Args:
            camera_id: Camera identifier

        Returns:
            Pipeline instance or None
        """
        return self.pipelines.get(camera_id)

    def get_all_stats(self) -> Dict[str, Any]:
        """
        Get statistics for all pipelines

        Returns:
            Dictionary of pipeline statistics
        """
        return {
            camera_id: pipeline.get_stats()
            for camera_id, pipeline in self.pipelines.items()
        }
