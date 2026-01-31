"""
Conversation Intelligence Layer - Configuration
================================================

Toggle flags for all conversation intelligence features.
Disabling ANY flag will NOT break the system - it falls back to baseline behavior.

USAGE:
------
    from src.chatbot.conversation_intelligence_config import *

    if ENABLE_PHASE_ENGINE:
        # use phase-based logic
    else:
        # use baseline logic

"""

# =============================================================================
# MASTER TOGGLE - Disable this to bypass entire intelligence layer
# =============================================================================

ENABLE_CONVERSATION_INTELLIGENCE = True


# =============================================================================
# FEATURE TOGGLES
# =============================================================================

# Phase Engine - Controls conversation flow phases
# (opening, sharing, venting, reflecting, calming, celebrating, closing)
ENABLE_PHASE_ENGINE = True

# Memory Recall - Enables topic/emotion memory callbacks
# Only recalls if turn_count >= 3 and topic appeared >= 2 times
ENABLE_MEMORY_RECALL = True

# Advice Detection - Detects vent_only vs advice_ok intent
# Prevents advice-giving when user just wants to vent
ENABLE_ADVICE_DETECTION = True

# Cooldowns - Prevents same reply category from firing repeatedly
ENABLE_COOLDOWNS = True

# Emotion Streaks - Tracks positive/neutral/distress streaks
# Enables phase transitions based on emotional patterns
ENABLE_EMOTION_STREAKS = True


# =============================================================================
# PHASE ENGINE SETTINGS
# =============================================================================

# Minimum message length to trigger venting phase (characters)
VENTING_MIN_LENGTH = 100

# Minimum word count to trigger venting phase
VENTING_MIN_WORDS = 20

# Signal spike threshold for venting detection
VENTING_SIGNAL_THRESHOLD = 2

# Turns required before reflecting phase is allowed
REFLECT_MIN_TURNS = 2

# Positive streak required for celebrating phase
CELEBRATING_STREAK_THRESHOLD = 2

# Distress streak required for calming phase
CALMING_STREAK_THRESHOLD = 2


# =============================================================================
# MEMORY RECALL SETTINGS
# =============================================================================

# Minimum turns before memory recall is allowed
MEMORY_RECALL_MIN_TURNS = 3

# Minimum topic occurrences before recall
MEMORY_RECALL_MIN_OCCURRENCES = 2

# Probability of triggering memory recall (when conditions met)
MEMORY_RECALL_PROBABILITY = 0.4

# Phases where memory recall is allowed
MEMORY_ALLOWED_PHASES = {"reflecting", "celebrating", "calming"}


# =============================================================================
# ADVICE DETECTION SETTINGS
# =============================================================================

# Rant indicators (trigger vent_only mode)
RANT_INDICATORS = {
    "i just need to vent",
    "let me vent",
    "just venting",
    "need to get this off my chest",
    "i dont need advice",
    "dont need advice",
    "not looking for advice",
    "just need someone to listen",
    "just listen",
    "dont tell me what to do",
    "let me rant"
}

# Explicit advice request phrases
ADVICE_REQUEST_INDICATORS = {
    "what should i do",
    "what do you think i should do",
    "what would you do",
    "any advice",
    "do you have advice",
    "give me advice",
    "need advice",
    "help me figure out",
    "what do you suggest",
    "should i"
}

# Minimum message length to consider as rant (vent_only)
RANT_MIN_LENGTH = 150


# =============================================================================
# COOLDOWN SETTINGS (turns)
# =============================================================================

# Default cooldown per category (in turns)
DEFAULT_COOLDOWN = 3

# Category-specific cooldowns
COOLDOWN_CONFIG = {
    "what_happened_question": 3,    # "what happened?" style questions
    "celebration_hype": 2,          # excited celebration responses
    "memory_callback": 4,           # memory-based responses
    "grounding_message": 3,         # calming/grounding messages
    "advice_prompt": 4,             # advice-giving responses
    "breathe_tip": 3,               # "take a breath" messages
    "validation_heavy": 2           # heavy validation responses
}

# Categories exempt from cooldowns in emergency phases
EMERGENCY_EXEMPT_CATEGORIES = {"grounding_message"}


# =============================================================================
# EMOTION STREAK THRESHOLDS
# =============================================================================

# Number of consecutive emotions to qualify as a streak
STREAK_THRESHOLD = 2

# Distress streak threshold for escalation
DISTRESS_ESCALATION_THRESHOLD = 3

# Positive streak threshold for celebration mode
POSITIVE_CELEBRATION_THRESHOLD = 2

# Neutral streak threshold for gentle invitation
NEUTRAL_INVITATION_THRESHOLD = 3


# =============================================================================
# VENTING SCORE SETTINGS
# =============================================================================

# Base score added for each rant indicator
VENT_INDICATOR_SCORE = 2

# Score added per 50 chars over VENTING_MIN_LENGTH
VENT_LENGTH_SCORE_PER_50 = 1

# Score threshold to classify as venting
VENT_SCORE_THRESHOLD = 3

# Max venting score (cap)
VENT_SCORE_MAX = 10


# =============================================================================
# DEBUG / LOGGING
# =============================================================================

# Enable verbose logging for conversation intelligence
VERBOSE_INTELLIGENCE_LOGGING = False
