"""
Feature Extraction Plugin Architecture
======================================

This module provides a modular, plugin-based feature extraction system.
Each feature module is independent and can be enabled/disabled via config.

MODULES:
--------
- tfidf_features:     TF-IDF vectorization (word + character)
- existing_features:  Word bank match features from original system
- lexicon_features:   Emotion lexicon scores (NRC-style)
- linguistic_features: Linguistic style features
- sentiment_features: Sentiment and polarity features

USAGE:
------
    from src.features import FeatureManager

    manager = FeatureManager()
    features = manager.extract_all(text)  # Returns numpy array

REMOVABILITY:
-------------
Each module can be disabled by setting its config flag to False.
The system will continue to work with remaining enabled modules.

"""

from .feature_manager import FeatureManager
from .base_feature import BaseFeatureExtractor

__all__ = ['FeatureManager', 'BaseFeatureExtractor']
