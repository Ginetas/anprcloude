"""
ANPR Edge Worker
License plate recognition system - Edge computing component

This package provides edge computing capabilities for the ANPR system,
including video stream processing with GStreamer, Hailo AI acceleration,
and event export to the central backend.
"""

__version__ = "0.1.0"
__author__ = "ANPR Team"

from loguru import logger
import sys

# Configure default logging
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)

__all__ = [
    "__version__",
    "__author__",
    "logger",
]
