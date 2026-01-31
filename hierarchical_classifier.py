"""
Hierarchical Classification System
===================================

Implements optional multi-stage hierarchical classification for emotion detection.

HIERARCHY STRUCTURE:
--------------------
Stage 1: Neutral vs Emotional
    |
    +-- Neutral -> Return "neutral"
    |
    +-- Emotional -> Stage 2
            |
            +-- Positive -> Return "positive"
            |
            +-- Negative -> Stage 3
                    |
                    +-- anxiety, sadness, anger, stress (fine-grained)

BENEFITS:
---------
1. More accurate neutral detection
2. Better separation of positive vs negative emotions
3. Fine-grained negative emotion classification

REMOVABILITY:
-------------
This module can be disabled by setting ENABLE_HIERARCHICAL_CLASSIFICATION = False.
When disabled, the system uses flat classification (baseline behavior).

CONFIG FLAGS:
- ENABLE_HIERARCHICAL_CLASSIFICATION: Master switch
- ENABLE_STAGE1_NEUTRAL_EMOTIONAL: Enable Stage 1
- ENABLE_STAGE2_POSITIVE_NEGATIVE: Enable Stage 2
- ENABLE_STAGE3_FINE_GRAINED: Enable Stage 3

"""

import numpy as np
import joblib
import os
import logging
from typing import List, Dict, Optional, Tuple, Any
from sklearn.linear_model import LogisticRegression
from sklearn.base import BaseEstimator, ClassifierMixin

import config
from features import FeatureManager

logger = logging.getLogger(__name__)


# Label mappings for each stage
STAGE1_LABELS = {
    'neutral': 0,
    'emotional': 1
}

STAGE2_LABELS = {
    'positive': 0,
    'negative': 1
}

STAGE3_LABELS = {
    'anxiety': 0,
    'sadness': 1,
    'anger': 2,
    'stress': 3
}

# Reverse mappings
STAGE1_REVERSE = {v: k for k, v in STAGE1_LABELS.items()}
STAGE2_REVERSE = {v: k for k, v in STAGE2_LABELS.items()}
STAGE3_REVERSE = {v: k for k, v in STAGE3_LABELS.items()}


class HierarchicalClassifier(BaseEstimator, ClassifierMixin):
    """
    Multi-stage hierarchical emotion classifier.

    Implements a decision tree-like classification:
    1. First distinguishes neutral from emotional
    2. Then separates positive from negative emotions
    3. Finally classifies fine-grained negative emotions

    REMOVABILITY:
    -------------
    Can be disabled via config. When disabled, use flat classifier.
    Individual stages can also be disabled.
    """

    def __init__(
        self,
        stage1_model=None,
        stage2_model=None,
        stage3_model=None
    ):
        """
        Initialize HierarchicalClassifier.

        Args:
            stage1_model: Model for neutral/emotional classification
            stage2_model: Model for positive/negative classification
            stage3_model: Model for fine-grained emotion classification
        """
        # Initialize models (use LogisticRegression by default)
        self.stage1_model = stage1_model or LogisticRegression(
            max_iter=1000,
            class_weight='balanced',
            n_jobs=-1
        )
        self.stage2_model = stage2_model or LogisticRegression(
            max_iter=1000,
            class_weight='balanced',
            n_jobs=-1
        )
        self.stage3_model = stage3_model or LogisticRegression(
            max_iter=1000,
            class_weight='balanced',
            n_jobs=-1
        )

        self._is_fitted = False
        self.classes_ = np.array(['neutral', 'positive', 'anxiety', 'sadness', 'anger', 'stress'])

    def _map_to_stage1(self, labels: np.ndarray) -> np.ndarray:
        """Map original labels to stage 1 (neutral vs emotional)."""
        mapped = []
        for label in labels:
            if label == 'neutral':
                mapped.append(0)  # neutral
            else:
                mapped.append(1)  # emotional
        return np.array(mapped)

    def _map_to_stage2(self, labels: np.ndarray) -> np.ndarray:
        """Map original labels to stage 2 (positive vs negative)."""
        mapped = []
        for label in labels:
            if label == 'positive':
                mapped.append(0)  # positive
            else:
                mapped.append(1)  # negative
        return np.array(mapped)

    def _map_to_stage3(self, labels: np.ndarray) -> np.ndarray:
        """Map original labels to stage 3 (fine-grained)."""
        # Map distress/strong_distress to anxiety for training
        label_map = {
            'anxiety': 0,
            'distress': 0,
            'strong_distress': 0,
            'sadness': 1,
            'sad': 1,
            'anger': 2,
            'angry': 2,
            'frustration': 2,
            'stress': 3,
            'stressed': 3
        }
        mapped = []
        for label in labels:
            mapped.append(label_map.get(label, 0))  # Default to anxiety
        return np.array(mapped)

    def fit(self, X: np.ndarray, y: np.ndarray):
        """
        Fit all stage classifiers.

        Args:
            X: Feature matrix
            y: Original emotion labels

        Returns:
            self
        """
        logger.info("Fitting hierarchical classifier...")

        # Stage 1: Neutral vs Emotional
        if config.ENABLE_STAGE1_NEUTRAL_EMOTIONAL:
            y_stage1 = self._map_to_stage1(y)
            logger.info(f"Stage 1: Training on {len(y)} samples "
                       f"(neutral={sum(y_stage1==0)}, emotional={sum(y_stage1==1)})")
            self.stage1_model.fit(X, y_stage1)

        # Stage 2: Positive vs Negative (only emotional samples)
        if config.ENABLE_STAGE2_POSITIVE_NEGATIVE:
            emotional_mask = (y != 'neutral')
            X_emotional = X[emotional_mask]
            y_emotional = y[emotional_mask]
            y_stage2 = self._map_to_stage2(y_emotional)
            logger.info(f"Stage 2: Training on {len(y_emotional)} emotional samples "
                       f"(positive={sum(y_stage2==0)}, negative={sum(y_stage2==1)})")
            self.stage2_model.fit(X_emotional, y_stage2)

        # Stage 3: Fine-grained (only negative samples)
        if config.ENABLE_STAGE3_FINE_GRAINED:
            negative_mask = ~np.isin(y, ['neutral', 'positive'])
            X_negative = X[negative_mask]
            y_negative = y[negative_mask]
            y_stage3 = self._map_to_stage3(y_negative)
            logger.info(f"Stage 3: Training on {len(y_negative)} negative samples")
            self.stage3_model.fit(X_negative, y_stage3)

        self._is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict emotion labels using hierarchical classification.

        Args:
            X: Feature matrix

        Returns:
            Array of predicted labels
        """
        if not self._is_fitted:
            raise ValueError("Classifier not fitted. Call fit() first.")

        predictions = []

        for i in range(X.shape[0]):
            x = X[i:i+1]
            pred = self._predict_single(x)
            predictions.append(pred)

        return np.array(predictions)

    def _predict_single(self, x: np.ndarray) -> str:
        """
        Predict single sample through hierarchy.

        Args:
            x: Single sample feature vector (1, n_features)

        Returns:
            Predicted emotion label
        """
        # Stage 1: Neutral vs Emotional
        if config.ENABLE_STAGE1_NEUTRAL_EMOTIONAL:
            stage1_pred = self.stage1_model.predict(x)[0]
            if stage1_pred == 0:  # Neutral
                return 'neutral'

        # Stage 2: Positive vs Negative
        if config.ENABLE_STAGE2_POSITIVE_NEGATIVE:
            stage2_pred = self.stage2_model.predict(x)[0]
            if stage2_pred == 0:  # Positive
                return 'positive'

        # Stage 3: Fine-grained emotion
        if config.ENABLE_STAGE3_FINE_GRAINED:
            stage3_pred = self.stage3_model.predict(x)[0]
            return STAGE3_REVERSE.get(stage3_pred, 'anxiety')

        # Fallback if stages are disabled
        return 'distress'

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict probabilities for all classes.

        Combines probabilities from all stages.

        Args:
            X: Feature matrix

        Returns:
            Probability matrix (n_samples, n_classes)
        """
        if not self._is_fitted:
            raise ValueError("Classifier not fitted. Call fit() first.")

        n_samples = X.shape[0]
        # Classes: neutral, positive, anxiety, sadness, anger, stress
        proba = np.zeros((n_samples, 6))

        for i in range(n_samples):
            x = X[i:i+1]
            proba[i] = self._predict_proba_single(x)

        return proba

    def _predict_proba_single(self, x: np.ndarray) -> np.ndarray:
        """
        Predict probabilities for single sample through hierarchy.

        Args:
            x: Single sample feature vector (1, n_features)

        Returns:
            Probability array for 6 classes
        """
        proba = np.zeros(6)
        # Index: 0=neutral, 1=positive, 2=anxiety, 3=sadness, 4=anger, 5=stress

        # Stage 1: P(neutral) vs P(emotional)
        if config.ENABLE_STAGE1_NEUTRAL_EMOTIONAL:
            s1_proba = self.stage1_model.predict_proba(x)[0]
            p_neutral = s1_proba[0]
            p_emotional = s1_proba[1]
        else:
            p_neutral = 0.0
            p_emotional = 1.0

        proba[0] = p_neutral

        # Stage 2: P(positive|emotional) vs P(negative|emotional)
        if config.ENABLE_STAGE2_POSITIVE_NEGATIVE:
            s2_proba = self.stage2_model.predict_proba(x)[0]
            p_positive = p_emotional * s2_proba[0]
            p_negative = p_emotional * s2_proba[1]
        else:
            p_positive = p_emotional * 0.5
            p_negative = p_emotional * 0.5

        proba[1] = p_positive

        # Stage 3: P(fine_grained|negative)
        if config.ENABLE_STAGE3_FINE_GRAINED:
            s3_proba = self.stage3_model.predict_proba(x)[0]
            proba[2] = p_negative * s3_proba[0]  # anxiety
            proba[3] = p_negative * s3_proba[1]  # sadness
            proba[4] = p_negative * s3_proba[2]  # anger
            proba[5] = p_negative * s3_proba[3]  # stress
        else:
            # Distribute evenly
            proba[2:6] = p_negative / 4

        return proba

    def save(self, base_path: str):
        """
        Save all stage models.

        Args:
            base_path: Base directory for models
        """
        os.makedirs(base_path, exist_ok=True)

        if config.ENABLE_STAGE1_NEUTRAL_EMOTIONAL:
            joblib.dump(self.stage1_model, os.path.join(base_path, 'stage1_neutral_emotional.pkl'))
        if config.ENABLE_STAGE2_POSITIVE_NEGATIVE:
            joblib.dump(self.stage2_model, os.path.join(base_path, 'stage2_positive_negative.pkl'))
        if config.ENABLE_STAGE3_FINE_GRAINED:
            joblib.dump(self.stage3_model, os.path.join(base_path, 'stage3_fine_grained.pkl'))

        logger.info(f"Saved hierarchical models to {base_path}")

    def load(self, base_path: str):
        """
        Load stage models from disk.

        Args:
            base_path: Base directory containing models
        """
        s1_path = os.path.join(base_path, 'stage1_neutral_emotional.pkl')
        s2_path = os.path.join(base_path, 'stage2_positive_negative.pkl')
        s3_path = os.path.join(base_path, 'stage3_fine_grained.pkl')

        if os.path.exists(s1_path):
            self.stage1_model = joblib.load(s1_path)
        if os.path.exists(s2_path):
            self.stage2_model = joblib.load(s2_path)
        if os.path.exists(s3_path):
            self.stage3_model = joblib.load(s3_path)

        self._is_fitted = True
        logger.info(f"Loaded hierarchical models from {base_path}")


def create_hierarchical_classifier() -> Optional[HierarchicalClassifier]:
    """
    Factory function to create HierarchicalClassifier if enabled.

    Returns:
        HierarchicalClassifier if enabled, None otherwise
    """
    if config.ENABLE_HIERARCHICAL_CLASSIFICATION:
        return HierarchicalClassifier()
    return None


