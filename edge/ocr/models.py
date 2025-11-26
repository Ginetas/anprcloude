"""
OCR Models
Wrappers for different OCR engines: PaddleOCR, EasyOCR, Tesseract
"""

from typing import List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import numpy as np
import cv2
from loguru import logger

from edge.config import OCRModelConfig


@dataclass
class OCRResult:
    """
    OCR result for detected text

    Attributes:
        text: Recognized text
        confidence: Recognition confidence
        engine: OCR engine name
    """
    text: str
    confidence: float
    engine: str


class BaseOCR(ABC):
    """
    Abstract base class for OCR engines
    """

    def __init__(self, config: OCRModelConfig):
        """
        Initialize OCR engine

        Args:
            config: OCR model configuration
        """
        self.config = config
        self.model = None

        logger.info(f"Initializing {config.engine} OCR engine")

    @abstractmethod
    def load_model(self):
        """Load OCR model"""
        pass

    @abstractmethod
    def recognize(self, image: np.ndarray) -> Optional[OCRResult]:
        """
        Recognize text in image

        Args:
            image: Input image (BGR or RGB format)

        Returns:
            OCR result or None if recognition failed
        """
        pass

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for OCR

        Args:
            image: Input image

        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Resize if too small
        h, w = gray.shape
        if h < 32 or w < 100:
            scale = max(32 / h, 100 / w)
            new_h, new_w = int(h * scale), int(w * scale)
            gray = cv2.resize(gray, (new_w, new_h))

        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)

        # Contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        # Binarization (Otsu's method)
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return binary


class PaddleOCR(BaseOCR):
    """
    PaddleOCR wrapper
    High accuracy OCR engine from PaddlePaddle
    """

    def load_model(self):
        """Load PaddleOCR model"""
        try:
            from paddleocr import PaddleOCR as PaddleOCREngine

            self.model = PaddleOCREngine(
                use_angle_cls=True,
                lang=self.config.language,
                use_gpu=False,  # Can be configured based on hardware
                show_log=False,
            )

            logger.info(f"PaddleOCR model loaded (language={self.config.language})")

        except Exception as e:
            logger.error(f"Failed to load PaddleOCR: {e}")
            raise

    def recognize(self, image: np.ndarray) -> Optional[OCRResult]:
        """
        Recognize text using PaddleOCR

        Args:
            image: Input image (BGR format)

        Returns:
            OCR result or None
        """
        if self.model is None:
            self.load_model()

        try:
            # Preprocess
            processed = self.preprocess(image)

            # Run OCR
            result = self.model.ocr(processed, cls=True)

            if not result or not result[0]:
                return None

            # Extract text and confidence
            texts = []
            confidences = []

            for line in result[0]:
                text = line[1][0]
                conf = line[1][1]
                texts.append(text)
                confidences.append(conf)

            # Combine all text
            combined_text = "".join(texts).replace(" ", "").upper()
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            if avg_confidence < self.config.confidence_threshold:
                return None

            return OCRResult(
                text=combined_text,
                confidence=avg_confidence,
                engine="paddleocr",
            )

        except Exception as e:
            logger.error(f"PaddleOCR recognition failed: {e}")
            return None


class EasyOCR(BaseOCR):
    """
    EasyOCR wrapper
    Easy-to-use OCR engine with good accuracy
    """

    def load_model(self):
        """Load EasyOCR model"""
        try:
            import easyocr

            # Initialize reader
            self.model = easyocr.Reader(
                [self.config.language],
                gpu=False,  # Can be configured based on hardware
                verbose=False,
            )

            logger.info(f"EasyOCR model loaded (language={self.config.language})")

        except Exception as e:
            logger.error(f"Failed to load EasyOCR: {e}")
            raise

    def recognize(self, image: np.ndarray) -> Optional[OCRResult]:
        """
        Recognize text using EasyOCR

        Args:
            image: Input image (BGR or RGB format)

        Returns:
            OCR result or None
        """
        if self.model is None:
            self.load_model()

        try:
            # Preprocess
            processed = self.preprocess(image)

            # Run OCR
            results = self.model.readtext(processed)

            if not results:
                return None

            # Extract text and confidence
            texts = []
            confidences = []

            for bbox, text, conf in results:
                texts.append(text)
                confidences.append(conf)

            # Combine all text
            combined_text = "".join(texts).replace(" ", "").upper()
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            if avg_confidence < self.config.confidence_threshold:
                return None

            return OCRResult(
                text=combined_text,
                confidence=avg_confidence,
                engine="easyocr",
            )

        except Exception as e:
            logger.error(f"EasyOCR recognition failed: {e}")
            return None


class TesseractOCR(BaseOCR):
    """
    Tesseract OCR wrapper
    Classic open-source OCR engine
    """

    def load_model(self):
        """Load Tesseract (no explicit loading needed)"""
        try:
            import pytesseract

            # Test if Tesseract is available
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract OCR ready (version={version})")

        except Exception as e:
            logger.error(f"Failed to initialize Tesseract: {e}")
            raise

    def recognize(self, image: np.ndarray) -> Optional[OCRResult]:
        """
        Recognize text using Tesseract

        Args:
            image: Input image (BGR or RGB format)

        Returns:
            OCR result or None
        """
        try:
            import pytesseract

            # Preprocess
            processed = self.preprocess(image)

            # Configure Tesseract for license plates
            # --psm 7: Treat image as a single text line
            # --oem 3: Default OCR Engine Mode
            custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

            # Run OCR
            text = pytesseract.image_to_string(processed, config=custom_config)
            text = text.strip().replace(" ", "").upper()

            if not text:
                return None

            # Get confidence
            data = pytesseract.image_to_data(processed, config=custom_config, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0

            if avg_confidence < self.config.confidence_threshold:
                return None

            return OCRResult(
                text=text,
                confidence=avg_confidence,
                engine="tesseract",
            )

        except Exception as e:
            logger.error(f"Tesseract recognition failed: {e}")
            return None


def create_ocr_engine(config: OCRModelConfig) -> BaseOCR:
    """
    Factory function to create OCR engine

    Args:
        config: OCR model configuration

    Returns:
        OCR engine instance

    Raises:
        ValueError: If engine type is unsupported
    """
    if config.engine == "paddleocr":
        return PaddleOCR(config)
    elif config.engine == "easyocr":
        return EasyOCR(config)
    elif config.engine == "tesseract":
        return TesseractOCR(config)
    else:
        raise ValueError(f"Unsupported OCR engine: {config.engine}")
