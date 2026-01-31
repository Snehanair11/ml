"""
Emotion Detector - Unified Interface
====================================

This is the main entry point for emotion detection using the enhanced system.
Provides a simple, unified interface that handles all optional components.

USAGE:
------
    from src.emotion_detector import EmotionDetector

    # Initialize (auto-loads models based on config)
    detector = EmotionDetector()

    # Simple prediction
    result = detector.predict("I'm feeling really anxious today")
    print(result.emotion, result.confidence)

    # With message context (if enabled)
    result = detector.predict(
        "I can't do this anymore",
        past_messages=["Work has been so stressful", "I'm exhausted"]
    )

    # Batch prediction
    results = detector.predict_batch(["I'm happy!", "I'm so stressed"])

CONFIG DEPENDENCY:
------------------
Behavior is controlled by src/config.py flags.
All optional components are automatically loaded based on config.

BACKWARD COMPATIBILITY:
-----------------------
The system maintains backward compatibility:
- If new features are disabled, behavior matches the original system
- Output always includes: emotion, confidence, confidence_level

"""

import os
import logging
import joblib
import numpy as np
from typing import List, Optional, Dict, Any, Union

from src import config
from src.features import FeatureManager
from src.confidence_predictor import (
    ConfidenceAwarePredictor,
    PredictionResult,
    format_prediction_for_api
)
from src.context_window import ContextWindow
from src.ensemble_classifier import create_classifier, EnsembleClassifier
from src.hierarchical_classifier import HierarchicalClassifier

logger = logging.getLogger(__name__)


class EmotionDetector:
    """
    Unified emotion detection interface.

    Automatically loads and configures all enabled components:
    - Feature extractors (TF-IDF, lexicon, linguistic, sentiment)
    - Classifier (single, ensemble, or hierarchical)
    - Context window (if enabled)

    All optional components are controlled via config.py.

    REMOVABILITY:
    -------------
    Disable any component by changing its config flag.
    The detector adapts automatically.
    """

    def __init__(
        self,
        model_dir: Optional[str] = None,
        verbose: bool = False
    ):
        """
        Initialize EmotionDetector.

        Args:
            model_dir: Directory containing trained models (default from config)
            verbose: Enable verbose logging
        """
        self.model_dir = model_dir or config.MODEL_DIR
        self.verbose = verbose or config.VERBOSE_LOGGING

        if self.verbose:
            logging.basicConfig(level=logging.INFO)

        # Initialize components
        self._init_feature_manager()
        self._init_classifier()
        self._init_predictor()

        logger.info("EmotionDetector initialized successfully")
        if self.verbose:
            self._print_config()

    def _init_feature_manager(self):
        """Initialize FeatureManager with enabled modules."""
        logger.info("Initializing FeatureManager...")

        self.feature_manager = FeatureManager(
            tfidf_word_path=config.MODELS.get('tfidf_word'),
            tfidf_char_path=config.MODELS.get('tfidf_char')
        )

        logger.info(f"Enabled modules: {self.feature_manager.enabled_modules}")
        logger.info(f"Total feature dimension: {self.feature_manager.output_dim}")

    def _init_classifier(self):
        """Initialize classifier based on config."""
        logger.info("Initializing classifier...")

        if config.ENABLE_HIERARCHICAL_CLASSIFICATION:
            logger.info("Using hierarchical classifier")
            self.classifier = HierarchicalClassifier()
            self.classifier.load(self.model_dir)

        elif config.ENABLE_ENSEMBLE:
            logger.info("Using ensemble classifier")
            self.classifier = EnsembleClassifier()
            self.classifier.load(self.model_dir)

        else:
            logger.info(f"Using single model: {config.DEFAULT_SINGLE_MODEL}")
            model_path = config.MODELS.get('emotion_model')
            if model_path and os.path.exists(model_path):
                self.classifier = joblib.load(model_path)
            else:
                raise FileNotFoundError(
                    f"Model not found at {model_path}. Run training first."
                )

        # Get class names
        if hasattr(self.classifier, 'classes_'):
            self.class_names = list(self.classifier.classes_)
        else:
            self.class_names = ['neutral', 'positive', 'distress', 'strong_distress']

    def _init_predictor(self):
        """Initialize confidence-aware predictor."""
        self.predictor = ConfidenceAwarePredictor(
            feature_manager=self.feature_manager,
            model=self.classifier,
            class_names=self.class_names,
            use_context=config.ENABLE_CONTEXT_WINDOW
        )

    def _print_config(self):
        """Print current configuration."""
        print("\n" + "=" * 50)
        print("EMOTION DETECTOR CONFIGURATION")
        print("=" * 50)
        print(f"Feature modules: {self.feature_manager.enabled_modules}")
        print(f"Context window: {'Enabled' if config.ENABLE_CONTEXT_WINDOW else 'Disabled'}")
        print(f"Hierarchical: {'Enabled' if config.ENABLE_HIERARCHICAL_CLASSIFICATION else 'Disabled'}")
        print(f"Ensemble: {'Enabled' if config.ENABLE_ENSEMBLE else 'Disabled'}")
        print("=" * 50 + "\n")

    def predict(
        self,
        text: str,
        past_messages: Optional[List[str]] = None,
        include_metadata: bool = False
    ) -> PredictionResult:
        """
        Predict emotion for a single text.

        Args:
            text: Input text to analyze
            past_messages: Optional list of past messages for context
            include_metadata: Include additional metadata in result

        Returns:
            PredictionResult with emotion, confidence, and uncertainty info
        """
        return self.predictor.predict(
            text=text,
            past_messages=past_messages,
            include_metadata=include_metadata
        )

    def predict_batch(
        self,
        texts: List[str],
        include_metadata: bool = False
    ) -> List[PredictionResult]:
        """
        Predict emotions for multiple texts.

        Note: Context window is not supported for batch prediction.

        Args:
            texts: List of texts to analyze
            include_metadata: Include additional metadata in results

        Returns:
            List of PredictionResult objects
        """
        return self.predictor.predict_batch(
            texts=texts,
            include_metadata=include_metadata
        )

    def predict_simple(self, text: str) -> Dict[str, Any]:
        """
        Simple prediction returning a dictionary.

        Backward-compatible format suitable for API responses.

        Args:
            text: Input text

        Returns:
            Dict with emotion, score, confidence_level, etc.
        """
        result = self.predict(text)
        return format_prediction_for_api(result)

    def get_feature_analysis(self, text: str) -> Dict[str, Any]:
        """
        Get detailed feature analysis for a text.

        Useful for debugging and understanding predictions.

        Args:
            text: Input text

        Returns:
            Dict with feature values and analysis
        """
        analysis = {
            'text': text,
            'features': {}
        }

        # Get individual feature module outputs
        for name in self.feature_manager.enabled_modules:
            extractor = self.feature_manager.get_extractor(name)
            if extractor:
                features = extractor.extract(text)
                analysis['features'][name] = {
                    'dim': len(features),
                    'values': features.tolist()[:10],  # First 10 values
                    'sum': float(np.sum(features)),
                    'mean': float(np.mean(features)),
                    'max': float(np.max(features))
                }

                # Get feature names if available
                if hasattr(extractor, 'get_feature_names'):
                    names = extractor.get_feature_names()
                    if len(names) <= 20:
                        analysis['features'][name]['feature_names'] = names

        # Add prediction
        result = self.predict(text, include_metadata=True)
        analysis['prediction'] = result.to_dict()

        return analysis

    def get_enabled_features(self) -> List[str]:
        """Get list of enabled feature modules."""
        return self.feature_manager.enabled_modules

    def get_config_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration."""
        return {
            'enabled_features': self.feature_manager.enabled_modules,
            'feature_dim': self.feature_manager.output_dim,
            'context_window_enabled': config.ENABLE_CONTEXT_WINDOW,
            'context_window_size': config.CONTEXT_WINDOW_SIZE if config.ENABLE_CONTEXT_WINDOW else None,
            'hierarchical_enabled': config.ENABLE_HIERARCHICAL_CLASSIFICATION,
            'ensemble_enabled': config.ENABLE_ENSEMBLE,
            'confidence_thresholds': {
                'high': config.CONFIDENCE_HIGH_THRESHOLD,
                'medium': config.CONFIDENCE_MEDIUM_THRESHOLD,
                'uncertainty': config.UNCERTAINTY_THRESHOLD
            },
            'class_names': self.class_names
        }


# Convenience function for quick predictions
def detect_emotion(text: str, **kwargs) -> PredictionResult:
    """
    Quick emotion detection function.

    Creates a detector instance and makes prediction.
    For repeated use, instantiate EmotionDetector directly.

    Args:
        text: Input text
        **kwargs: Additional arguments for predict()

    Returns:
        PredictionResult
    """
    detector = EmotionDetector()
    return detector.predict(text, **kwargs)


# Module-level detector instance (lazy initialization)
_detector_instance = None


def get_detector() -> EmotionDetector:
    """
    Get singleton EmotionDetector instance.

    Useful for applications that need repeated predictions.

    Returns:
        EmotionDetector instance
    """
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = EmotionDetector()
    return _detector_instance
