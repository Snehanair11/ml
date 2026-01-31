# src/signal_mapper.py
"""
Signal Mapper - Maps predictions to signals and analyzes patterns
Handles signal counting for pattern-based response selection
"""

# ======================================================
# SIGNAL MAPPING
# ======================================================

def map_signal(prediction, confidence):
    """Map a single prediction to a signal level."""
    if prediction == "distress":
        if confidence >= 0.80:
            return "STRONG_DISTRESS"
        elif confidence >= 0.65:
            return "MODERATE_DISTRESS"
        else:
            return "WEAK_DISTRESS"
    elif prediction == "positive":
        if confidence >= 0.80:
            return "STRONG_POSITIVE"
        elif confidence >= 0.65:
            return "MODERATE_POSITIVE"
        else:
            return "WEAK_POSITIVE"
    else:
        return "NEUTRAL"


# ======================================================
# SIGNAL COUNTING & PATTERN DETECTION
# ======================================================

# Keywords/phrases for detecting distress signals in text
DISTRESS_KEYWORDS = {
    # strong distress
    "cant take it", "can't take it", "cant do this", "can't do this",
    "want to die", "wanna die", "kill myself", "end it all", "give up",
    "hopeless", "worthless", "hate myself", "no point", "cant cope",
    "falling apart", "breaking down", "losing it", "going crazy",
    "cant breathe", "suffocating", "drowning", "trapped", "stuck",
    "everything hurts", "so much pain", "cant handle", "overwhelmed",
    # moderate distress
    "stressed", "anxious", "worried", "scared", "afraid", "nervous",
    "depressed", "sad", "upset", "hurt", "lonely", "alone", "empty",
    "exhausted", "drained", "burned out", "burnt out", "tired",
    "frustrated", "angry", "mad", "pissed", "annoyed", "irritated",
    "crying", "tears", "sobbing", "heartbroken", "devastated",
    "distress", "distressed", "causing me distress", "gives me distress",
    "pressure", "pressures", "pressuring", "pressured",
    # weak distress
    "not okay", "not fine", "not good", "feeling off", "feeling down",
    "kinda sad", "bit sad", "little sad", "not great", "meh",
    "struggling", "having a hard time", "difficult", "rough",
    "bad day", "tough day", "hard day", "rough day", "stressful day",
    # work/job distress
    "done with my job", "done with this job", "done with work",
    "hate my job", "hate this job", "hate work", "job sucks",
    "work sucks", "job is killing", "work is killing",
    "drains me", "draining me", "draines me", "draines",
    "useless", "incompetent", "toxic", "nightmare",
    "cant stand", "can't stand", "sick of", "fed up",
    "so done", "im done", "i'm done", "over it",
    # typo variations
    "exhuasted", "exausted", "tierd", "streesed", "stresed",
    "anxous", "depresed", "fustrated", "frustarted",
    "annyoed", "anoyed", "iritated", "exausting",
    # more phrases
    "killing me", "driving me crazy", "driving me insane",
    "at my limit", "at my wits end", "end of my rope",
    "cant anymore", "can't anymore", "no more",
    "breaking point", "about to snap", "gonna snap",
    "miserable", "suffering", "in pain", "hurting",
    # too much / overwhelming
    "too much", "getting too much", "its too much", "it's too much",
    "way too much", "all too much", "becoming too much",
    "cant handle it", "can't handle it", "cant deal", "can't deal",
    # single word emotions (important!)
    "hate", "sucks", "awful", "terrible", "horrible", "worst",
    "ugh", "ughh", "ughhh", "argh", "arghhh", "fml", "smh",
    "crying", "cried", "cry", "sobbing", "sobbed",
    "dying", "dead", "done", "finished", "ruined",
    "failed", "failing", "failure", "loser",
    "pathetic", "stupid", "idiot", "dumb",
    "boring", "bored", "suck", "hate it", "hate this",
    "i hate", "so tired", "so stressed", "so sad", "so done",
    "im sad", "i'm sad", "im tired", "i'm tired",
    "im stressed", "i'm stressed", "im anxious", "i'm anxious",
    "im depressed", "i'm depressed", "im lonely", "i'm lonely",
    "im scared", "i'm scared", "im worried", "i'm worried",
    "im upset", "i'm upset", "im hurt", "i'm hurt",
    "im angry", "i'm angry", "im mad", "i'm mad",
    "im frustrated", "i'm frustrated", "im annoyed", "i'm annoyed",
    "feeling sad", "feeling tired", "feeling stressed",
    "feeling anxious", "feeling depressed", "feeling lonely",
    "feeling scared", "feeling worried", "feeling upset",
    "feeling angry", "feeling frustrated", "feeling annoyed",
    "feeling bad", "feeling terrible", "feeling awful",
    "feeling horrible", "feeling down", "feeling low",
    "not happy", "unhappy", "dissatisfied", "disappointed",
    "disappointing", "heartbreak", "painful", "pain",
    # more common words
    "bad", "worse", "sucky", "crappy", "crap", "shit", "shitty",
    "trash", "garbage", "hell", "damn", "dammit", "wtf", "wth",
    "annoying", "irritating", "frustrating", "stressful",
    "overwhelming", "exhausting", "draining", "tiring",
    "depressing", "upsetting", "hurtful", "scary", "terrifying",
    "anxious", "nervous", "worried", "stressed", "panicking",
    "freaking out", "losing my mind", "going insane",
    "cant sleep", "can't sleep", "insomnia", "restless",
    "headache", "migraine", "sick", "ill", "unwell",
    "broken", "shattered", "crushed", "destroyed",
    "helpless", "powerless", "weak", "vulnerable",
    "rejected", "abandoned", "ignored", "neglected",
    "betrayed", "cheated", "lied to", "used",
    "embarrassed", "humiliated", "ashamed", "guilty",
    "regret", "remorse", "sorry", "apologize",
    "confused", "lost", "uncertain", "unsure", "doubtful",
    "numb", "detached", "disconnected", "empty inside",
    # grief / loss / death
    "died", "passed away", "passed on", "lost my", "death",
    "funeral", "grieving", "grief", "mourning", "miss them",
    "miss her", "miss him", "gone forever", "never coming back",
    "lost someone", "loved one", "heartbroken", "devastated",
    "broke up", "breakup", "dumped", "left me", "divorced",
    # humiliation / degradation
    "humiliated", "humiliates", "humiliating", "humiliation",
    "degraded", "degrading", "degradation", "belittled", "belittling",
    "disrespected", "disrespecting", "disrespectful", "insulted", "insulting",
    # mental health collapsing / deteriorating
    "collapsing", "mental health collapsing", "health is collapsing",
    "deteriorating", "mental health deteriorating", "health deteriorating",
    "falling apart mentally", "mentally falling apart",
    # forcing / coercion
    "forcing me", "forced me", "forcing us", "being forced", "theyre forcing",
    "they are forcing", "made me do", "making me do", "have no choice",
    # no one understands / isolated
    "no one understands", "nobody understands", "noone understands",
    "no one gets it", "nobody gets it", "no one gets me", "nobody gets me",
    "no one listens", "nobody listens", "feel unheard", "feeling unheard",
    "alone in this", "all alone", "completely alone", "feel so alone",
    # underpaid / compensation issues
    "underpaid", "not paid well", "poorly paid", "not paid enough",
    "pay is terrible", "pay is shit", "pay sucks", "salary sucks",
    "deserve better pay", "not compensated", "undervalued", "underappreciated",
    # regret / mistake
    "regret this", "regret taking", "regret joining", "i regret",
    "biggest mistake", "shouldnt have", "should not have", "wish i didnt",
    # suffocation / trapped at work
    "suffocates me", "this place suffocates", "work suffocates",
    "feel suffocated", "feeling suffocated", "cant escape", "no way out",
    "trapped here", "stuck here", "cant leave", "feel trapped",
    # seeking peace / escape from stress
    "i want peace", "want peace", "need peace", "just want peace",
    "i need peace", "give me peace", "want some peace", "need some peace",
    "peace in my life", "want peace in my life", "need peace in my life",
    "peace of mind", "want peace of mind", "need peace of mind",
    "just want to be at peace", "want to feel at peace", "need to feel at peace",
    "want quiet", "need quiet", "want silence", "need silence",
    "want to be left alone", "leave me alone", "need space", "need a break",
    "need to escape", "want to escape", "want to run away", "need to get away"
}

# Keywords/phrases for detecting positive signals in text
POSITIVE_KEYWORDS = {
    # strong positive
    "so happy", "really happy", "super happy", "extremely happy",
    "best day", "amazing", "incredible", "fantastic", "wonderful",
    "excited", "thrilled", "ecstatic", "overjoyed", "blessed",
    "love this", "love it", "perfect", "awesome", "brilliant",
    "got promoted", "got the job", "passed", "won", "achieved",
    # moderate positive
    "happy", "good", "great", "nice", "lovely", "fun", "enjoy",
    "glad", "pleased", "grateful", "thankful", "relieved",
    "proud", "accomplished", "satisfied", "content", "peaceful",
    "hopeful", "optimistic", "looking forward", "cant wait",
    # weak positive
    "okay", "fine", "alright", "not bad", "pretty good", "decent",
    "better", "improving", "getting better", "doing okay",
    "feeling good", "feeling better", "feeling positive"
}

# Neutral indicators
NEUTRAL_KEYWORDS = {
    "idk", "dunno", "whatever", "nothing much", "just chilling",
    "bored", "meh", "same old", "nothing new", "just here",
    "normal", "regular", "usual", "typical", "average"
}


def count_signals_in_text(text: str) -> dict:
    """
    Count distress and positive signals in text.
    Returns dict with counts and dominant signal type.
    """
    text_lower = text.lower()

    distress_count = 0
    positive_count = 0
    neutral_count = 0

    # Count distress keywords
    for keyword in DISTRESS_KEYWORDS:
        if keyword in text_lower:
            distress_count += 1

    # Count positive keywords
    for keyword in POSITIVE_KEYWORDS:
        if keyword in text_lower:
            positive_count += 1

    # Count neutral keywords
    for keyword in NEUTRAL_KEYWORDS:
        if keyword in text_lower:
            neutral_count += 1

    # Determine dominant signal
    if distress_count >= 3:
        dominant = "distress_heavy"
    elif distress_count > positive_count and distress_count >= 2:
        dominant = "distress_moderate"
    elif distress_count > positive_count:
        dominant = "distress_light"
    elif positive_count >= 3:
        dominant = "positive_heavy"
    elif positive_count > distress_count and positive_count >= 2:
        dominant = "positive_moderate"
    elif positive_count > distress_count:
        dominant = "positive_light"
    elif distress_count == positive_count and distress_count > 0:
        dominant = "mixed"
    else:
        dominant = "neutral"

    return {
        "distress_count": distress_count,
        "positive_count": positive_count,
        "neutral_count": neutral_count,
        "dominant": dominant,
        "total_signals": distress_count + positive_count + neutral_count
    }


def analyze_signal_pattern(signals_history: list) -> dict:
    """
    Analyze a list of signals to determine overall pattern.
    signals_history: list of dicts with {signal: str, confidence: float}
    Returns pattern analysis.
    """
    if not signals_history:
        return {"pattern": "unknown", "recommendation": "neutral"}

    distress_signals = 0
    positive_signals = 0
    strong_distress = 0
    strong_positive = 0

    for s in signals_history:
        signal = s.get("signal", "NEUTRAL")
        if "DISTRESS" in signal:
            distress_signals += 1
            if "STRONG" in signal:
                strong_distress += 1
        elif "POSITIVE" in signal:
            positive_signals += 1
            if "STRONG" in signal:
                strong_positive += 1

    total = len(signals_history)

    # Pattern detection logic
    # More than 3 distress signals = heavy distress pattern
    if distress_signals >= 3 or strong_distress >= 2:
        pattern = "heavy_distress"
        recommendation = "strong_support"
    elif distress_signals > positive_signals and distress_signals >= 2:
        pattern = "moderate_distress"
        recommendation = "support"
    elif distress_signals > positive_signals:
        pattern = "light_distress"
        recommendation = "empathy"
    # More than 3 positive signals = heavy positive pattern
    elif positive_signals >= 3 or strong_positive >= 2:
        pattern = "heavy_positive"
        recommendation = "celebration"
    elif positive_signals > distress_signals and positive_signals >= 2:
        pattern = "moderate_positive"
        recommendation = "encourage"
    elif positive_signals > distress_signals:
        pattern = "light_positive"
        recommendation = "acknowledge"
    elif distress_signals == positive_signals and distress_signals > 0:
        pattern = "mixed_emotions"
        recommendation = "balanced"
    else:
        pattern = "neutral"
        recommendation = "open"

    return {
        "pattern": pattern,
        "recommendation": recommendation,
        "distress_count": distress_signals,
        "positive_count": positive_signals,
        "strong_distress": strong_distress,
        "strong_positive": strong_positive,
        "total_signals": total
    }


def get_response_mode(text: str, prediction: str, confidence: float) -> dict:
    """
    Determine the appropriate response mode based on all signals.
    Combines text analysis with ML prediction.
    """
    # Get text-based signal counts
    text_signals = count_signals_in_text(text)

    # Get ML-based signal
    ml_signal = map_signal(prediction, confidence)

    # Combine for final decision
    distress_total = text_signals["distress_count"]
    positive_total = text_signals["positive_count"]

    # Add weight from ML prediction
    if "DISTRESS" in ml_signal:
        distress_total += 2 if "STRONG" in ml_signal else 1
    elif "POSITIVE" in ml_signal:
        positive_total += 2 if "STRONG" in ml_signal else 1

    # Determine response mode
    if distress_total >= 4:  # 3+ distress keywords OR 2+ with ML distress
        mode = "heavy_distress"
        emotion = "strong_distress"
    elif distress_total >= 3:
        mode = "moderate_distress"
        emotion = "distress"
    elif distress_total > positive_total and distress_total >= 2:
        mode = "light_distress"
        emotion = "distress"
    elif positive_total >= 4:  # 3+ positive keywords OR 2+ with ML positive
        mode = "heavy_positive"
        emotion = "positive"
    elif positive_total >= 3:
        mode = "moderate_positive"
        emotion = "positive"
    elif positive_total > distress_total and positive_total >= 2:
        mode = "light_positive"
        emotion = "positive"
    elif distress_total > 0 and positive_total > 0:
        mode = "mixed"
        emotion = "distress" if distress_total >= positive_total else "positive"
    else:
        mode = "neutral"
        emotion = prediction if prediction in {"positive", "distress", "neutral"} else "neutral"

    return {
        "mode": mode,
        "emotion": emotion,
        "ml_signal": ml_signal,
        "text_signals": text_signals,
        "distress_total": distress_total,
        "positive_total": positive_total
    }
