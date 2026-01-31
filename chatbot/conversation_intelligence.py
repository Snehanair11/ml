"""
Conversation Intelligence Layer
===============================

Central orchestration module for conversation intelligence.
This layer runs BEFORE reply selection and determines:

- Allowed reply categories
- Whether questions are allowed
- Whether memory recall is allowed
- Which phase is active
- Advice mode (vent vs advice)

INTEGRATION POINT:
------------------
This module runs before reply_manager.generate_reply() and provides
context that guides reply selection without modifying reply text.

DECISION FLOW:
--------------
1. Get/create enhanced state for user
2. Update state with new message info
3. Calculate venting score
4. Detect advice mode
5. Determine conversation phase
6. Get phase rules
7. Check memory recall eligibility
8. Compile reply constraints
9. Return intelligence context

REMOVABILITY:
-------------
Disable via ENABLE_CONVERSATION_INTELLIGENCE = False in config.
When disabled, all functions return safe defaults.

"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from chatbot.enhanced_conversation_state import (
    EnhancedConversationState,
    Phase,
    AdviceMode,
    get_enhanced_state,
    reset_enhanced_state
)
from chatbot.phase_engine import (
    determine_phase,
    get_phase_rules,
    PhaseEngine
)
from chatbot.advice_detector import (
    detect_advice_mode,
    calculate_venting_score,
    should_ask_about_advice,
    get_advice_question
)
from chatbot.memory_recall_controller import check_memory_recall
from chatbot.cooldown_manager import (
    apply_cooldowns,
    filter_replies_by_cooldown,
    is_category_on_cooldown
)
from chatbot import conversation_intelligence_config as ci_config

logger = logging.getLogger(__name__)


# =============================================================================
# INTELLIGENCE CONTEXT OUTPUT
# =============================================================================

@dataclass
class IntelligenceContext:
    """
    Output from the conversation intelligence layer.

    Passed to reply generation to guide reply selection.
    All existing reply text is preserved - this only guides selection.
    """

    # --- Phase Info ---
    phase: str = Phase.OPENING
    phase_reason: str = ""
    previous_phase: Optional[str] = None

    # --- Emotion Info ---
    emotion: str = "neutral"
    emotion_trend: str = "unknown"
    emotion_changed: bool = False

    # --- Venting/Advice ---
    advice_mode: str = AdviceMode.UNKNOWN
    venting_score: float = 0.0
    should_ask_advice_preference: bool = False

    # --- Reply Constraints ---
    allow_questions: bool = True
    allow_memory_recall: bool = False
    allow_advice: bool = False
    max_questions: int = 1
    recommended_tone: str = "engaged"

    # --- Blocked Categories ---
    blocked_categories: List[str] = field(default_factory=list)

    # --- Memory Recall ---
    memory_response: Optional[str] = None

    # --- Streaks ---
    positive_streak: int = 0
    neutral_streak: int = 0
    distress_streak: int = 0

    # --- Context ---
    turn_count: int = 0
    is_first_message: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for passing to reply generation."""
        return {
            # Phase
            "phase": self.phase,
            "phase_reason": self.phase_reason,
            "previous_phase": self.previous_phase,

            # Emotion
            "emotion": self.emotion,
            "emotion_trend": self.emotion_trend,
            "emotion_changed": self.emotion_changed,

            # Venting/Advice
            "advice_mode": self.advice_mode,
            "venting_score": self.venting_score,
            "should_ask_advice_preference": self.should_ask_advice_preference,

            # Constraints
            "allow_questions": self.allow_questions,
            "allow_memory_recall": self.allow_memory_recall,
            "allow_advice": self.allow_advice,
            "max_questions": self.max_questions,
            "recommended_tone": self.recommended_tone,

            # Blocked
            "blocked_categories": self.blocked_categories,

            # Memory
            "memory_response": self.memory_response,

            # Streaks
            "positive_streak": self.positive_streak,
            "neutral_streak": self.neutral_streak,
            "distress_streak": self.distress_streak,

            # Context
            "turn_count": self.turn_count,
            "is_first_message": self.is_first_message
        }


# =============================================================================
# MAIN INTELLIGENCE LAYER
# =============================================================================

class ConversationIntelligenceLayer:
    """
    Main orchestration class for conversation intelligence.

    Runs BEFORE reply selection to provide context that guides
    reply generation without modifying existing reply text.
    """

    def __init__(self):
        """Initialize the intelligence layer."""
        self.enabled = ci_config.ENABLE_CONVERSATION_INTELLIGENCE

    def process(
        self,
        anon_id: str,
        text: str,
        emotion: str,
        signals: Dict[str, int],
        conversation_context: Optional[Dict] = None
    ) -> IntelligenceContext:
        """
        Process a message through the intelligence layer.

        This is the main entry point. Call this BEFORE reply generation.

        Args:
            anon_id: User identifier
            text: Message text
            emotion: Detected emotion
            signals: Signal counts {distress_count, positive_count, ...}
            conversation_context: Optional existing conversation context

        Returns:
            IntelligenceContext with guidance for reply generation
        """
        # If disabled, return safe defaults
        if not self.enabled:
            return self._get_default_context(emotion)

        try:
            # Step 1: Get enhanced state
            state = get_enhanced_state(anon_id)

            # Step 2: Increment turn and update emotion
            state.increment_turn()
            state.update_emotion(emotion)
            state.add_message(text, emotion, signals)

            # Step 3: Calculate venting score
            venting_score = calculate_venting_score(text, signals, state)
            state.venting_score = venting_score

            # Step 4: Detect advice mode
            advice_mode, advice_confidence, advice_reason = detect_advice_mode(text, state)
            state.advice_mode = advice_mode

            # Step 5: Determine phase
            new_phase, phase_reason = determine_phase(state, text, emotion, signals)
            state.previous_phase = state.phase
            state.phase = new_phase

            # Step 6: Get phase rules
            rules = get_phase_rules(new_phase)

            # Step 7: Check memory recall
            memory_response = None
            if rules.get("allow_memory_recall", False):
                memory_response = check_memory_recall(
                    anon_id, text, state, new_phase, emotion
                )

            # Step 8: Determine advice allowance
            allow_advice = False
            if rules.get("allow_advice") == "check_mode":
                allow_advice = (advice_mode == AdviceMode.ADVICE_OK)
            elif rules.get("allow_advice"):
                allow_advice = True

            # Step 9: Check if should ask about advice preference
            should_ask = should_ask_about_advice(state)

            # Step 10: Get blocked categories from cooldowns
            blocked = []
            if ci_config.ENABLE_COOLDOWNS:
                from src.chatbot.cooldown_manager import get_cooldown_manager
                blocked_set = get_cooldown_manager().get_blocked_categories(state, new_phase)
                blocked = list(blocked_set)

            # Step 11: Build context
            context = IntelligenceContext(
                # Phase
                phase=new_phase,
                phase_reason=phase_reason,
                previous_phase=state.previous_phase,

                # Emotion
                emotion=emotion,
                emotion_trend=state.emotion_trend,
                emotion_changed=(
                    len(state.emotion_history) >= 2 and
                    state.emotion_history[-1] != state.emotion_history[-2]
                ),

                # Venting/Advice
                advice_mode=advice_mode,
                venting_score=venting_score,
                should_ask_advice_preference=should_ask,

                # Constraints from phase rules
                allow_questions=rules.get("allow_questions", True),
                allow_memory_recall=rules.get("allow_memory_recall", False),
                allow_advice=allow_advice,
                max_questions=rules.get("max_questions", 1),
                recommended_tone=rules.get("tone", "engaged"),

                # Blocked categories
                blocked_categories=blocked,

                # Memory
                memory_response=memory_response,

                # Streaks
                positive_streak=state.positive_streak,
                neutral_streak=state.neutral_streak,
                distress_streak=state.distress_streak,

                # Context
                turn_count=state.turn_count,
                is_first_message=(state.turn_count <= 1)
            )

            # Log if verbose
            if ci_config.VERBOSE_INTELLIGENCE_LOGGING:
                self._log_context(context)

            return context

        except Exception as e:
            logger.error(f"Error in intelligence layer: {e}")
            return self._get_default_context(emotion)

    def _get_default_context(self, emotion: str) -> IntelligenceContext:
        """Get safe default context when disabled or on error."""
        return IntelligenceContext(
            phase=Phase.SHARING,
            emotion=emotion,
            allow_questions=True,
            allow_advice=False,
            allow_memory_recall=False
        )

    def _log_context(self, context: IntelligenceContext):
        """Log context details for debugging."""
        logger.info(f"Intelligence Context:")
        logger.info(f"  Phase: {context.phase} ({context.phase_reason})")
        logger.info(f"  Emotion: {context.emotion} (trend: {context.emotion_trend})")
        logger.info(f"  Advice Mode: {context.advice_mode}")
        logger.info(f"  Venting Score: {context.venting_score:.1f}")
        logger.info(f"  Allow Questions: {context.allow_questions}")
        logger.info(f"  Allow Advice: {context.allow_advice}")
        logger.info(f"  Blocked: {context.blocked_categories}")

    def post_reply(
        self,
        anon_id: str,
        reply_text: str,
        reply_category: Optional[str] = None
    ):
        """
        Update state after reply is generated.

        Call this AFTER reply generation to update cooldowns.

        Args:
            anon_id: User identifier
            reply_text: The generated reply
            reply_category: Optional explicit category
        """
        if not self.enabled:
            return

        state = get_enhanced_state(anon_id)

        # Apply cooldowns based on reply content
        apply_cooldowns(state, reply_text)

        # Track reply type
        if reply_category:
            state.last_reply_category = reply_category

    def reset_user(self, anon_id: str):
        """Reset state for a user (new conversation)."""
        reset_enhanced_state(anon_id)


# =============================================================================
# MODULE-LEVEL INSTANCE & CONVENIENCE FUNCTIONS
# =============================================================================

_intelligence_layer: Optional[ConversationIntelligenceLayer] = None


def get_intelligence_layer() -> ConversationIntelligenceLayer:
    """Get singleton ConversationIntelligenceLayer instance."""
    global _intelligence_layer
    if _intelligence_layer is None:
        _intelligence_layer = ConversationIntelligenceLayer()
    return _intelligence_layer


def process_intelligence(
    anon_id: str,
    text: str,
    emotion: str,
    signals: Dict[str, int],
    conversation_context: Optional[Dict] = None
) -> IntelligenceContext:
    """
    Process a message through the intelligence layer.

    Convenience function for the main entry point.

    Args:
        anon_id: User identifier
        text: Message text
        emotion: Detected emotion
        signals: Signal counts

    Returns:
        IntelligenceContext
    """
    return get_intelligence_layer().process(
        anon_id, text, emotion, signals, conversation_context
    )


def post_reply_update(
    anon_id: str,
    reply_text: str,
    reply_category: Optional[str] = None
):
    """Update state after reply generation."""
    get_intelligence_layer().post_reply(anon_id, reply_text, reply_category)


def get_advice_question_if_needed(context: IntelligenceContext) -> Optional[str]:
    """
    Get advice preference question if it should be asked.

    Args:
        context: Intelligence context

    Returns:
        Question string or None
    """
    if context.should_ask_advice_preference:
        return get_advice_question()
    return None

