"""
Central Configuration for Emotion Detection System
===================================================

All enhancement modules can be toggled ON/OFF via this file.
Disabling any feature will NOT break training or inference.

USAGE:
------
1. Set any flag to False to disable that feature
2. No code changes required elsewhere
3. System falls back to baseline behavior automatically

"""

# =============================================================================
# FEATURE MODULES (Plugin Architecture)
# =============================================================================

# Core TF-IDF features (baseline - always enabled for backward compatibility)
ENABLE_TFIDF_FEATURES = True

# Word bank / rule-based features from existing system
ENABLE_EXISTING_FEATURES = True

# Emotion lexicon features (NRC, custom lexicons)
# Extracts: anxiety/fear, sadness, anger, joy scores
ENABLE_LEXICON_FEATURES = True

# Linguistic style features
# Extracts: avg sentence length, negation count, pronoun ratio, etc.
ENABLE_LINGUISTIC_FEATURES = True

# Sentiment signal features
# Extracts: polarity, subjectivity, emotional intensity
ENABLE_SENTIMENT_FEATURES = True


# =============================================================================
# CONTEXT WINDOW (Message History)
# =============================================================================

# Enable context-aware prediction using message history
ENABLE_CONTEXT_WINDOW = False

# Maximum number of past messages to consider
CONTEXT_WINDOW_SIZE = 3

# Weights for combining messages (most recent first)
# Latest message gets highest weight
CONTEXT_WEIGHTS = [0.6, 0.25, 0.15]


# =============================================================================
# HIERARCHICAL CLASSIFICATION
# =============================================================================

# Enable multi-stage hierarchical classification
# Stage 1: Neutral vs Emotional
# Stage 2: Positive vs Negative
# Stage 3: Fine-grained emotion
ENABLE_HIERARCHICAL_CLASSIFICATION = False

# Enable/disable individual stages (only if ENABLE_HIERARCHICAL_CLASSIFICATION=True)
ENABLE_STAGE1_NEUTRAL_EMOTIONAL = True
ENABLE_STAGE2_POSITIVE_NEGATIVE = True
ENABLE_STAGE3_FINE_GRAINED = True


# =============================================================================
# ENSEMBLE STRATEGY
# =============================================================================

# Enable weighted soft-voting ensemble
ENABLE_ENSEMBLE = False

# Model weights for ensemble (must sum to 1.0)
# Only used if ENABLE_ENSEMBLE=True
ENSEMBLE_WEIGHTS = {
    'logistic_regression': 0.35,
    'svm': 0.30,
    'xgboost': 0.35
}

# Fallback model when ensemble is disabled
# Options: 'logistic_regression', 'svm', 'xgboost'
DEFAULT_SINGLE_MODEL = 'logistic_regression'


# =============================================================================
# CONFIDENCE THRESHOLDS
# =============================================================================

# Confidence thresholds for output categorization
CONFIDENCE_HIGH_THRESHOLD = 0.75
CONFIDENCE_MEDIUM_THRESHOLD = 0.50
CONFIDENCE_LOW_THRESHOLD = 0.30

# Mark predictions below this threshold as "uncertain"
UNCERTAINTY_THRESHOLD = 0.35


# =============================================================================
# FEATURE DIMENSIONS (for reference/validation)
# =============================================================================

# Expected feature dimensions per module
FEATURE_DIMS = {
    'tfidf_word': 6000,
    'tfidf_char': 8000,
    'existing': 10,       # Word bank match counts
    'lexicon': 8,         # Emotion lexicon scores
    'linguistic': 6,      # Linguistic style features
    'sentiment': 4        # Sentiment features
}


# =============================================================================
# MODEL PATHS
# =============================================================================

import os

# Base directory for models
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')

# Model file paths
MODELS = {
    'emotion_model': os.path.join(MODEL_DIR, 'emotion_model.pkl'),
    'tfidf_word': os.path.join(MODEL_DIR, 'tfidf_word.pkl'),
    'tfidf_char': os.path.join(MODEL_DIR, 'tfidf_char.pkl'),

    # New models (created when enabled)
    'svm_model': os.path.join(MODEL_DIR, 'svm_model.pkl'),
    'xgboost_model': os.path.join(MODEL_DIR, 'xgboost_model.pkl'),

    # Hierarchical models
    'stage1_model': os.path.join(MODEL_DIR, 'stage1_neutral_emotional.pkl'),
    'stage2_model': os.path.join(MODEL_DIR, 'stage2_positive_negative.pkl'),
    'stage3_model': os.path.join(MODEL_DIR, 'stage3_fine_grained.pkl'),
}


# =============================================================================
# LOGGING
# =============================================================================

# Enable verbose logging for debugging
VERBOSE_LOGGING = False


# =============================================================================
# HELPER FUNCTION
# =============================================================================

def get_enabled_features():
    """Returns list of enabled feature module names."""
    enabled = []
    if ENABLE_TFIDF_FEATURES:
        enabled.append('tfidf')
    if ENABLE_EXISTING_FEATURES:
        enabled.append('existing')
    if ENABLE_LEXICON_FEATURES:
        enabled.append('lexicon')
    if ENABLE_LINGUISTIC_FEATURES:
        enabled.append('linguistic')
    if ENABLE_SENTIMENT_FEATURES:
        enabled.append('sentiment')
    return enabled


def print_config():
    """Print current configuration for debugging."""
    print("=" * 60)
    print("EMOTION DETECTION SYSTEM CONFIGURATION")
    print("=" * 60)
    print(f"\nFeature Modules:")
    print(f"  TF-IDF Features:      {ENABLE_TFIDF_FEATURES}")
    print(f"  Existing Features:    {ENABLE_EXISTING_FEATURES}")
    print(f"  Lexicon Features:     {ENABLE_LEXICON_FEATURES}")
    print(f"  Linguistic Features:  {ENABLE_LINGUISTIC_FEATURES}")
    print(f"  Sentiment Features:   {ENABLE_SENTIMENT_FEATURES}")
    print(f"\nContext Window:")
    print(f"  Enabled:              {ENABLE_CONTEXT_WINDOW}")
    print(f"  Window Size:          {CONTEXT_WINDOW_SIZE}")
    print(f"\nHierarchical Classification:")
    print(f"  Enabled:              {ENABLE_HIERARCHICAL_CLASSIFICATION}")
    print(f"\nEnsemble:")
    print(f"  Enabled:              {ENABLE_ENSEMBLE}")
    print(f"  Default Model:        {DEFAULT_SINGLE_MODEL}")
    print(f"\nConfidence Thresholds:")
    print(f"  High:                 {CONFIDENCE_HIGH_THRESHOLD}")
    print(f"  Medium:               {CONFIDENCE_MEDIUM_THRESHOLD}")
    print(f"  Uncertainty:          {UNCERTAINTY_THRESHOLD}")
    print("=" * 60)
