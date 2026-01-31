"""
TF-IDF Feature Extractor
========================

Extracts TF-IDF features using word-level and character-level vectorizers.
This is the core feature module from the original system.

FEATURES:
---------
- Word-level TF-IDF (unigrams + bigrams, 6000 features)
- Character-level TF-IDF (3-5 char n-grams, 8000 features)
- Combined: 14000 total features

REMOVABILITY:
-------------
This module can be disabled by setting ENABLE_TFIDF_FEATURES = False in config.
However, it is recommended to keep this enabled as it provides baseline features.

CONFIG FLAG: ENABLE_TFIDF_FEATURES

"""

import numpy as np
import joblib
import os
import logging
from typing import List, Optional
from scipy.sparse import hstack, issparse
from sklearn.feature_extraction.text import TfidfVectorizer

from .base_feature import BaseFeatureExtractor

logger = logging.getLogger(__name__)


class TfidfFeatureExtractor(BaseFeatureExtractor):
    """
    TF-IDF feature extractor combining word and character n-grams.

    This is the baseline feature extractor that provides robust text
    representation for emotion classification.

    REMOVABILITY:
    -------------
    Can be disabled via config, but not recommended as it provides
    the core feature representation.
    """

    # Default configuration for vectorizers
    WORD_MAX_FEATURES = 6000
    CHAR_MAX_FEATURES = 8000

    def __init__(
        self,
        word_vectorizer_path: Optional[str] = None,
        char_vectorizer_path: Optional[str] = None
    ):
        """
        Initialize TF-IDF feature extractor.

        Args:
            word_vectorizer_path: Path to fitted word vectorizer (None to create new)
            char_vectorizer_path: Path to fitted char vectorizer (None to create new)
        """
        super().__init__(name='tfidf')

        self.word_vectorizer = None
        self.char_vectorizer = None

        # Load pre-trained vectorizers if paths provided
        if word_vectorizer_path and os.path.exists(word_vectorizer_path):
            self.word_vectorizer = joblib.load(word_vectorizer_path)
            logger.info(f"Loaded word vectorizer from {word_vectorizer_path}")

        if char_vectorizer_path and os.path.exists(char_vectorizer_path):
            self.char_vectorizer = joblib.load(char_vectorizer_path)
            logger.info(f"Loaded char vectorizer from {char_vectorizer_path}")

        # Create new vectorizers if not loaded
        if self.word_vectorizer is None:
            self.word_vectorizer = TfidfVectorizer(
                analyzer='word',
                ngram_range=(1, 2),
                max_features=self.WORD_MAX_FEATURES,
                stop_words='english',
                lowercase=True
            )

        if self.char_vectorizer is None:
            self.char_vectorizer = TfidfVectorizer(
                analyzer='char_wb',
                ngram_range=(3, 5),
                max_features=self.CHAR_MAX_FEATURES,
                lowercase=True
            )

        # Check if vectorizers are already fitted
        self._is_fitted = (
            hasattr(self.word_vectorizer, 'vocabulary_') and
            hasattr(self.char_vectorizer, 'vocabulary_')
        )

    @property
    def output_dim(self) -> int:
        """Return total feature dimension (word + char)."""
        return self.WORD_MAX_FEATURES + self.CHAR_MAX_FEATURES

    def fit(self, texts: List[str], y=None):
        """
        Fit both vectorizers on training texts.

        Args:
            texts: List of training texts
            y: Ignored (for sklearn compatibility)

        Returns:
            self
        """
        logger.info("Fitting TF-IDF vectorizers...")
        self.word_vectorizer.fit(texts)
        self.char_vectorizer.fit(texts)
        self._is_fitted = True
        logger.info(f"TF-IDF fitted: word vocab={len(self.word_vectorizer.vocabulary_)}, "
                   f"char vocab={len(self.char_vectorizer.vocabulary_)}")
        return self

    def extract(self, text: str) -> np.ndarray:
        """
        Extract TF-IDF features from a single text.

        Args:
            text: Input text string

        Returns:
            np.ndarray: Feature vector of shape (output_dim,)
        """
        if not self._is_fitted:
            logger.warning("TF-IDF vectorizers not fitted, returning zeros")
            return self._get_zero_features()

        try:
            # Transform text using both vectorizers
            word_features = self.word_vectorizer.transform([text])
            char_features = self.char_vectorizer.transform([text])

            # Combine features
            combined = hstack([word_features, char_features])

            # Convert to dense array
            if issparse(combined):
                combined = combined.toarray()

            return combined.flatten()

        except Exception as e:
            logger.error(f"TF-IDF extraction error: {e}")
            return self._get_zero_features()

    def extract_batch(self, texts: List[str]) -> np.ndarray:
        """
        Extract TF-IDF features from multiple texts efficiently.

        Args:
            texts: List of input texts

        Returns:
            np.ndarray: Feature matrix of shape (n_texts, output_dim)
        """
        if not self._is_fitted:
            logger.warning("TF-IDF vectorizers not fitted, returning zeros")
            return np.zeros((len(texts), self.output_dim))

        try:
            # Batch transform is more efficient
            word_features = self.word_vectorizer.transform(texts)
            char_features = self.char_vectorizer.transform(texts)

            # Combine features
            combined = hstack([word_features, char_features])

            # Convert to dense array
            if issparse(combined):
                combined = combined.toarray()

            return combined

        except Exception as e:
            logger.error(f"TF-IDF batch extraction error: {e}")
            return np.zeros((len(texts), self.output_dim))

    def extract_sparse(self, texts: List[str]):
        """
        Extract features and keep as sparse matrix (memory efficient).

        Args:
            texts: List of input texts

        Returns:
            scipy.sparse matrix: Sparse feature matrix
        """
        if not self._is_fitted:
            raise ValueError("TF-IDF vectorizers not fitted")

        word_features = self.word_vectorizer.transform(texts)
        char_features = self.char_vectorizer.transform(texts)
        return hstack([word_features, char_features])

    def save(self, word_path: str, char_path: str):
        """
        Save fitted vectorizers to disk.

        Args:
            word_path: Path for word vectorizer
            char_path: Path for char vectorizer
        """
        if not self._is_fitted:
            raise ValueError("Cannot save unfitted vectorizers")

        joblib.dump(self.word_vectorizer, word_path)
        joblib.dump(self.char_vectorizer, char_path)
        logger.info(f"Saved TF-IDF vectorizers to {word_path}, {char_path}")

    def get_feature_names(self) -> List[str]:
        """
        Get feature names for interpretability.

        Returns:
            List of feature names
        """
        if not self._is_fitted:
            return []

        word_names = [f"word_{n}" for n in self.word_vectorizer.get_feature_names_out()]
        char_names = [f"char_{n}" for n in self.char_vectorizer.get_feature_names_out()]
        return word_names + char_names
