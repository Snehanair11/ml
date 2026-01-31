"""
Memory Policy - Decide if memory recall is allowed
"""

# ========================
# CONFIG FLAG
# ========================
ENABLE_MEMORY_POLICY = True

# ========================
# CONFIG
# ========================
MIN_TURNS_FOR_MEMORY = 3

ALLOWED_PHASES = {"reflecting", "celebrating", "calming"}
BLOCKED_PHASES = {"opening", "closing"}

# ========================
# MAIN FUNCTION
# ========================
def is_memory_allowed(phase: str, turn_count: int) -> bool:
    """
    Decide if memory recall is allowed.

    Returns: True if allowed, False otherwise
    """
    if not ENABLE_MEMORY_POLICY:
        return True  # Allow by default if disabled

    # Too early
    if turn_count < MIN_TURNS_FOR_MEMORY:
        return False

    # Blocked phases
    if phase in BLOCKED_PHASES:
        return False

    # Explicitly allowed phases
    if phase in ALLOWED_PHASES:
        return True

    # Default: allow after minimum turns
    return turn_count >= MIN_TURNS_FOR_MEMORY
