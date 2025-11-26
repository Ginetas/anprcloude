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


class FastPlateOCR(BaseOCR):
    """
    Fast Plate OCR wrapper
    High-performance license plate OCR optimized for Hailo-8L NPU
    https://github.com/ankandrew/fast-plate-ocr
    """

    def load_model(self):
        """Load Fast Plate OCR model"""
        try:
            from fast_plate_ocr import ONNXPlateRecognizer

            # Model path from config
            model_path = self.config.model_path or "model.onnx"

            # Initialize recognizer
            # For Hailo-8L: model should be converted to HEF format
            if hasattr(self.config, 'use_hailo') and self.config.use_hailo:
                # Use Hailo runtime
                logger.info("Loading Fast Plate OCR with Hailo-8L acceleration")
                self.model = self._load_hailo_model(model_path)
            else:
                # Use ONNX Runtime
                logger.info(f"Loading Fast Plate OCR ONNX model: {model_path}")
                self.model = ONNXPlateRecognizer(model_path)

            logger.info(f"Fast Plate OCR model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load Fast Plate OCR: {e}")
            raise

    def _load_hailo_model(self, model_path: str):
        """
        Load model for Hailo-8L NPU

        Args:
            model_path: Path to HEF model file

        Returns:
            Hailo model wrapper
        """
        try:
            from hailo_platform import (
                HEF,
                VDevice,
                HailoStreamInterface,
                InferVStreams,
                ConfigureParams,
                InputVStreamParams,
                OutputVStreamParams,
                FormatType
            )

            # Load HEF file
            hef_path = model_path.replace('.onnx', '.hef')
            logger.info(f"Loading HEF model: {hef_path}")

            hef = HEF(hef_path)

            # Get VDevice
            params = VDevice.create_params()
            params.scheduling_algorithm = VDevice.SchedulingAlgorithm.ROUND_ROBIN
            vdevice = VDevice(params)

            # Configure network
            network_group = vdevice.configure(hef)[0]
            network_group_params = network_group.create_params()

            # Create input/output streams
            input_vstreams_params = InputVStreamParams.make_from_network_group(
                network_group, quantized=False, format_type=FormatType.FLOAT32
            )
            output_vstreams_params = OutputVStreamParams.make_from_network_group(
                network_group, quantized=False, format_type=FormatType.FLOAT32
            )

            # Return wrapper
            return {
                'hef': hef,
                'vdevice': vdevice,
                'network_group': network_group,
                'input_params': input_vstreams_params,
                'output_params': output_vstreams_params,
            }

        except ImportError as e:
            logger.warning(f"Hailo platform not available: {e}")
            logger.warning("Falling back to ONNX Runtime")
            # Fallback to ONNX
            from fast_plate_ocr import ONNXPlateRecognizer
            return ONNXPlateRecognizer(model_path)
        except Exception as e:
            logger.error(f"Failed to load Hailo model: {e}")
            raise

    def recognize(self, image: np.ndarray) -> Optional[OCRResult]:
        """
        Recognize text using Fast Plate OCR

        Args:
            image: Input image (BGR format)

        Returns:
            OCR result or None
        """
        if self.model is None:
            self.load_model()

        try:
            # Check if using Hailo
            if isinstance(self.model, dict) and 'hef' in self.model:
                text, confidence = self._recognize_hailo(image)
            else:
                # Use standard ONNX inference
                text, confidence = self._recognize_onnx(image)

            if not text:
                return None

            # Clean up text
            text = text.strip().replace(" ", "").upper()

            if confidence < self.config.confidence_threshold:
                return None

            return OCRResult(
                text=text,
                confidence=confidence,
                engine="fast_plate_ocr",
            )

        except Exception as e:
            logger.error(f"Fast Plate OCR recognition failed: {e}")
            return None

    def _recognize_onnx(self, image: np.ndarray) -> tuple[str, float]:
        """
        Recognize using ONNX Runtime

        Args:
            image: Input image

        Returns:
            Tuple of (text, confidence)
        """
        # Convert BGR to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = image

        # Run inference
        result = self.model.run(rgb_image)

        # Extract text and confidence
        text = result[0] if isinstance(result, (list, tuple)) else result
        confidence = result[1] if isinstance(result, (list, tuple)) and len(result) > 1 else 0.95

        return str(text), float(confidence)

    def _recognize_hailo(self, image: np.ndarray) -> tuple[str, float]:
        """
        Recognize using Hailo-8L NPU

        Args:
            image: Input image

        Returns:
            Tuple of (text, confidence)
        """
        from hailo_platform import InferVStreams

        model_dict = self.model

        # Preprocess image
        preprocessed = self._preprocess_for_hailo(image)

        # Run inference
        with InferVStreams(model_dict['network_group'],
                          model_dict['input_params'],
                          model_dict['output_params']) as infer_pipeline:

            # Prepare input data
            input_data = {
                list(model_dict['input_params'].keys())[0]: preprocessed
            }

            # Run inference
            output = infer_pipeline.infer(input_data)

            # Post-process output
            text, confidence = self._postprocess_hailo_output(output)

            return text, confidence

    def _preprocess_for_hailo(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for Hailo inference

        Args:
            image: Input image

        Returns:
            Preprocessed image array
        """
        # Resize to model input size (typically 128x64 or similar)
        target_height = 64
        target_width = 128

        resized = cv2.resize(image, (target_width, target_height))

        # Convert BGR to RGB
        if len(resized.shape) == 3 and resized.shape[2] == 3:
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        else:
            rgb = cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)

        # Normalize to [0, 1]
        normalized = rgb.astype(np.float32) / 255.0

        # Add batch dimension
        batched = np.expand_dims(normalized, axis=0)

        return batched

    def _postprocess_hailo_output(self, output: dict) -> tuple[str, float]:
        """
        Post-process Hailo inference output

        Args:
            output: Raw output from Hailo

        Returns:
            Tuple of (text, confidence)
        """
        # Get output tensor (assuming CTC or similar output)
        output_key = list(output.keys())[0]
        logits = output[output_key]

        # Decode CTC output
        # This is a simplified version - adjust based on actual model output
        text = self._decode_ctc(logits)
        confidence = self._calculate_confidence(logits)

        return text, confidence

    def _decode_ctc(self, logits: np.ndarray) -> str:
        """
        Decode CTC output to text

        Args:
            logits: Model output logits

        Returns:
            Decoded text
        """
        # Character set for license plates
        charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        blank_idx = len(charset)

        # Get best path (greedy decoding)
        best_path = np.argmax(logits, axis=-1)

        # Remove blanks and duplicates
        decoded = []
        prev_idx = -1

        for idx in best_path.flatten():
            if idx != blank_idx and idx != prev_idx:
                if idx < len(charset):
                    decoded.append(charset[idx])
            prev_idx = idx

        return "".join(decoded)

    def _calculate_confidence(self, logits: np.ndarray) -> float:
        """
        Calculate confidence from logits

        Args:
            logits: Model output logits

        Returns:
            Confidence score
        """
        # Apply softmax
        exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
        probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)

        # Get max probabilities
        max_probs = np.max(probs, axis=-1)

        # Average confidence
        avg_confidence = np.mean(max_probs)

        return float(avg_confidence)


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
    elif config.engine == "fast_plate_ocr":
        return FastPlateOCR(config)
    else:
        raise ValueError(f"Unsupported OCR engine: {config.engine}")
