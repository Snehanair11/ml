"""
Phase Manager - Determine conversation phase
"""

# ========================
# CONFIG FLAG
# ========================
ENABLE_PHASE_MANAGER = True

# ========================
# PHASE LABELS
# ========================
OPENING = "opening"
SHARING = "sharing"
VENTING = "venting"
REFLECTING = "reflecting"
CALMING = "calming"
CELEBRATING = "celebrating"
CLOSING = "closing"

# ========================
# EXIT PHRASES
# ========================
EXIT_PHRASES = {"bye", "goodbye", "see you", "gtg", "gotta go", "ttyl", "later"}

# ========================
# MAIN FUNCTION
# ========================
def determine_phase(
    emotion: str,
    turn_count: int,
    distress_count: int = 0,
    positive_count: int = 0,
    text: str = ""
) -> str:
    """
    Determine conversation phase based on context.

    Returns: phase label string
    """
    if not ENABLE_PHASE_MANAGER:
        return SHARING  # Safe default

    text_lower = text.lower()

    # First message = opening
    if turn_count <= 1:
        return OPENING

    # Check for exit
    for phrase in EXIT_PHRASES:
        if phrase in text_lower:
            return CLOSING

    # Strong distress = calming
    if emotion == "strong_distress":
        return CALMING

    # High distress signals = calming
    if distress_count >= 3:
        return CALMING

    # Long message or high signals = venting
    is_long = len(text) > 100 or len(text.split()) > 20
    if is_long and emotion in {"distress", "strong_distress"}:
        return VENTING

    # Positive emotion with signals = celebrating
    if emotion == "positive" and positive_count >= 2:
        return CELEBRATING

    # After turn 3, can reflect
    if turn_count >= 3 and len(text) < 50:
        return REFLECTING

    # Default
    if emotion == "positive":
        return CELEBRATING
    elif emotion in {"distress", "strong_distress"}:
        return VENTING

    return SHARING
