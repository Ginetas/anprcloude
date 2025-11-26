"""
GStreamer pipeline for RTSP input with Raspberry Pi hardware H.264 decoding
and Hailo AI accelerator integration for license plate detection and OCR.
"""

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class ANPRPipeline:
    """
    GStreamer pipeline for ANPR with hardware acceleration.

    Pipeline flow:
    RTSP source → H.264 decode (hardware) → scale → format convert →
    Hailo detection → crop plates → Hailo OCR → results sink
    """

    def __init__(
        self,
        camera_id: int,
        rtsp_url: str,
        detection_model_path: str,
        ocr_model_path: str,
        target_width: int = 640,
        target_height: int = 480,
        detection_threshold: float = 0.5,
        result_callback: Optional[Callable] = None
    ):
        """
        Initialize ANPR pipeline.

        Args:
            camera_id: Unique camera identifier
            rtsp_url: RTSP stream URL
            detection_model_path: Path to Hailo detection model (.hef)
            ocr_model_path: Path to Hailo OCR model (.hef)
            target_width: Target frame width for inference
            target_height: Target frame height for inference
            detection_threshold: Detection confidence threshold
            result_callback: Callback function for results
        """
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.detection_model_path = detection_model_path
        self.ocr_model_path = ocr_model_path
        self.target_width = target_width
        self.target_height = target_height
        self.detection_threshold = detection_threshold
        self.result_callback = result_callback

        # Initialize GStreamer
        Gst.init(None)

        self.pipeline = None
        self.loop = None
        self.bus = None

    def build_pipeline(self) -> str:
        """
        Build the GStreamer pipeline string.

        Returns:
            GStreamer pipeline string
        """
        pipeline = f"""
            rtspsrc location={self.rtsp_url} latency=200 !
            rtph264depay !
            h264parse !
            v4l2h264dec !
            videoscale !
            video/x-raw,width={self.target_width},height={self.target_height} !
            videoconvert !
            hailonet hef-path={self.detection_model_path} !
            queue !
            hailofilter function-name=plate_detection so-path=./libplate_detection.so qos=false !
            hailocropper function-name=crop_plates so-path=./libplate_crop.so !
            hailonet hef-path={self.ocr_model_path} !
            queue !
            hailofilter function-name=plate_ocr so-path=./libplate_ocr.so qos=false !
            identity name=result_sink !
            fakesink
        """
        return " ".join(pipeline.split())

    def on_message(self, bus, message):
        """Handle GStreamer bus messages"""
        t = message.type

        if t == Gst.MessageType.EOS:
            logger.info(f"Camera {self.camera_id}: End-of-stream")
            self.stop()
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            logger.error(f"Camera {self.camera_id}: Error: {err}, {debug}")
            self.stop()
        elif t == Gst.MessageType.WARNING:
            warn, debug = message.parse_warning()
            logger.warning(f"Camera {self.camera_id}: Warning: {warn}, {debug}")

        return True

    def on_result(self, element, buf):
        """
        Callback for plate detection results.

        This is called when a plate is detected and OCR'd.
        """
        if self.result_callback:
            # Extract metadata from buffer
            # This will be populated by the Hailo post-processing
            meta = buf.get_meta("HailoDetectionMeta")
            if meta:
                self.result_callback(self.camera_id, meta)

    def start(self):
        """Start the GStreamer pipeline"""
        try:
            # Create pipeline
            pipeline_str = self.build_pipeline()
            logger.info(f"Camera {self.camera_id}: Creating pipeline")
            logger.debug(f"Pipeline: {pipeline_str}")

            self.pipeline = Gst.parse_launch(pipeline_str)

            # Get result sink element and connect callback
            result_sink = self.pipeline.get_by_name("result_sink")
            if result_sink:
                result_sink.connect("handoff", self.on_result)

            # Setup bus
            self.bus = self.pipeline.get_bus()
            self.bus.add_signal_watch()
            self.bus.connect("message", self.on_message)

            # Start pipeline
            ret = self.pipeline.set_state(Gst.State.PLAYING)
            if ret == Gst.StateChangeReturn.FAILURE:
                logger.error(f"Camera {self.camera_id}: Failed to start pipeline")
                return False

            logger.info(f"Camera {self.camera_id}: Pipeline started")

            # Create main loop
            self.loop = GLib.MainLoop()

            return True

        except Exception as e:
            logger.error(f"Camera {self.camera_id}: Failed to start: {e}")
            return False

    def run(self):
        """Run the pipeline (blocking)"""
        if self.loop:
            try:
                self.loop.run()
            except KeyboardInterrupt:
                logger.info(f"Camera {self.camera_id}: Interrupted by user")
                self.stop()

    def stop(self):
        """Stop the pipeline"""
        if self.pipeline:
            logger.info(f"Camera {self.camera_id}: Stopping pipeline")
            self.pipeline.set_state(Gst.State.NULL)

        if self.loop:
            self.loop.quit()

    def get_stats(self) -> dict:
        """Get pipeline statistics"""
        if not self.pipeline:
            return {}

        # Query pipeline for statistics
        # This would include FPS, latency, dropped frames, etc.
        return {
            "camera_id": self.camera_id,
            "state": self.pipeline.get_state(0)[1].value_nick,
            # Add more stats as needed
        }
