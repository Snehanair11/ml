"""
Ensemble Classifier - Weighted Soft Voting
==========================================

Implements optional weighted soft-voting ensemble combining multiple classifiers.

SUPPORTED MODELS:
-----------------
1. Logistic Regression (baseline)
2. Support Vector Machine (SVM)
3. XGBoost (gradient boosting)

ENSEMBLE STRATEGY:
------------------
Weighted soft voting combines probability predictions:
    P(class) = sum(weight_i * P_i(class)) for each model i

Default weights (configurable):
- Logistic Regression: 0.35
- SVM: 0.30
- XGBoost: 0.35

REMOVABILITY:
-------------
This module can be disabled by setting ENABLE_ENSEMBLE = False in config.
When disabled, the system uses DEFAULT_SINGLE_MODEL (default: logistic_regression).

CONFIG FLAGS:
- ENABLE_ENSEMBLE: Master switch
- ENSEMBLE_WEIGHTS: Dict of model weights
- DEFAULT_SINGLE_MODEL: Fallback model when ensemble disabled

"""

import numpy as np
import joblib
import os
import logging
from typing import Dict, List, Optional, Any
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.base import BaseEstimator, ClassifierMixin

import config

logger = logging.getLogger(__name__)

# Check if XGBoost is available
try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logger.warning("XGBoost not available. Ensemble will use LR + SVM only.")


class EnsembleClassifier(BaseEstimator, ClassifierMixin):
    """
    Weighted soft-voting ensemble classifier.

    Combines predictions from multiple models using configurable weights.
    Supports Logistic Regression, SVM, and XGBoost.

    REMOVABILITY:
    -------------
    Can be disabled via config. When disabled, uses single best model.
    """

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        use_xgboost: bool = True
    ):
        """
        Initialize EnsembleClassifier.

        Args:
            weights: Dict mapping model names to weights (default from config)
            use_xgboost: Whether to include XGBoost (default True if available)
        """
        self.weights = weights or config.ENSEMBLE_WEIGHTS.copy()
        self.use_xgboost = use_xgboost and XGBOOST_AVAILABLE

        # Initialize models
        self.models: Dict[str, Any] = {}
        self._init_models()

        self._is_fitted = False
        self.classes_ = None

    def _init_models(self):
        """Initialize individual classifiers."""

        # Logistic Regression (always available)
        self.models['logistic_regression'] = LogisticRegression(
            max_iter=1000,
            class_weight='balanced',
            n_jobs=-1,
            random_state=42
        )

        # SVM with probability estimates
        self.models['svm'] = SVC(
            kernel='rbf',
            probability=True,  # Required for soft voting
            class_weight='balanced',
            random_state=42
        )

        # XGBoost (if available)
        if self.use_xgboost:
            self.models['xgboost'] = XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                n_jobs=-1,
                random_state=42,
                use_label_encoder=False,
                eval_metric='mlogloss'
            )
        else:
            # Remove XGBoost from weights if not available
            if 'xgboost' in self.weights:
                xgb_weight = self.weights.pop('xgboost')
                # Redistribute weight
                remaining_models = list(self.weights.keys())
                if remaining_models:
                    extra_per_model = xgb_weight / len(remaining_models)
                    for model in remaining_models:
                        self.weights[model] += extra_per_model

        # Normalize weights
        self._normalize_weights()

        logger.info(f"Ensemble initialized with models: {list(self.models.keys())}")
        logger.info(f"Weights: {self.weights}")

    def _normalize_weights(self):
        """Normalize weights to sum to 1."""
        total = sum(self.weights.values())
        if total > 0:
            for model in self.weights:
                self.weights[model] /= total

    def fit(self, X: np.ndarray, y: np.ndarray):
        """
        Fit all models in the ensemble.

        Args:
            X: Feature matrix
            y: Labels

        Returns:
            self
        """
        logger.info(f"Fitting ensemble on {X.shape[0]} samples...")

        self.classes_ = np.unique(y)

        for name, model in self.models.items():
            logger.info(f"  Training {name}...")
            try:
                model.fit(X, y)
            except Exception as e:
                logger.error(f"  Failed to train {name}: {e}")
                # Remove from ensemble
                self.weights.pop(name, None)
                self._normalize_weights()

        self._is_fitted = True
        logger.info("Ensemble training complete.")
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict using weighted soft voting.

        Args:
            X: Feature matrix

        Returns:
            Array of predicted labels
        """
        proba = self.predict_proba(X)
        return self.classes_[np.argmax(proba, axis=1)]

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict probabilities using weighted soft voting.

        Args:
            X: Feature matrix

        Returns:
            Probability matrix
        """
        if not self._is_fitted:
            raise ValueError("Ensemble not fitted. Call fit() first.")

        # Initialize with zeros
        n_samples = X.shape[0]
        n_classes = len(self.classes_)
        weighted_proba = np.zeros((n_samples, n_classes))

        # Accumulate weighted probabilities
        for name, model in self.models.items():
            if name not in self.weights:
                continue

            weight = self.weights[name]
            try:
                proba = model.predict_proba(X)
                weighted_proba += weight * proba
            except Exception as e:
                logger.warning(f"Error getting probabilities from {name}: {e}")

        return weighted_proba

    def get_model(self, name: str):
        """
        Get a specific model from the ensemble.

        Args:
            name: Model name ('logistic_regression', 'svm', 'xgboost')

        Returns:
            The model or None
        """
        return self.models.get(name)

    def get_individual_predictions(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Get predictions from each individual model.

        Useful for debugging and analysis.

        Args:
            X: Feature matrix

        Returns:
            Dict mapping model names to predictions
        """
        predictions = {}
        for name, model in self.models.items():
            try:
                predictions[name] = model.predict(X)
            except Exception as e:
                logger.warning(f"Error getting predictions from {name}: {e}")
        return predictions

    def get_model_agreement(self, X: np.ndarray) -> np.ndarray:
        """
        Calculate agreement score among models.

        Higher score = more models agree on prediction.

        Args:
            X: Feature matrix

        Returns:
            Agreement scores (0 to 1) for each sample
        """
        predictions = self.get_individual_predictions(X)
        if not predictions:
            return np.ones(X.shape[0])

        n_samples = X.shape[0]
        n_models = len(predictions)
        agreement = np.zeros(n_samples)

        pred_matrix = np.array(list(predictions.values())).T  # (n_samples, n_models)

        for i in range(n_samples):
            # Count most common prediction
            unique, counts = np.unique(pred_matrix[i], return_counts=True)
            agreement[i] = counts.max() / n_models

        return agreement

    def save(self, base_path: str):
        """
        Save all models in the ensemble.

        Args:
            base_path: Base directory for models
        """
        os.makedirs(base_path, exist_ok=True)

        for name, model in self.models.items():
            path = os.path.join(base_path, f'{name}_model.pkl')
            joblib.dump(model, path)
            logger.info(f"Saved {name} to {path}")

        # Save weights
        weights_path = os.path.join(base_path, 'ensemble_weights.pkl')
        joblib.dump(self.weights, weights_path)

    def load(self, base_path: str):
        """
        Load models from disk.

        Args:
            base_path: Base directory containing models
        """
        # Load weights
        weights_path = os.path.join(base_path, 'ensemble_weights.pkl')
        if os.path.exists(weights_path):
            self.weights = joblib.load(weights_path)

        # Load models
        for name in list(self.models.keys()):
            path = os.path.join(base_path, f'{name}_model.pkl')
            if os.path.exists(path):
                self.models[name] = joblib.load(path)
                logger.info(f"Loaded {name} from {path}")

        self._is_fitted = True


class SingleModelClassifier(BaseEstimator, ClassifierMixin):
    """
    Wrapper for single model (when ensemble is disabled).

    Provides consistent interface with EnsembleClassifier.

    USAGE:
    ------
    Used when ENABLE_ENSEMBLE = False.
    Uses model specified by DEFAULT_SINGLE_MODEL config.
    """

    def __init__(self, model_type: Optional[str] = None):
        """
        Initialize with specified model type.

        Args:
            model_type: One of 'logistic_regression', 'svm', 'xgboost'
        """
        self.model_type = model_type or config.DEFAULT_SINGLE_MODEL

        # Initialize model
        if self.model_type == 'logistic_regression':
            self.model = LogisticRegression(
                max_iter=1000,
                class_weight='balanced',
                n_jobs=-1,
                random_state=42
            )
        elif self.model_type == 'svm':
            self.model = SVC(
                kernel='rbf',
                probability=True,
                class_weight='balanced',
                random_state=42
            )
        elif self.model_type == 'xgboost' and XGBOOST_AVAILABLE:
            self.model = XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                n_jobs=-1,
                random_state=42,
                use_label_encoder=False,
                eval_metric='mlogloss'
            )
        else:
            # Fallback to Logistic Regression
            logger.warning(f"Model type '{self.model_type}' not available. Using Logistic Regression.")
            self.model_type = 'logistic_regression'
            self.model = LogisticRegression(
                max_iter=1000,
                class_weight='balanced',
                n_jobs=-1,
                random_state=42
            )

        self._is_fitted = False
        self.classes_ = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Fit the model."""
        logger.info(f"Fitting {self.model_type} on {X.shape[0]} samples...")
        self.classes_ = np.unique(y)
        self.model.fit(X, y)
        self._is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict labels."""
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities."""
        return self.model.predict_proba(X)

    def save(self, path: str):
        """Save model to disk."""
        joblib.dump(self.model, path)

    def load(self, path: str):
        """Load model from disk."""
        self.model = joblib.load(path)
        self._is_fitted = True


def create_classifier() -> BaseEstimator:
    """
    Factory function to create appropriate classifier based on config.

    Returns:
        EnsembleClassifier if enabled, SingleModelClassifier otherwise
    """
    if config.ENABLE_ENSEMBLE:
        return EnsembleClassifier(weights=config.ENSEMBLE_WEIGHTS.copy())
    else:
        return SingleModelClassifier(model_type=config.DEFAULT_SINGLE_MODEL)

