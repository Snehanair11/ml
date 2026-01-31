def decide_next_step(emotion: str, score: float, phase: str = None, intent: str = None):
    """
    Decide next step with optional phase/intent from new modules.
    If phase/intent are None, behaves exactly as before.
    """
    if emotion == "positive":
        decision = {"pace": "normal", "mode": "engage"}

    elif emotion == "neutral":
        decision = {"pace": "normal", "mode": "open"}

    elif emotion == "distress":
        decision = {"pace": "slow", "mode": "support"}

    elif emotion == "strong_distress":
        decision = {"pace": "slow", "mode": "ground"}

    else:
        decision = {"pace": "normal", "mode": "open"}

    # ---- INTEGRATE NEW MODULES (if provided) ----
    if phase:
        decision["phase"] = phase
        if phase == "venting":
            decision["allow_questions"] = False
        elif phase == "calming":
            decision["mode"] = "ground"
        elif phase == "celebrating":
            decision["mode"] = "celebrate"

    if intent:
        decision["intent"] = intent
        if intent == "vent_only":
            decision["allow_advice"] = False

    return decision
