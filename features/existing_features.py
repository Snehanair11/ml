"""
Existing Features Extractor
===========================

Extracts features based on the existing word bank matching system.
This preserves the rule-based intelligence from the original pipeline.

FEATURES (10 total):
--------------------
1. positive_word_count:   Count of positive emotion words
2. sad_word_count:        Count of sadness words
3. distress_word_count:   Count of distress/anxiety words
4. anger_word_count:      Count of anger words
5. exhaustion_phrase_count: Count of exhaustion phrases
6. positive_ratio:        Ratio of positive to total emotion words
7. negative_ratio:        Ratio of negative to total emotion words
8. has_intense_words:     Binary: contains intense/elongated words
9. has_profanity:         Binary: contains curse words
10. word_count:           Total word count (normalized)

REMOVABILITY:
-------------
This module can be disabled by setting ENABLE_EXISTING_FEATURES = False in config.
The system will continue to work using TF-IDF and other features.

CONFIG FLAG: ENABLE_EXISTING_FEATURES

"""

import numpy as np
import re
from typing import List, Set
import logging

from .base_feature import BaseFeatureExtractor

logger = logging.getLogger(__name__)


class ExistingFeatureExtractor(BaseFeatureExtractor):
    """
    Feature extractor based on existing word bank matching system.

    This preserves the domain knowledge encoded in the original
    emotion detection word banks and rules.

    REMOVABILITY:
    -------------
    Can be disabled via config without affecting other features.
    """

    # Output dimension
    OUTPUT_DIM = 10

    def __init__(self):
        """Initialize with word banks from original system."""
        super().__init__(name='existing')
        self._is_fitted = True  # No fitting required

        # Word banks (condensed from original system)
        self._init_word_banks()

    def _init_word_banks(self):
        """Initialize emotion word banks."""

        # Positive emotion words
        self.positive_words: Set[str] = {
            'happy', 'joy', 'excited', 'grateful', 'thankful', 'blessed',
            'amazing', 'wonderful', 'great', 'awesome', 'fantastic', 'excellent',
            'proud', 'accomplished', 'successful', 'loved', 'appreciated',
            'hopeful', 'optimistic', 'confident', 'peaceful', 'calm', 'relaxed',
            'thrilled', 'delighted', 'overjoyed', 'ecstatic', 'elated',
            'content', 'satisfied', 'fulfilled', 'encouraged', 'inspired',
            'motivated', 'energized', 'refreshed', 'relieved', 'secure',
            'cheerful', 'joyful', 'blissful', 'radiant', 'glowing',
            'promoted', 'hired', 'raise', 'bonus', 'recognition', 'praise',
            'celebration', 'achievement', 'milestone', 'breakthrough',
            'yay', 'woohoo', 'hurray', 'yes', 'finally'
        }

        # Sadness words
        self.sad_words: Set[str] = {
            'sad', 'depressed', 'hopeless', 'lonely', 'isolated', 'empty',
            'heartbroken', 'devastated', 'crushed', 'shattered', 'broken',
            'grief', 'mourning', 'loss', 'bereaved', 'widow', 'widower',
            'crying', 'tears', 'weeping', 'sobbing', 'wept',
            'miserable', 'unhappy', 'gloomy', 'melancholy', 'despondent',
            'down', 'blue', 'low', 'dejected', 'downcast', 'crestfallen',
            'hurt', 'wounded', 'pained', 'aching', 'suffering',
            'abandoned', 'rejected', 'unwanted', 'neglected', 'forgotten',
            'fired', 'terminated', 'laid off', 'let go', 'dismissed',
            'failed', 'failure', 'lost', 'losing', 'miss', 'missing'
        }

        # Distress/anxiety words
        self.distress_words: Set[str] = {
            'anxious', 'anxiety', 'worried', 'nervous', 'panicked', 'panic',
            'scared', 'afraid', 'terrified', 'frightened', 'fearful', 'fear',
            'stressed', 'overwhelmed', 'overloaded', 'swamped', 'drowning',
            'exhausted', 'burned out', 'burnout', 'depleted', 'drained',
            'tired', 'fatigued', 'weary', 'worn out', 'spent',
            'struggling', 'suffering', 'helpless', 'trapped', 'stuck',
            'desperate', 'frantic', 'frenzied', 'hysterical',
            'tense', 'on edge', 'restless', 'agitated', 'jittery',
            'cant cope', 'cant handle', 'too much', 'breaking down',
            'falling apart', 'losing it', 'going crazy', 'losing my mind',
            'workload', 'deadline', 'pressure', 'demands', 'expectations',
            'insomnia', 'cant sleep', 'nightmares', 'racing thoughts'
        }

        # Anger words
        self.anger_words: Set[str] = {
            'angry', 'furious', 'enraged', 'livid', 'seething', 'fuming',
            'mad', 'pissed', 'irritated', 'annoyed', 'frustrated', 'aggravated',
            'outraged', 'incensed', 'infuriated', 'irate', 'wrathful',
            'hate', 'hatred', 'loathe', 'despise', 'detest', 'resent',
            'bitter', 'resentful', 'hostile', 'antagonistic', 'aggressive',
            'betrayed', 'backstabbed', 'cheated', 'wronged', 'mistreated',
            'unfair', 'unjust', 'discriminated', 'harassed', 'bullied',
            'disrespected', 'insulted', 'humiliated', 'degraded', 'belittled',
            'sick of', 'fed up', 'had enough', 'done with', 'over it'
        }

        # Exhaustion phrases (exact matches)
        self.exhaustion_phrases: List[str] = [
            "i can't do this anymore",
            "i cant do this anymore",
            "i give up",
            "i want to quit",
            "i need a break",
            "burning out",
            "at my limit",
            "reached my limit",
            "can't take it",
            "cant take it",
            "too much pressure",
            "falling apart",
            "breaking down",
            "losing my mind",
            "going crazy",
            "mental health",
            "need help",
            "rock bottom",
            "hitting bottom",
            "end of my rope"
        ]

        # Intense words (elongations, emphasis)
        self.intense_words: Set[str] = {
            'soooo', 'sooo', 'ugh', 'ughhh', 'argh', 'arghhh',
            'nooo', 'noooo', 'whyyy', 'whhyy', 'help', 'helpp',
            'please', 'pleaseee', 'stop', 'stopp', 'enough',
            'die', 'dying', 'kill', 'killing', 'dead'
        }

        # Profanity indicators
        self.profanity_words: Set[str] = {
            'fuck', 'fucking', 'fucked', 'shit', 'shitty', 'damn',
            'damned', 'hell', 'ass', 'crap', 'bullshit', 'bastard'
        }

    @property
    def output_dim(self) -> int:
        """Return feature dimension."""
        return self.OUTPUT_DIM

    def extract(self, text: str) -> np.ndarray:
        """
        Extract word bank-based features from text.

        Args:
            text: Input text string

        Returns:
            np.ndarray: Feature vector of shape (10,)
        """
        try:
            # Normalize text
            text_lower = text.lower()
            words = set(re.findall(r'\b\w+\b', text_lower))
            word_count = len(words) if words else 1

            # Count matches in each category
            positive_count = len(words & self.positive_words)
            sad_count = len(words & self.sad_words)
            distress_count = len(words & self.distress_words)
            anger_count = len(words & self.anger_words)

            # Count exhaustion phrases
            exhaustion_count = sum(
                1 for phrase in self.exhaustion_phrases
                if phrase in text_lower
            )

            # Calculate ratios
            total_emotion = positive_count + sad_count + distress_count + anger_count
            total_emotion = max(total_emotion, 1)  # Avoid division by zero

            positive_ratio = positive_count / total_emotion
            negative_ratio = (sad_count + distress_count + anger_count) / total_emotion

            # Binary features
            has_intense = 1.0 if len(words & self.intense_words) > 0 else 0.0
            has_profanity = 1.0 if len(words & self.profanity_words) > 0 else 0.0

            # Normalized word count (log scale)
            normalized_word_count = np.log1p(word_count) / 10.0

            # Build feature vector
            features = np.array([
                positive_count / max(word_count, 1),      # 0: positive ratio to words
                sad_count / max(word_count, 1),           # 1: sad ratio to words
                distress_count / max(word_count, 1),      # 2: distress ratio to words
                anger_count / max(word_count, 1),         # 3: anger ratio to words
                exhaustion_count / 5.0,                    # 4: exhaustion (normalized)
                positive_ratio,                            # 5: positive vs emotions
                negative_ratio,                            # 6: negative vs emotions
                has_intense,                               # 7: intense words
                has_profanity,                             # 8: profanity
                normalized_word_count                      # 9: word count
            ], dtype=np.float32)

            return features

        except Exception as e:
            logger.error(f"Existing features extraction error: {e}")
            return self._get_zero_features()

    def get_feature_names(self) -> List[str]:
        """Get feature names for interpretability."""
        return [
            'positive_word_ratio',
            'sad_word_ratio',
            'distress_word_ratio',
            'anger_word_ratio',
            'exhaustion_phrase_count',
            'positive_emotion_ratio',
            'negative_emotion_ratio',
            'has_intense_words',
            'has_profanity',
            'normalized_word_count'
        ]
