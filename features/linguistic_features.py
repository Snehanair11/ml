"""
Linguistic Style Feature Extractor
==================================

Extracts linguistic style features that correlate with emotional expression.

FEATURES (6 total):
-------------------
1. avg_sentence_length:    Average words per sentence (normalized)
2. negation_count:         Count of negation words (normalized)
3. first_person_ratio:     Ratio of first-person pronouns
4. question_mark_count:    Number of question marks (normalized)
5. exclamation_count:      Number of exclamation marks (normalized)
6. short_sentence_ratio:   Ratio of short sentences (<5 words)

REMOVABILITY:
-------------
This module can be disabled by setting ENABLE_LINGUISTIC_FEATURES = False in config.
The system will continue using TF-IDF and other features.

CONFIG FLAG: ENABLE_LINGUISTIC_FEATURES

"""

import numpy as np
import re
from typing import List, Set
import logging

from .base_feature import BaseFeatureExtractor

logger = logging.getLogger(__name__)


class LinguisticFeatureExtractor(BaseFeatureExtractor):
    """
    Linguistic style-based feature extractor.

    Extracts features related to writing style, sentence structure,
    and linguistic patterns that correlate with emotional states.

    REMOVABILITY:
    -------------
    Can be disabled via config without affecting other features.
    No external dependencies required.
    """

    # Output dimension
    OUTPUT_DIM = 6

    def __init__(self):
        """Initialize linguistic patterns."""
        super().__init__(name='linguistic')
        self._is_fitted = True  # No fitting required

        # Negation words
        self.negation_words: Set[str] = {
            'not', 'no', 'never', 'none', 'nothing', 'nowhere', 'neither',
            'nobody', 'cant', "can't", 'cannot', 'wont', "won't", 'dont',
            "don't", 'doesnt', "doesn't", 'didnt', "didn't", 'isnt', "isn't",
            'arent', "aren't", 'wasnt', "wasn't", 'werent', "weren't",
            'havent', "haven't", 'hasnt', "hasn't", 'hadnt', "hadn't",
            'wouldnt', "wouldn't", 'couldnt', "couldn't", 'shouldnt', "shouldn't",
            'without', 'hardly', 'barely', 'scarcely', 'seldom', 'rarely'
        }

        # First-person pronouns
        self.first_person_pronouns: Set[str] = {
            'i', 'me', 'my', 'mine', 'myself',
            'we', 'us', 'our', 'ours', 'ourselves'
        }

        # Second-person pronouns (for contrast)
        self.second_person_pronouns: Set[str] = {
            'you', 'your', 'yours', 'yourself', 'yourselves'
        }

        # Third-person pronouns
        self.third_person_pronouns: Set[str] = {
            'he', 'him', 'his', 'himself',
            'she', 'her', 'hers', 'herself',
            'it', 'its', 'itself',
            'they', 'them', 'their', 'theirs', 'themselves'
        }

    @property
    def output_dim(self) -> int:
        """Return feature dimension."""
        return self.OUTPUT_DIM

    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: Input text

        Returns:
            List of sentence strings
        """
        # Split on sentence-ending punctuation
        sentences = re.split(r'[.!?]+', text)
        # Filter empty sentences and strip whitespace
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences if sentences else ['']

    def _count_words(self, text: str) -> int:
        """Count words in text."""
        words = re.findall(r'\b\w+\b', text.lower())
        return len(words)

    def extract(self, text: str) -> np.ndarray:
        """
        Extract linguistic style features from text.

        Args:
            text: Input text string

        Returns:
            np.ndarray: Feature vector of shape (6,)
        """
        try:
            # Split into sentences
            sentences = self._split_sentences(text)
            num_sentences = max(len(sentences), 1)

            # Get words
            words = re.findall(r'\b\w+\b', text.lower())
            word_count = max(len(words), 1)
            word_set = set(words)

            # 1. Average sentence length (normalized by log)
            sentence_lengths = [self._count_words(s) for s in sentences]
            avg_sentence_length = np.mean(sentence_lengths) if sentence_lengths else 0
            # Normalize: typical sentences are 10-20 words
            avg_sentence_length_norm = min(avg_sentence_length / 25.0, 1.0)

            # 2. Negation count (normalized by word count)
            negation_count = sum(1 for w in words if w in self.negation_words)
            negation_ratio = negation_count / word_count

            # 3. First-person pronoun ratio
            first_person_count = sum(1 for w in words if w in self.first_person_pronouns)
            first_person_ratio = first_person_count / word_count

            # 4. Question mark count (normalized)
            question_count = text.count('?')
            question_ratio = min(question_count / num_sentences, 1.0)

            # 5. Exclamation mark count (normalized)
            exclamation_count = text.count('!')
            exclamation_ratio = min(exclamation_count / num_sentences, 1.0)

            # 6. Short sentence ratio (sentences with < 5 words)
            short_sentences = sum(1 for length in sentence_lengths if length < 5)
            short_sentence_ratio = short_sentences / num_sentences

            # Build feature vector
            features = np.array([
                avg_sentence_length_norm,    # 0: avg sentence length
                negation_ratio,              # 1: negation ratio
                first_person_ratio,          # 2: first person pronoun ratio
                question_ratio,              # 3: question mark ratio
                exclamation_ratio,           # 4: exclamation ratio
                short_sentence_ratio         # 5: short sentence ratio
            ], dtype=np.float32)

            return features

        except Exception as e:
            logger.error(f"Linguistic features extraction error: {e}")
            return self._get_zero_features()

    def get_detailed_analysis(self, text: str) -> dict:
        """
        Get detailed linguistic analysis for interpretability.

        Args:
            text: Input text

        Returns:
            Dict with detailed linguistic metrics
        """
        sentences = self._split_sentences(text)
        words = re.findall(r'\b\w+\b', text.lower())
        word_count = len(words)

        return {
            'total_words': word_count,
            'total_sentences': len(sentences),
            'avg_sentence_length': word_count / max(len(sentences), 1),
            'negation_count': sum(1 for w in words if w in self.negation_words),
            'first_person_pronouns': sum(1 for w in words if w in self.first_person_pronouns),
            'second_person_pronouns': sum(1 for w in words if w in self.second_person_pronouns),
            'question_marks': text.count('?'),
            'exclamation_marks': text.count('!')
        }

    def get_feature_names(self) -> List[str]:
        """Get feature names for interpretability."""
        return [
            'avg_sentence_length_norm',
            'negation_ratio',
            'first_person_ratio',
            'question_ratio',
            'exclamation_ratio',
            'short_sentence_ratio'
        ]
