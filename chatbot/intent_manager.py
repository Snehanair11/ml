"""
Intent Manager - Detect user intent (vent vs advice)
"""

# ========================
# CONFIG FLAG
# ========================
ENABLE_INTENT_MANAGER = True

# ========================
# INTENT LABELS
# ========================
VENT_ONLY = "vent_only"
ADVICE_OK = "advice_ok"
UNKNOWN = "unknown"

# ========================
# PHRASE SETS
# ========================
VENT_PHRASES = {
    "just need to vent", "let me vent", "just venting",
    "dont need advice", "don't need advice", "not looking for advice",
    "just want to talk", "just listen", "let me rant"
}

ADVICE_PHRASES = {
    "what should i do", "any advice", "help me figure out",
    "what do you think", "should i", "what would you do",
    "do you have advice", "your thoughts"
}

# ========================
# MAIN FUNCTION
# ========================
def detect_intent(text: str, message_length: int = None) -> str:
    """
    Detect user intent from message.

    Returns: VENT_ONLY, ADVICE_OK, or UNKNOWN
    """
    if not ENABLE_INTENT_MANAGER:
        return UNKNOWN

    text_lower = text.lower()

    # Check explicit vent phrases
    for phrase in VENT_PHRASES:
        if phrase in text_lower:
            return VENT_ONLY

    # Check explicit advice phrases
    for phrase in ADVICE_PHRASES:
        if phrase in text_lower:
            return ADVICE_OK

    # Long message = likely venting
    length = message_length or len(text)
    if length > 200:
        return VENT_ONLY

    return UNKNOWN
