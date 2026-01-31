"""
Enhanced Conversation State
===========================

Extended state schema for the Conversation Intelligence Layer.
Works alongside existing ConversationState - does NOT replace it.

This module adds:
- Emotion trend tracking (improving / stable / worsening)
- Venting score calculation
- Conversation phase tracking
- Advice mode detection
- Reply cooldowns
- Emotion streaks (positive, neutral, distress)
- Memory topic tracking

REMOVABILITY:
-------------
This module can be completely disabled via ENABLE_CONVERSATION_INTELLIGENCE = False
in conversation_intelligence_config.py. When disabled, the system uses baseline state.

"""

from datetime import datetime
from typing import Dict, List, Optional, Set, Any
from collections import deque
from dataclasses import dataclass, field

from chatbot import conversation_intelligence_config as ci_config


# =============================================================================
# PHASE DEFINITIONS
# =============================================================================

class Phase:
    """Conversation phase constants."""
    OPENING = "opening"
    SHARING = "sharing"
    VENTING = "venting"
    REFLECTING = "reflecting"
    CALMING = "calming"
    CELEBRATING = "celebrating"
    CLOSING = "closing"


class EmotionTrend:
    """Emotion trend constants."""
    IMPROVING = "improving"
    STABLE = "stable"
    WORSENING = "worsening"
    UNKNOWN = "unknown"


class AdviceMode:
    """Advice mode constants."""
    VENT_ONLY = "vent_only"
    ADVICE_OK = "advice_ok"
    UNKNOWN = "unknown"


# =============================================================================
# ENHANCED STATE CLASS
# =============================================================================

@dataclass
class EnhancedConversationState:
    """
    Enhanced conversation state with intelligence layer fields.

    This extends the baseline ConversationState with additional tracking
    for phases, trends, cooldowns, and streaks.

    SAFE DEFAULTS:
    --------------
    All fields have safe defaults so partial state is always valid.
    """

    # --- Core Identity ---
    anon_id: str = ""

    # --- Emotion Tracking ---
    current_emotion: str = "neutral"
    initial_emotion: Optional[str] = None
    emotion_history: List[str] = field(default_factory=list)  # Last N emotions
    emotion_trend: str = EmotionTrend.UNKNOWN

    # --- Turn Tracking ---
    turn_count: int = 0

    # --- Venting Detection ---
    venting_score: float = 0.0

    # --- Phase Management ---
    phase: str = Phase.OPENING
    previous_phase: Optional[str] = None

    # --- Advice Mode ---
    advice_mode: str = AdviceMode.UNKNOWN
    advice_asked: bool = False  # Have we asked about advice preference?

    # --- Reply Tracking ---
    last_reply_type: Optional[str] = None
    last_reply_category: Optional[str] = None

    # --- Cooldowns (category -> turns remaining) ---
    cooldowns: Dict[str, int] = field(default_factory=dict)

    # --- Emotion Streaks ---
    positive_streak: int = 0
    neutral_streak: int = 0
    distress_streak: int = 0
    strong_distress_streak: int = 0

    # --- Memory Tracking ---
    memory_topics_seen: Set[str] = field(default_factory=set)
    memory_recall_used_this_turn: bool = False

    # --- Timestamps ---
    started_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

    # --- Message Cache (for context) ---
    recent_messages: List[Dict[str, Any]] = field(default_factory=list)

    # --- Max history length ---
    MAX_EMOTION_HISTORY: int = 10
    MAX_RECENT_MESSAGES: int = 5

    def update_emotion(self, emotion: str):
        """
        Update emotion and recalculate trends/streaks.

        Args:
            emotion: New emotion label
        """
        # Store initial emotion
        if self.initial_emotion is None:
            self.initial_emotion = emotion

        # Update history (keep last N)
        self.emotion_history.append(emotion)
        if len(self.emotion_history) > self.MAX_EMOTION_HISTORY:
            self.emotion_history = self.emotion_history[-self.MAX_EMOTION_HISTORY:]

        # Update current
        old_emotion = self.current_emotion
        self.current_emotion = emotion

        # Update streaks
        self._update_streaks(emotion)

        # Update trend
        self._update_trend()

    def _update_streaks(self, emotion: str):
        """Update emotion streaks based on new emotion."""
        # Reset all streaks first
        if emotion != "positive":
            self.positive_streak = 0
        if emotion != "neutral":
            self.neutral_streak = 0
        if emotion not in {"distress", "strong_distress"}:
            self.distress_streak = 0
        if emotion != "strong_distress":
            self.strong_distress_streak = 0

        # Increment relevant streak
        if emotion == "positive":
            self.positive_streak += 1
        elif emotion == "neutral":
            self.neutral_streak += 1
        elif emotion == "distress":
            self.distress_streak += 1
        elif emotion == "strong_distress":
            self.strong_distress_streak += 1
            self.distress_streak += 1  # Also counts as general distress

    def _update_trend(self):
        """Calculate emotion trend from history."""
        if len(self.emotion_history) < 3:
            self.emotion_trend = EmotionTrend.UNKNOWN
            return

        # Define emotion valence (higher = more positive)
        valence = {
            "positive": 3,
            "neutral": 2,
            "distress": 1,
            "strong_distress": 0,
            "mixed": 1.5
        }

        # Get last 3 emotions
        recent = self.emotion_history[-3:]
        scores = [valence.get(e, 1.5) for e in recent]

        # Calculate trend
        if scores[2] > scores[0]:
            self.emotion_trend = EmotionTrend.IMPROVING
        elif scores[2] < scores[0]:
            self.emotion_trend = EmotionTrend.WORSENING
        else:
            self.emotion_trend = EmotionTrend.STABLE

    def increment_turn(self):
        """Increment turn counter and update timestamps."""
        self.turn_count += 1
        self.last_activity = datetime.now()
        self.memory_recall_used_this_turn = False

        # Decrement all cooldowns
        self._decrement_cooldowns()

    def _decrement_cooldowns(self):
        """Decrement all active cooldowns by 1."""
        expired = []
        for category, turns in self.cooldowns.items():
            if turns > 1:
                self.cooldowns[category] = turns - 1
            else:
                expired.append(category)

        # Remove expired cooldowns
        for cat in expired:
            del self.cooldowns[cat]

    def set_cooldown(self, category: str, turns: Optional[int] = None):
        """
        Set cooldown for a reply category.

        Args:
            category: Reply category name
            turns: Cooldown duration (default from config)
        """
        if turns is None:
            turns = ci_config.COOLDOWN_CONFIG.get(
                category,
                ci_config.DEFAULT_COOLDOWN
            )
        self.cooldowns[category] = turns

    def is_on_cooldown(self, category: str) -> bool:
        """Check if a category is on cooldown."""
        return self.cooldowns.get(category, 0) > 0

    def add_message(self, text: str, emotion: str, signals: Optional[Dict] = None):
        """
        Add a message to recent history.

        Args:
            text: Message text
            emotion: Detected emotion
            signals: Optional signal counts
        """
        msg = {
            "text": text,
            "emotion": emotion,
            "signals": signals or {},
            "turn": self.turn_count,
            "timestamp": datetime.now()
        }
        self.recent_messages.append(msg)

        # Keep only recent messages
        if len(self.recent_messages) > self.MAX_RECENT_MESSAGES:
            self.recent_messages = self.recent_messages[-self.MAX_RECENT_MESSAGES:]

    def add_memory_topic(self, topic: str):
        """Record that a topic was seen."""
        self.memory_topics_seen.add(topic)

    def get_topic_occurrence_count(self, topic: str) -> int:
        """Count how many times a topic has been mentioned."""
        count = 0
        for msg in self.recent_messages:
            if topic in msg.get("text", "").lower():
                count += 1
        return count

    def to_dict(self) -> Dict[str, Any]:
        """
        Export state as dictionary for passing to reply generation.

        Returns:
            Dict with all relevant state fields
        """
        return {
            # Core
            "anon_id": self.anon_id,
            "turn_count": self.turn_count,

            # Emotions
            "current_emotion": self.current_emotion,
            "initial_emotion": self.initial_emotion,
            "emotion_history": self.emotion_history.copy(),
            "emotion_trend": self.emotion_trend,

            # Phase
            "phase": self.phase,
            "previous_phase": self.previous_phase,

            # Venting
            "venting_score": self.venting_score,
            "advice_mode": self.advice_mode,

            # Streaks
            "positive_streak": self.positive_streak,
            "neutral_streak": self.neutral_streak,
            "distress_streak": self.distress_streak,
            "strong_distress_streak": self.strong_distress_streak,

            # Cooldowns
            "cooldowns": self.cooldowns.copy(),

            # Reply
            "last_reply_type": self.last_reply_type,
            "last_reply_category": self.last_reply_category,

            # Memory
            "memory_topics_seen": list(self.memory_topics_seen),
            "memory_recall_used_this_turn": self.memory_recall_used_this_turn,

            # Computed flags
            "is_first_message": self.turn_count <= 1,
            "emotion_changed": (
                len(self.emotion_history) >= 2 and
                self.emotion_history[-1] != self.emotion_history[-2]
            )
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnhancedConversationState":
        """
        Create state from dictionary (for deserialization).

        Args:
            data: State dictionary

        Returns:
            EnhancedConversationState instance
        """
        state = cls()
        for key, value in data.items():
            if hasattr(state, key):
                if key == "memory_topics_seen" and isinstance(value, list):
                    setattr(state, key, set(value))
                else:
                    setattr(state, key, value)
        return state


# =============================================================================
# STATE STORAGE
# =============================================================================

# Store enhanced states per user
_enhanced_states: Dict[str, EnhancedConversationState] = {}


def get_enhanced_state(anon_id: str) -> EnhancedConversationState:
    """
    Get or create enhanced conversation state for a user.

    Args:
        anon_id: User identifier

    Returns:
        EnhancedConversationState instance
    """
    if anon_id not in _enhanced_states:
        _enhanced_states[anon_id] = EnhancedConversationState(anon_id=anon_id)
    return _enhanced_states[anon_id]


def reset_enhanced_state(anon_id: str):
    """Reset enhanced state for a user (start fresh conversation)."""
    _enhanced_states[anon_id] = EnhancedConversationState(anon_id=anon_id)


def clear_all_enhanced_states():
    """Clear all enhanced states (for testing/reset)."""
    _enhanced_states.clear()

