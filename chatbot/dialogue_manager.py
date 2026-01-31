from inference.predict_emotion import predict_emotion
from chatbot.decision_manager import decide_next_step
from chatbot.reply_manager import generate_reply
from chatbot.memory_manager import update_memory
from chatbot.conversation_state import update_conversation, mark_followup_done
from signal_mapper import count_signals_in_text

# ---- NEW MODULE IMPORTS ----
from chatbot.phase_manager import determine_phase, ENABLE_PHASE_MANAGER
from chatbot.intent_manager import detect_intent, ENABLE_INTENT_MANAGER
from chatbot.cooldown_manager import decrement_cooldowns, ENABLE_COOLDOWNS
from chatbot.memory_policy import is_memory_allowed, ENABLE_MEMORY_POLICY

def handle_message(payload: dict):
    anon_id = payload["anon_id"]
    text = payload["text"]
    conversation_history = payload.get("conversation_history", [])

    result = predict_emotion(text)
    emotion = result["emotion"]
    score = result["score"]

    # ---- SIGNAL-BASED EMOTION CORRECTION ----
    # Override ML prediction if text signals clearly indicate otherwise
    signals = count_signals_in_text(text)
    distress_count = signals["distress_count"]
    positive_count = signals["positive_count"]

    # If 3+ distress signals detected, override to strong_distress
    if distress_count >= 3:
        emotion = "strong_distress"
        score = 0.90
    # If 2 distress signals and more than positive, override to distress
    elif distress_count >= 2 and distress_count > positive_count:
        emotion = "distress"
        score = max(score, 0.75)
    # If 1 distress signal and NO positive signals, set to distress (fixes neutral issue)
    elif distress_count >= 1 and positive_count == 0 and emotion == "neutral":
        emotion = "distress"
        score = max(score, 0.65)
    # If 3+ positive signals detected, override to positive
    elif positive_count >= 3:
        emotion = "positive"
        score = 0.90
    # If 2 positive signals and more than distress, override to positive
    elif positive_count >= 2 and positive_count > distress_count:
        emotion = "positive"
        score = max(score, 0.75)
    # If 1 positive signal and NO distress signals, set to positive (fixes neutral issue)
    elif positive_count >= 1 and distress_count == 0 and emotion == "neutral":
        emotion = "positive"
        score = max(score, 0.65)

    # Update conversation state and get context
    conversation_context = update_conversation(anon_id, text, emotion)
    turn_count = conversation_context.get("turn_count", 1)

    # ---- NEW MODULES INTEGRATION ----
    phase = None
    intent = None
    allow_memory = True

    if ENABLE_PHASE_MANAGER:
        phase = determine_phase(emotion, turn_count, distress_count, positive_count, text)

    if ENABLE_INTENT_MANAGER:
        intent = detect_intent(text)

    if ENABLE_COOLDOWNS:
        decrement_cooldowns(anon_id)

    if ENABLE_MEMORY_POLICY:
        allow_memory = is_memory_allowed(phase or "sharing", turn_count)

    # Pass phase/intent to decision
    decision = decide_next_step(emotion, score, phase, intent)
    decision["allow_memory"] = allow_memory

    reply = generate_reply(
        anon_id=anon_id,
        emotion=emotion,
        decision=decision,
        text=text,
        conversation_context=conversation_context,
        conversation_history=conversation_history
    )

    # Track that we asked a follow-up if needed
    if conversation_context.get("needs_followup"):
        mark_followup_done(anon_id)

    update_memory(anon_id, emotion, text)

    return {
        "emotion": emotion,
        "score": score,
        "reply": reply,
        "conversation_context": {
            "turn": conversation_context.get("turn_count"),
            "initial_emotion": conversation_context.get("initial_emotion"),
            "topic": conversation_context.get("topic")
        }
    }

