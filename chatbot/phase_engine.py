"""
Phase Engine - Universal Conversation Flow Controller
=====================================================

Controls conversation phases across ALL emotions.
Phases are emotion-aware but NOT emotion-exclusive.

PHASES:
-------
1. OPENING    - First interaction, light and curious
2. SHARING    - User describing events (neutral/light positive)
3. VENTING    - User releasing emotions (any emotion)
4. REFLECTING - Validation + gentle clarification
5. CALMING    - Grounding for emotional overload
6. CELEBRATING - High positive engagement
7. CLOSING    - Exit / rest / disengage

TRANSITIONS:
------------
Phase transitions are based on:
- Turn count
- Message characteristics (length, signals)
- Emotion and emotion streaks
- User intent (venting vs advice-seeking)

REMOVABILITY:
-------------
Disable via ENABLE_PHASE_ENGINE = False in config.
When disabled, no phase logic is applied.

"""

import logging
from typing import Dict, Optional, Tuple, Any

from chatbot.enhanced_conversation_state import (
    EnhancedConversationState,
    Phase,
    EmotionTrend
)
from chatbot import conversation_intelligence_config as ci_config

logger = logging.getLogger(__name__)


# =============================================================================
# PHASE TRANSITION TABLE
# =============================================================================

"""
PHASE TRANSITION RULES:

FROM         | TO           | CONDITIONS
-------------|--------------|--------------------------------------------
opening      | sharing      | turn > 1, neutral/positive emotion
opening      | venting      | turn > 1, distress + high venting score
opening      | celebrating  | turn > 1, positive + positive signals
sharing      | venting      | long message OR signal spike OR rant starter
sharing      | reflecting   | turn >= 3, stable emotion
sharing      | celebrating  | positive streak >= 2
venting      | reflecting   | user pauses (short message) after long vent
venting      | calming      | distress streak >= 2 OR strong_distress
venting      | closing      | exit phrases detected
reflecting   | venting      | user continues with long emotional message
reflecting   | calming      | worsening trend + distress
reflecting   | celebrating  | improving trend + positive
reflecting   | closing      | user ready to go
calming      | reflecting   | emotion stabilizes
calming      | closing      | user indicates rest/exit
celebrating  | sharing      | emotion becomes neutral
celebrating  | reflecting   | turn >= 3, natural pause
celebrating  | closing      | user indicates exit
closing      | *            | (terminal unless user continues)
"""


# =============================================================================
# PHRASE DETECTION HELPERS
# =============================================================================

# Exit/closing phrases (subset for phase detection)
CLOSING_PHRASES = {
    "bye", "goodbye", "see you", "see ya", "later", "gotta go", "gtg",
    "im going", "im leaving", "im out", "peace", "ttyl", "talk later",
    "thats all", "thats it", "im done", "nothing more"
}

# Rant starters (indicate venting)
RANT_STARTERS = {
    "i just", "i cant", "i can't", "i hate", "i need to vent",
    "omg", "ugh", "bruh", "dude", "like seriously",
    "you wont believe", "you won't believe", "guess what"
}

# Celebration triggers
CELEBRATION_TRIGGERS = {
    "yay", "omg yes", "i did it", "finally", "lets go", "let's go",
    "woooo", "yasss", "amazing news", "good news", "great news"
}

# Calming need triggers
CALMING_TRIGGERS = {
    "i cant breathe", "i can't breathe", "panicking", "panic attack",
    "having a breakdown", "breaking down", "losing it", "cant cope",
    "can't cope", "overwhelmed", "drowning", "suffocating"
}


def _has_phrase(text: str, phrases: set) -> bool:
    """Check if text contains any of the phrases."""
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in phrases)


def _get_text_length_category(text: str) -> str:
    """Categorize text by length: short, medium, long."""
    char_count = len(text)
    word_count = len(text.split())

    if char_count > ci_config.VENTING_MIN_LENGTH or word_count > ci_config.VENTING_MIN_WORDS:
        return "long"
    elif char_count > 50 or word_count > 10:
        return "medium"
    return "short"


# =============================================================================
# PHASE ENGINE CLASS
# =============================================================================

class PhaseEngine:
    """
    Universal phase controller for conversation flow.

    Determines and transitions between conversation phases based on
    message content, emotion, and context.

    USAGE:
    ------
        engine = PhaseEngine()
        new_phase, reason = engine.determine_phase(state, text, emotion, signals)
    """

    def __init__(self):
        """Initialize phase engine."""
        self.enabled = ci_config.ENABLE_PHASE_ENGINE

    def determine_phase(
        self,
        state: EnhancedConversationState,
        text: str,
        emotion: str,
        signals: Dict[str, int]
    ) -> Tuple[str, str]:
        """
        Determine the appropriate conversation phase.

        Args:
            state: Enhanced conversation state
            text: Current message text
            emotion: Detected emotion
            signals: Signal counts {distress_count, positive_count, ...}

        Returns:
            Tuple of (new_phase, transition_reason)
        """
        if not self.enabled:
            return state.phase, "phase_engine_disabled"

        current_phase = state.phase
        turn = state.turn_count

        # Get message characteristics
        text_length = _get_text_length_category(text)
        distress_signals = signals.get("distress_count", 0)
        positive_signals = signals.get("positive_count", 0)

        # --- FIRST MESSAGE: Always opening ---
        if turn <= 1:
            return Phase.OPENING, "first_message"

        # --- CHECK FOR CLOSING TRIGGERS (any phase) ---
        if _has_phrase(text, CLOSING_PHRASES):
            return Phase.CLOSING, "exit_phrase_detected"

        # --- EMERGENCY: CALMING OVERRIDE ---
        # Strong distress or calming triggers override other logic
        if emotion == "strong_distress" or _has_phrase(text, CALMING_TRIGGERS):
            return Phase.CALMING, "strong_distress_or_crisis"

        if state.distress_streak >= ci_config.CALMING_STREAK_THRESHOLD:
            return Phase.CALMING, "distress_streak_threshold"

        # --- CELEBRATION OVERRIDE ---
        if emotion == "positive" and (
            positive_signals >= 3 or
            _has_phrase(text, CELEBRATION_TRIGGERS) or
            state.positive_streak >= ci_config.CELEBRATING_STREAK_THRESHOLD
        ):
            return Phase.CELEBRATING, "positive_celebration_trigger"

        # --- VENTING DETECTION ---
        is_venting = self._detect_venting(text, text_length, emotion, signals, state)
        if is_venting:
            return Phase.VENTING, "venting_detected"

        # --- PHASE-SPECIFIC TRANSITIONS ---
        new_phase, reason = self._transition_from_current(
            current_phase, state, text, text_length, emotion, signals
        )

        return new_phase, reason

    def _detect_venting(
        self,
        text: str,
        text_length: str,
        emotion: str,
        signals: Dict[str, int],
        state: EnhancedConversationState
    ) -> bool:
        """
        Detect if user is venting (any emotion).

        Venting indicators:
        - Long message (>100 chars or >20 words)
        - Rant starters present
        - High signal count (distress OR positive overflow)
        - Repetition (same topic/emotion multiple times)
        """
        # Long emotional message
        if text_length == "long":
            return True

        # Rant starters
        if _has_phrase(text, RANT_STARTERS):
            return True

        # Signal spike (any direction)
        total_signals = signals.get("distress_count", 0) + signals.get("positive_count", 0)
        if total_signals >= ci_config.VENTING_SIGNAL_THRESHOLD + 1:
            return True

        # High venting score from state
        if state.venting_score >= ci_config.VENT_SCORE_THRESHOLD:
            return True

        return False

    def _transition_from_current(
        self,
        current: str,
        state: EnhancedConversationState,
        text: str,
        text_length: str,
        emotion: str,
        signals: Dict[str, int]
    ) -> Tuple[str, str]:
        """
        Determine transition based on current phase.

        Returns:
            Tuple of (new_phase, reason)
        """
        turn = state.turn_count

        # --- FROM OPENING ---
        if current == Phase.OPENING:
            if emotion == "positive":
                return Phase.SHARING, "opening_to_sharing_positive"
            elif emotion == "neutral":
                return Phase.SHARING, "opening_to_sharing_neutral"
            elif emotion in {"distress", "strong_distress"}:
                return Phase.VENTING, "opening_to_venting_distress"
            return Phase.SHARING, "opening_to_sharing_default"

        # --- FROM SHARING ---
        if current == Phase.SHARING:
            if turn >= ci_config.REFLECT_MIN_TURNS and text_length == "short":
                return Phase.REFLECTING, "sharing_to_reflecting_pause"
            if emotion in {"distress", "strong_distress"}:
                return Phase.VENTING, "sharing_to_venting_distress"
            return Phase.SHARING, "stay_sharing"

        # --- FROM VENTING ---
        if current == Phase.VENTING:
            # Short message after venting = pause, move to reflecting
            if text_length == "short" and turn >= 3:
                return Phase.REFLECTING, "venting_to_reflecting_pause"
            # Stay in venting for continued long messages
            return Phase.VENTING, "stay_venting"

        # --- FROM REFLECTING ---
        if current == Phase.REFLECTING:
            if text_length == "long":
                return Phase.VENTING, "reflecting_to_venting_resume"
            if state.emotion_trend == EmotionTrend.IMPROVING and emotion == "positive":
                return Phase.CELEBRATING, "reflecting_to_celebrating_improved"
            if state.emotion_trend == EmotionTrend.WORSENING:
                return Phase.CALMING, "reflecting_to_calming_worsening"
            return Phase.REFLECTING, "stay_reflecting"

        # --- FROM CALMING ---
        if current == Phase.CALMING:
            if emotion in {"positive", "neutral"} and state.emotion_trend != EmotionTrend.WORSENING:
                return Phase.REFLECTING, "calming_to_reflecting_stabilized"
            return Phase.CALMING, "stay_calming"

        # --- FROM CELEBRATING ---
        if current == Phase.CELEBRATING:
            if emotion == "neutral":
                return Phase.SHARING, "celebrating_to_sharing_neutral"
            if emotion in {"distress", "strong_distress"}:
                return Phase.REFLECTING, "celebrating_to_reflecting_shift"
            return Phase.CELEBRATING, "stay_celebrating"

        # --- FROM CLOSING ---
        if current == Phase.CLOSING:
            # If user continues, they're not actually leaving
            if text_length in {"medium", "long"}:
                return Phase.SHARING, "closing_to_sharing_continued"
            return Phase.CLOSING, "stay_closing"

        # Default: stay in current phase
        return current, "no_transition"

    def get_phase_rules(self, phase: str) -> Dict[str, Any]:
        """
        Get behavioral rules for a given phase.

        Args:
            phase: Phase name

        Returns:
            Dict with rules for reply generation
        """
        rules = {
            Phase.OPENING: {
                "allow_questions": True,
                "allow_memory_recall": False,
                "tone": "curious",
                "max_questions": 1,
                "allow_advice": False,
                "priority_categories": ["greeting", "light_opener"]
            },
            Phase.SHARING: {
                "allow_questions": True,
                "allow_memory_recall": False,  # Too early
                "tone": "engaged",
                "max_questions": 1,
                "allow_advice": False,  # Still gathering info
                "priority_categories": ["acknowledgment", "follow_up"]
            },
            Phase.VENTING: {
                "allow_questions": False,  # Let them vent
                "allow_memory_recall": False,
                "tone": "supportive",
                "max_questions": 0,
                "allow_advice": False,  # Definitely not during venting
                "priority_categories": ["validation", "presence", "continuation"]
            },
            Phase.REFLECTING: {
                "allow_questions": True,
                "allow_memory_recall": True,  # Can recall similar situations
                "tone": "thoughtful",
                "max_questions": 1,
                "allow_advice": "check_mode",  # Check advice_mode
                "priority_categories": ["validation", "clarify", "memory_callback"]
            },
            Phase.CALMING: {
                "allow_questions": False,  # Focus on grounding
                "allow_memory_recall": True,  # Positive memories can help
                "tone": "grounding",
                "max_questions": 0,
                "allow_advice": False,
                "priority_categories": ["grounding_message", "presence", "breathe_tip"]
            },
            Phase.CELEBRATING: {
                "allow_questions": True,
                "allow_memory_recall": True,  # Recall past wins
                "tone": "excited",
                "max_questions": 1,
                "allow_advice": False,  # No advice during celebration
                "priority_categories": ["celebration_hype", "curiosity", "memory_positive"]
            },
            Phase.CLOSING: {
                "allow_questions": False,
                "allow_memory_recall": False,
                "tone": "warm",
                "max_questions": 0,
                "allow_advice": False,
                "priority_categories": ["exit_reply", "send_off"]
            }
        }

        return rules.get(phase, rules[Phase.SHARING])


# =============================================================================
# MODULE-LEVEL INSTANCE
# =============================================================================

_phase_engine: Optional[PhaseEngine] = None


def get_phase_engine() -> PhaseEngine:
    """Get singleton PhaseEngine instance."""
    global _phase_engine
    if _phase_engine is None:
        _phase_engine = PhaseEngine()
    return _phase_engine


def determine_phase(
    state: EnhancedConversationState,
    text: str,
    emotion: str,
    signals: Dict[str, int]
) -> Tuple[str, str]:
    """
    Convenience function to determine phase.

    Args:
        state: Enhanced conversation state
        text: Message text
        emotion: Detected emotion
        signals: Signal counts

    Returns:
        Tuple of (phase, reason)
    """
    return get_phase_engine().determine_phase(state, text, emotion, signals)


def get_phase_rules(phase: str) -> Dict[str, Any]:
    """Get rules for a phase."""
    return get_phase_engine().get_phase_rules(phase)

