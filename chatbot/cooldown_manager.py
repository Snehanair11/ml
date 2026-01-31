"""
Cooldown Manager - Prevent reply repetition
"""
from collections import defaultdict

# ========================
# CONFIG FLAG
# ========================
ENABLE_COOLDOWNS = True

# ========================
# COOLDOWN CONFIG
# ========================
DEFAULT_COOLDOWN = 3  # turns

CATEGORY_COOLDOWNS = {
    "what_happened": 3,
    "memory_callback": 4,
    "breathe_tip": 3,
    "celebration": 2,
    "grounding": 3
}

# ========================
# STATE STORAGE
# ========================
_cooldowns = defaultdict(lambda: defaultdict(int))  # {anon_id: {category: turns}}

# ========================
# FUNCTIONS
# ========================
def is_on_cooldown(anon_id: str, category: str) -> bool:
    """Check if category is on cooldown for user."""
    if not ENABLE_COOLDOWNS:
        return False
    return _cooldowns[anon_id].get(category, 0) > 0


def set_cooldown(anon_id: str, category: str, turns: int = None):
    """Set cooldown for a category."""
    if not ENABLE_COOLDOWNS:
        return
    if turns is None:
        turns = CATEGORY_COOLDOWNS.get(category, DEFAULT_COOLDOWN)
    _cooldowns[anon_id][category] = turns


def decrement_cooldowns(anon_id: str):
    """Decrement all cooldowns by 1 (call once per turn)."""
    if not ENABLE_COOLDOWNS:
        return
    expired = []
    for category, turns in _cooldowns[anon_id].items():
        if turns > 1:
            _cooldowns[anon_id][category] = turns - 1
        else:
            expired.append(category)
    for cat in expired:
        del _cooldowns[anon_id][cat]


def get_blocked_categories(anon_id: str) -> set:
    """Get set of blocked category names."""
    if not ENABLE_COOLDOWNS:
        return set()
    return {cat for cat, turns in _cooldowns[anon_id].items() if turns > 0}


def reset_cooldowns(anon_id: str):
    """Clear all cooldowns for user."""
    if anon_id in _cooldowns:
        del _cooldowns[anon_id]
