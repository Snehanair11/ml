from collections import defaultdict, deque

MEMORY = defaultdict(lambda: deque(maxlen=5))

# ======================================================
# TOPIC KEYWORDS FOR MEMORY MATCHING
# ======================================================

TOPIC_KEYWORDS = {
    "work": {"work", "job", "boss", "office", "meeting", "deadline", "coworker",
             "colleague", "manager", "promotion", "fired", "quit", "salary", "overtime",
             "workload", "project", "client", "team", "hired", "interview"},
    "relationship": {"boyfriend", "girlfriend", "bf", "gf", "partner", "ex", "dating",
                     "relationship", "breakup", "broke up", "crush", "love", "married",
                     "husband", "wife", "spouse", "divorce", "cheated", "toxic"},
    "family": {"mom", "dad", "mother", "father", "parent", "parents", "sibling",
               "brother", "sister", "family", "grandma", "grandpa", "aunt", "uncle",
               "cousin", "kid", "child", "children", "son", "daughter"},
    "friend": {"friend", "friends", "bestie", "bff", "bsf", "squad", "group",
               "friendship", "buddy", "pal", "homie"},
    "school": {"school", "college", "university", "class", "exam", "test", "study",
               "homework", "assignment", "professor", "teacher", "grade", "gpa",
               "semester", "finals", "midterm", "degree", "graduate"},
    "health": {"sick", "ill", "health", "doctor", "hospital", "medicine", "pain",
               "headache", "tired", "sleep", "insomnia", "anxiety", "depression",
               "therapy", "therapist", "mental health", "physical"},
    "money": {"money", "broke", "poor", "rich", "salary", "pay", "rent", "bills",
              "debt", "loan", "savings", "expensive", "afford", "budget", "financial"},
    "self": {"myself", "self", "me", "i feel", "i am", "im feeling", "personally",
             "my life", "my own", "alone", "lonely", "worthless", "useless", "hate myself"}
}

def extract_topics(text: str) -> set:
    """Extract topics mentioned in the text"""
    text_lower = text.lower()
    found_topics = set()

    for topic, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_topics.add(topic)
                break

    return found_topics

def update_memory(anon_id: str, emotion: str, text: str):
    topics = extract_topics(text)
    MEMORY[anon_id].append({
        "emotion": emotion,
        "text": text,
        "topics": topics
    })

def get_memory_hint(anon_id: str):
    if anon_id not in MEMORY or not MEMORY[anon_id]:
        return None
    return MEMORY[anon_id][-1]["emotion"]

def get_similar_past_topic(anon_id: str, current_text: str):
    """
    Check if user mentioned similar topic before.
    Returns dict with topic and past emotion if found, None otherwise.
    """
    if anon_id not in MEMORY or len(MEMORY[anon_id]) < 2:
        return None

    current_topics = extract_topics(current_text)
    if not current_topics:
        return None

    # check previous messages (skip the most recent one)
    past_entries = list(MEMORY[anon_id])[:-1]

    for entry in reversed(past_entries):
        past_topics = entry.get("topics", set())
        common_topics = current_topics & past_topics

        if common_topics:
            return {
                "topic": list(common_topics)[0],
                "past_emotion": entry["emotion"],
                "past_text": entry["text"][:50]  # snippet
            }

    return None

def get_recurring_emotion(anon_id: str, emotion: str):
    """
    Check if user has been feeling same emotion repeatedly.
    Returns count of similar emotions in memory.
    """
    if anon_id not in MEMORY:
        return 0

    count = sum(1 for entry in MEMORY[anon_id] if entry["emotion"] == emotion)
    return count

def has_mentioned_before(anon_id: str, keywords: list) -> bool:
    """
    Check if user mentioned any of these keywords before.
    """
    if anon_id not in MEMORY:
        return False

    for entry in MEMORY[anon_id]:
        text_lower = entry["text"].lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return True
    return False
