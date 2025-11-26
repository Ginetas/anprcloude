"""
OCR Module
License plate text recognition using multiple OCR engines
"""

from edge.ocr.models import BaseOCR, OCRResult, PaddleOCR, EasyOCR, TesseractOCR
from edge.ocr.ensemble import OCREnsemble

__all__ = [
    "BaseOCR",
    "OCRResult",
    "PaddleOCR",
    "EasyOCR",
    "TesseractOCR",
    "OCREnsemble",
]
