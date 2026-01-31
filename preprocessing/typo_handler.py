# src/preprocessing/typo_handler.py

import re
from difflib import SequenceMatcher

# ======================================================
# COMMON TYPO MAPPINGS
# ======================================================

TYPO_CORRECTIONS = {
    # pain / hurt variations
    "pian": "pain", "paine": "pain", "painn": "pain", "pein": "pain",
    "pani": "pain", "apni": "pain", "pina": "pain", "paain": "pain",
    "hrt": "hurt", "hrut": "hurt", "hutr": "hurt", "hurtt": "hurt",
    "hurttt": "hurt", "hutrt": "hurt", "hute": "hurt", "hurat": "hurt",

    # sad variations
    "sda": "sad", "sadd": "sad", "saddd": "sad", "sadddd": "sad",
    "saf": "sad", "sas": "sad", "szd": "sad", "asd": "sad",

    # tired variations
    "tird": "tired", "tierd": "tired", "tred": "tired", "tiredd": "tired",
    "tirde": "tired", "itred": "tired", "tored": "tired", "tyred": "tired",

    # angry / mad variations
    "angyr": "angry", "anrgy": "angry", "angrey": "angry", "agry": "angry",
    "angy": "angry", "angryy": "angry", "amgry": "angry", "sngry": "angry",
    "madd": "mad", "maddd": "mad", "maf": "mad", "mas": "mad",

    # hate variations
    "haet": "hate", "htae": "hate", "hste": "hate", "hatee": "hate",
    "hateee": "hate", "ahte": "hate", "haye": "hate", "hte": "hate",

    # stressed variations
    "stresed": "stressed", "stressd": "stressed", "stessed": "stressed",
    "streesed": "stressed", "strssed": "stressed", "stresssed": "stressed",
    "stressedd": "stressed", "stresedd": "stressed", "streessed": "stressed",
    "stresses": "stressed", "stressss": "stressed", "streesss": "stressed",
    "stresss": "stressed", "stresss": "stressed", "stressin": "stressing",
    "stressingg": "stressing", "stresin": "stressing", "stresing": "stressing",

    # depressed variations
    "depresed": "depressed", "derpessed": "depressed", "depreesed": "depressed",
    "depresssed": "depressed", "depreseed": "depressed", "deppressed": "depressed",

    # anxious variations
    "anxous": "anxious", "anixous": "anxious", "anxios": "anxious",
    "anxoius": "anxious", "anixious": "anxious", "anxiuos": "anxious",

    # lonely variations
    "lonley": "lonely", "lonly": "lonely", "lonaly": "lonely",
    "loneyl": "lonely", "loneley": "lonely", "loenyl": "lonely",

    # exhausted variations
    "exhuasted": "exhausted", "exausted": "exhausted", "exhaustd": "exhausted",
    "exhasuted": "exhausted", "exhaused": "exhausted", "exhaustedd": "exhausted",

    # frustrated variations
    "frustarted": "frustrated", "frsutrated": "frustrated", "frustated": "frustrated",
    "frustrted": "frustrated", "frustatred": "frustrated", "frustratedd": "frustrated",
    "frustrasted": "frustrated", "fustrated": "frustrated", "frustred": "frustrated",

    # annoying / annoyed variations
    "annyoing": "annoying", "annoyin": "annoying", "annoyng": "annoying",
    "annoynig": "annoying", "anoying": "annoying", "annoyingg": "annoying",
    "annoyedd": "annoyed", "anoyed": "annoyed", "annyed": "annoyed",
    "annoing": "annoying", "anooying": "annoying", "annoyig": "annoying",

    # rest / sleep / break variations
    "rset": "rest", "resr": "rest", "restt": "rest", "reast": "rest",
    "slep": "sleep", "slepe": "sleep", "slepp": "sleep", "slee": "sleep",
    "sleepy": "sleepy", "sleeppy": "sleepy", "sleeepy": "sleepy",
    "brek": "break", "braek": "break", "breal": "break", "breka": "break",
    "npa": "nap", "naap": "nap", "napp": "nap",

    # breathe variations
    "breahte": "breathe", "breathee": "breathe", "breateh": "breathe",
    "breethe": "breathe", "brethe": "breathe", "breathh": "breathe",

    # sick / unwell variations
    "sicj": "sick", "sck": "sick", "sik": "sick", "sickk": "sick",
    "feelig": "feeling", "feleing": "feeling", "feling": "feeling",
    "unwel": "unwell", "unwll": "unwell", "unweell": "unwell",
    "headahce": "headache", "headche": "headache", "hedache": "headache",
    "feevr": "fever", "fevr": "fever", "fver": "fever", "feveer": "fever",
    "nasueous": "nauseous", "nauseus": "nauseous", "naseuous": "nauseous",
    "dizy": "dizzy", "dizzy": "dizzy", "dizzzy": "dizzy", "dizzyy": "dizzy",
    "stomahc": "stomach", "stomch": "stomach", "stomache": "stomach",
    "throiwng": "throwing", "throwng": "throwing", "throwin": "throwing",

    # overwhelmed variations
    "overwhlemed": "overwhelmed", "overwhelemd": "overwhelmed",
    "overwhlmed": "overwhelmed", "overwhemled": "overwhelmed",
    "overwhelmedd": "overwhelmed", "overwhelmd": "overwhelmed",

    # terrible variations
    "terrbile": "terrible", "terirble": "terrible", "terible": "terrible",
    "terrilbe": "terrible", "terribel": "terrible", "terrble": "terrible",

    # horrible variations
    "horrble": "horrible", "horrbile": "horrible", "horible": "horrible",
    "horrilbe": "horrible", "horribel": "horrible", "horribile": "horrible",

    # miserable variations
    "miserble": "miserable", "misrable": "miserable", "miseralbe": "miserable",
    "miserabel": "miserable", "miserablee": "miserable", "miserbale": "miserable",

    # heartbroken variations
    "heartborken": "heartbroken", "heartbroen": "heartbroken",
    "hearbroken": "heartbroken", "heartbrokne": "heartbroken",
    "heartbrokenn": "heartbroken", "haertbroken": "heartbroken",

    # cry / crying variations
    "cyr": "cry", "crey": "cry", "cri": "cry", "cryi": "cry",
    "cryng": "crying", "cryign": "crying", "criyng": "crying",
    "cring": "crying", "cyring": "crying", "crynig": "crying",

    # hopeless variations
    "hopless": "hopeless", "hoepless": "hopeless", "hopelss": "hopeless",
    "hoepelss": "hopeless", "hopelesss": "hopeless", "hopelees": "hopeless",

    # worthless variations
    "worthles": "worthless", "worthelss": "worthless", "wortless": "worthless",
    "worhtless": "worthless", "worthlesss": "worthless", "worthlees": "worthless",

    # useless variations
    "useles": "useless", "uselss": "useless", "uselees": "useless",
    "uesless": "useless", "uselesss": "useless", "uselass": "useless",

    # curse words typos
    "fuk": "fuck", "fck": "fuck", "fcuk": "fuck", "fukc": "fuck",
    "fucc": "fuck", "fuxk": "fuck", "fucj": "fuck", "fukk": "fuck",
    "sht": "shit", "shti": "shit", "siht": "shit", "shitt": "shit",
    "shyt": "shit", "shiit": "shit", "shiz": "shit", "shite": "shit",
    "btch": "bitch", "bich": "bitch", "bicth": "bitch", "bithc": "bitch",
    "biatch": "bitch", "bytch": "bitch", "btich": "bitch",
    "asss": "ass", "azz": "ass", "arse": "ass", "a$$": "ass",
    "assss": "ass", "azss": "ass",
    "dmn": "damn", "danm": "damn", "damm": "damn", "dman": "damn",
    "damnn": "damn", "daamn": "damn", "dayum": "damn",
    "hel": "hell", "helll": "hell", "heell": "hell",
    "crpa": "crap", "carp": "crap", "crapp": "crap", "craap": "crap",

    # common typos for expressions
    "ughhh": "ugh", "ughh": "ugh", "ugg": "ugh", "uhg": "ugh",
    "omgg": "omg", "omggg": "omg", "ogm": "omg", "omgod": "omg",
    "wtff": "wtf", "wft": "wtf", "wtfff": "wtf",
    "wthh": "wth", "wht": "wth", "wthh": "wth",

    # emotion words typos
    "hapy": "happy", "happpy": "happy", "hpapy": "happy", "happyy": "happy",
    "exicted": "excited", "excitd": "excited", "exited": "excited",
    "scaerd": "scared", "scarred": "scared", "scred": "scared",
    "woried": "worried", "worred": "worried", "worreid": "worried",
    "nervos": "nervous", "nervious": "nervous", "nervosu": "nervous",

    # common word typos
    "teh": "the", "hte": "the", "tthe": "the",
    "adn": "and", "nad": "and", "andd": "and",
    "taht": "that", "htat": "that", "thta": "that",
    "jsut": "just", "juts": "just", "jst": "just",
    "dont": "don't", "dnt": "don't", "dontt": "don't",
    "cant": "can't", "cnat": "can't", "cantt": "can't",
    "wont": "won't", "wnt": "won't", "wontt": "won't",
    "im": "i'm", "iam": "i'm", "imm": "i'm",
    "youre": "you're", "ur": "you're", "yuor": "your",
    "thier": "their", "tehir": "their", "theri": "their",
    "becuase": "because", "becasue": "because", "beacuse": "because",
    "becuse": "because", "bcause": "because", "bcuz": "because",
    "somthing": "something", "somethign": "something", "smth": "something",
    "nothign": "nothing", "ntohing": "nothing", "nthing": "nothing",
    "evrything": "everything", "everythign": "everything", "everthing": "everything",
    "anyting": "anything", "anythign": "anything", "anythin": "anything",
    "poeple": "people", "peopel": "people", "ppl": "people",
    "realy": "really", "relly": "really", "reallly": "really",
    "actualy": "actually", "actaully": "actually", "acutally": "actually",
    "definetly": "definitely", "definately": "definitely", "defintely": "definitely",
    "probaly": "probably", "probbaly": "probably", "prolly": "probably",

    # feelings / states
    "emtpy": "empty", "emptty": "empty", "emty": "empty",
    "borken": "broken", "brokne": "broken", "brokenn": "broken",
    "aloen": "alone", "alonee": "alone", "aline": "alone",
    "scuk": "suck", "sukc": "suck", "suk": "suck", "suckss": "sucks",
    "awfull": "awful", "aweful": "awful", "awflu": "awful",

    # work related
    "wrk": "work", "wrok": "work", "workk": "work", "owrk": "work",
    "jbo": "job", "joob": "job", "jobb": "job",
    "bos": "boss", "boos": "boss", "bosss": "boss",

    # relationship
    "freind": "friend", "frend": "friend", "fiend": "friend",
    "frineds": "friends", "freinds": "friends", "frnds": "friends",
    "relatioship": "relationship", "realtionship": "relationship",
    "boyfreind": "boyfriend", "girlfreind": "girlfriend",

    # common shortforms / abbreviations (gen-z texting)
    "wtvr": "whatever", "wtevr": "whatever", "watever": "whatever",
    "whatevr": "whatever", "whtever": "whatever", "whatevs": "whatever",
    "uk": "you know", "yk": "you know", "yanno": "you know",
    "u kno": "you know", "yknow": "you know",
    "nvm": "nevermind", "nvrmnd": "nevermind", "nevrmind": "nevermind",
    "smth": "something", "smthn": "something", "sumthin": "something",
    "sumn": "something", "smthng": "something",
    "nth": "nothing", "nthn": "nothing", "nuthin": "nothing",
    "anth": "anything", "anythn": "anything",
    "prly": "probably", "prolly": "probably", "probs": "probably",
    "prbly": "probably", "probly": "probably",
    "def": "definitely", "deffo": "definitely", "defs": "definitely",
    "defo": "definitely", "defn": "definitely",
    "tbh": "to be honest", "tbe": "to be honest",
    "ngl": "not gonna lie", "ngl": "not gonna lie",
    "imo": "in my opinion", "imho": "in my humble opinion",
    "idk": "i dont know", "idek": "i dont even know",
    "idc": "i dont care", "idrc": "i dont really care",
    "iirc": "if i remember correctly",
    "afaik": "as far as i know",
    "rn": "right now", "atm": "at the moment",
    "asap": "as soon as possible",
    "btw": "by the way", "byw": "by the way",
    "omw": "on my way", "otw": "on the way",
    "lmk": "let me know", "lemme": "let me",
    "hmu": "hit me up", "ttyl": "talk to you later",
    "brb": "be right back", "bbl": "be back later",
    "gtg": "got to go", "g2g": "got to go",
    "wya": "where you at", "wru": "where are you",
    "wyd": "what you doing", "wbu": "what about you",
    "hbu": "how about you", "hru": "how are you",
    "ily": "i love you", "ilysm": "i love you so much",
    "lysm": "love you so much", "ly": "love you",
    "ikr": "i know right", "fr": "for real", "frfr": "for real for real",
    "ong": "on god", "istg": "i swear to god", "stg": "swear to god",
    "lowkey": "low key", "highkey": "high key",
    "nbd": "no big deal", "np": "no problem", "nw": "no worries",
    "jk": "just kidding", "jks": "just kidding", "jp": "just playing",
    "lol": "laughing out loud", "lmao": "laughing my ass off",
    "lmfao": "laughing my fucking ass off", "rofl": "rolling on floor laughing",
    "smh": "shaking my head", "fml": "fuck my life",
    "omfg": "oh my fucking god", "omgg": "oh my god",
    "wtf": "what the fuck", "wth": "what the hell",
    "tf": "the fuck", "af": "as fuck", "asf": "as fuck",
    "ofc": "of course", "obvi": "obviously", "obvs": "obviously",
    "ig": "i guess", "igs": "i guess so",
    "tho": "though", "doe": "though", "altho": "although",
    "cuz": "because", "bc": "because", "bcs": "because",
    "bcz": "because", "coz": "because", "cos": "because",
    "w": "with", "wo": "without", "w/o": "without",
    "abt": "about", "bout": "about",
    "thru": "through", "tru": "true",
    "b4": "before", "2day": "today", "2moro": "tomorrow",
    "2nite": "tonight", "l8r": "later", "l8": "late",
    "ppl": "people", "peeps": "people",
    "bf": "boyfriend", "gf": "girlfriend", "bff": "best friend forever",
    "bsf": "best friend", "bestie": "best friend",
    "fam": "family", "bro": "brother", "sis": "sister",
    "bruh": "bro", "bruv": "bro",
    "gonna": "going to", "gon": "going to", "gna": "going to",
    "wanna": "want to", "wan": "want to",
    "gotta": "got to", "gta": "got to",
    "kinda": "kind of", "sorta": "sort of",
    "tryna": "trying to", "trna": "trying to",
    "finna": "fixing to", "boutta": "about to", "bout to": "about to",
    "shoulda": "should have", "woulda": "would have", "coulda": "could have",
    "mighta": "might have", "musta": "must have",
    "gimme": "give me", "gotcha": "got you",
    "dunno": "dont know", "donno": "dont know",
    "yall": "you all", "y'all": "you all",
    "em": "them", "im": "i am", "imma": "i am going to",
    "ur": "your", "ure": "you are", "youre": "you are",
    "theyre": "they are", "thats": "that is", "whats": "what is",
    "hows": "how is", "wheres": "where is", "whos": "who is",
    "dont": "do not", "doesnt": "does not", "didnt": "did not",
    "cant": "cannot", "wont": "will not", "wouldnt": "would not",
    "couldnt": "could not", "shouldnt": "should not",
    "isnt": "is not", "arent": "are not", "wasnt": "was not",
    "werent": "were not", "hasnt": "has not", "havent": "have not",
    "hadnt": "had not", "aint": "is not",
    "yea": "yeah", "yeh": "yeah", "yuh": "yeah", "yep": "yes",
    "nah": "no", "nope": "no", "na": "no",
    "ye": "yes", "yah": "yes", "yas": "yes", "yass": "yes",
    "k": "okay", "kk": "okay", "okk": "okay", "okie": "okay",
    "mk": "okay", "mhm": "yes", "mhmm": "yes",
    "uh": "uh", "uhh": "uh", "um": "um", "umm": "um",
    "hm": "hmm", "hmm": "hmm", "hmmm": "hmm",
    "eh": "eh", "meh": "meh", "bleh": "bleh",
    "plz": "please", "pls": "please", "plss": "please",
    "thx": "thanks", "thnx": "thanks", "ty": "thank you",
    "tysm": "thank you so much", "tyvm": "thank you very much",
    "yw": "you are welcome", "np": "no problem",
    "sry": "sorry", "srry": "sorry", "soz": "sorry", "mb": "my bad",
    "jus": "just", "js": "just", "jst": "just",
    "rly": "really", "rlly": "really", "relly": "really",
    "srsly": "seriously", "srs": "serious",
    "v": "very", "vry": "very", "vv": "very very",
    "p": "pretty", "prty": "pretty",
    "lil": "little", "sm": "some", "alot": "a lot",
    "tmi": "too much information", "tldr": "too long didnt read",
    "fyi": "for your information", "ftr": "for the record",
    "icymi": "in case you missed it",
    "ftw": "for the win", "ftl": "for the loss",
    "goat": "greatest of all time", "goated": "greatest of all time",
    "sus": "suspicious", "sussy": "suspicious",
    "lit": "exciting", "fire": "amazing", "bussin": "amazing",
    "mid": "mediocre", "cap": "lie", "nocap": "no lie",
    "bet": "okay", "aight": "alright", "ight": "alright",
    "yeet": "throw", "sheesh": "wow", "oof": "ouch",
    "periodt": "period", "slay": "amazing", "ate": "did well",
    "stan": "support", "vibe": "feeling", "vibes": "feelings",
    "mood": "relatable", "valid": "acceptable", "based": "good",
    "cringe": "embarrassing", "simp": "overly devoted",
    "ghosted": "ignored", "ratio": "outvoted",
}

# ======================================================
# KEYBOARD PROXIMITY (for smart typo detection)
# ======================================================

KEYBOARD_NEIGHBORS = {
    'q': ['w', 'a', 's'],
    'w': ['q', 'e', 'a', 's', 'd'],
    'e': ['w', 'r', 's', 'd', 'f'],
    'r': ['e', 't', 'd', 'f', 'g'],
    't': ['r', 'y', 'f', 'g', 'h'],
    'y': ['t', 'u', 'g', 'h', 'j'],
    'u': ['y', 'i', 'h', 'j', 'k'],
    'i': ['u', 'o', 'j', 'k', 'l'],
    'o': ['i', 'p', 'k', 'l'],
    'p': ['o', 'l'],
    'a': ['q', 'w', 's', 'z', 'x'],
    's': ['q', 'w', 'e', 'a', 'd', 'z', 'x', 'c'],
    'd': ['w', 'e', 'r', 's', 'f', 'x', 'c', 'v'],
    'f': ['e', 'r', 't', 'd', 'g', 'c', 'v', 'b'],
    'g': ['r', 't', 'y', 'f', 'h', 'v', 'b', 'n'],
    'h': ['t', 'y', 'u', 'g', 'j', 'b', 'n', 'm'],
    'j': ['y', 'u', 'i', 'h', 'k', 'n', 'm'],
    'k': ['u', 'i', 'o', 'j', 'l', 'm'],
    'l': ['i', 'o', 'p', 'k'],
    'z': ['a', 's', 'x'],
    'x': ['z', 's', 'd', 'c'],
    'c': ['x', 'd', 'f', 'v'],
    'v': ['c', 'f', 'g', 'b'],
    'b': ['v', 'g', 'h', 'n'],
    'n': ['b', 'h', 'j', 'm'],
    'm': ['n', 'j', 'k'],
}

# Important emotion words to fuzzy match
EMOTION_VOCABULARY = {
    "pain", "hurt", "sad", "angry", "mad", "hate", "tired", "exhausted",
    "stressed", "depressed", "anxious", "lonely", "alone", "frustrated",
    "annoyed", "annoying", "overwhelmed", "terrible", "horrible", "miserable",
    "heartbroken", "crying", "cry", "hopeless", "worthless", "useless",
    "scared", "worried", "nervous", "happy", "excited", "love", "good",
    "great", "amazing", "awesome", "fuck", "shit", "bitch", "ass", "damn",
    "hell", "crap", "ugh", "suck", "awful", "broken", "empty", "numb",
    "work", "job", "boss", "friend", "relationship", "family"
}


def similarity_ratio(word1: str, word2: str) -> float:
    """Calculate similarity between two words using SequenceMatcher."""
    return SequenceMatcher(None, word1.lower(), word2.lower()).ratio()


def is_keyboard_typo(char1: str, char2: str) -> bool:
    """Check if two characters are keyboard neighbors (likely typo)."""
    char1, char2 = char1.lower(), char2.lower()
    if char1 in KEYBOARD_NEIGHBORS:
        return char2 in KEYBOARD_NEIGHBORS[char1]
    return False


def find_best_match(word: str, vocabulary: set, threshold: float = 0.7) -> str:
    """Find the best matching word from vocabulary if similarity > threshold."""
    word_lower = word.lower()

    # Skip if word is too short
    if len(word_lower) < 3:
        return word

    best_match = None
    best_score = 0

    for vocab_word in vocabulary:
        # Quick length check - skip if lengths differ too much
        if abs(len(word_lower) - len(vocab_word)) > 3:
            continue

        score = similarity_ratio(word_lower, vocab_word)
        if score > best_score and score >= threshold:
            best_score = score
            best_match = vocab_word

    return best_match if best_match else word


def correct_typo(word: str) -> str:
    """
    Correct a single word typo.
    1. First check direct mapping
    2. Then try fuzzy matching with emotion vocabulary
    """
    word_lower = word.lower()

    # Direct mapping lookup
    if word_lower in TYPO_CORRECTIONS:
        return TYPO_CORRECTIONS[word_lower]

    # Fuzzy match for emotion words (only if word is 4+ chars)
    if len(word_lower) >= 4:
        match = find_best_match(word_lower, EMOTION_VOCABULARY, threshold=0.75)
        if match != word_lower:
            return match

    return word


def fix_typos(text: str) -> str:
    """
    Fix typos in the entire text.
    Returns corrected text.
    """
    if not isinstance(text, str):
        return ""

    words = text.split()
    corrected = []

    for word in words:
        # Preserve punctuation
        prefix = ""
        suffix = ""

        # Extract leading punctuation
        while word and not word[0].isalnum():
            prefix += word[0]
            word = word[1:]

        # Extract trailing punctuation
        while word and not word[-1].isalnum():
            suffix = word[-1] + suffix
            word = word[:-1]

        if word:
            corrected_word = correct_typo(word)
            corrected.append(prefix + corrected_word + suffix)
        else:
            corrected.append(prefix + suffix)

    return " ".join(corrected)


def fix_repeated_chars(text: str) -> str:
    """
    Reduce excessive character repetition.
    E.g., "soooooo" -> "sooo", "painnnnn" -> "painn"
    Keeps max 3 repeated chars for expression, 2 for normal words.
    """
    # For expressive words (ugh, omg, etc.) keep up to 3
    text = re.sub(r'(.)\1{3,}', r'\1\1\1', text)
    return text


def normalize_text_with_typo_fix(text: str) -> str:
    """
    Full text normalization with typo fixing.
    1. Fix repeated characters
    2. Fix known typos
    """
    if not isinstance(text, str):
        return ""

    text = text.lower()
    text = fix_repeated_chars(text)
    text = fix_typos(text)

    return text
