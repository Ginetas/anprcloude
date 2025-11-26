"""
OCR Ensemble
Combines multiple OCR engines using voting/consensus algorithms
"""

from typing import List, Optional, Dict
from collections import Counter
import re
from loguru import logger

from edge.ocr.models import BaseOCR, OCRResult, create_ocr_engine
from edge.config import OCRConfig
import numpy as np


class OCREnsemble:
    """
    OCR ensemble that combines results from multiple OCR engines

    Supports multiple consensus methods:
    - voting: Character-level majority voting
    - weighted: Confidence-weighted voting
    - best: Select result with highest confidence
    """

    def __init__(self, config: OCRConfig):
        """
        Initialize OCR ensemble

        Args:
            config: OCR configuration with multiple models
        """
        self.config = config
        self.engines: List[BaseOCR] = []

        # Initialize OCR engines
        for model_config in config.models:
            if not model_config.enabled:
                logger.info(f"Skipping disabled OCR engine: {model_config.engine}")
                continue

            try:
                engine = create_ocr_engine(model_config)
                engine.load_model()
                self.engines.append(engine)
                logger.info(f"Loaded OCR engine: {model_config.engine}")
            except Exception as e:
                logger.error(f"Failed to load OCR engine {model_config.engine}: {e}")

        if not self.engines:
            raise RuntimeError("No OCR engines loaded")

        logger.info(f"OCR ensemble initialized with {len(self.engines)} engine(s)")

    def recognize(self, image: np.ndarray) -> Optional[OCRResult]:
        """
        Recognize text using ensemble of OCR engines

        Args:
            image: Input image (BGR format)

        Returns:
            Consensus OCR result or None
        """
        # Run all OCR engines
        results = []
        for engine in self.engines:
            try:
                result = engine.recognize(image)
                if result:
                    results.append(result)
                    logger.debug(f"{result.engine}: {result.text} ({result.confidence:.2f})")
            except Exception as e:
                logger.error(f"OCR engine {engine.config.engine} failed: {e}")

        if not results:
            logger.debug("No OCR results from any engine")
            return None

        # Apply consensus method
        if self.config.ensemble_method == "voting":
            consensus = self._voting_consensus(results)
        elif self.config.ensemble_method == "weighted":
            consensus = self._weighted_consensus(results)
        elif self.config.ensemble_method == "best":
            consensus = self._best_consensus(results)
        else:
            logger.warning(f"Unknown ensemble method: {self.config.ensemble_method}, using voting")
            consensus = self._voting_consensus(results)

        # Validate plate format if regex is provided
        if consensus and self.config.plate_format_regex:
            if not self._validate_format(consensus.text):
                logger.debug(f"Plate text {consensus.text} does not match format regex")
                return None

        return consensus

    def _voting_consensus(self, results: List[OCRResult]) -> Optional[OCRResult]:
        """
        Character-level majority voting

        Args:
            results: List of OCR results

        Returns:
            Consensus result or None
        """
        if len(results) < self.config.min_agreement:
            logger.debug(f"Not enough results for consensus: {len(results)} < {self.config.min_agreement}")
            return None

        # Find maximum text length
        max_len = max(len(r.text) for r in results)

        # Pad all texts to same length
        padded_texts = [r.text.ljust(max_len, ' ') for r in results]

        # Character-level voting
        consensus_text = ""
        for i in range(max_len):
            chars = [text[i] for text in padded_texts if i < len(text)]
            if not chars:
                break

            # Count character votes
            counter = Counter(chars)
            most_common_char, votes = counter.most_common(1)[0]

            # Require minimum agreement
            if votes < self.config.min_agreement:
                # Not enough agreement, try to use most common
                if most_common_char != ' ':
                    consensus_text += most_common_char
            else:
                if most_common_char != ' ':
                    consensus_text += most_common_char

        # Calculate average confidence
        avg_confidence = sum(r.confidence for r in results) / len(results)

        if not consensus_text:
            return None

        return OCRResult(
            text=consensus_text.strip(),
            confidence=avg_confidence,
            engine="ensemble_voting",
        )

    def _weighted_consensus(self, results: List[OCRResult]) -> Optional[OCRResult]:
        """
        Confidence-weighted character voting

        Args:
            results: List of OCR results

        Returns:
            Consensus result or None
        """
        if len(results) < self.config.min_agreement:
            return None

        # Find maximum text length
        max_len = max(len(r.text) for r in results)

        # Character-level weighted voting
        consensus_text = ""
        for i in range(max_len):
            char_weights: Dict[str, float] = {}

            for result in results:
                if i < len(result.text):
                    char = result.text[i]
                    if char != ' ':
                        char_weights[char] = char_weights.get(char, 0.0) + result.confidence

            if not char_weights:
                break

            # Select character with highest weighted vote
            best_char = max(char_weights.items(), key=lambda x: x[1])[0]
            consensus_text += best_char

        # Calculate weighted average confidence
        total_confidence = sum(r.confidence for r in results)
        weighted_confidence = total_confidence / len(results)

        if not consensus_text:
            return None

        return OCRResult(
            text=consensus_text.strip(),
            confidence=weighted_confidence,
            engine="ensemble_weighted",
        )

    def _best_consensus(self, results: List[OCRResult]) -> Optional[OCRResult]:
        """
        Select result with highest confidence

        Args:
            results: List of OCR results

        Returns:
            Best result or None
        """
        if not results:
            return None

        # Sort by confidence
        sorted_results = sorted(results, key=lambda r: r.confidence, reverse=True)
        best = sorted_results[0]

        return OCRResult(
            text=best.text,
            confidence=best.confidence,
            engine=f"ensemble_best({best.engine})",
        )

    def _validate_format(self, text: str) -> bool:
        """
        Validate plate text against format regex

        Args:
            text: Plate text to validate

        Returns:
            True if valid, False otherwise
        """
        if not self.config.plate_format_regex:
            return True

        try:
            pattern = re.compile(self.config.plate_format_regex)
            return bool(pattern.match(text))
        except Exception as e:
            logger.error(f"Failed to validate plate format: {e}")
            return True  # Allow if validation fails

    def post_process_text(self, text: str) -> str:
        """
        Post-process OCR text to fix common errors

        Args:
            text: Raw OCR text

        Returns:
            Processed text
        """
        # Remove spaces
        text = text.replace(" ", "")

        # Common OCR error corrections for Lithuanian plates
        corrections = {
            "0": "O",  # Zero to letter O (context-dependent)
            "1": "I",  # One to letter I (context-dependent)
            "8": "B",  # Eight to letter B (context-dependent)
            "5": "S",  # Five to letter S (context-dependent)
        }

        # Apply corrections based on position (first 3 chars should be letters)
        if len(text) >= 3:
            # First 3 characters should be letters
            for i in range(3):
                if i < len(text):
                    char = text[i]
                    if char in corrections:
                        text = text[:i] + corrections[char] + text[i+1:]

            # Last 3 characters should be numbers
            if len(text) >= 6:
                reverse_corrections = {v: k for k, v in corrections.items()}
                for i in range(3, 6):
                    if i < len(text):
                        char = text[i]
                        if char in reverse_corrections:
                            text = text[:i] + reverse_corrections[char] + text[i+1:]

        return text.upper()

    def recognize_with_post_processing(self, image: np.ndarray) -> Optional[OCRResult]:
        """
        Recognize text with post-processing

        Args:
            image: Input image

        Returns:
            OCR result with post-processed text
        """
        result = self.recognize(image)

        if result:
            processed_text = self.post_process_text(result.text)
            result.text = processed_text

        return result

    def get_stats(self) -> Dict:
        """
        Get ensemble statistics

        Returns:
            Dictionary of statistics
        """
        return {
            "num_engines": len(self.engines),
            "engines": [engine.config.engine for engine in self.engines],
            "ensemble_method": self.config.ensemble_method,
            "min_agreement": self.config.min_agreement,
        }
