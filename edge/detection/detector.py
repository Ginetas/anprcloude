"""
Object Detection
Supports multiple detection models and frameworks for vehicle and license plate detection
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import numpy as np
import cv2
from loguru import logger

from edge.config import DetectionModelConfig, HardwareAccelerationConfig


@dataclass
class DetectionResult:
    """
    Detection result for a single object

    Attributes:
        class_name: Object class (vehicle, license_plate, etc.)
        confidence: Detection confidence score
        bbox: Bounding box coordinates (x1, y1, x2, y2)
        class_id: Class ID
    """
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    class_id: int


class BaseDetector(ABC):
    """
    Abstract base class for object detectors
    """

    def __init__(
        self,
        model_config: DetectionModelConfig,
        hardware_config: HardwareAccelerationConfig,
    ):
        """
        Initialize detector

        Args:
            model_config: Detection model configuration
            hardware_config: Hardware acceleration configuration
        """
        self.model_config = model_config
        self.hardware_config = hardware_config
        self.model = None

        logger.info(
            f"Initializing {model_config.type} detector with {model_config.framework} framework"
        )

    @abstractmethod
    def load_model(self):
        """Load detection model"""
        pass

    @abstractmethod
    def detect(self, frame: np.ndarray) -> List[DetectionResult]:
        """
        Detect objects in frame

        Args:
            frame: Input image (BGR format)

        Returns:
            List of detection results
        """
        pass

    def preprocess(self, frame: np.ndarray) -> np.ndarray:
        """
        Preprocess frame for detection

        Args:
            frame: Input image

        Returns:
            Preprocessed image
        """
        # Resize to model input size
        input_size = self.model_config.input_size
        resized = cv2.resize(frame, (input_size, input_size))

        # Convert BGR to RGB
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

        # Normalize
        normalized = rgb.astype(np.float32) / 255.0

        return normalized

    def postprocess(
        self,
        detections: np.ndarray,
        original_shape: Tuple[int, int],
    ) -> List[DetectionResult]:
        """
        Postprocess model outputs to detection results

        Args:
            detections: Raw model detections
            original_shape: Original image shape (height, width)

        Returns:
            List of detection results
        """
        results = []
        input_size = self.model_config.input_size
        h_orig, w_orig = original_shape[:2]

        for det in detections:
            confidence = float(det[4])
            if confidence < self.model_config.confidence_threshold:
                continue

            # Get class ID and name
            class_id = int(det[5])
            if class_id >= len(self.model_config.classes):
                continue

            class_name = self.model_config.classes[class_id]

            # Scale bounding box to original image size
            x1 = int(det[0] * w_orig / input_size)
            y1 = int(det[1] * h_orig / input_size)
            x2 = int(det[2] * w_orig / input_size)
            y2 = int(det[3] * h_orig / input_size)

            # Clamp to image boundaries
            x1 = max(0, min(x1, w_orig))
            y1 = max(0, min(y1, h_orig))
            x2 = max(0, min(x2, w_orig))
            y2 = max(0, min(y2, h_orig))

            results.append(
                DetectionResult(
                    class_name=class_name,
                    confidence=confidence,
                    bbox=(x1, y1, x2, y2),
                    class_id=class_id,
                )
            )

        return results


class YOLOv8Detector(BaseDetector):
    """
    YOLOv8 detector using Ultralytics
    """

    def load_model(self):
        """Load YOLOv8 model"""
        from ultralytics import YOLO

        try:
            self.model = YOLO(self.model_config.weights_path)

            # Set device
            if self.hardware_config.use_cuda and self.hardware_config.type == "gpu":
                device = f"cuda:{self.hardware_config.cuda_device}"
            else:
                device = "cpu"

            self.model.to(device)

            logger.info(f"YOLOv8 model loaded from {self.model_config.weights_path} on {device}")

        except Exception as e:
            logger.error(f"Failed to load YOLOv8 model: {e}")
            raise

    def detect(self, frame: np.ndarray) -> List[DetectionResult]:
        """
        Detect objects using YOLOv8

        Args:
            frame: Input image (BGR format)

        Returns:
            List of detection results
        """
        if self.model is None:
            self.load_model()

        try:
            # Run inference
            results = self.model(
                frame,
                conf=self.model_config.confidence_threshold,
                iou=self.model_config.nms_threshold,
                verbose=False,
            )[0]

            # Convert to DetectionResult list
            detections = []
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])

                if class_id < len(self.model_config.classes):
                    class_name = self.model_config.classes[class_id]
                else:
                    class_name = f"class_{class_id}"

                detections.append(
                    DetectionResult(
                        class_name=class_name,
                        confidence=confidence,
                        bbox=(int(x1), int(y1), int(x2), int(y2)),
                        class_id=class_id,
                    )
                )

            return detections

        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return []


class YOLOv5Detector(BaseDetector):
    """
    YOLOv5 detector using PyTorch Hub
    """

    def load_model(self):
        """Load YOLOv5 model"""
        import torch

        try:
            # Load model from torch hub or local weights
            if self.model_config.weights_path.endswith('.pt'):
                self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=self.model_config.weights_path)
            else:
                self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

            # Set device
            if self.hardware_config.use_cuda and self.hardware_config.type == "gpu":
                device = f"cuda:{self.hardware_config.cuda_device}"
            else:
                device = "cpu"

            self.model.to(device)
            self.model.conf = self.model_config.confidence_threshold
            self.model.iou = self.model_config.nms_threshold

            logger.info(f"YOLOv5 model loaded from {self.model_config.weights_path} on {device}")

        except Exception as e:
            logger.error(f"Failed to load YOLOv5 model: {e}")
            raise

    def detect(self, frame: np.ndarray) -> List[DetectionResult]:
        """
        Detect objects using YOLOv5

        Args:
            frame: Input image (BGR format)

        Returns:
            List of detection results
        """
        if self.model is None:
            self.load_model()

        try:
            # Run inference
            results = self.model(frame)

            # Parse results
            detections = []
            for *xyxy, conf, cls_id in results.xyxy[0].cpu().numpy():
                x1, y1, x2, y2 = map(int, xyxy)
                confidence = float(conf)
                class_id = int(cls_id)

                if class_id < len(self.model_config.classes):
                    class_name = self.model_config.classes[class_id]
                else:
                    class_name = f"class_{class_id}"

                detections.append(
                    DetectionResult(
                        class_name=class_name,
                        confidence=confidence,
                        bbox=(x1, y1, x2, y2),
                        class_id=class_id,
                    )
                )

            return detections

        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return []


class ONNXDetector(BaseDetector):
    """
    ONNX Runtime detector for cross-platform inference
    """

    def load_model(self):
        """Load ONNX model"""
        import onnxruntime as ort

        try:
            # Set execution providers
            providers = []
            if self.hardware_config.use_cuda and self.hardware_config.type == "gpu":
                providers.append('CUDAExecutionProvider')
            providers.append('CPUExecutionProvider')

            # Create inference session
            self.model = ort.InferenceSession(
                self.model_config.weights_path,
                providers=providers
            )

            # Get input name
            self.input_name = self.model.get_inputs()[0].name

            logger.info(f"ONNX model loaded from {self.model_config.weights_path}")
            logger.info(f"Execution providers: {self.model.get_providers()}")

        except Exception as e:
            logger.error(f"Failed to load ONNX model: {e}")
            raise

    def detect(self, frame: np.ndarray) -> List[DetectionResult]:
        """
        Detect objects using ONNX Runtime

        Args:
            frame: Input image (BGR format)

        Returns:
            List of detection results
        """
        if self.model is None:
            self.load_model()

        try:
            # Preprocess
            input_tensor = self.preprocess(frame)
            input_tensor = np.expand_dims(input_tensor, axis=0)  # Add batch dimension
            input_tensor = input_tensor.transpose(0, 3, 1, 2)  # NHWC to NCHW

            # Run inference
            outputs = self.model.run(None, {self.input_name: input_tensor})

            # Postprocess (model-specific, this is a generic example)
            detections = self.postprocess(outputs[0], frame.shape)

            return detections

        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return []


class Detector:
    """
    Unified detector interface that supports multiple model types
    """

    def __init__(
        self,
        model_config: DetectionModelConfig,
        hardware_config: HardwareAccelerationConfig,
    ):
        """
        Initialize detector

        Args:
            model_config: Detection model configuration
            hardware_config: Hardware acceleration configuration
        """
        self.model_config = model_config
        self.hardware_config = hardware_config

        # Create appropriate detector based on model type and framework
        if model_config.framework == "onnx":
            self.detector = ONNXDetector(model_config, hardware_config)
        elif model_config.type == "yolov8":
            self.detector = YOLOv8Detector(model_config, hardware_config)
        elif model_config.type == "yolov5":
            self.detector = YOLOv5Detector(model_config, hardware_config)
        else:
            raise ValueError(f"Unsupported model type: {model_config.type}")

        # Load model
        self.detector.load_model()

        logger.info("Detector initialized successfully")

    def detect(self, frame: np.ndarray) -> List[DetectionResult]:
        """
        Detect objects in frame

        Args:
            frame: Input image (BGR format)

        Returns:
            List of detection results
        """
        return self.detector.detect(frame)

    def detect_vehicles_and_plates(
        self, frame: np.ndarray
    ) -> Tuple[List[DetectionResult], List[DetectionResult]]:
        """
        Detect vehicles and license plates separately

        Args:
            frame: Input image (BGR format)

        Returns:
            Tuple of (vehicles, plates) detection results
        """
        detections = self.detect(frame)

        vehicles = [d for d in detections if d.class_name == "vehicle"]
        plates = [d for d in detections if d.class_name == "license_plate"]

        return vehicles, plates

    def extract_plate_image(
        self, frame: np.ndarray, detection: DetectionResult, padding: int = 5
    ) -> Optional[np.ndarray]:
        """
        Extract license plate region from frame

        Args:
            frame: Input image
            detection: Plate detection result
            padding: Padding around bounding box

        Returns:
            Cropped plate image or None
        """
        x1, y1, x2, y2 = detection.bbox

        # Add padding
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(frame.shape[1], x2 + padding)
        y2 = min(frame.shape[0], y2 + padding)

        # Extract region
        plate_img = frame[y1:y2, x1:x2]

        if plate_img.size == 0:
            return None

        return plate_img
