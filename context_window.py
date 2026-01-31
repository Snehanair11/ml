"""
Context Window - Message History Support
========================================

Provides optional support for considering message history in emotion prediction.
When enabled, combines features from past messages with weighted importance.

FUNCTIONALITY:
--------------
1. Accept a list of past messages (default max = 3)
2. Combine message features using configurable weights
3. Latest message gets highest weight

DEFAULT WEIGHTS:
----------------
- Latest message:   0.60
- Previous message: 0.25
- Oldest message:   0.15

REMOVABILITY:
-------------
This module can be disabled by setting ENABLE_CONTEXT_WINDOW = False in config.
When disabled, the system processes only the current message (baseline behavior).

CONFIG FLAG: ENABLE_CONTEXT_WINDOW

"""

import numpy as np
from typing import List, Optional, Union
import logging

from src import config
from src.features import FeatureManager

logger = logging.getLogger(__name__)


class ContextWindow:
    """
    Manages message context for improved emotion prediction.

    Combines features from multiple messages using weighted averaging.
    More recent messages receive higher weights.

    REMOVABILITY:
    -------------
    Can be disabled via config. When disabled, only processes current message.
    """

    def __init__(
        self,
        feature_manager: FeatureManager,
        window_size: Optional[int] = None,
        weights: Optional[List[float]] = None
    ):
        """
        Initialize ContextWindow.

        Args:
            feature_manager: FeatureManager instance for feature extraction
            window_size: Max number of past messages (default from config)
            weights: Weights for combining messages (default from config)
        """
        self.feature_manager = feature_manager
        self.window_size = window_size or config.CONTEXT_WINDOW_SIZE
        self.weights = weights or config.CONTEXT_WEIGHTS

        # Validate weights
        if len(self.weights) != self.window_size:
            logger.warning(
                f"Weight length ({len(self.weights)}) != window size ({self.window_size}). "
                "Adjusting weights."
            )
            self.weights = self._generate_default_weights(self.window_size)

        # Normalize weights to sum to 1
        weight_sum = sum(self.weights)
        self.weights = [w / weight_sum for w in self.weights]

        logger.info(
            f"ContextWindow initialized: window_size={self.window_size}, "
            f"weights={self.weights}"
        )

    def _generate_default_weights(self, size: int) -> List[float]:
        """
        Generate default weights that decay exponentially.

        Args:
            size: Number of weights needed

        Returns:
            List of weights (most recent first)
        """
        # Exponential decay: [0.6, 0.25, 0.15] style
        weights = []
        remaining = 1.0
        for i in range(size):
            if i == size - 1:
                weights.append(remaining)
            else:
                w = remaining * 0.6 if i == 0 else remaining * 0.4
                weights.append(w)
                remaining -= w
        return weights

    def extract_with_context(
        self,
        current_message: str,
        past_messages: Optional[List[str]] = None
    ) -> np.ndarray:
        """
        Extract features considering message history.

        Args:
            current_message: The current/latest message
            past_messages: List of past messages (most recent first), optional

        Returns:
            np.ndarray: Weighted combination of features
        """
        # If context is disabled, just return current message features
        if not config.ENABLE_CONTEXT_WINDOW:
            return self.feature_manager.extract(current_message)

        # If no past messages, just return current
        if not past_messages:
            return self.feature_manager.extract(current_message)

        # Build message list (current first, then past)
        messages = [current_message] + list(past_messages)

        # Limit to window size
        messages = messages[:self.window_size]

        # Extract features for all messages
        all_features = []
        for msg in messages:
            features = self.feature_manager.extract(msg)
            all_features.append(features)

        # Get appropriate weights
        num_messages = len(all_features)
        weights = self.weights[:num_messages]

        # Re-normalize weights for actual number of messages
        weight_sum = sum(weights)
        weights = [w / weight_sum for w in weights]

        # Weighted combination
        combined = np.zeros_like(all_features[0])
        for features, weight in zip(all_features, weights):
            combined += features * weight

        return combined

    def combine_messages(
        self,
        messages: List[str],
        weights: Optional[List[float]] = None
    ) -> str:
        """
        Combine multiple messages into a single text.

        Alternative approach: concatenate messages instead of feature combination.
        Useful for some models that work better with raw text.

        Args:
            messages: List of messages (most recent first)
            weights: Optional weights (not used for text combination)

        Returns:
            Combined message string
        """
        if not messages:
            return ""

        if len(messages) == 1:
            return messages[0]

        # Simple concatenation with separator
        return " [SEP] ".join(messages)


class ContextAwarePredictor:
    """
    Wrapper that adds context awareness to any predictor.

    REMOVABILITY:
    -------------
    If ENABLE_CONTEXT_WINDOW=False, this behaves identically to
    a regular predictor (no context consideration).
    """

    def __init__(
        self,
        feature_manager: FeatureManager,
        model,
        window_size: Optional[int] = None
    ):
        """
        Initialize context-aware predictor.

        Args:
            feature_manager: FeatureManager for feature extraction
            model: Trained sklearn model with predict/predict_proba
            window_size: Context window size (default from config)
        """
        self.feature_manager = feature_manager
        self.model = model
        self.context_window = ContextWindow(
            feature_manager,
            window_size=window_size
        )

    def predict(
        self,
        text: str,
        past_messages: Optional[List[str]] = None
    ) -> str:
        """
        Predict emotion with optional context.

        Args:
            text: Current message text
            past_messages: Optional list of past messages

        Returns:
            Predicted emotion label
        """
        # Extract features (with or without context)
        if config.ENABLE_CONTEXT_WINDOW and past_messages:
            features = self.context_window.extract_with_context(text, past_messages)
        else:
            features = self.feature_manager.extract(text)

        # Reshape for single prediction
        features = features.reshape(1, -1)

        return self.model.predict(features)[0]

    def predict_proba(
        self,
        text: str,
        past_messages: Optional[List[str]] = None
    ) -> np.ndarray:
        """
        Predict emotion probabilities with optional context.

        Args:
            text: Current message text
            past_messages: Optional list of past messages

        Returns:
            Probability array for each class
        """
        # Extract features (with or without context)
        if config.ENABLE_CONTEXT_WINDOW and past_messages:
            features = self.context_window.extract_with_context(text, past_messages)
        else:
            features = self.feature_manager.extract(text)

        # Reshape for single prediction
        features = features.reshape(1, -1)

        return self.model.predict_proba(features)[0]


def create_context_window(feature_manager: FeatureManager) -> Optional[ContextWindow]:
    """
    Factory function to create ContextWindow if enabled.

    Args:
        feature_manager: FeatureManager instance

    Returns:
        ContextWindow if enabled, None otherwise
    """
    if config.ENABLE_CONTEXT_WINDOW:
        return ContextWindow(feature_manager)
    return None
