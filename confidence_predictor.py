"""
Confidence-Aware Predictor (MANDATORY)
======================================

Provides confidence-aware emotion prediction with detailed output.
This module is MANDATORY and always active.

OUTPUT STRUCTURE:
-----------------
{
    "emotion": str,           # Predicted emotion label
    "confidence": float,      # Confidence score (0-1)
    "confidence_level": str,  # "high", "medium", or "low"
    "is_uncertain": bool,     # True if confidence < threshold
    "probabilities": dict,    # Per-class probabilities
    "metadata": dict          # Additional info (optional)
}

CONFIDENCE LEVELS:
------------------
- High:   confidence >= 0.75
- Medium: confidence >= 0.50
- Low:    confidence < 0.50

UNCERTAINTY:
------------
If confidence < UNCERTAINTY_THRESHOLD (default 0.35):
- is_uncertain = True
- emotion is still provided but flagged as uncertain
- Consumer should NOT force a strong emotion response

"""

import numpy as np
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import logging

from src import config
from src.features import FeatureManager
from src.context_window import ContextWindow

logger = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    """
    Structured prediction result with confidence information.

    Attributes:
        emotion: Predicted emotion label
        confidence: Confidence score (0 to 1)
        confidence_level: Categorical level ("high", "medium", "low")
        is_uncertain: Whether prediction is uncertain
        probabilities: Dict mapping class names to probabilities
        metadata: Additional information (optional)
    """
    emotion: str
    confidence: float
    confidence_level: str
    is_uncertain: bool
    probabilities: Dict[str, float]
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        if result['metadata'] is None:
            del result['metadata']
        return result

    def __repr__(self) -> str:
        uncertain_str = " (UNCERTAIN)" if self.is_uncertain else ""
        return (
            f"PredictionResult(emotion='{self.emotion}', "
            f"confidence={self.confidence:.3f}, "
            f"level='{self.confidence_level}'{uncertain_str})"
        )


class ConfidenceAwarePredictor:
    """
    Main prediction interface with confidence-aware output.

    Combines:
    - Feature extraction (via FeatureManager)
    - Optional context window
    - Model prediction
    - Confidence scoring and thresholding

    This is the recommended entry point for all predictions.
    """

    def __init__(
        self,
        feature_manager: FeatureManager,
        model,
        class_names: Optional[List[str]] = None,
        use_context: bool = True
    ):
        """
        Initialize ConfidenceAwarePredictor.

        Args:
            feature_manager: FeatureManager for feature extraction
            model: Trained classifier with predict_proba method
            class_names: List of class names (inferred from model if not provided)
            use_context: Whether to use context window (default True if enabled)
        """
        self.feature_manager = feature_manager
        self.model = model

        # Get class names
        if class_names is not None:
            self.class_names = list(class_names)
        elif hasattr(model, 'classes_'):
            self.class_names = list(model.classes_)
        else:
            self.class_names = ['neutral', 'positive', 'distress', 'strong_distress']

        # Initialize context window if enabled
        self.context_window = None
        if use_context and config.ENABLE_CONTEXT_WINDOW:
            self.context_window = ContextWindow(feature_manager)

        # Confidence thresholds from config
        self.high_threshold = config.CONFIDENCE_HIGH_THRESHOLD
        self.medium_threshold = config.CONFIDENCE_MEDIUM_THRESHOLD
        self.uncertainty_threshold = config.UNCERTAINTY_THRESHOLD

    def predict(
        self,
        text: str,
        past_messages: Optional[List[str]] = None,
        include_metadata: bool = False
    ) -> PredictionResult:
        """
        Make confidence-aware prediction.

        Args:
            text: Input text
            past_messages: Optional list of past messages for context
            include_metadata: Whether to include additional metadata

        Returns:
            PredictionResult with emotion, confidence, and uncertainty info
        """
        # Extract features
        if self.context_window and past_messages:
            features = self.context_window.extract_with_context(text, past_messages)
        else:
            features = self.feature_manager.extract(text)

        # Reshape for prediction
        features = features.reshape(1, -1)

        # Get probabilities
        probabilities = self.model.predict_proba(features)[0]

        # Get prediction and confidence
        pred_idx = np.argmax(probabilities)
        emotion = self.class_names[pred_idx]
        confidence = float(probabilities[pred_idx])

        # Determine confidence level
        confidence_level = self._get_confidence_level(confidence)

        # Check uncertainty
        is_uncertain = confidence < self.uncertainty_threshold

        # Build probability dict
        prob_dict = {
            self.class_names[i]: float(probabilities[i])
            for i in range(len(self.class_names))
        }

        # Build metadata if requested
        metadata = None
        if include_metadata:
            metadata = {
                'text_length': len(text),
                'context_used': bool(past_messages and self.context_window),
                'context_size': len(past_messages) if past_messages else 0,
                'top_3_emotions': self._get_top_emotions(prob_dict, n=3)
            }

        return PredictionResult(
            emotion=emotion,
            confidence=confidence,
            confidence_level=confidence_level,
            is_uncertain=is_uncertain,
            probabilities=prob_dict,
            metadata=metadata
        )

    def predict_batch(
        self,
        texts: List[str],
        include_metadata: bool = False
    ) -> List[PredictionResult]:
        """
        Make predictions for multiple texts.

        Note: Context window is not supported for batch prediction.

        Args:
            texts: List of input texts
            include_metadata: Whether to include additional metadata

        Returns:
            List of PredictionResult objects
        """
        # Extract features
        features = self.feature_manager.extract_batch(texts)

        # Get probabilities
        all_proba = self.model.predict_proba(features)

        # Build results
        results = []
        for i, (text, proba) in enumerate(zip(texts, all_proba)):
            pred_idx = np.argmax(proba)
            emotion = self.class_names[pred_idx]
            confidence = float(proba[pred_idx])
            confidence_level = self._get_confidence_level(confidence)
            is_uncertain = confidence < self.uncertainty_threshold

            prob_dict = {
                self.class_names[j]: float(proba[j])
                for j in range(len(self.class_names))
            }

            metadata = None
            if include_metadata:
                metadata = {
                    'text_length': len(text),
                    'batch_index': i,
                    'top_3_emotions': self._get_top_emotions(prob_dict, n=3)
                }

            results.append(PredictionResult(
                emotion=emotion,
                confidence=confidence,
                confidence_level=confidence_level,
                is_uncertain=is_uncertain,
                probabilities=prob_dict,
                metadata=metadata
            ))

        return results

    def _get_confidence_level(self, confidence: float) -> str:
        """
        Determine confidence level category.

        Args:
            confidence: Confidence score (0 to 1)

        Returns:
            "high", "medium", or "low"
        """
        if confidence >= self.high_threshold:
            return "high"
        elif confidence >= self.medium_threshold:
            return "medium"
        else:
            return "low"

    def _get_top_emotions(
        self,
        prob_dict: Dict[str, float],
        n: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get top N emotions by probability.

        Args:
            prob_dict: Dict of class probabilities
            n: Number of top emotions to return

        Returns:
            List of {emotion, probability} dicts
        """
        sorted_emotions = sorted(
            prob_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]

        return [
            {"emotion": e, "probability": round(p, 4)}
            for e, p in sorted_emotions
        ]


def format_prediction_for_api(result: PredictionResult) -> Dict[str, Any]:
    """
    Format prediction result for API response.

    Provides backward-compatible format with enhanced information.

    Args:
        result: PredictionResult object

    Returns:
        Dict suitable for API response
    """
    return {
        # Core fields (backward compatible)
        "emotion": result.emotion,
        "score": result.confidence,

        # Enhanced fields
        "confidence_level": result.confidence_level,
        "is_uncertain": result.is_uncertain,

        # Detailed probabilities
        "probabilities": result.probabilities,

        # Warning for uncertain predictions
        "warning": "Low confidence prediction" if result.is_uncertain else None
    }


def create_predictor(
    feature_manager: FeatureManager,
    model,
    class_names: Optional[List[str]] = None
) -> ConfidenceAwarePredictor:
    """
    Factory function to create ConfidenceAwarePredictor.

    Args:
        feature_manager: FeatureManager instance
        model: Trained model
        class_names: Optional list of class names

    Returns:
        Configured ConfidenceAwarePredictor
    """
    return ConfidenceAwarePredictor(
        feature_manager=feature_manager,
        model=model,
        class_names=class_names
    )
