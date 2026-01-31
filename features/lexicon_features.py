"""
Emotion Lexicon Feature Extractor
=================================

Extracts emotion scores using a lightweight built-in emotion lexicon.
Inspired by NRC Emotion Lexicon but self-contained (no external dependencies).

FEATURES (8 total):
-------------------
1. fear_score:      Normalized fear/anxiety score
2. sadness_score:   Normalized sadness score
3. anger_score:     Normalized anger score
4. joy_score:       Normalized joy/happiness score
5. trust_score:     Normalized trust score
6. anticipation_score: Normalized anticipation score
7. disgust_score:   Normalized disgust score
8. surprise_score:  Normalized surprise score

REMOVABILITY:
-------------
This module can be disabled by setting ENABLE_LEXICON_FEATURES = False in config.
The system will continue using TF-IDF and other features.

CONFIG FLAG: ENABLE_LEXICON_FEATURES

"""

import numpy as np
import re
from typing import List, Dict, Set
import logging

from .base_feature import BaseFeatureExtractor

logger = logging.getLogger(__name__)


class LexiconFeatureExtractor(BaseFeatureExtractor):
    """
    Emotion lexicon-based feature extractor.

    Uses a built-in emotion lexicon mapping words to emotion categories.
    Each word can belong to multiple emotion categories with different intensities.

    REMOVABILITY:
    -------------
    Can be disabled via config without affecting other features.
    No external dependencies required.
    """

    # Output dimension (8 emotion categories)
    OUTPUT_DIM = 8

    # Emotion categories
    EMOTIONS = ['fear', 'sadness', 'anger', 'joy', 'trust', 'anticipation', 'disgust', 'surprise']

    def __init__(self):
        """Initialize with built-in emotion lexicon."""
        super().__init__(name='lexicon')
        self._is_fitted = True  # No fitting required

        # Build emotion lexicon
        self._build_lexicon()

    def _build_lexicon(self):
        """
        Build built-in emotion lexicon.

        Each word maps to a dict of {emotion: intensity} where intensity is 0.0-1.0.
        This is a curated lexicon optimized for mental health/workplace contexts.
        """
        self.lexicon: Dict[str, Dict[str, float]] = {}

        # Fear/Anxiety words
        fear_words = {
            # High intensity (1.0)
            'terrified': 1.0, 'petrified': 1.0, 'horrified': 1.0, 'panicked': 1.0,
            'panic': 1.0, 'terror': 1.0, 'phobia': 1.0, 'dread': 1.0,
            # Medium-high (0.8)
            'afraid': 0.8, 'scared': 0.8, 'frightened': 0.8, 'fearful': 0.8,
            'anxious': 0.8, 'anxiety': 0.8, 'worried': 0.8, 'alarmed': 0.8,
            # Medium (0.6)
            'nervous': 0.6, 'uneasy': 0.6, 'tense': 0.6, 'apprehensive': 0.6,
            'stressed': 0.6, 'overwhelmed': 0.6, 'insecure': 0.6, 'vulnerable': 0.6,
            # Low-medium (0.4)
            'concerned': 0.4, 'unsure': 0.4, 'hesitant': 0.4, 'doubtful': 0.4,
            'uncertain': 0.4, 'wary': 0.4, 'cautious': 0.4, 'restless': 0.4
        }
        for word, intensity in fear_words.items():
            self._add_emotion(word, 'fear', intensity)

        # Sadness words
        sadness_words = {
            # High intensity (1.0)
            'devastated': 1.0, 'heartbroken': 1.0, 'anguish': 1.0, 'despair': 1.0,
            'grief': 1.0, 'mourning': 1.0, 'bereaved': 1.0, 'suicidal': 1.0,
            # Medium-high (0.8)
            'depressed': 0.8, 'hopeless': 0.8, 'miserable': 0.8, 'despondent': 0.8,
            'dejected': 0.8, 'crushed': 0.8, 'broken': 0.8, 'shattered': 0.8,
            # Medium (0.6)
            'sad': 0.6, 'unhappy': 0.6, 'sorrowful': 0.6, 'melancholy': 0.6,
            'gloomy': 0.6, 'downcast': 0.6, 'disheartened': 0.6, 'lonely': 0.6,
            # Low-medium (0.4)
            'down': 0.4, 'blue': 0.4, 'low': 0.4, 'disappointed': 0.4,
            'hurt': 0.4, 'upset': 0.4, 'tearful': 0.4, 'crying': 0.4
        }
        for word, intensity in sadness_words.items():
            self._add_emotion(word, 'sadness', intensity)

        # Anger words
        anger_words = {
            # High intensity (1.0)
            'furious': 1.0, 'enraged': 1.0, 'livid': 1.0, 'seething': 1.0,
            'outraged': 1.0, 'incensed': 1.0, 'wrathful': 1.0, 'vengeful': 1.0,
            # Medium-high (0.8)
            'angry': 0.8, 'mad': 0.8, 'irate': 0.8, 'infuriated': 0.8,
            'hostile': 0.8, 'aggressive': 0.8, 'hate': 0.8, 'hatred': 0.8,
            # Medium (0.6)
            'frustrated': 0.6, 'irritated': 0.6, 'annoyed': 0.6, 'aggravated': 0.6,
            'resentful': 0.6, 'bitter': 0.6, 'indignant': 0.6, 'offended': 0.6,
            # Low-medium (0.4)
            'bothered': 0.4, 'peeved': 0.4, 'irked': 0.4, 'displeased': 0.4,
            'impatient': 0.4, 'exasperated': 0.4, 'ticked': 0.4, 'vexed': 0.4
        }
        for word, intensity in anger_words.items():
            self._add_emotion(word, 'anger', intensity)

        # Joy/Happiness words
        joy_words = {
            # High intensity (1.0)
            'ecstatic': 1.0, 'elated': 1.0, 'overjoyed': 1.0, 'thrilled': 1.0,
            'euphoric': 1.0, 'blissful': 1.0, 'rapturous': 1.0, 'jubilant': 1.0,
            # Medium-high (0.8)
            'happy': 0.8, 'joyful': 0.8, 'delighted': 0.8, 'excited': 0.8,
            'cheerful': 0.8, 'gleeful': 0.8, 'merry': 0.8, 'radiant': 0.8,
            # Medium (0.6)
            'pleased': 0.6, 'glad': 0.6, 'content': 0.6, 'satisfied': 0.6,
            'grateful': 0.6, 'thankful': 0.6, 'blessed': 0.6, 'fortunate': 0.6,
            # Low-medium (0.4)
            'amused': 0.4, 'entertained': 0.4, 'lighthearted': 0.4, 'carefree': 0.4,
            'relaxed': 0.4, 'comfortable': 0.4, 'peaceful': 0.4, 'calm': 0.4
        }
        for word, intensity in joy_words.items():
            self._add_emotion(word, 'joy', intensity)

        # Trust words
        trust_words = {
            'trust': 0.8, 'confident': 0.8, 'secure': 0.8, 'reliable': 0.7,
            'faithful': 0.7, 'loyal': 0.7, 'dependable': 0.7, 'honest': 0.6,
            'sincere': 0.6, 'genuine': 0.6, 'authentic': 0.6, 'supportive': 0.6,
            'safe': 0.5, 'protected': 0.5, 'assured': 0.5, 'certain': 0.5
        }
        for word, intensity in trust_words.items():
            self._add_emotion(word, 'trust', intensity)

        # Anticipation words
        anticipation_words = {
            'eager': 0.8, 'excited': 0.8, 'hopeful': 0.7, 'expectant': 0.7,
            'looking forward': 0.7, 'anticipating': 0.7, 'awaiting': 0.6,
            'curious': 0.5, 'interested': 0.5, 'intrigued': 0.5, 'wondering': 0.4
        }
        for word, intensity in anticipation_words.items():
            self._add_emotion(word, 'anticipation', intensity)

        # Disgust words
        disgust_words = {
            'disgusted': 1.0, 'revolted': 1.0, 'repulsed': 1.0, 'sickened': 0.9,
            'nauseated': 0.8, 'appalled': 0.8, 'horrified': 0.7, 'offended': 0.6,
            'gross': 0.6, 'yuck': 0.6, 'ew': 0.5, 'distasteful': 0.5
        }
        for word, intensity in disgust_words.items():
            self._add_emotion(word, 'disgust', intensity)

        # Surprise words
        surprise_words = {
            'shocked': 0.9, 'astonished': 0.9, 'stunned': 0.8, 'amazed': 0.8,
            'astounded': 0.8, 'startled': 0.7, 'surprised': 0.7, 'unexpected': 0.6,
            'wow': 0.6, 'whoa': 0.6, 'unbelievable': 0.5, 'incredible': 0.5
        }
        for word, intensity in surprise_words.items():
            self._add_emotion(word, 'surprise', intensity)

        logger.info(f"Lexicon loaded with {len(self.lexicon)} words")

    def _add_emotion(self, word: str, emotion: str, intensity: float):
        """Add word-emotion mapping to lexicon."""
        if word not in self.lexicon:
            self.lexicon[word] = {}
        self.lexicon[word][emotion] = intensity

    @property
    def output_dim(self) -> int:
        """Return feature dimension."""
        return self.OUTPUT_DIM

    def extract(self, text: str) -> np.ndarray:
        """
        Extract emotion lexicon scores from text.

        Args:
            text: Input text string

        Returns:
            np.ndarray: Feature vector of shape (8,) with emotion scores
        """
        try:
            # Normalize text and extract words
            text_lower = text.lower()
            words = re.findall(r'\b\w+\b', text_lower)
            word_count = len(words) if words else 1

            # Initialize emotion scores
            scores = {emotion: 0.0 for emotion in self.EMOTIONS}

            # Accumulate scores from lexicon matches
            matches = 0
            for word in words:
                if word in self.lexicon:
                    matches += 1
                    for emotion, intensity in self.lexicon[word].items():
                        scores[emotion] += intensity

            # Normalize by word count (to handle different text lengths)
            if matches > 0:
                for emotion in scores:
                    scores[emotion] = scores[emotion] / word_count
                    # Clip to [0, 1] range
                    scores[emotion] = min(1.0, scores[emotion])

            # Build feature vector in consistent order
            features = np.array([
                scores['fear'],
                scores['sadness'],
                scores['anger'],
                scores['joy'],
                scores['trust'],
                scores['anticipation'],
                scores['disgust'],
                scores['surprise']
            ], dtype=np.float32)

            return features

        except Exception as e:
            logger.error(f"Lexicon features extraction error: {e}")
            return self._get_zero_features()

    def get_emotion_breakdown(self, text: str) -> Dict[str, float]:
        """
        Get detailed emotion breakdown for interpretability.

        Args:
            text: Input text

        Returns:
            Dict mapping emotion names to scores
        """
        features = self.extract(text)
        return dict(zip(self.EMOTIONS, features.tolist()))

    def get_dominant_emotion(self, text: str) -> tuple:
        """
        Get the dominant emotion from text.

        Args:
            text: Input text

        Returns:
            Tuple of (emotion_name, score)
        """
        features = self.extract(text)
        idx = np.argmax(features)
        return self.EMOTIONS[idx], features[idx]

    def get_feature_names(self) -> List[str]:
        """Get feature names for interpretability."""
        return [f'{emotion}_score' for emotion in self.EMOTIONS]
