"""
Advice Detection - Venting vs Advice Intent
============================================

Detects whether user wants to vent or is seeking advice.
Works across ALL emotions.

MODES:
------
- VENT_ONLY:  User just wants to express, no advice wanted
- ADVICE_OK:  User is open to suggestions/guidance
- UNKNOWN:    Cannot determine, may ask once

INDICATORS:
-----------
Vent-only signals:
- Long messages (rants)
- Rant starters ("i just need to...", "let me vent")
- Emotional intensity (positive or negative)
- Explicit "no advice" phrases

Advice-ok signals:
- Direct questions ("what should i do?")
- Explicit advice requests
- Problem-solution framing

RULES:
------
- In VENT_ONLY: No advice, no "what should you do"
- In ADVICE_OK: Gentle guidance allowed
- In UNKNOWN: Ask ONCE "do you want advice or just want to vent?"

REMOVABILITY:
-------------
Disable via ENABLE_ADVICE_DETECTION = False in config.

"""

import re
from typing import Tuple, Optional

from src.chatbot.enhanced_conversation_state import (
    EnhancedConversationState,
    AdviceMode
)
from src.chatbot import conversation_intelligence_config as ci_config


# =============================================================================
# PHRASE SETS
# =============================================================================

# Explicit vent-only phrases
VENT_ONLY_PHRASES = {
    # Direct statements
    "i just need to vent",
    "let me vent",
    "just venting",
    "need to get this off my chest",
    "i dont need advice",
    "i don't need advice",
    "dont need advice",
    "don't need advice",
    "not looking for advice",
    "just need someone to listen",
    "just listen",
    "dont tell me what to do",
    "don't tell me what to do",
    "let me rant",
    "i need to rant",
    "just need to talk",
    "not asking for advice",
    "not looking for solutions",
    "dont fix it",
    "don't fix it",
    "just let me complain",
    "i just want to talk",
    "i just wanna talk"
}

# Explicit advice request phrases
ADVICE_REQUEST_PHRASES = {
    "what should i do",
    "what do you think i should do",
    "what would you do",
    "any advice",
    "do you have advice",
    "give me advice",
    "need advice",
    "help me figure out",
    "what do you suggest",
    "should i",
    "how do i",
    "how should i",
    "what can i do",
    "is there anything i can do",
    "help me decide",
    "i need help with",
    "can you help me",
    "what do you recommend",
    "your opinion",
    "your thoughts"
}

# Rant starters (indicate venting intent)
RANT_STARTERS = {
    "i just",
    "i cant believe",
    "i can't believe",
    "omg",
    "like seriously",
    "bruh",
    "you wont believe",
    "you won't believe",
    "i swear",
    "honestly",
    "ugh",
    "why does",
    "why do",
    "im so done",
    "i'm so done",
    "i hate",
    "i love how"  # sarcastic
}

# Ask-about-advice prompt (used when mode is UNKNOWN)
ADVICE_QUESTION = "do you want me to help you think through this, or do you just need to vent rn? either is totally cool"


# =============================================================================
# DETECTION FUNCTIONS
# =============================================================================

def _has_phrase(text: str, phrases: set) -> bool:
    """Check if text contains any phrase from set."""
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in phrases)


def _count_matching_phrases(text: str, phrases: set) -> int:
    """Count how many phrases match."""
    text_lower = text.lower()
    return sum(1 for phrase in phrases if phrase in text_lower)


def detect_advice_mode(
    text: str,
    state: EnhancedConversationState
) -> Tuple[str, float, str]:
    """
    Detect user's advice preference from message.

    Args:
        text: Message text
        state: Enhanced conversation state

    Returns:
        Tuple of (mode, confidence, reason)
        - mode: VENT_ONLY, ADVICE_OK, or UNKNOWN
        - confidence: 0.0 to 1.0
        - reason: Explanation for detection
    """
    if not ci_config.ENABLE_ADVICE_DETECTION:
        return AdviceMode.UNKNOWN, 0.0, "detection_disabled"

    text_lower = text.lower()

    # --- EXPLICIT VENT-ONLY DETECTION ---
    if _has_phrase(text, VENT_ONLY_PHRASES):
        return AdviceMode.VENT_ONLY, 1.0, "explicit_vent_phrase"

    # --- EXPLICIT ADVICE REQUEST ---
    if _has_phrase(text, ADVICE_REQUEST_PHRASES):
        return AdviceMode.ADVICE_OK, 1.0, "explicit_advice_request"

    # --- IMPLICIT VENT DETECTION ---
    vent_score = 0.0

    # Long message = likely venting
    char_count = len(text)
    word_count = len(text.split())

    if char_count > ci_config.RANT_MIN_LENGTH:
        vent_score += 0.4

    if word_count > 30:
        vent_score += 0.3

    # Rant starters
    if _has_phrase(text, RANT_STARTERS):
        vent_score += 0.3

    # Multiple sentences with emotional punctuation
    exclamation_count = text.count('!')
    if exclamation_count >= 2:
        vent_score += 0.2

    # All caps words (emphasis/emotion)
    caps_words = len(re.findall(r'\b[A-Z]{2,}\b', text))
    if caps_words >= 2:
        vent_score += 0.1

    # --- IMPLICIT ADVICE SEEKING ---
    advice_score = 0.0

    # Questions that imply seeking guidance
    question_patterns = [
        r'\bwhat (should|can|do)\b',
        r'\bhow (do|can|should)\b',
        r'\bis (it|this|that) (okay|normal|right)\b',
        r'\bshould i\b',
        r'\bdo you think\b'
    ]

    for pattern in question_patterns:
        if re.search(pattern, text_lower):
            advice_score += 0.3

    # Short, focused question (not rant)
    if word_count < 15 and text.count('?') >= 1:
        advice_score += 0.2

    # --- DETERMINE MODE ---
    if vent_score >= 0.6:
        return AdviceMode.VENT_ONLY, min(vent_score, 1.0), "implicit_vent_detected"

    if advice_score >= 0.5:
        return AdviceMode.ADVICE_OK, min(advice_score, 1.0), "implicit_advice_seeking"

    # Check if state already has a mode set from previous detection
    if state.advice_mode != AdviceMode.UNKNOWN:
        return state.advice_mode, 0.5, "using_previous_mode"

    return AdviceMode.UNKNOWN, 0.0, "cannot_determine"


def calculate_venting_score(
    text: str,
    signals: dict,
    state: EnhancedConversationState
) -> float:
    """
    Calculate a venting score for the message.

    Higher score = more likely user is venting.

    Args:
        text: Message text
        signals: Signal counts
        state: Conversation state

    Returns:
        Venting score (0.0 to MAX)
    """
    score = 0.0

    # Length-based scoring
    char_count = len(text)
    if char_count > ci_config.VENTING_MIN_LENGTH:
        extra_chars = char_count - ci_config.VENTING_MIN_LENGTH
        score += (extra_chars // 50) * ci_config.VENT_LENGTH_SCORE_PER_50

    # Rant indicator scoring
    for indicator in ci_config.RANT_INDICATORS:
        if indicator in text.lower():
            score += ci_config.VENT_INDICATOR_SCORE

    # Signal-based scoring
    distress_signals = signals.get("distress_count", 0)
    positive_signals = signals.get("positive_count", 0)

    # High emotional signals (either direction) = venting
    total_signals = distress_signals + positive_signals
    if total_signals >= 3:
        score += 2.0

    # Repetition scoring (same emotion multiple turns)
    if len(state.emotion_history) >= 2:
        recent = state.emotion_history[-2:]
        if recent[0] == recent[1]:
            score += 1.0

    # Cap the score
    return min(score, ci_config.VENT_SCORE_MAX)


def should_ask_about_advice(state: EnhancedConversationState) -> bool:
    """
    Determine if we should ask user about advice preference.

    Conditions:
    - advice_mode is UNKNOWN
    - We haven't already asked (advice_asked = False)
    - Turn count >= 2 (not first message)

    Args:
        state: Conversation state

    Returns:
        True if we should ask
    """
    if not ci_config.ENABLE_ADVICE_DETECTION:
        return False

    if state.advice_mode != AdviceMode.UNKNOWN:
        return False

    if state.advice_asked:
        return False

    if state.turn_count < 2:
        return False

    return True


def get_advice_question() -> str:
    """Get the standard advice preference question."""
    return ADVICE_QUESTION


def update_advice_mode_from_response(
    text: str,
    state: EnhancedConversationState
) -> bool:
    """
    Update advice mode based on user's response to our question.

    Called when we previously asked about advice preference.

    Args:
        text: User's response
        state: Conversation state

    Returns:
        True if mode was updated
    """
    text_lower = text.lower()

    # Check for vent response
    vent_responses = {
        "just vent", "vent", "just want to vent", "just wanna vent",
        "dont need advice", "no advice", "just talk", "just listen"
    }

    # Check for advice response
    advice_responses = {
        "advice", "help me", "help think", "think through",
        "yes advice", "yeah advice", "advice please", "your thoughts"
    }

    if any(resp in text_lower for resp in vent_responses):
        state.advice_mode = AdviceMode.VENT_ONLY
        return True

    if any(resp in text_lower for resp in advice_responses):
        state.advice_mode = AdviceMode.ADVICE_OK
        return True

    return False
