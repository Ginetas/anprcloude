"""
Object Tracking
Centroid-based tracking for vehicles and license plates with zone crossing detection
"""

from typing import Dict, Tuple, Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from scipy.spatial import distance as dist
import numpy as np
from loguru import logger

from edge.detection.detector import DetectionResult
from edge.config import TrackingConfig


@dataclass
class TrackedObject:
    """
    Tracked object with history

    Attributes:
        object_id: Unique object ID
        class_name: Object class
        centroid: Current centroid position (x, y)
        bbox: Current bounding box (x1, y1, x2, y2)
        confidence: Detection confidence
        first_seen: Timestamp when first detected
        last_seen: Timestamp when last detected
        disappeared: Number of frames disappeared
        history: List of centroid positions
        plate_text: Recognized plate text (if applicable)
        plate_confidence: Plate recognition confidence
    """
    object_id: int
    class_name: str
    centroid: Tuple[float, float]
    bbox: Tuple[int, int, int, int]
    confidence: float
    first_seen: datetime
    last_seen: datetime
    disappeared: int = 0
    history: List[Tuple[float, float]] = field(default_factory=list)
    plate_text: Optional[str] = None
    plate_confidence: Optional[float] = None


class CentroidTracker:
    """
    Centroid-based object tracker

    Tracks objects across frames using centroid distance matching.
    Handles object disappearance, zone crossing, and cooldown management.
    """

    def __init__(self, config: TrackingConfig):
        """
        Initialize centroid tracker

        Args:
            config: Tracking configuration
        """
        self.config = config
        self.next_object_id = 0
        self.objects: Dict[int, TrackedObject] = {}
        self.cooldown: Dict[str, datetime] = {}  # plate_text -> last_detection_time

        logger.info(
            f"Centroid tracker initialized (max_disappeared={config.max_disappeared}, "
            f"max_distance={config.max_distance}, cooldown={config.cooldown_seconds}s)"
        )

    def register(self, detection: DetectionResult, timestamp: datetime) -> TrackedObject:
        """
        Register a new tracked object

        Args:
            detection: Detection result
            timestamp: Current timestamp

        Returns:
            Newly created tracked object
        """
        centroid = self._compute_centroid(detection.bbox)

        obj = TrackedObject(
            object_id=self.next_object_id,
            class_name=detection.class_name,
            centroid=centroid,
            bbox=detection.bbox,
            confidence=detection.confidence,
            first_seen=timestamp,
            last_seen=timestamp,
            history=[centroid],
        )

        self.objects[self.next_object_id] = obj
        self.next_object_id += 1

        logger.debug(f"Registered new object: ID={obj.object_id}, class={obj.class_name}")
        return obj

    def deregister(self, object_id: int):
        """
        Deregister a tracked object

        Args:
            object_id: Object ID to deregister
        """
        if object_id in self.objects:
            obj = self.objects[object_id]
            logger.debug(
                f"Deregistering object: ID={object_id}, class={obj.class_name}, "
                f"lifetime={obj.last_seen - obj.first_seen}"
            )
            del self.objects[object_id]

    def update(
        self,
        detections: List[DetectionResult],
        timestamp: datetime,
    ) -> Dict[int, TrackedObject]:
        """
        Update tracker with new detections

        Args:
            detections: List of detection results
            timestamp: Current timestamp

        Returns:
            Dictionary of tracked objects (object_id -> TrackedObject)
        """
        # If no detections, mark all objects as disappeared
        if len(detections) == 0:
            for object_id in list(self.objects.keys()):
                self.objects[object_id].disappeared += 1

                # Deregister if disappeared too long
                if self.objects[object_id].disappeared > self.config.max_disappeared:
                    self.deregister(object_id)

            return self.objects

        # Compute centroids for new detections
        input_centroids = np.array([self._compute_centroid(d.bbox) for d in detections])

        # If no tracked objects, register all detections
        if len(self.objects) == 0:
            for detection in detections:
                self.register(detection, timestamp)
            return self.objects

        # Get existing object IDs and centroids
        object_ids = list(self.objects.keys())
        object_centroids = np.array([self.objects[oid].centroid for oid in object_ids])

        # Compute distance matrix
        D = dist.cdist(object_centroids, input_centroids)

        # Match detections to existing objects
        rows = D.min(axis=1).argsort()
        cols = D.argmin(axis=1)[rows]

        used_rows = set()
        used_cols = set()

        for row, col in zip(rows, cols):
            if row in used_rows or col in used_cols:
                continue

            # Check if distance is within threshold
            if D[row, col] > self.config.max_distance:
                continue

            # Update object
            object_id = object_ids[row]
            detection = detections[col]

            self._update_object(object_id, detection, timestamp)

            used_rows.add(row)
            used_cols.add(col)

        # Handle disappeared objects
        unused_rows = set(range(D.shape[0])) - used_rows
        for row in unused_rows:
            object_id = object_ids[row]
            self.objects[object_id].disappeared += 1

            # Deregister if disappeared too long
            if self.objects[object_id].disappeared > self.config.max_disappeared:
                self.deregister(object_id)

        # Register new objects
        unused_cols = set(range(D.shape[1])) - used_cols
        for col in unused_cols:
            self.register(detections[col], timestamp)

        return self.objects

    def _update_object(self, object_id: int, detection: DetectionResult, timestamp: datetime):
        """
        Update existing tracked object

        Args:
            object_id: Object ID
            detection: New detection result
            timestamp: Current timestamp
        """
        obj = self.objects[object_id]
        centroid = self._compute_centroid(detection.bbox)

        obj.centroid = centroid
        obj.bbox = detection.bbox
        obj.confidence = detection.confidence
        obj.last_seen = timestamp
        obj.disappeared = 0
        obj.history.append(centroid)

        # Limit history size
        if len(obj.history) > 100:
            obj.history = obj.history[-100:]

    def _compute_centroid(self, bbox: Tuple[int, int, int, int]) -> Tuple[float, float]:
        """
        Compute centroid of bounding box

        Args:
            bbox: Bounding box (x1, y1, x2, y2)

        Returns:
            Centroid coordinates (cx, cy)
        """
        x1, y1, x2, y2 = bbox
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        return (cx, cy)

    def set_plate_text(self, object_id: int, plate_text: str, confidence: float):
        """
        Set plate text for tracked object

        Args:
            object_id: Object ID
            plate_text: Recognized plate text
            confidence: Recognition confidence
        """
        if object_id in self.objects:
            self.objects[object_id].plate_text = plate_text
            self.objects[object_id].plate_confidence = confidence
            logger.debug(f"Set plate text for object {object_id}: {plate_text} ({confidence:.2f})")

    def is_in_cooldown(self, plate_text: str) -> bool:
        """
        Check if plate is in cooldown period

        Args:
            plate_text: Plate text to check

        Returns:
            True if in cooldown, False otherwise
        """
        if plate_text not in self.cooldown:
            return False

        last_detection = self.cooldown[plate_text]
        cooldown_delta = timedelta(seconds=self.config.cooldown_seconds)

        return datetime.utcnow() - last_detection < cooldown_delta

    def add_to_cooldown(self, plate_text: str):
        """
        Add plate to cooldown

        Args:
            plate_text: Plate text
        """
        self.cooldown[plate_text] = datetime.utcnow()
        logger.debug(f"Added plate to cooldown: {plate_text}")

    def cleanup_cooldown(self):
        """
        Remove expired cooldown entries
        """
        now = datetime.utcnow()
        cooldown_delta = timedelta(seconds=self.config.cooldown_seconds)

        expired = [
            plate_text
            for plate_text, last_time in self.cooldown.items()
            if now - last_time > cooldown_delta
        ]

        for plate_text in expired:
            del self.cooldown[plate_text]

        if expired:
            logger.debug(f"Cleaned up {len(expired)} expired cooldown entries")

    def get_active_objects(self) -> List[TrackedObject]:
        """
        Get list of active tracked objects

        Returns:
            List of tracked objects
        """
        return list(self.objects.values())

    def get_object(self, object_id: int) -> Optional[TrackedObject]:
        """
        Get tracked object by ID

        Args:
            object_id: Object ID

        Returns:
            Tracked object or None
        """
        return self.objects.get(object_id)

    def get_stats(self) -> Dict:
        """
        Get tracker statistics

        Returns:
            Dictionary of statistics
        """
        return {
            "tracked_objects": len(self.objects),
            "cooldown_entries": len(self.cooldown),
            "next_object_id": self.next_object_id,
        }


class ZoneTracker:
    """
    Zone crossing detection for vehicles

    Tracks when objects enter/exit defined zones (e.g., entry/exit lanes)
    """

    def __init__(self):
        """Initialize zone tracker"""
        self.zones: Dict[str, np.ndarray] = {}  # zone_name -> polygon
        self.object_zones: Dict[int, Set[str]] = {}  # object_id -> set of zones

        logger.info("Zone tracker initialized")

    def add_zone(self, zone_name: str, polygon: np.ndarray):
        """
        Add detection zone

        Args:
            zone_name: Zone identifier
            polygon: Polygon coordinates [(x1, y1), (x2, y2), ...]
        """
        self.zones[zone_name] = polygon
        logger.info(f"Added zone: {zone_name} with {len(polygon)} points")

    def check_zone_crossing(
        self, object_id: int, centroid: Tuple[float, float]
    ) -> Dict[str, str]:
        """
        Check if object crossed any zones

        Args:
            object_id: Object ID
            centroid: Object centroid

        Returns:
            Dictionary of zone events (zone_name -> 'entered'/'exited')
        """
        events = {}

        # Get current zones for object
        if object_id not in self.object_zones:
            self.object_zones[object_id] = set()

        current_zones = self.object_zones[object_id]
        new_zones = set()

        # Check each zone
        for zone_name, polygon in self.zones.items():
            inside = self._point_in_polygon(centroid, polygon)

            if inside:
                new_zones.add(zone_name)
                if zone_name not in current_zones:
                    events[zone_name] = "entered"
            else:
                if zone_name in current_zones:
                    events[zone_name] = "exited"

        # Update object zones
        self.object_zones[object_id] = new_zones

        return events

    def _point_in_polygon(
        self, point: Tuple[float, float], polygon: np.ndarray
    ) -> bool:
        """
        Check if point is inside polygon using ray casting

        Args:
            point: Point coordinates (x, y)
            polygon: Polygon coordinates

        Returns:
            True if point is inside polygon
        """
        x, y = point
        n = len(polygon)
        inside = False

        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def cleanup_object(self, object_id: int):
        """
        Remove object from zone tracking

        Args:
            object_id: Object ID
        """
        if object_id in self.object_zones:
            del self.object_zones[object_id]
