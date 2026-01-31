"""
Memory Recall Controller
========================

Controls when and how memory callbacks are used in replies.
Works across ALL emotions with tone-appropriate recall.

MEMORY TYPES:
-------------
1. Recurring Topic:  work, money, relationships, health, self
2. Recurring Emotion: positive streaks, neutral loops, distress cycles

RULES:
------
Memory recall is allowed ONLY if:
- turn_count >= 3
- topic/emotion appeared >= 2 times
- Current phase allows it (reflecting, celebrating, calming)
- NOT in opening phase

TONE RULES:
-----------
- Positive memory → affirm growth or consistency
- Neutral memory → gentle observation
- Distress memory → empathetic, non-judgmental

REMOVABILITY:
-------------
Disable via ENABLE_MEMORY_RECALL = False in config.

"""

import random
from typing import Dict, Optional, Tuple, Any

from chatbot.enhanced_conversation_state import (
    EnhancedConversationState,
    Phase
)
from chatbot import conversation_intelligence_config as ci_config
from chatbot.memory_manager import (
    get_similar_past_topic,
    get_recurring_emotion,
    TOPIC_KEYWORDS
)


# =============================================================================
# MEMORY RECALL RESPONSES (by emotion tone)
# =============================================================================

# Positive memory responses (affirm growth/consistency)
POSITIVE_MEMORY_RESPONSES = {
    "topic": [
        "this sounds like good vibes again 💛 i remember u mentioned {topic} before too!",
        "wait {topic} again?? love that for u honestly 😊",
        "ooh {topic} coming thru again!! ur on a roll fr",
        "{topic} is really working out for u huh 💛 that's awesome",
        "yess more {topic} wins!! i love seeing this pattern 😊"
    ],
    "emotion": [
        "uve been feeling pretty good lately 💛 i love this energy",
        "this is like the {count}th time u seem happy!! love that for u 😊",
        "ur good vibes are consistent fr 💛 keep it up!!",
        "ive noticed u feeling good more often now 😊 thats growth!!"
    ]
}

# Neutral memory responses (gentle observation)
NEUTRAL_MEMORY_RESPONSES = {
    "topic": [
        "u mentioned {topic} before too — seems like its been on ur mind?",
        "{topic} keeps coming up huh 🤔 wanna talk more about it?",
        "ive noticed {topic} is a recurring thing for u — how r u feeling about it?",
        "{topic} again — is everything okay with that?"
    ],
    "emotion": [
        "uve been pretty chill lately — how r things going in general?",
        "things seem steady for u — anything u wanna share?",
        "uve been neutral a few times now — just checking in 💙"
    ]
}

# Distress memory responses (empathetic, non-judgmental)
DISTRESS_MEMORY_RESPONSES = {
    "topic": [
        "i remember u mentioned {topic} before too 💙 it sounds like its still weighing on u",
        "{topic} keeps coming up — i can tell its really affecting u 💙",
        "this {topic} situation seems to be sticking with u... im here for u okay?",
        "uve talked about {topic} before — its okay that its still hard 💙",
        "{topic} again huh 💙 u dont have to figure it all out rn"
    ],
    "emotion": [
        "uve been going thru a lot lately 💙 im here for u okay?",
        "i can tell things have been tough for u... u dont have to carry it alone",
        "ive noticed uve been struggling 💙 whatever ur feeling is valid",
        "its been heavy for u lately huh 💙 take ur time... im listening"
    ]
}


# =============================================================================
# MEMORY RECALL CONTROLLER
# =============================================================================

class MemoryRecallController:
    """
    Controls memory recall based on conversation context.

    Determines:
    - Whether memory recall is allowed in current context
    - What type of memory to recall (topic vs emotion)
    - Appropriate tone for the recall
    """

    def __init__(self):
        """Initialize memory recall controller."""
        self.enabled = ci_config.ENABLE_MEMORY_RECALL

    def should_recall_memory(
        self,
        state: EnhancedConversationState,
        phase: str,
        emotion: str
    ) -> Tuple[bool, str]:
        """
        Determine if memory recall should be used.

        Args:
            state: Enhanced conversation state
            phase: Current conversation phase
            emotion: Current emotion

        Returns:
            Tuple of (should_recall, reason)
        """
        if not self.enabled:
            return False, "memory_recall_disabled"

        # Check minimum turn count
        if state.turn_count < ci_config.MEMORY_RECALL_MIN_TURNS:
            return False, f"turn_count_too_low_{state.turn_count}"

        # Check phase allows memory recall
        if phase not in ci_config.MEMORY_ALLOWED_PHASES:
            return False, f"phase_not_allowed_{phase}"

        # Check if already used this turn
        if state.memory_recall_used_this_turn:
            return False, "already_used_this_turn"

        # Check cooldown
        if state.is_on_cooldown("memory_callback"):
            return False, "on_cooldown"

        # Random probability check
        if random.random() > ci_config.MEMORY_RECALL_PROBABILITY:
            return False, "probability_skip"

        return True, "conditions_met"

    def get_memory_recall(
        self,
        anon_id: str,
        text: str,
        state: EnhancedConversationState,
        emotion: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get memory recall information if available.

        Args:
            anon_id: User identifier
            text: Current message text
            state: Enhanced conversation state
            emotion: Current emotion

        Returns:
            Dict with recall info or None
        """
        if not self.enabled:
            return None

        # Try to find recurring topic
        past_topic = get_similar_past_topic(anon_id, text)

        if past_topic:
            return {
                "type": "topic",
                "topic": past_topic["topic"],
                "past_emotion": past_topic.get("past_emotion"),
                "current_emotion": emotion
            }

        # Try to find recurring emotion
        emotion_count = get_recurring_emotion(anon_id, emotion)

        if emotion_count >= ci_config.MEMORY_RECALL_MIN_OCCURRENCES:
            return {
                "type": "emotion",
                "emotion": emotion,
                "count": emotion_count
            }

        return None

    def format_memory_response(
        self,
        memory_info: Dict[str, Any],
        current_emotion: str
    ) -> Optional[str]:
        """
        Format a memory recall response with appropriate tone.

        Args:
            memory_info: Memory recall info from get_memory_recall
            current_emotion: Current emotion for tone selection

        Returns:
            Formatted response string or None
        """
        if not memory_info:
            return None

        # Determine tone based on current emotion
        if current_emotion == "positive":
            responses = POSITIVE_MEMORY_RESPONSES
        elif current_emotion in {"distress", "strong_distress"}:
            responses = DISTRESS_MEMORY_RESPONSES
        else:
            responses = NEUTRAL_MEMORY_RESPONSES

        # Get appropriate response template
        recall_type = memory_info.get("type")

        if recall_type == "topic":
            topic = memory_info.get("topic", "this")
            templates = responses.get("topic", [])
            if templates:
                template = random.choice(templates)
                return template.format(topic=topic)

        elif recall_type == "emotion":
            count = memory_info.get("count", 2)
            templates = responses.get("emotion", [])
            if templates:
                template = random.choice(templates)
                return template.format(count=count)

        return None


# =============================================================================
# MODULE-LEVEL INSTANCE
# =============================================================================

_memory_controller: Optional[MemoryRecallController] = None


def get_memory_controller() -> MemoryRecallController:
    """Get singleton MemoryRecallController instance."""
    global _memory_controller
    if _memory_controller is None:
        _memory_controller = MemoryRecallController()
    return _memory_controller


def check_memory_recall(
    anon_id: str,
    text: str,
    state: EnhancedConversationState,
    phase: str,
    emotion: str
) -> Optional[str]:
    """
    Convenience function to check and format memory recall.

    Args:
        anon_id: User identifier
        text: Current message
        state: Enhanced conversation state
        phase: Current phase
        emotion: Current emotion

    Returns:
        Formatted memory response or None
    """
    controller = get_memory_controller()

    # Check if recall should happen
    should_recall, reason = controller.should_recall_memory(state, phase, emotion)

    if not should_recall:
        return None

    # Get memory info
    memory_info = controller.get_memory_recall(anon_id, text, state, emotion)

    if not memory_info:
        return None

    # Format response
    response = controller.format_memory_response(memory_info, emotion)

    if response:
        # Mark as used and set cooldown
        state.memory_recall_used_this_turn = True
        state.set_cooldown("memory_callback")

        # Track topic if applicable
        if memory_info.get("topic"):
            state.add_memory_topic(memory_info["topic"])

    return response

