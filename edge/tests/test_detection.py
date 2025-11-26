"""
Detection Tests
Basic tests for vehicle and license plate detection
"""

import pytest
import numpy as np
import cv2
from edge.detection.detector import DetectionResult, Detector
from edge.detection.tracker import CentroidTracker, TrackedObject
from edge.config import DetectionModelConfig, HardwareAccelerationConfig, TrackingConfig
from datetime import datetime


class TestDetectionResult:
    """Test DetectionResult dataclass"""

    def test_detection_result_creation(self):
        """Test creating a detection result"""
        result = DetectionResult(
            class_name="vehicle",
            confidence=0.95,
            bbox=(100, 100, 200, 200),
            class_id=0,
        )

        assert result.class_name == "vehicle"
        assert result.confidence == 0.95
        assert result.bbox == (100, 100, 200, 200)
        assert result.class_id == 0

    def test_detection_result_attributes(self):
        """Test detection result attributes"""
        result = DetectionResult(
            class_name="license_plate",
            confidence=0.85,
            bbox=(150, 150, 250, 180),
            class_id=1,
        )

        x1, y1, x2, y2 = result.bbox
        assert x1 < x2
        assert y1 < y2
        assert 0 <= result.confidence <= 1.0


class TestCentroidTracker:
    """Test CentroidTracker"""

    @pytest.fixture
    def tracker_config(self):
        """Create tracker configuration"""
        return TrackingConfig(
            max_disappeared=5,
            max_distance=50.0,
            cooldown_seconds=60,
        )

    @pytest.fixture
    def tracker(self, tracker_config):
        """Create tracker instance"""
        return CentroidTracker(tracker_config)

    def test_tracker_initialization(self, tracker):
        """Test tracker initialization"""
        assert tracker.next_object_id == 0
        assert len(tracker.objects) == 0
        assert len(tracker.cooldown) == 0

    def test_register_object(self, tracker):
        """Test registering a new object"""
        detection = DetectionResult(
            class_name="vehicle",
            confidence=0.9,
            bbox=(100, 100, 200, 200),
            class_id=0,
        )

        obj = tracker.register(detection, datetime.utcnow())

        assert obj.object_id == 0
        assert obj.class_name == "vehicle"
        assert obj.confidence == 0.9
        assert len(tracker.objects) == 1

    def test_deregister_object(self, tracker):
        """Test deregistering an object"""
        detection = DetectionResult(
            class_name="vehicle",
            confidence=0.9,
            bbox=(100, 100, 200, 200),
            class_id=0,
        )

        obj = tracker.register(detection, datetime.utcnow())
        tracker.deregister(obj.object_id)

        assert len(tracker.objects) == 0

    def test_update_with_no_detections(self, tracker):
        """Test update with no detections"""
        # Register an object
        detection = DetectionResult(
            class_name="vehicle",
            confidence=0.9,
            bbox=(100, 100, 200, 200),
            class_id=0,
        )
        tracker.register(detection, datetime.utcnow())

        # Update with no detections
        tracker.update([], datetime.utcnow())

        # Object should still exist but marked as disappeared
        assert len(tracker.objects) == 1
        obj = list(tracker.objects.values())[0]
        assert obj.disappeared == 1

    def test_update_with_matching_detection(self, tracker):
        """Test update with matching detection"""
        # Register an object
        detection1 = DetectionResult(
            class_name="vehicle",
            confidence=0.9,
            bbox=(100, 100, 200, 200),
            class_id=0,
        )
        obj = tracker.register(detection1, datetime.utcnow())

        # Update with similar detection (nearby)
        detection2 = DetectionResult(
            class_name="vehicle",
            confidence=0.92,
            bbox=(105, 105, 205, 205),
            class_id=0,
        )
        tracker.update([detection2], datetime.utcnow())

        # Should still have only one object
        assert len(tracker.objects) == 1
        updated_obj = tracker.objects[obj.object_id]
        assert updated_obj.disappeared == 0
        assert len(updated_obj.history) == 2

    def test_cooldown_management(self, tracker):
        """Test cooldown management"""
        plate_text = "ABC123"

        # Check not in cooldown
        assert not tracker.is_in_cooldown(plate_text)

        # Add to cooldown
        tracker.add_to_cooldown(plate_text)
        assert tracker.is_in_cooldown(plate_text)

        # Cleanup (should not remove recent entry)
        tracker.cleanup_cooldown()
        assert tracker.is_in_cooldown(plate_text)

    def test_set_plate_text(self, tracker):
        """Test setting plate text for tracked object"""
        detection = DetectionResult(
            class_name="vehicle",
            confidence=0.9,
            bbox=(100, 100, 200, 200),
            class_id=0,
        )
        obj = tracker.register(detection, datetime.utcnow())

        # Set plate text
        tracker.set_plate_text(obj.object_id, "ABC123", 0.95)

        # Check it was set
        tracked_obj = tracker.get_object(obj.object_id)
        assert tracked_obj.plate_text == "ABC123"
        assert tracked_obj.plate_confidence == 0.95

    def test_get_active_objects(self, tracker):
        """Test getting active objects"""
        # Register multiple objects
        for i in range(3):
            detection = DetectionResult(
                class_name="vehicle",
                confidence=0.9,
                bbox=(100 + i * 50, 100, 200 + i * 50, 200),
                class_id=0,
            )
            tracker.register(detection, datetime.utcnow())

        active = tracker.get_active_objects()
        assert len(active) == 3

    def test_get_stats(self, tracker):
        """Test getting tracker statistics"""
        stats = tracker.get_stats()

        assert "tracked_objects" in stats
        assert "cooldown_entries" in stats
        assert "next_object_id" in stats


class TestDetector:
    """Test Detector (mock tests - requires actual model)"""

    @pytest.fixture
    def mock_model_config(self):
        """Create mock model configuration"""
        return DetectionModelConfig(
            type="yolov8",
            weights_path="/tmp/mock_model.pt",
            framework="pytorch",
            confidence_threshold=0.5,
            nms_threshold=0.4,
            input_size=640,
            classes=["vehicle", "license_plate"],
        )

    @pytest.fixture
    def hardware_config(self):
        """Create hardware configuration"""
        return HardwareAccelerationConfig(
            type="cpu",
            num_threads=4,
        )

    def test_detector_config(self, mock_model_config, hardware_config):
        """Test detector configuration"""
        assert mock_model_config.type == "yolov8"
        assert mock_model_config.confidence_threshold == 0.5
        assert hardware_config.type == "cpu"

    def test_extract_plate_image(self):
        """Test extracting plate region from frame"""
        # Create a dummy frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Create a mock detector (without actual model loading)
        detection = DetectionResult(
            class_name="license_plate",
            confidence=0.9,
            bbox=(100, 100, 200, 150),
            class_id=1,
        )

        # Extract region manually (simulating detector.extract_plate_image)
        x1, y1, x2, y2 = detection.bbox
        plate_img = frame[y1:y2, x1:x2]

        assert plate_img.shape == (50, 100, 3)


class TestImagePreprocessing:
    """Test image preprocessing utilities"""

    def test_image_resize(self):
        """Test image resizing"""
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        resized = cv2.resize(img, (320, 240))

        assert resized.shape == (240, 320, 3)

    def test_color_conversion(self):
        """Test BGR to RGB conversion"""
        bgr = np.zeros((100, 100, 3), dtype=np.uint8)
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

        assert rgb.shape == bgr.shape

    def test_grayscale_conversion(self):
        """Test grayscale conversion"""
        bgr = np.zeros((100, 100, 3), dtype=np.uint8)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

        assert gray.shape == (100, 100)
        assert len(gray.shape) == 2


# Integration test helpers
def create_test_frame(width=640, height=480):
    """
    Create a test frame for testing

    Args:
        width: Frame width
        height: Frame height

    Returns:
        Test frame (numpy array)
    """
    frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    return frame


def create_test_detection(class_name="vehicle", bbox=(100, 100, 200, 200)):
    """
    Create a test detection

    Args:
        class_name: Object class
        bbox: Bounding box

    Returns:
        DetectionResult instance
    """
    return DetectionResult(
        class_name=class_name,
        confidence=0.9,
        bbox=bbox,
        class_id=0 if class_name == "vehicle" else 1,
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
