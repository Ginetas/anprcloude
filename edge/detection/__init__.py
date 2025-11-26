"""
Detection Module
Vehicle and license plate detection using deep learning models
"""

from edge.detection.detector import Detector, DetectionResult
from edge.detection.tracker import CentroidTracker

__all__ = [
    "Detector",
    "DetectionResult",
    "CentroidTracker",
]
