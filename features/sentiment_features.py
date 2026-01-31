"""
Sentiment Signal Feature Extractor
==================================

Extracts sentiment-related features using a lightweight built-in sentiment analyzer.
No external dependencies (TextBlob, VADER) required.

FEATURES (4 total):
-------------------
1. polarity_score:     Overall sentiment polarity (-1 to 1, scaled to 0-1)
2. subjectivity_score: How subjective/opinionated the text is (0-1)
3. intensity_score:    Emotional intensity proxy (0-1)
4. valence_shift:      Sentiment shift within text (0-1)

REMOVABILITY:
-------------
This module can be disabled by setting ENABLE_SENTIMENT_FEATURES = False in config.
The system will continue using TF-IDF and other features.

CONFIG FLAG: ENABLE_SENTIMENT_FEATURES

"""

import numpy as np
import re
from typing import List, Dict, Tuple
import logging

from .base_feature import BaseFeatureExtractor

logger = logging.getLogger(__name__)


class SentimentFeatureExtractor(BaseFeatureExtractor):
    """
    Sentiment-based feature extractor.

    Uses a built-in sentiment lexicon to compute polarity, subjectivity,
    and emotional intensity features.

    REMOVABILITY:
    -------------
    Can be disabled via config without affecting other features.
    No external dependencies required.
    """

    # Output dimension
    OUTPUT_DIM = 4

    def __init__(self):
        """Initialize sentiment lexicons."""
        super().__init__(name='sentiment')
        self._is_fitted = True  # No fitting required

        # Build sentiment lexicons
        self._build_lexicons()

    def _build_lexicons(self):
        """Build sentiment word lexicons with polarity scores."""

        # Positive words with polarity scores (0.1 to 1.0)
        self.positive_words: Dict[str, float] = {
            # Strong positive (0.8-1.0)
            'excellent': 1.0, 'amazing': 1.0, 'wonderful': 1.0, 'fantastic': 0.95,
            'outstanding': 0.95, 'incredible': 0.95, 'brilliant': 0.95, 'perfect': 1.0,
            'love': 0.9, 'adore': 0.9, 'thrilled': 0.9, 'ecstatic': 0.95,
            # Medium positive (0.5-0.8)
            'good': 0.6, 'great': 0.75, 'nice': 0.5, 'happy': 0.7, 'pleased': 0.65,
            'glad': 0.6, 'delighted': 0.8, 'satisfied': 0.6, 'content': 0.55,
            'enjoy': 0.65, 'like': 0.5, 'appreciate': 0.6, 'grateful': 0.7,
            # Mild positive (0.2-0.5)
            'okay': 0.3, 'fine': 0.35, 'decent': 0.4, 'acceptable': 0.35,
            'interesting': 0.4, 'helpful': 0.5, 'useful': 0.45, 'pleasant': 0.5
        }

        # Negative words with polarity scores (-0.1 to -1.0)
        self.negative_words: Dict[str, float] = {
            # Strong negative (-0.8 to -1.0)
            'terrible': -1.0, 'horrible': -1.0, 'awful': -0.95, 'dreadful': -0.95,
            'hate': -0.9, 'despise': -0.95, 'loathe': -0.95, 'worst': -1.0,
            'devastating': -0.95, 'catastrophic': -1.0, 'disgusting': -0.9,
            # Medium negative (-0.5 to -0.8)
            'bad': -0.6, 'poor': -0.55, 'wrong': -0.5, 'sad': -0.6, 'unhappy': -0.65,
            'upset': -0.6, 'angry': -0.7, 'frustrated': -0.65, 'disappointed': -0.6,
            'annoyed': -0.55, 'irritated': -0.55, 'worried': -0.6, 'anxious': -0.65,
            # Mild negative (-0.2 to -0.5)
            'boring': -0.4, 'dull': -0.35, 'mediocre': -0.3, 'meh': -0.25,
            'difficult': -0.35, 'hard': -0.3, 'challenging': -0.25, 'confusing': -0.4
        }

        # Intensifiers (multiply polarity)
        self.intensifiers: Dict[str, float] = {
            'very': 1.5, 'really': 1.4, 'extremely': 1.8, 'incredibly': 1.7,
            'absolutely': 1.8, 'totally': 1.5, 'completely': 1.6, 'utterly': 1.7,
            'highly': 1.4, 'deeply': 1.5, 'strongly': 1.4, 'seriously': 1.4,
            'so': 1.3, 'too': 1.2, 'quite': 1.2, 'rather': 1.1
        }

        # Diminishers (reduce polarity)
        self.diminishers: Dict[str, float] = {
            'slightly': 0.5, 'somewhat': 0.6, 'a bit': 0.6, 'kind of': 0.5,
            'sort of': 0.5, 'a little': 0.5, 'barely': 0.3, 'hardly': 0.3,
            'almost': 0.7, 'nearly': 0.7
        }

        # Negators (flip polarity)
        self.negators: set = {
            'not', 'no', 'never', 'neither', 'nobody', 'nothing', 'nowhere',
            "n't", 'nt', 'cant', 'wont', 'dont', 'isnt', 'arent', 'wasnt'
        }

        # Subjective words (indicate opinion vs fact)
        self.subjective_words: set = {
            'think', 'feel', 'believe', 'opinion', 'seems', 'appears',
            'probably', 'maybe', 'perhaps', 'might', 'could', 'would',
            'personally', 'honestly', 'frankly', 'actually', 'basically',
            'i', 'my', 'me', 'myself', 'we', 'our', 'us'
        }

        # High-intensity emotion words
        self.intensity_words: set = {
            'very', 'extremely', 'incredibly', 'absolutely', 'totally',
            'completely', 'utterly', 'definitely', 'certainly', 'obviously',
            '!', '!!', '!!!', '?!', 'omg', 'wow', 'god', 'damn', 'hell',
            'fucking', 'freaking', 'bloody', 'shit', 'crap'
        }

    @property
    def output_dim(self) -> int:
        """Return feature dimension."""
        return self.OUTPUT_DIM

    def _calculate_polarity(self, text: str) -> float:
        """
        Calculate overall sentiment polarity.

        Args:
            text: Input text

        Returns:
            Polarity score from -1 (negative) to 1 (positive)
        """
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0.0

        total_score = 0.0
        word_count = 0
        negation_active = False
        intensifier = 1.0

        for i, word in enumerate(words):
            # Check for negation
            if word in self.negators:
                negation_active = True
                continue

            # Check for intensifier
            if word in self.intensifiers:
                intensifier = self.intensifiers[word]
                continue

            # Check for diminisher
            if word in self.diminishers:
                intensifier = self.diminishers[word]
                continue

            # Check sentiment words
            score = 0.0
            if word in self.positive_words:
                score = self.positive_words[word]
            elif word in self.negative_words:
                score = self.negative_words[word]

            if score != 0.0:
                # Apply modifiers
                if negation_active:
                    score = -score * 0.8  # Flip but slightly reduced
                    negation_active = False
                score *= intensifier
                intensifier = 1.0  # Reset

                total_score += score
                word_count += 1

            # Reset negation after a few words
            if i > 0 and i % 3 == 0:
                negation_active = False

        # Normalize
        if word_count > 0:
            return np.clip(total_score / word_count, -1.0, 1.0)
        return 0.0

    def _calculate_subjectivity(self, text: str) -> float:
        """
        Calculate subjectivity score (opinion vs fact).

        Args:
            text: Input text

        Returns:
            Subjectivity score from 0 (objective) to 1 (subjective)
        """
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0.0

        subjective_count = sum(1 for w in words if w in self.subjective_words)

        # Also count opinion words
        opinion_count = sum(1 for w in words if w in self.positive_words or w in self.negative_words)

        # Combine counts
        total = subjective_count + opinion_count * 0.5
        return min(total / len(words) * 3, 1.0)  # Scale up and cap at 1

    def _calculate_intensity(self, text: str) -> float:
        """
        Calculate emotional intensity.

        Args:
            text: Input text

        Returns:
            Intensity score from 0 (calm) to 1 (intense)
        """
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        if not words:
            return 0.0

        # Count intensity markers
        intensity_count = 0

        # Check intensity words
        intensity_count += sum(1 for w in words if w in self.intensity_words)

        # Check punctuation intensity
        intensity_count += text.count('!') * 0.5
        intensity_count += text.count('?') * 0.3
        intensity_count += len(re.findall(r'[A-Z]{2,}', text)) * 0.5  # ALL CAPS

        # Check elongation (e.g., "sooooo")
        intensity_count += len(re.findall(r'(.)\1{2,}', text)) * 0.3

        # Normalize
        return min(intensity_count / len(words) * 5, 1.0)

    def _calculate_valence_shift(self, text: str) -> float:
        """
        Calculate sentiment shift within text.

        Detects if sentiment changes (e.g., starts positive, ends negative).

        Args:
            text: Input text

        Returns:
            Valence shift score from 0 (consistent) to 1 (high shift)
        """
        # Split into segments
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            return 0.0

        # Calculate polarity for each segment
        polarities = [self._calculate_polarity(s) for s in sentences]

        # Calculate variance/shift
        if len(polarities) >= 2:
            # Check for sign changes
            sign_changes = sum(
                1 for i in range(1, len(polarities))
                if polarities[i] * polarities[i-1] < 0
            )

            # Check polarity variance
            variance = np.var(polarities)

            # Combine metrics
            shift = (sign_changes / (len(polarities) - 1)) * 0.6 + min(variance * 2, 0.4)
            return min(shift, 1.0)

        return 0.0

    def extract(self, text: str) -> np.ndarray:
        """
        Extract sentiment features from text.

        Args:
            text: Input text string

        Returns:
            np.ndarray: Feature vector of shape (4,)
        """
        try:
            # Calculate all sentiment features
            polarity = self._calculate_polarity(text)
            subjectivity = self._calculate_subjectivity(text)
            intensity = self._calculate_intensity(text)
            valence_shift = self._calculate_valence_shift(text)

            # Scale polarity from [-1, 1] to [0, 1] for consistency
            polarity_scaled = (polarity + 1) / 2

            # Build feature vector
            features = np.array([
                polarity_scaled,    # 0: polarity (0=negative, 0.5=neutral, 1=positive)
                subjectivity,       # 1: subjectivity (0=objective, 1=subjective)
                intensity,          # 2: emotional intensity
                valence_shift       # 3: sentiment shift
            ], dtype=np.float32)

            return features

        except Exception as e:
            logger.error(f"Sentiment features extraction error: {e}")
            return self._get_zero_features()

    def get_detailed_sentiment(self, text: str) -> dict:
        """
        Get detailed sentiment analysis for interpretability.

        Args:
            text: Input text

        Returns:
            Dict with detailed sentiment metrics
        """
        polarity = self._calculate_polarity(text)

        return {
            'polarity': polarity,
            'polarity_label': 'positive' if polarity > 0.1 else ('negative' if polarity < -0.1 else 'neutral'),
            'subjectivity': self._calculate_subjectivity(text),
            'intensity': self._calculate_intensity(text),
            'valence_shift': self._calculate_valence_shift(text)
        }

    def get_feature_names(self) -> List[str]:
        """Get feature names for interpretability."""
        return [
            'polarity_score',
            'subjectivity_score',
            'intensity_score',
            'valence_shift_score'
        ]
