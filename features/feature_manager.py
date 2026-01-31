"""
Feature Manager - Central Feature Orchestration
================================================

The FeatureManager is the central hub for feature extraction.
It dynamically loads and combines feature modules based on configuration.

RESPONSIBILITIES:
-----------------
1. Load enabled feature modules from config
2. Concatenate feature outputs dynamically
3. Handle failures gracefully (disable failing modules)
4. Provide unified interface for training and inference

USAGE:
------
    from src.features import FeatureManager
    from src import config

    # Initialize with config-based module loading
    manager = FeatureManager()

    # Fit on training data (if needed)
    manager.fit(train_texts)

    # Extract features for single text
    features = manager.extract(text)  # Returns numpy array

    # Extract features for batch
    features = manager.extract_batch(texts)  # Returns numpy array

REMOVABILITY:
-------------
Each module can be disabled by setting its config flag to False.
The manager will skip disabled modules automatically.

"""

import numpy as np
import logging
from typing import List, Dict, Optional, Any
from scipy.sparse import issparse

# Import config
from src import config

# Import feature extractors
from .tfidf_features import TfidfFeatureExtractor
from .existing_features import ExistingFeatureExtractor
from .lexicon_features import LexiconFeatureExtractor
from .linguistic_features import LinguisticFeatureExtractor
from .sentiment_features import SentimentFeatureExtractor
from .base_feature import BaseFeatureExtractor

logger = logging.getLogger(__name__)


class FeatureManager:
    """
    Central manager for feature extraction plugins.

    Dynamically loads and combines feature modules based on configuration.
    Provides a unified interface for training and inference.

    PLUGIN ARCHITECTURE:
    --------------------
    - Each feature module is independent
    - Modules are loaded based on config flags
    - Outputs are concatenated dynamically
    - Failing modules are skipped gracefully

    REMOVABILITY:
    -------------
    Disable any module by setting its config flag to False.
    No code changes required.
    """

    def __init__(
        self,
        tfidf_word_path: Optional[str] = None,
        tfidf_char_path: Optional[str] = None
    ):
        """
        Initialize FeatureManager with enabled modules.

        Args:
            tfidf_word_path: Path to pre-trained word TF-IDF vectorizer
            tfidf_char_path: Path to pre-trained char TF-IDF vectorizer
        """
        self.extractors: Dict[str, BaseFeatureExtractor] = {}
        self._extractor_order: List[str] = []  # Maintain consistent order
        self._output_dim = 0
        self._is_fitted = False

        # Load enabled modules
        self._load_modules(tfidf_word_path, tfidf_char_path)

        logger.info(f"FeatureManager initialized with modules: {list(self.extractors.keys())}")
        logger.info(f"Total feature dimension: {self._output_dim}")

    def _load_modules(
        self,
        tfidf_word_path: Optional[str],
        tfidf_char_path: Optional[str]
    ):
        """
        Load enabled feature modules based on config.

        Args:
            tfidf_word_path: Path to word vectorizer
            tfidf_char_path: Path to char vectorizer
        """
        # Use default paths if not provided
        if tfidf_word_path is None:
            tfidf_word_path = config.MODELS.get('tfidf_word')
        if tfidf_char_path is None:
            tfidf_char_path = config.MODELS.get('tfidf_char')

        # Load TF-IDF features (core module)
        if config.ENABLE_TFIDF_FEATURES:
            try:
                extractor = TfidfFeatureExtractor(
                    word_vectorizer_path=tfidf_word_path,
                    char_vectorizer_path=tfidf_char_path
                )
                self._add_extractor('tfidf', extractor)
                logger.info(f"Loaded TF-IDF features (dim={extractor.output_dim})")
            except Exception as e:
                logger.error(f"Failed to load TF-IDF features: {e}")

        # Load existing word bank features
        if config.ENABLE_EXISTING_FEATURES:
            try:
                extractor = ExistingFeatureExtractor()
                self._add_extractor('existing', extractor)
                logger.info(f"Loaded existing features (dim={extractor.output_dim})")
            except Exception as e:
                logger.error(f"Failed to load existing features: {e}")

        # Load lexicon features
        if config.ENABLE_LEXICON_FEATURES:
            try:
                extractor = LexiconFeatureExtractor()
                self._add_extractor('lexicon', extractor)
                logger.info(f"Loaded lexicon features (dim={extractor.output_dim})")
            except Exception as e:
                logger.error(f"Failed to load lexicon features: {e}")

        # Load linguistic features
        if config.ENABLE_LINGUISTIC_FEATURES:
            try:
                extractor = LinguisticFeatureExtractor()
                self._add_extractor('linguistic', extractor)
                logger.info(f"Loaded linguistic features (dim={extractor.output_dim})")
            except Exception as e:
                logger.error(f"Failed to load linguistic features: {e}")

        # Load sentiment features
        if config.ENABLE_SENTIMENT_FEATURES:
            try:
                extractor = SentimentFeatureExtractor()
                self._add_extractor('sentiment', extractor)
                logger.info(f"Loaded sentiment features (dim={extractor.output_dim})")
            except Exception as e:
                logger.error(f"Failed to load sentiment features: {e}")

    def _add_extractor(self, name: str, extractor: BaseFeatureExtractor):
        """Add extractor and update dimensions."""
        self.extractors[name] = extractor
        self._extractor_order.append(name)
        self._output_dim += extractor.output_dim

    @property
    def output_dim(self) -> int:
        """Return total output dimension of all enabled extractors."""
        return self._output_dim

    @property
    def enabled_modules(self) -> List[str]:
        """Return list of enabled module names."""
        return list(self._extractor_order)

    def fit(self, texts: List[str], y=None):
        """
        Fit all extractors that require fitting.

        Args:
            texts: Training texts
            y: Optional labels (for supervised fitting)

        Returns:
            self
        """
        logger.info(f"Fitting FeatureManager on {len(texts)} texts...")

        for name in self._extractor_order:
            extractor = self.extractors[name]
            if not extractor.is_fitted():
                logger.info(f"Fitting {name} extractor...")
                try:
                    extractor.fit(texts, y)
                except Exception as e:
                    logger.error(f"Failed to fit {name}: {e}")

        self._is_fitted = True
        return self

    def is_fitted(self) -> bool:
        """Check if all extractors are fitted."""
        return all(
            self.extractors[name].is_fitted()
            for name in self._extractor_order
        )

    def extract(self, text: str) -> np.ndarray:
        """
        Extract features from a single text.

        Args:
            text: Input text string

        Returns:
            np.ndarray: Concatenated feature vector from all enabled modules
        """
        features_list = []

        for name in self._extractor_order:
            extractor = self.extractors[name]
            try:
                features = extractor.extract(text)

                # Convert sparse to dense if needed
                if issparse(features):
                    features = features.toarray().flatten()

                features_list.append(features)

            except Exception as e:
                logger.warning(f"Error extracting {name} features: {e}")
                # Return zeros for failed extractor
                features_list.append(np.zeros(extractor.output_dim))

        if not features_list:
            logger.error("No features extracted!")
            return np.zeros(self._output_dim)

        return np.concatenate(features_list)

    def extract_batch(self, texts: List[str]) -> np.ndarray:
        """
        Extract features from multiple texts efficiently.

        Args:
            texts: List of input texts

        Returns:
            np.ndarray: Feature matrix of shape (n_texts, output_dim)
        """
        if not texts:
            return np.zeros((0, self._output_dim))

        features_list = []

        for name in self._extractor_order:
            extractor = self.extractors[name]
            try:
                features = extractor.extract_batch(texts)

                # Convert sparse to dense if needed
                if issparse(features):
                    features = features.toarray()

                features_list.append(features)

            except Exception as e:
                logger.warning(f"Error extracting {name} features: {e}")
                # Return zeros for failed extractor
                features_list.append(np.zeros((len(texts), extractor.output_dim)))

        if not features_list:
            return np.zeros((len(texts), self._output_dim))

        return np.hstack(features_list)

    def get_feature_info(self) -> Dict[str, Any]:
        """
        Get information about enabled features.

        Returns:
            Dict with module info, dimensions, and feature names
        """
        info = {
            'total_dim': self._output_dim,
            'modules': {},
            'feature_names': []
        }

        start_idx = 0
        for name in self._extractor_order:
            extractor = self.extractors[name]
            end_idx = start_idx + extractor.output_dim

            info['modules'][name] = {
                'dim': extractor.output_dim,
                'start_idx': start_idx,
                'end_idx': end_idx,
                'is_fitted': extractor.is_fitted()
            }

            # Get feature names if available
            if hasattr(extractor, 'get_feature_names'):
                names = extractor.get_feature_names()
                info['feature_names'].extend(names)
            else:
                # Generate generic names
                info['feature_names'].extend([
                    f"{name}_{i}" for i in range(extractor.output_dim)
                ])

            start_idx = end_idx

        return info

    def get_extractor(self, name: str) -> Optional[BaseFeatureExtractor]:
        """
        Get a specific extractor by name.

        Args:
            name: Extractor name ('tfidf', 'lexicon', etc.)

        Returns:
            The extractor or None if not found
        """
        return self.extractors.get(name)

    def save_tfidf(self, word_path: str, char_path: str):
        """
        Save TF-IDF vectorizers (if enabled).

        Args:
            word_path: Path for word vectorizer
            char_path: Path for char vectorizer
        """
        if 'tfidf' in self.extractors:
            self.extractors['tfidf'].save(word_path, char_path)

    def __repr__(self) -> str:
        modules = ', '.join(self._extractor_order)
        return f"FeatureManager(modules=[{modules}], dim={self._output_dim})"


def create_feature_manager_from_config() -> FeatureManager:
    """
    Factory function to create FeatureManager from current config.

    Returns:
        Configured FeatureManager instance
    """
    return FeatureManager(
        tfidf_word_path=config.MODELS.get('tfidf_word'),
        tfidf_char_path=config.MODELS.get('tfidf_char')
    )
