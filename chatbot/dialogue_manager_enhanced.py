"""
Enhanced Dialogue Manager
=========================

Integrates the Conversation Intelligence Layer with the existing dialogue flow.
This module runs the intelligence layer BEFORE reply generation.

INTEGRATION FLOW:
-----------------
1. Predict emotion (existing)
2. Apply signal-based correction (existing)
3. Update baseline conversation state (existing)
4. **RUN INTELLIGENCE LAYER** (NEW)
5. Decide next step (existing)
6. Generate reply with intelligence context (ENHANCED)
7. Post-reply update (NEW)
8. Update memory (existing)
9. Return response

BACKWARD COMPATIBILITY:
-----------------------
If ENABLE_CONVERSATION_INTELLIGENCE = False, this behaves exactly
like the original dialogue_manager.py.

USAGE:
------
Replace or alias the original handle_message with this module:

    from src.chatbot.dialogue_manager_enhanced import handle_message

Or keep both and switch via config.

"""

from inference.predict_emotion import predict_emotion
from chatbot.decision_manager import decide_next_step
from chatbot.reply_manager import generate_reply
from chatbot.memory_manager import update_memory
from chatbot.conversation_state import update_conversation, mark_followup_done
from signal_mapper import count_signals_in_text

# Import intelligence layer
from chatbot.conversation_intelligence import (
    process_intelligence,
    post_reply_update,
    get_advice_question_if_needed,
    IntelligenceContext
)
from chatbot import conversation_intelligence_config as ci_config


def handle_message(payload: dict) -> dict:
    """
    Handle incoming message with conversation intelligence.

    This is the enhanced version of handle_message that integrates
    the Conversation Intelligence Layer.

    Args:
        payload: Dict with anon_id, text, and optional fields

    Returns:
        Dict with emotion, score, reply, and conversation_context
    """
    anon_id = payload["anon_id"]
    text = payload["text"]

    # ---- STEP 1: PREDICT EMOTION (existing) ----
    result = predict_emotion(text)
    emotion = result["emotion"]
    score = result["score"]

    # ---- STEP 2: SIGNAL-BASED EMOTION CORRECTION (existing) ----
    signals = count_signals_in_text(text)
    distress_count = signals["distress_count"]
    positive_count = signals["positive_count"]

    # Apply signal-based overrides (same logic as original)
    if distress_count >= 3:
        emotion = "strong_distress"
        score = 0.90
    elif distress_count >= 2 and distress_count > positive_count:
        emotion = "distress"
        score = max(score, 0.75)
    elif distress_count >= 1 and positive_count == 0 and emotion == "neutral":
        emotion = "distress"
        score = max(score, 0.65)
    elif positive_count >= 3:
        emotion = "positive"
        score = 0.90
    elif positive_count >= 2 and positive_count > distress_count:
        emotion = "positive"
        score = max(score, 0.75)
    elif positive_count >= 1 and distress_count == 0 and emotion == "neutral":
        emotion = "positive"
        score = max(score, 0.65)

    # ---- STEP 3: UPDATE BASELINE CONVERSATION STATE (existing) ----
    conversation_context = update_conversation(anon_id, text, emotion)

    # ---- STEP 4: RUN INTELLIGENCE LAYER (NEW) ----
    intelligence_context = None
    if ci_config.ENABLE_CONVERSATION_INTELLIGENCE:
        intelligence_context = process_intelligence(
            anon_id=anon_id,
            text=text,
            emotion=emotion,
            signals=signals,
            conversation_context=conversation_context
        )

    # ---- STEP 5: DECIDE NEXT STEP (existing) ----
    decision = decide_next_step(emotion, score)

    # Enhance decision with intelligence context
    if intelligence_context:
        decision = _enhance_decision(decision, intelligence_context)

    # ---- STEP 6: GENERATE REPLY (enhanced with intelligence) ----
    # Merge intelligence context into conversation context
    enhanced_context = _merge_contexts(conversation_context, intelligence_context)

    reply = generate_reply(
        anon_id=anon_id,
        emotion=emotion,
        decision=decision,
        text=text,
        conversation_context=enhanced_context
    )

    # ---- STEP 7: POST-REPLY UPDATE (NEW) ----
    if ci_config.ENABLE_CONVERSATION_INTELLIGENCE:
        post_reply_update(anon_id, reply)

    # ---- STEP 8: TRACK FOLLOW-UP (existing) ----
    if conversation_context.get("needs_followup"):
        mark_followup_done(anon_id)

    # ---- STEP 9: UPDATE MEMORY (existing) ----
    update_memory(anon_id, emotion, text)

    # ---- STEP 10: BUILD RESPONSE ----
    response = {
        "emotion": emotion,
        "score": score,
        "reply": reply,
        "conversation_context": {
            "turn": conversation_context.get("turn_count"),
            "initial_emotion": conversation_context.get("initial_emotion"),
            "topic": conversation_context.get("topic")
        }
    }

    # Add intelligence info if available
    if intelligence_context:
        response["intelligence"] = {
            "phase": intelligence_context.phase,
            "advice_mode": intelligence_context.advice_mode,
            "emotion_trend": intelligence_context.emotion_trend
        }

    return response


def _enhance_decision(
    decision: dict,
    intelligence: IntelligenceContext
) -> dict:
    """
    Enhance decision dict with intelligence context.

    Args:
        decision: Original decision from decide_next_step
        intelligence: Intelligence context

    Returns:
        Enhanced decision dict
    """
    enhanced = decision.copy()

    # Add phase-based mode hints
    phase = intelligence.phase

    if phase == "venting":
        enhanced["mode"] = "listen"
        enhanced["allow_questions"] = False

    elif phase == "calming":
        enhanced["mode"] = "ground"
        enhanced["pace"] = "slow"

    elif phase == "celebrating":
        enhanced["mode"] = "celebrate"
        enhanced["pace"] = "normal"

    elif phase == "closing":
        enhanced["mode"] = "close"

    # Pass through intelligence constraints
    enhanced["allow_questions"] = intelligence.allow_questions
    enhanced["allow_advice"] = intelligence.allow_advice
    enhanced["allow_memory_recall"] = intelligence.allow_memory_recall
    enhanced["blocked_categories"] = intelligence.blocked_categories

    return enhanced


def _merge_contexts(
    conversation_context: dict,
    intelligence: IntelligenceContext
) -> dict:
    """
    Merge baseline conversation context with intelligence context.

    Args:
        conversation_context: Baseline context from conversation_state
        intelligence: Intelligence context (may be None)

    Returns:
        Merged context dict
    """
    merged = conversation_context.copy()

    if intelligence is None:
        return merged

    # Add intelligence fields
    merged["phase"] = intelligence.phase
    merged["phase_reason"] = intelligence.phase_reason
    merged["advice_mode"] = intelligence.advice_mode
    merged["venting_score"] = intelligence.venting_score
    merged["emotion_trend"] = intelligence.emotion_trend

    # Constraints
    merged["allow_questions"] = intelligence.allow_questions
    merged["allow_advice"] = intelligence.allow_advice
    merged["allow_memory_recall"] = intelligence.allow_memory_recall
    merged["max_questions"] = intelligence.max_questions
    merged["recommended_tone"] = intelligence.recommended_tone

    # Blocked categories
    merged["blocked_categories"] = intelligence.blocked_categories

    # Memory
    merged["memory_response"] = intelligence.memory_response

    # Streaks
    merged["positive_streak"] = intelligence.positive_streak
    merged["neutral_streak"] = intelligence.neutral_streak
    merged["distress_streak"] = intelligence.distress_streak

    # Advice question
    if intelligence.should_ask_advice_preference:
        merged["ask_advice_preference"] = True
        merged["advice_question"] = get_advice_question_if_needed(intelligence)

    return merged


# =============================================================================
# BACKWARD COMPATIBLE ALIAS
# =============================================================================

def handle_message_original(payload: dict) -> dict:
    """
    Original handle_message without intelligence layer.

    Use this if you need to bypass the intelligence layer completely.
    """
    from src.chatbot.dialogue_manager import handle_message as original
    return original(payload)

