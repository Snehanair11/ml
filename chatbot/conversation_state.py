# src/chatbot/conversation_state.py
"""
Conversation State Manager
Tracks the emotional flow of conversations to provide contextually appropriate responses.
"""

from datetime import datetime, timedelta
from collections import defaultdict

# ======================================================
# CONVERSATION STATE STORAGE
# ======================================================

# Store conversation states per user
# Structure: {anon_id: ConversationState}
_conversation_states = {}

# Conversation timeout (minutes) - after this, start fresh
CONVERSATION_TIMEOUT = 30

# ======================================================
# CONVERSATION STATE CLASS
# ======================================================

class ConversationState:
    def __init__(self, anon_id: str):
        self.anon_id = anon_id
        self.messages = []  # list of {text, emotion, timestamp}
        self.initial_emotion = None  # first emotion detected in convo
        self.current_emotion = None  # most recent emotion
        self.emotion_history = []  # track emotion changes
        self.turn_count = 0
        self.started_at = datetime.now()
        self.last_activity = datetime.now()
        self.conversation_topic = None  # detected topic (work, relationship, etc.)
        self.needs_followup = False  # whether we should ask follow-up
        self.followup_count = 0  # how many follow-ups we've done

    def is_expired(self) -> bool:
        """Check if conversation has timed out."""
        elapsed = datetime.now() - self.last_activity
        return elapsed > timedelta(minutes=CONVERSATION_TIMEOUT)

    def add_message(self, text: str, emotion: str):
        """Add a new message to the conversation."""
        self.last_activity = datetime.now()
        self.turn_count += 1

        message = {
            "text": text,
            "emotion": emotion,
            "timestamp": datetime.now(),
            "turn": self.turn_count
        }
        self.messages.append(message)

        # Track emotion changes
        if self.current_emotion != emotion:
            self.emotion_history.append({
                "from": self.current_emotion,
                "to": emotion,
                "turn": self.turn_count
            })

        # Set initial emotion on first message
        if self.initial_emotion is None:
            self.initial_emotion = emotion

        self.current_emotion = emotion

        # Determine if we need follow-up based on emotion
        self._update_followup_need(emotion)

        # Try to detect topic
        self._detect_topic(text)

    def _update_followup_need(self, emotion: str):
        """Determine if conversation needs follow-up questions."""
        # For distress/strong_distress, we should keep following up
        if emotion in {"distress", "strong_distress"}:
            self.needs_followup = True
        # For positive emotions, we can celebrate and ask for details
        elif emotion == "positive":
            self.needs_followup = True
        # Neutral - mild follow-up
        else:
            # Only follow up on neutral if it's early in conversation
            self.needs_followup = self.turn_count <= 2

    def _detect_topic(self, text: str):
        """Try to detect the conversation topic."""
        text_lower = text.lower()

        topic_keywords = {
            "work": ["job", "work", "office", "boss", "manager", "coworker",
                     "fired", "hired", "promotion", "salary", "deadline", "meeting"],
            "relationship": ["boyfriend", "girlfriend", "partner", "husband", "wife",
                            "dating", "breakup", "broke up", "relationship", "love",
                            "crush", "ex", "married", "divorce"],
            "family": ["mom", "dad", "mother", "father", "parent", "sibling",
                      "brother", "sister", "family", "son", "daughter", "grandma",
                      "grandpa", "aunt", "uncle"],
            "friend": ["friend", "bestie", "bff", "buddy", "pal", "friendship",
                      "friends"],
            "school": ["school", "college", "university", "class", "exam", "test",
                      "study", "homework", "assignment", "professor", "teacher",
                      "grade", "gpa"],
            "health": ["sick", "ill", "doctor", "hospital", "pain", "headache",
                      "fever", "tired", "sleep", "anxiety", "depression", "therapy",
                      "medication", "health"]
        }

        for topic, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                self.conversation_topic = topic
                break

    def get_conversation_context(self) -> dict:
        """Get context info for reply generation."""
        return {
            "initial_emotion": self.initial_emotion,
            "current_emotion": self.current_emotion,
            "emotion_history": self.emotion_history,
            "turn_count": self.turn_count,
            "topic": self.conversation_topic,
            "needs_followup": self.needs_followup,
            "followup_count": self.followup_count,
            "emotion_changed": len(self.emotion_history) > 0,
            "is_first_message": self.turn_count == 1,
            "recent_messages": self.messages[-3:] if len(self.messages) >= 3 else self.messages
        }

    def increment_followup(self):
        """Track that we've asked a follow-up."""
        self.followup_count += 1
        # After 3-4 follow-ups, reduce follow-up need
        if self.followup_count >= 4:
            self.needs_followup = False


# ======================================================
# PUBLIC FUNCTIONS
# ======================================================

def get_conversation_state(anon_id: str) -> ConversationState:
    """Get or create conversation state for a user."""
    if anon_id in _conversation_states:
        state = _conversation_states[anon_id]
        # Check if conversation has expired
        if state.is_expired():
            # Start fresh conversation
            state = ConversationState(anon_id)
            _conversation_states[anon_id] = state
        return state
    else:
        # Create new conversation
        state = ConversationState(anon_id)
        _conversation_states[anon_id] = state
        return state


def update_conversation(anon_id: str, text: str, emotion: str) -> dict:
    """
    Update conversation state with new message.
    Returns conversation context for reply generation.
    """
    state = get_conversation_state(anon_id)
    state.add_message(text, emotion)
    return state.get_conversation_context()


def get_conversation_context(anon_id: str) -> dict:
    """Get current conversation context without adding a message."""
    state = get_conversation_state(anon_id)
    return state.get_conversation_context()


def mark_followup_done(anon_id: str):
    """Mark that a follow-up question was asked."""
    if anon_id in _conversation_states:
        _conversation_states[anon_id].increment_followup()


def end_conversation(anon_id: str):
    """Explicitly end a conversation (e.g., user says bye)."""
    if anon_id in _conversation_states:
        del _conversation_states[anon_id]


def is_conversation_ongoing(anon_id: str) -> bool:
    """Check if there's an active conversation."""
    if anon_id not in _conversation_states:
        return False
    return not _conversation_states[anon_id].is_expired()
