"""
Base Feature Extractor
======================

Abstract base class for all feature extraction modules.
All feature modules MUST inherit from this class.

REQUIREMENTS FOR SUBCLASSES:
----------------------------
1. Implement extract(text) -> numpy array
2. Define output_dim property
3. Handle errors gracefully (return zeros on failure)

"""

from abc import ABC, abstractmethod
import numpy as np
from typing import Union, List
import logging

logger = logging.getLogger(__name__)


class BaseFeatureExtractor(ABC):
    """
    Abstract base class for feature extractors.

    All feature modules must inherit from this class and implement:
    - extract(text): Returns feature vector as numpy array
    - output_dim: Property returning expected output dimension

    REMOVABILITY:
    -------------
    This module can be safely disabled via config.
    When disabled, FeatureManager will skip this extractor entirely.
    """

    def __init__(self, name: str):
        """
        Initialize the feature extractor.

        Args:
            name: Unique identifier for this feature module
        """
        self.name = name
        self._is_fitted = False
        self._output_dim = None

    @property
    @abstractmethod
    def output_dim(self) -> int:
        """
        Return the expected output dimension of extract().

        Returns:
            int: Number of features this extractor produces
        """
        pass

    @abstractmethod
    def extract(self, text: str) -> np.ndarray:
        """
        Extract features from input text.

        Args:
            text: Input text string

        Returns:
            np.ndarray: Feature vector of shape (output_dim,)

        Note:
            Must handle errors gracefully and return zeros on failure.
        """
        pass

    def extract_batch(self, texts: List[str]) -> np.ndarray:
        """
        Extract features from multiple texts.

        Args:
            texts: List of input text strings

        Returns:
            np.ndarray: Feature matrix of shape (n_texts, output_dim)
        """
        features = []
        for text in texts:
            try:
                feat = self.extract(text)
                features.append(feat)
            except Exception as e:
                logger.warning(f"{self.name}: Error extracting features: {e}")
                features.append(self._get_zero_features())
        return np.vstack(features)

    def _get_zero_features(self) -> np.ndarray:
        """
        Return zero vector for fallback.

        Returns:
            np.ndarray: Zero vector of shape (output_dim,)
        """
        return np.zeros(self.output_dim)

    def fit(self, texts: List[str], y=None):
        """
        Fit the feature extractor (if applicable).

        Args:
            texts: Training texts
            y: Optional labels (unused by most extractors)

        Returns:
            self
        """
        self._is_fitted = True
        return self

    def is_fitted(self) -> bool:
        """Check if extractor has been fitted."""
        return self._is_fitted

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', dim={self.output_dim})"
