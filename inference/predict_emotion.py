import re
import joblib
from scipy.sparse import hstack
from nltk.stem import WordNetLemmatizer
from src.preprocessing.preprocess_text import preprocess_text
from src.preprocessing.typo_handler import normalize_text_with_typo_fix

# ======================================================
# INIT
# ======================================================

lemmatizer = WordNetLemmatizer()

model = joblib.load("models/emotion_model.pkl")
word_vec = joblib.load("models/tfidf_word.pkl")
char_vec = joblib.load("models/tfidf_char.pkl")

# ======================================================
# WORD BANKS (BASE WORDS ONLY)
# ======================================================

POSITIVE = {
    "happy", "excited", "proud", "relieved", "grateful",
    "love", "loved", "loving",
    "good", "great", "amazing", "awesome",
    "finally", "win", "enjoy", "care", "miss",

    # ✅ appreciation / praise
    "appreciation", "appreciated",
    "praised", "praise",
    "recognition", "recognized",
    "acknowledged",
    "compliment", "complimented",
    "thank", "thanks",

    # ✅ joy / celebration
    "joy", "joyful", "celebrate", "celebration",
    "cheerful", "delighted", "thrilled", "ecstatic",
    "blessed", "fortunate", "lucky",

    # ✅ success / achievement
    "success", "successful", "accomplish", "accomplished",
    "achieve", "achieved", "victory", "triumph",
    "progress", "improved", "breakthrough",

    # ✅ contentment / peace
    "content", "satisfied", "peaceful", "calm",
    "serene", "relaxed", "comfortable", "cozy",
    "safe", "secure", "stable",

    # ✅ optimism / hope
    "hopeful", "optimistic", "confident", "encouraged",
    "inspired", "motivated", "eager", "enthusiastic",
    "positive", "bright", "promising",

    # ✅ affection / connection
    "adore", "cherish", "treasure", "fond",
    "warm", "kind", "gentle", "sweet",
    "support", "supported", "hug", "smile",

    # ✅ surprise / excitement
    "surprised", "surprise", "shocking", "shocked",
    "unexpected", "unbelievable", "incredible", "insane",
    "omg", "wow", "woah", "whoa", "yay", "yess", "yesss",
    "cant believe", "no way", "what the",
    "hyped", "pumped", "stoked", "fired up", "buzzing",

    # ✅ excitement / energy
    "exciting", "excitement", "exhilarating", "electric",
    "alive", "energized", "vibrant", "glowing",
    "soaring", "flying", "on top of the world",
    "best day", "best feeling", "so happy", "so excited",

    # ✅ fun / playful
    "fun", "funny", "hilarious", "laughing", "lol", "lmao",
    "haha", "hahaha", "dying", "dead", "im crying",
    "adorable", "cute", "wholesome", "precious",

    # ✅ excitement expressions / slang
    "yayyy", "yayyyy", "yasss", "yassss", "yasssss",
    "woohoo", "woohooo", "wooohooo", "ayeee", "ayyyy",
    "lessgo", "lets go", "lets goo", "lets gooo",
    "slay", "slayed", "slaying", "ate", "periodt", "period",
    "iconic", "queen", "king", "boss", "legend", "goat",
    "fire", "lit", "vibes", "vibe", "mood", "based",
    "sheesh", "sheeesh", "sheeeesh", "bussin", "bussing",
    "valid", "lowkey", "highkey", "fr", "frfr", "no cap",
    "ong", "on god", "swear", "bet", "facts", "real",
    "dope", "sick", "rad", "epic", "legendary", "goated",
    "W", "dub", "massive W", "huge W", "big W",

    # ✅ excited curse words (positive context)
    "holy shit", "holy crap", "holy fuck",
    "no fucking way", "fucking amazing", "fucking awesome",
    "so fucking good", "so fucking happy", "fucking finally",
    "damn thats good", "damn thats amazing",
    "shit thats awesome", "thats the shit",
    "hell yeah", "hell yes", "fuck yeah", "fuck yes",
    "badass", "kickass", "damn right",

    # ✅ work / office - positive
    "promotion", "promoted", "raise", "bonus", "increment",
    "hired", "got the job", "job offer", "offer letter",
    "interview went well", "cleared interview", "got selected",
    "appreciation mail", "good feedback", "positive review",
    "appraisal", "performance bonus", "spot award",
    "team lead", "manager", "senior", "lead role",
    "project success", "delivered", "shipped", "launched",
    "client happy", "client appreciated", "deal closed",
    "onsite", "opportunity", "new role", "dream job",
    "wfh", "work from home", "remote", "flexible",
    "good team", "supportive manager", "great colleagues"
}

# ======================================================
# CURSE WORDS THAT CAN BE POSITIVE OR NEGATIVE
# (context-dependent - not in ANGER by default)
# ======================================================

CONTEXT_CURSES = {
    "fuck", "fucking", "fucked", "fucks", "fck", "fuk", "fuq",
    "shit", "shitty", "shits", "sht", "shyt",
    "damn", "damnn", "damnnn", "dammit", "damnit",
    "hell", "crap", "crappy", "ass", "arse",
    "bitch", "bitches", "bitchin", "biatch", "bytch",
    "wtf", "wth", "omfg", "lmfao", "stfu", "gtfo", "ffs"
}

# phrases that make curses POSITIVE
POSITIVE_CURSE_CONTEXT = {
    "holy shit", "holy crap", "holy fuck", "holy hell",
    "no fucking way", "fucking amazing", "fucking awesome",
    "fucking incredible", "fucking beautiful", "fucking love",
    "so fucking good", "so fucking happy", "so fucking excited",
    "fucking finally", "fucking proud", "fucking great",
    "damn thats good", "damn thats amazing", "damn thats awesome",
    "damn good", "damn proud", "damn happy",
    "shit thats awesome", "thats the shit", "good shit",
    "hell yeah", "hell yes", "fuck yeah", "fuck yes",
    "badass", "kickass", "damn right", "fucking right",
    "im so fucking happy", "im so fucking proud",
    "this is fucking amazing", "youre fucking awesome",
    "fucking killed it", "fucking nailed it", "fucking crushed it",
    # more positive curse contexts
    "shit worked", "shit actually worked", "this shit worked",
    "it worked", "finally worked", "omg it worked",
    "happy af", "excited af", "hyped af", "pumped af",
    "so happy", "im so happy", "im happy", "so excited",
    "yay", "yayy", "yayyy", "yesss", "yessss",
    "lets go", "lets goo", "lets gooo", "lessgo",
    "hell of a", "damn it worked", "shit yes",
    "fucking works", "it fucking works", "shit it works"
}

# words that indicate POSITIVE emotion (override distress if present with these)
POSITIVE_INDICATORS = {
    "happy", "excited", "yay", "yayy", "yayyy", "yess", "yesss",
    "amazing", "awesome", "great", "good", "love", "loved",
    "finally", "worked", "works", "success", "won", "win",
    "proud", "glad", "thrilled", "pumped", "hyped", "stoked"
}

SAD = {
    "sad", "down", "empty", "lonely", "numb",
    "hopeless", "cry", "hurt", "heartbreak",
    "hate", "disappointment", "broke",
    "humiliated", "insult", "painful",

    # 😢 grief / loss
    "grief", "grieving", "mourn", "mourning", "loss",
    "lost", "gone", "missing", "widow", "orphan",

    # 😢 despair / hopelessness
    "despair", "desperate", "worthless", "useless",
    "pointless", "meaningless", "hollow", "void",
    "abandoned", "rejected", "forgotten", "invisible",

    # 😢 tears / crying
    "crying", "sobbing", "weeping", "tears", "teary",
    "bawling", "wailing",

    # 😢 heartache / emotional pain
    "heartbroken", "shattered", "crushed", "devastated",
    "destroyed", "ruined", "broken", "torn",
    "ache", "aching", "sorrow", "sorrowful", "miserable",
    "pain", "painful", "agony", "suffering", "torment",
    "anguish", "distress", "trauma", "traumatic", "scarred",
    "wounded", "bleeding", "raw", "numb", "paralyzed",

    # 😢 loneliness / isolation
    "alone", "isolated", "disconnected", "unwanted",
    "unloved", "neglected", "ignored", "left out",

    # 😢 work / office - sad
    "fired", "terminated", "laid off", "layoff", "let go",
    "lost my job", "jobless", "unemployed", "no job",
    "rejected", "didnt get the job", "failed interview",
    "passed over", "not selected", "didnt make it",
    "demoted", "demotion", "pay cut", "salary cut",
    "no appraisal", "bad review", "negative feedback",
    "pip", "performance improvement", "warning letter",
    "left out of project", "removed from team",
    "no recognition", "unappreciated", "taken for granted","quit","quitting","overwhelmed"
}

DISTRESS = {
    "tired", "exhaust", "burn", "overwhelm",
    "drain", "stress", "stressed", "stressing", "stressful",
    "anxious", "panic", "pressure", "frustrate", "stuck",
    "done", "overworked",

    # 😰 anxiety / worry
    "worry", "worried", "worrying", "nervous", "tense",
    "uneasy", "restless", "jittery", "shaky", "trembling",
    "dread", "dreading", "terrified", "scared", "fear",

    # 😰 burnout / exhaustion
    "burnout", "burned", "exhausted", "depleted", "spent",
    "wiped", "fatigued", "weary", "worn", "running on empty",

    # 😰 overwhelm / pressure
    "overwhelmed", "swamped", "drowning", "suffocating",
    "crushed", "buried", "overloaded", "stretched",
    "breaking", "cracking", "snapping",

    # 😰 mental struggle
    "struggling", "suffering", "spiraling", "falling apart",
    "losing it", "going crazy", "mental breakdown",
    "cant think", "cant focus", "cant breathe",
    "shutting down", "giving up", "checking out",

    # 😰 need rest / break
    "need rest", "need a break", "need sleep", "need a nap",
    "wanna rest", "want to rest", "gotta rest",
    "so tired", "too tired", "dead tired", "exhausted af",
    "need time", "need space", "need to recharge",
    "running on fumes", "barely functioning", "cant keep going",

    # 🤒 sick / unwell / not feeling good
    "sick", "ill", "unwell", "not feeling well", "not feeling good",
    "feeling sick", "feel sick", "feeling unwell", "feel unwell",
    "under the weather", "fever", "cold", "flu", "headache",
    "migraine", "nauseous", "dizzy", "weak", "faint",
    "body aches", "stomach hurts", "head hurts", "cramps",
    "throwing up", "vomit", "puke", "cant eat", "no appetite",
    "feeling terrible", "feeling awful", "health issues",

    # 😰 work / office - distress
    "workload", "too much work", "overloaded", "swamped with work",
    "deadlines", "deadline pressure", "tight deadline",
    "overtime", "working late", "no work life balance",
    "toxic workplace", "toxic boss", "toxic manager",
    "micromanaged", "micromanaging", "no autonomy",
    "job stress", "work stress", "office politics",
    "meetings all day", "back to back meetings",
    "unrealistic expectations", "impossible targets",
    "underpaid", "not paid enough", "deserve more",
    "no growth", "stagnant", "stuck in same role",
    "hate my job", "hate going to work", "dread mondays",
    "sunday scaries", "monday blues"
}

ANGER = {
    "angry", "mad", "furious",
    "hate", "hated", "hating",
    "resent", "annoy", "irritate",
    "cant stand",

    # 😡 rage / fury
    "rage", "raging", "livid", "seething", "fuming",
    "enraged", "outraged", "infuriated", "pissed",
    "boiling", "explosive", "violent",

    # 😡 frustration / irritation
    "frustrated", "annoyed", "irritated", "aggravated",
    "agitated", "bothered", "fed up", "sick of",
    "had enough", "over it",

    # 😡 resentment / bitterness
    "resentful", "bitter", "vengeful", "spiteful",
    "jealous", "envious", "betrayed", "backstabbed",

    # 😡 insults / swearing (NEGATIVE context curses)
    "stupid", "dumb", "moron", "jerk", "bastard",
    "dick", "trash", "garbage", "pathetic",
    "idiot", "asshole", "asswipe", "dumbass", "jackass",
    "dipshit", "shithead", "fuckhead", "dickhead",
    "motherfucker", "mf", "pos", "piece of shit",
    "scumbag", "loser", "clown", "joke", "fraud",
    "liar", "fake", "phony", "hypocrite",
    "prick", "douche", "douchebag", "tool", "wanker",
    "twat", "cunt", "whore", "slut", "hoe",
    "retard", "retarded", "imbecile", "dimwit",
    # more ass variations
    "smartass", "fatass", "lazyass", "badass", "hardass",
    "kissass", "kickass", "deadass", "weakass", "lameass",
    "dirtbag", "scum", "creep", "perv", "pervert",
    "numskull", "bonehead", "blockhead", "airhead", "meathead",
    "butthead", "poophead", "crackhead", "pothead",
    # pain / frustration words
    "annoying", "irritating", "infuriating", "maddening",
    "ridiculous", "absurd", "insane", "crazy", "nuts",
    "bullcrap", "horseshit", "dogshit", "apeshit",

    # 😡 angry curse phrases
    "fuck you", "fuck off", "fuck this", "fuck that",
    "fuck it", "fucked up", "fucking hate", "fucking stupid",
    "fucking annoying", "fucking tired", "fucking done",
    "fucking sick of", "fucking ridiculous", "fucking bullshit",
    "go to hell", "screw you", "screw this", "screw that",
    "piss off", "pissed off", "piss me off",
    "shut up", "shut the fuck up", "stfu",
    "bullshit", "bs", "this is bs", "such bs",
    "what the fuck", "what the hell", "wtf is this",
    "are you kidding", "are you serious", "seriously",
    "i cant with", "im done with", "im so done",

    # 😡 hostility / aggression
    "hostile", "aggressive", "vicious", "cruel",
    "nasty", "toxic", "disgusted", "repulsed",
    "kill", "destroy", "punch", "hit", "fight",
    "strangle", "murder", "beat", "slap", "kick",

    # 😡 work / office - anger
    "unfair", "favoritism", "biased", "discrimination",
    "harassment", "harassed", "bullied", "bully",
    "blame", "blamed", "scapegoat", "thrown under bus",
    "credit stolen", "took my credit", "stole my idea",
    "gaslighting", "manipulated", "used",
    "unprofessional", "disrespectful", "rude boss",
    "yelled", "yelling", "yelled at", "screamed", "screaming", "screamed at", "humiliated at work",
    "toxic coworker", "backstabbing colleague",
    "passed over for promotion", "deserved that promotion",
    "overworked underpaid", "exploited", "taken advantage of"
}

# phrases that MUST override ML
EXHAUSTION_PHRASES = {
    # 🔴 general exhaustion
    "tired of everything",
    "so tired of everything",
    "done with everything",
    "cant deal anymore",
    "cant handle this",
    "fed up with everything",
    "i hate everything",
    "i cant anymore",
    "nothing feels right",
    "everything feels wrong",
    "i feel stuck",
    "i feel trapped",
    "im done",
    "im exhausted",
    "im so tired",

    # 🔴 giving up / hopelessness
    "i give up",
    "whats the point",
    "why bother",
    "why even try",
    "nothing matters",
    "nobody cares",
    "no one cares",
    "i dont matter",
    "i dont care anymore",
    "i stopped caring",
    "lost all hope",
    "theres no hope",

    # 🔴 breaking point
    "i cant do this",
    "i cant take it",
    "i cant take this anymore",
    "im breaking down",
    "im falling apart",
    "im losing my mind",
    "im going insane",
    "i want to scream",
    "i want to cry",
    "i want to disappear",
    "i want it to stop",
    "make it stop",

    # 🔴 emotional overwhelm
    "too much to handle",
    "everything is too much",
    "i cant breathe",
    "i feel suffocated",
    "drowning in",
    "buried under",
    "crushed by",
    "cant escape",
    "no way out",

    # 🔴 life struggles
    "life is hard",
    "life sucks",
    "everything sucks",
    "hate my life",
    "hate myself",
    "sick of this",
    "sick of life",
    "sick of everything",
    "tired of life",
    "tired of trying",
    "tired of fighting",
    "tired of pretending",

    # 🔴 loneliness / isolation
    "nobody understands",
    "no one understands",
    "i feel alone",
    "i feel so alone",
    "i have no one",
    "im all alone",
    "nobody loves me",
    "no one loves me",
    "everyone left",
    "everyone leaves",

    # 🔴 worthlessness
    "im worthless",
    "im useless",
    "im a failure",
    "im not good enough",
    "ill never be good enough",
    "i hate myself",
    "i disgust myself",
    "whats wrong with me",
    "im so stupid",
    "im such an idiot",

    # 🔴 work / office - exhaustion phrases
    "i cant do this job anymore",
    "i want to quit",
    "want to quit",
    "wanna quit",
    "thinking of quitting",
    "thinking about quitting",
    "considering quitting",
    "might quit",
    "gonna quit",
    "going to quit",
    "planning to quit",
    "ready to quit",
    "about to quit",
    "thinking of resigning",
    "thinking about resigning",
    "considering resigning",
    "cant take this job",
    "work is killing me",
    "this job is killing me",
    "burnt out from work",
    "exhausted from work",
    "dreading work tomorrow",
    "cant face work",
    "calling in sick",
    "need a break from work",
    "work is destroying me",
    "office is suffocating",
    "cant deal with my boss",
    "cant deal with coworkers",
    "want to walk out",
    "about to snap at work",
    "losing it at work",

    # 🔴 can't continue / giving up
    "cant continue",
    "can not continue",
    "unable to continue",
    "not able to continue",
    "wont be able to continue",
    "dont think i can continue",
    "idk if i can continue",
    "idk if i would be able to continue",
    "dont know if i can continue",
    "not sure if i can continue",
    "not sure if would be able to",
    "not sure if i would be able to",
    "im not sure if i can",
    "im not sure if would be able",
    "cant keep doing this",
    "cant keep going",
    "cant go on",
    "cant do this anymore",
    "wont be able to complete",
    "not able to complete",
    "cant complete",
    "unable to complete",

    # 🔴 stressed / stress related
    "so stressed",
    "im so stressed",
    "im stressed",
    "really stressed",
    "super stressed",
    "extremely stressed",
    "stressed out",
    "stressed af",
    "too stressed",
    "way too stressed",
    "stressed about",
    "stressing out",
    "stressing me out",
    "this is stressing me",
    "everything is stressing me",

    # 🔴 not letting me rest / no peace
    "not letting me rest",
    "wont let me rest",
    "not letting me sleep",
    "wont let me sleep",
    "not giving me space",
    "not leaving me alone",
    "wont leave me alone",
    "cant get any peace",
    "cant get any rest",
    "no peace",
    "always bothering me",
    "keeps bothering me",
    "always nagging",
    "keeps nagging",
    "breathing down my neck",
    "on my case",
    "cant catch a break",
    "never get a break",
    "always something",
    "one thing after another",
    "ppl wont let me",
    "they wont let me",
    "cant even rest",
    "cant even relax",
    "no time for myself",

    # 🔴 mental health crisis
    "mental health is crashing",
    "my mental health is crashing",
    "mental health crashing",
    "mental health is declining",
    "mental health declining",
    "mental health is bad",
    "mental health is terrible",
    "mental health is awful",
    "mental health is shit",
    "mental health is trash",
    "mental health is gone",
    "mental health is falling apart",
    "losing my mental health",
    "my mental health is gone",
    "mentally breaking down",
    "emotionally breaking down",
    "having a breakdown",
    "having a mental breakdown",
    "on the verge of breakdown",
    "about to break down",
    "falling apart inside",
    "everything is falling apart",
    "my life is falling apart",
    "going crazy",
    "im going crazy",
    "going insane",
    "cant think straight",
    "head is a mess",
    "my head is a mess",
    "mind is a mess",
    "cant cope",
    "cant handle this",
    "cant handle it",
    "cant deal with this",
    "cant take it anymore",
    "had enough",
    "ive had enough",
    "spiraling",
    "im spiraling",
    "in a dark place",
    "im in a dark place",
    "at my lowest",
    "im at my lowest",
    "hit rock bottom",
    "rock bottom",
    "at rock bottom",
    "mentally exhausted",
    "emotionally exhausted",
    "mentally drained",
    "emotionally drained",
    "mentally done",
    "emotionally done",
    "brain is fried",
    "my brain is fried",
    "its all too much",
    "overwhelmed by everything",
    "drowning in everything",
    "suffocating",
    "im suffocating",
    "feel like im drowning",
    "no point anymore",
    "dont see the point",
    "losing hope",
    "lost all hope",
    "no hope left"
}

# ======================================================
# ABBREVIATIONS / SHORT FORMS
# ======================================================

ABBREVIATIONS = {
    # common text abbreviations
    "u": "you",
    "ur": "your",
    "ure": "you are",
    "r": "are",
    "n": "and",
    "b": "be",
    "c": "see",
    "k": "okay",
    "y": "why",
    "w": "with",
    "2": "to",
    "4": "for",
    "b4": "before",

    # because variations
    "bc": "because",
    "bcs": "because",
    "bcz": "because",
    "bcse": "because",
    "bcoz": "because",
    "cuz": "because",
    "coz": "because",
    "cos": "because",
    "cause": "because",

    # you know / i know
    "uk": "you know",
    "yk": "you know",
    "ik": "i know",
    "ikr": "i know right",

    # i don't know variations
    "idk": "i dont know",
    "idek": "i dont even know",
    "ion": "i dont",
    "iono": "i dont know",
    "dunno": "dont know",
    "dk": "dont know",

    # right now / right
    "rn": "right now",
    "rly": "really",
    "rlly": "really",
    "srsly": "seriously",
    "srsy": "seriously",

    # to be honest / honest
    "tbh": "to be honest",
    "tbf": "to be fair",
    "ngl": "not gonna lie",
    "frl": "for real",
    "frfr": "for real for real",
    "fr": "for real",
    "lowkey": "low key",
    "highkey": "high key",

    # i'm / i am
    "im": "i am",
    "iam": "i am",
    "ima": "i am going to",
    "imma": "i am going to",
    "ill": "i will",
    "iv": "i have",
    "ive": "i have",
    "id": "i would",

    # other pronouns
    "hes": "he is",
    "shes": "she is",
    "theyre": "they are",
    "thats": "that is",
    "whats": "what is",
    "whos": "who is",
    "hows": "how is",
    "wheres": "where is",
    "theres": "there is",
    "its": "it is",
    "isnt": "is not",
    "arent": "are not",
    "wasnt": "was not",
    "werent": "were not",
    "dont": "do not",
    "doesnt": "does not",
    "didnt": "did not",
    "wont": "will not",
    "wouldnt": "would not",
    "couldnt": "could not",
    "shouldnt": "should not",
    "cant": "cannot",
    "hadnt": "had not",
    "hasnt": "has not",
    "havent": "have not",

    # common words
    "abt": "about",
    "bout": "about",
    "w/": "with",
    "w/o": "without",
    "wo": "without",
    "wout": "without",
    "thru": "through",
    "tho": "though",
    "altho": "although",
    "btwn": "between",
    "prob": "probably",
    "probs": "probably",
    "prolly": "probably",
    "def": "definitely",
    "defo": "definitely",
    "defs": "definitely",
    "obv": "obviously",
    "obvs": "obviously",
    "obvi": "obviously",
    "esp": "especially",
    "v": "very",
    "rn": "right now",
    "atm": "at the moment",
    "asap": "as soon as possible",

    # feelings / emotions
    "luv": "love",
    "luving": "loving",
    "luvd": "loved",
    "h8": "hate",
    "h8ing": "hating",
    "h8d": "hated",

    # actions
    "gonna": "going to",
    "gon": "going to",
    "wanna": "want to",
    "gotta": "got to",
    "kinda": "kind of",
    "sorta": "sort of",
    "tryna": "trying to",
    "needa": "need to",
    "shoulda": "should have",
    "woulda": "would have",
    "coulda": "could have",
    "mighta": "might have",
    "musta": "must have",
    "oughta": "ought to",
    "hafta": "have to",
    "hasta": "has to",
    "useta": "used to",
    "supposta": "supposed to",
    "sposeta": "supposed to",
    "lemme": "let me",
    "gimme": "give me",
    "gotcha": "got you",
    "getcha": "get you",

    # greetings / responses
    "wassup": "what is up",
    "sup": "what is up",
    "wazzup": "what is up",
    "waddup": "what is up",
    "heya": "hey",
    "hiya": "hi",
    "yo": "hey",
    "hai": "hi",
    "henlo": "hello",
    "hihi": "hi",
    "hewwo": "hello",
    "hewlo": "hello",
    "ty": "thank you",
    "tysm": "thank you so much",
    "tyvm": "thank you very much",
    "thx": "thanks",
    "thnx": "thanks",
    "thanku": "thank you",
    "tku": "thank you",
    "yw": "you are welcome",
    "np": "no problem",
    "nw": "no worries",
    "sry": "sorry",
    "srry": "sorry",
    "soz": "sorry",
    "mb": "my bad",
    "oops": "oops",
    "oopsie": "oops",
    "pls": "please",
    "plz": "please",
    "plss": "please",
    "plzz": "please",

    # agreement / disagreement
    "yh": "yeah",
    "yea": "yeah",
    "yup": "yes",
    "yep": "yes",
    "ya": "yes",
    "yass": "yes",
    "nah": "no",
    "nope": "no",
    "nop": "no",
    "na": "no",
    "ofc": "of course",
    "obv": "obviously",
    "ig": "i guess",
    "igs": "i guess so",

    # questions
    "wyd": "what are you doing",
    "wya": "where are you at",
    "wru": "where are you",
    "hru": "how are you",
    "hbu": "how about you",
    "wbu": "what about you",
    "whyd": "why did",
    "howcome": "how come",

    # time related
    "tmrw": "tomorrow",
    "tmr": "tomorrow",
    "2moro": "tomorrow",
    "2day": "today",
    "2nite": "tonight",
    "yday": "yesterday",
    "ystrdy": "yesterday",
    "l8r": "later",
    "l8": "late",
    "2nite": "tonight",

    # people
    "bf": "boyfriend",
    "gf": "girlfriend",
    "bff": "best friend forever",
    "bsf": "best friend",
    "bestie": "best friend",
    "fam": "family",
    "bro": "brother",
    "sis": "sister",
    "bruh": "bro",
    "fren": "friend",
    "frens": "friends",
    "sm1": "someone",
    "sum1": "someone",
    "any1": "anyone",
    "no1": "no one",
    "evry1": "everyone",
    "every1": "everyone",

    # internet slang
    "lmk": "let me know",
    "hmu": "hit me up",
    "ttyl": "talk to you later",
    "ttys": "talk to you soon",
    "brb": "be right back",
    "bbl": "be back later",
    "gtg": "got to go",
    "g2g": "got to go",
    "omw": "on my way",
    "otw": "on the way",
    "fyi": "for your information",
    "btw": "by the way",
    "imo": "in my opinion",
    "imho": "in my humble opinion",
    "smh": "shaking my head",
    "fml": "fuck my life",
    "tmi": "too much information",
    "tldr": "too long didnt read",
    "afaik": "as far as i know",
    "afk": "away from keyboard",
    "irl": "in real life",
    "dm": "direct message",
    "pm": "private message",
    "rt": "retweet",
    "jk": "just kidding",
    "jks": "just kidding",
    "jp": "just playing",

    # emotions / reactions
    "lol": "laughing out loud",
    "lmao": "laughing my ass off",
    "lmfao": "laughing my fucking ass off",
    "rofl": "rolling on floor laughing",
    "roflmao": "rolling on floor laughing my ass off",
    "omg": "oh my god",
    "omfg": "oh my fucking god",
    "wtf": "what the fuck",
    "wth": "what the hell",
    "tf": "the fuck",
    "af": "as fuck",
    "asf": "as fuck",
    "asl": "as hell",
    "smth": "something",
    "sth": "something",
    "nth": "nothing",
    "anth": "anything",
    "everth": "everything",

    # work / professional
    "mgr": "manager",
    "hr": "human resources",
    "ceo": "chief executive officer",
    "cto": "chief technology officer",
    "cfo": "chief financial officer",
    "asst": "assistant",
    "dept": "department",
    "govt": "government",
    "proj": "project",
    "mtg": "meeting",
    "pls": "please",
    "rgds": "regards",
    "fwd": "forward",
    "re": "regarding",
    "cc": "carbon copy",
    "bcc": "blind carbon copy",
    "etc": "et cetera",
    "info": "information",
    "doc": "document",
    "docs": "documents",
    "msg": "message",
    "msgs": "messages",
    "appt": "appointment",
    "est": "estimated",
    "approx": "approximately",
    "qty": "quantity",
    "yr": "year",
    "yrs": "years",
    "mo": "month",
    "mos": "months",
    "wk": "week",
    "wks": "weeks",
    "hr": "hour",
    "hrs": "hours",
    "min": "minute",
    "mins": "minutes",
    "sec": "second",
    "secs": "seconds",

    # misc common
    "ppl": "people",
    "peeps": "people",
    "txt": "text",
    "pic": "picture",
    "pics": "pictures",
    "vid": "video",
    "vids": "videos",
    "diff": "different",
    "diff": "difference",
    "prb": "problem",
    "prblm": "problem",
    "cld": "could",
    "shld": "should",
    "wld": "would",
    "nvr": "never",
    "evr": "ever",
    "alrdy": "already",
    "alr": "already",
    "rdy": "ready",
    "acc": "actually",
    "actly": "actually",
    "acty": "actually",
    "jus": "just",
    "js": "just",
    "mayb": "maybe",
    "mby": "maybe",
    "tht": "that",
    "ths": "this",
    "wht": "what",
    "hw": "how",
    "wen": "when",
    "wer": "where",
    "hav": "have",
    "hv": "have",
    "giv": "give",
    "gv": "give",
    "knw": "know",
    "kno": "know",
    "thnk": "think",
    "thk": "think",
    "mk": "make",
    "mke": "make",
    "tk": "take",
    "tke": "take",
    "gt": "get",
    "gt": "got",
    "gd": "good",
    "bd": "bad",
    "sm": "some",
    "smthn": "something",
    "ntn": "nothing",
    "anythn": "anything",
    "evrythn": "everything",
    "dn": "done",
    "dne": "done",
    "nd": "need",
    "wnt": "want",
    "lk": "like",
    "lyk": "like",
    "nt": "not",
    "bt": "but",
    "jst": "just",
    "stl": "still",
    "evn": "even",
    "alws": "always",
    "neva": "never",
    "nvr": "never",
    "mayb": "maybe",
    "prbly": "probably",
    "cpl": "couple",
    "fav": "favorite",
    "favs": "favorites"
}

def expand_abbreviations(text: str) -> str:
    """
    Expand common text abbreviations to their full forms.
    E.g., "idk y u r sad rn" → "i dont know why you are sad right now"
    """
    words = text.lower().split()
    expanded = []

    i = 0
    while i < len(words):
        word = words[i]

        # clean word of punctuation for matching
        word_clean = re.sub(r'[^\w]', '', word)

        # check if word is an abbreviation
        if word_clean in ABBREVIATIONS:
            # preserve any trailing punctuation
            trailing = ""
            if word != word_clean:
                trailing = word[len(word_clean):]
            expanded.append(ABBREVIATIONS[word_clean] + trailing)
        else:
            expanded.append(word)

        i += 1

    return " ".join(expanded)

# ======================================================
# HELPERS
# ======================================================

# words that are neutral even when elongated (hmmm, okayy, etc.)
NEUTRAL_ELONGATED = {
    "hm", "hmm", "hmmm", "hmmmm", "hmmmmm",
    "um", "umm", "ummm", "ummmm",
    "ok", "okay", "okayy", "okayyy", "okayyyy",
    "ah", "ahh", "ahhh", "ahhhh",
    "oh", "ohh", "ohhh", "ohhhh",
    "ee", "eee", "eeee",
    "oo", "ooo", "oooo",
    "ya", "yaa", "yaaa", "yaaaa",
    "na", "naa", "naaa", "naaaa",
    "mhm", "mhmm", "mhmmm",
    "eh", "ehh", "ehhh",
    "uh", "uhh", "uhhh",
    "mm", "mmm", "mmmm", "mmmmm",
    "aa", "aaa", "aaaa",
    "hey", "heyy", "heyyy", "heyyyy", "heyyyyy",
    "hi", "hii", "hiii", "hiiii",
    "hello", "helloo", "hellooo",
    "bye", "byee", "byeee", "byeeee",
    "yay", "yayy", "yayyy", "yayyyy",
    "yass", "yasss", "yassss", "yasssss",
    "no", "noo", "nooo", "noooo",
    "yes", "yess", "yesss", "yessss",
    "yeah", "yeahh", "yeahhh", "yeahhhh",
    "yep", "yepp", "yeppp",
    "nope", "nopee", "nopeee",
    "well", "welll", "wellll",
    "so", "soo", "sooo", "soooo",
    "too", "tooo", "toooo",
    "see", "seee", "seeee",
    "me", "mee", "meee",
    "be", "bee", "beee",
    "we", "wee", "weee",
    "please", "pleasee", "pleaseee", "pleaseeee",
    "thanks", "thankss", "thanksss",
    "thankyou", "thankyouu", "thankyouuu",
    "sorry", "sorryy", "sorryyy", "sorryyyy",
    "really", "reallyy", "reallyyy",
    "literally", "literallyy", "literallyyy",
    "actually", "actuallyy", "actuallyyy",
    "basically", "basicallyy", "basicallyyy",
    "honestly", "honestlyy", "honestlyyy",
    "like", "likee", "likeee",
    "love", "lovee", "loveee", "loveeee",
    "nice", "nicee", "niceee",
    "cool", "cooll", "coolll",
    "good", "goodd", "gooddd",
    "great", "greatt", "greattt",
    "same", "samee", "sameee",
    "true", "truee", "trueee",
    "right", "rightt", "righttt",
    "wow", "woww", "wowww", "wowwww",
    "omg", "omgg", "omggg", "omgggg",
    "lol", "loll", "lolll", "lollll",
    "haha", "hahaa", "hahaaa", "hahaha", "hahahaha",
    "hehe", "hehee", "heheee", "hehehe",
    "aww", "awww", "awwww", "awwwww",
    "ooh", "oohh", "oohhh",
    "oof", "ooff", "oofff",
    "bruh", "bruhh", "bruhhh",
    "bro", "broo", "brooo",
    "dude", "dudee", "dudeee",
    "man", "mann", "mannn",
    "girl", "girll", "girlll",
    "sis", "siss", "sisss",
    "bestie", "bestiee", "bestieee"
}

# words that indicate intensity/distress when elongated
INTENSE_WORDS = {
    # curse words
    "shit", "fuck", "damn", "hell", "crap",
    "ass", "bitch", "dick", "cunt", "arse",
    "fck", "fuk", "sht", "shyt",
    # anger
    "hate", "angry", "mad", "furious", "rage",
    "pissed", "livid", "fuming", "annoyed", "irritated",
    # sadness
    "sad", "cry", "hurt", "pain", "ache",
    "depressed", "miserable", "broken", "shattered",
    "heartbroken", "gutted", "crushed", "devastated",
    # exhaustion
    "tired", "exhaust", "stress", "frustrat",
    "drain", "burn", "overwhelm", "drained", "spent",
    # expressions
    "ugh", "arg", "grr", "argh", "gah", "ffs", "smh",
    # death/violence
    "die", "dead", "kill", "murder",
    # negative
    "sick", "awful", "terrible", "horrible",
    "worst", "bad", "suck", "trash", "garbage",
    "pathetic", "useless", "worthless", "hopeless",
    # isolation
    "alone", "lonely", "empty", "lost", "abandoned",
    # desperation
    "help", "cant", "stop", "need", "please",
    # pain variations
    "painful", "agony", "suffering", "torture", "torment",
    "misery", "distress", "anguish", "sore", "wound",
    # exclamations (can be positive OR negative - context matters)
    "god", "lord", "jesus", "christ", "omg",
    "what", "why", "how"
}

def collapse_elongated(text: str) -> str:
    """Collapse repeated characters: shiiit → shit, hmmmmm → hmm"""
    return re.sub(r'(.)\1{2,}', r'\1\1', text.lower())

def normalize(text: str):
    words = re.findall(r"[a-zA-Z']+", text.lower())
    return [lemmatizer.lemmatize(w) for w in words]

def normalize_with_collapse(text: str):
    """Normalize AND collapse elongated words for better matching"""
    collapsed = collapse_elongated(text)
    words = re.findall(r"[a-zA-Z']+", collapsed)
    return [lemmatizer.lemmatize(w) for w in words]

def has_any(tokens, vocab):
    return any(w in tokens for w in vocab)

def has_phrase(text, phrases):
    return any(p in text for p in phrases)

def has_intensity(text):
    """
    Check if text has elongated words that indicate emotional intensity.
    Only returns True for distress-related words, not neutral ones.
    """
    text_lower = text.lower()

    # find all words with 3+ repeated characters
    elongated_matches = re.findall(r'\b\w*(.)\1{2,}\w*\b', text_lower)
    if not elongated_matches:
        return False

    # get the actual elongated words by splitting and checking each word
    words = text_lower.split()
    elongated_words = [w for w in words if re.search(r'(.)\1{2,}', w)]

    for word in elongated_words:
        # skip if it's a known neutral word
        if word in NEUTRAL_ELONGATED:
            continue

        # collapse the word and check if base form is intense
        collapsed = re.sub(r'(.)\1{2,}', r'\1\1', word)
        collapsed_single = re.sub(r'(.)\1+', r'\1', word)

        # check if any intense word is in the collapsed form
        for intense in INTENSE_WORDS:
            if intense in collapsed or intense in collapsed_single:
                return True

        # if it's an elongated word not in neutral list, consider it intense
        # (catches things like "stooop", "nooooo" in distress context)
        if len(word) > 4:  # only for words with significant elongation
            return True

    return False

# ======================================================
# MAIN
# ======================================================

def analyze_long_text(text: str) -> dict:
    """
    Analyze long paragraphs/rants by breaking into sentences and
    finding the dominant emotional signals.
    Returns dict with emotion counts and key phrases found.
    """
    # Split by sentence endings and common breaks
    import re
    sentences = re.split(r'[.!?\n]+|(?:and then|but then|so then|then)', text.lower())
    sentences = [s.strip() for s in sentences if s.strip()]

    emotion_signals = {
        "positive": 0,
        "distress": 0,
        "anger": 0,
        "sad": 0,
        "exhaustion": 0
    }

    key_phrases_found = []

    for sentence in sentences:
        tokens = normalize(sentence)
        tokens_collapsed = normalize_with_collapse(sentence)

        # Check for exhaustion phrases (high priority)
        if has_phrase(sentence, EXHAUSTION_PHRASES):
            emotion_signals["exhaustion"] += 2
            key_phrases_found.append(("exhaustion", sentence[:50]))

        # Check word banks
        if has_any(tokens, POSITIVE) or has_any(tokens_collapsed, POSITIVE):
            emotion_signals["positive"] += 1

        if has_any(tokens, SAD) or has_any(tokens_collapsed, SAD):
            emotion_signals["sad"] += 1

        if has_any(tokens, ANGER) or has_any(tokens_collapsed, ANGER):
            emotion_signals["anger"] += 1

        if has_any(tokens, DISTRESS) or has_any(tokens_collapsed, DISTRESS):
            emotion_signals["distress"] += 1

    return {
        "signals": emotion_signals,
        "sentence_count": len(sentences),
        "key_phrases": key_phrases_found,
        "is_long": len(sentences) >= 3 or len(text) > 150
    }

def predict_emotion(text: str):

    # ✅ FIX: greetings shortcut
    if text.strip().lower() in {"hey", "hi", "hello"}:
        return {
            "emotion": "neutral",
            "score": 0.9
        }

    # ✅ LONG TEXT / RANT ANALYSIS
    # For longer messages, analyze sentence by sentence
    long_analysis = analyze_long_text(text)

    # ✅ FIX TYPOS FIRST
    # e.g., "im so sda and tird" → "im so sad and tired"
    text_typo_fixed = normalize_text_with_typo_fix(text)

    # ✅ EXPAND ABBREVIATIONS
    # e.g., "idk y u r sad rn" → "i dont know why you are sad right now"
    text_expanded = expand_abbreviations(text_typo_fixed)

    clean = preprocess_text(text_expanded)
    tokens = normalize(clean)
    t = " ".join(tokens)

    # ✅ FIX: also get collapsed tokens (shiiit → shit, hmmm → hmm)
    tokens_collapsed = normalize_with_collapse(clean)
    t_collapsed = " ".join(tokens_collapsed)

    # -----------------------------
    # ML PREDICTION
    # -----------------------------
    X = hstack([
        word_vec.transform([clean]),
        char_vec.transform([clean])
    ])

    probs = model.predict_proba(X)[0]
    labels = model.classes_
    scores = dict(zip(labels, probs))

    emotion = max(scores, key=scores.get)
    score = float(scores[emotion])

    # -----------------------------
    # INTERNAL RULE DETECTION
    # -----------------------------
    internal = None

    # ✅ CHECK FOR POSITIVE CURSE CONTEXT FIRST
    # (e.g., "holy shit thats amazing", "fuck yeah", "fucking finally")
    has_positive_curse = has_phrase(t, POSITIVE_CURSE_CONTEXT) or has_phrase(t_collapsed, POSITIVE_CURSE_CONTEXT)

    # ✅ CHECK FOR POSITIVE INDICATORS (happy, excited, yay, worked, etc.)
    has_positive_indicator = has_any(tokens, POSITIVE_INDICATORS) or has_any(tokens_collapsed, POSITIVE_INDICATORS)

    # ✅ If POSITIVE word + curse word together = POSITIVE (not distress)
    # e.g., "im so happy shit worked yayy" should be POSITIVE
    has_curse = has_any(tokens, CONTEXT_CURSES) or has_any(tokens_collapsed, CONTEXT_CURSES)
    positive_with_curse = has_positive_indicator and has_curse

    # check both normal tokens AND collapsed tokens for better matching
    if has_any(tokens, POSITIVE) or has_any(tokens_collapsed, POSITIVE):
        internal = "positive"

    # ✅ If positive curse phrase detected, override to positive
    if has_positive_curse:
        internal = "positive"

    # ✅ If positive indicator + curse = positive (happy shit worked = positive)
    if positive_with_curse:
        internal = "positive"

    # ✅ Only mark as distress if NOT a positive context
    if not has_positive_curse and not positive_with_curse:
        if (
            has_any(tokens, SAD) or has_any(tokens_collapsed, SAD)
            or has_any(tokens, DISTRESS) or has_any(tokens_collapsed, DISTRESS)
            or has_any(tokens, ANGER) or has_any(tokens_collapsed, ANGER)
        ):
            internal = "distress"

    # -----------------------------
    # MAP INTERNAL → FINAL
    # -----------------------------
    if internal == "positive":
        emotion = "positive"
        score = max(score, 0.7)

    elif internal == "distress":
        emotion = "distress"
        score = max(score, 0.7)

    # -----------------------------
    # ❤️ LOVE + PAIN = DISTRESS (but not if positive context)
    # -----------------------------
    if not has_positive_curse and not positive_with_curse:
        if (
            ("love" in tokens or "love" in tokens_collapsed)
            and (
                has_any(tokens, ANGER) or has_any(tokens_collapsed, ANGER)
                or has_any(tokens, DISTRESS) or has_any(tokens_collapsed, DISTRESS)
                or has_phrase(t, EXHAUSTION_PHRASES) or has_phrase(t_collapsed, EXHAUSTION_PHRASES)
            )
        ):
            emotion = "distress"
            score = max(score, 0.75)

    # -----------------------------
    # 🔴 FORCE STRONG DISTRESS (but not if positive context)
    # -----------------------------
    if not has_positive_curse and not positive_with_curse:
        if has_intensity(clean) or has_phrase(t, EXHAUSTION_PHRASES) or has_phrase(t_collapsed, EXHAUSTION_PHRASES):
            emotion = "strong_distress"
            score = max(score, 0.85)

    # -----------------------------
    # 📝 LONG TEXT / RANT HANDLING
    # For longer messages, use aggregated signals
    # -----------------------------
    if long_analysis["is_long"] and not has_positive_curse and not positive_with_curse:
        signals = long_analysis["signals"]

        # Calculate negative signals total
        negative_total = signals["distress"] + signals["sad"] + signals["anger"] + signals["exhaustion"]
        positive_total = signals["positive"]

        # If predominantly negative signals in a long rant
        if negative_total > positive_total and negative_total >= 2:
            # Exhaustion phrases = strong distress
            if signals["exhaustion"] >= 1:
                emotion = "strong_distress"
                score = max(score, 0.85)
            else:
                emotion = "distress"
                score = max(score, 0.75)

        # If there are exhaustion key phrases found
        if long_analysis["key_phrases"]:
            emotion = "strong_distress"
            score = max(score, 0.85)

    # -----------------------------
    # FINAL SAFETY
    # -----------------------------
    if emotion not in {
        "positive", "neutral", "distress", "strong_distress"
    }:
        emotion = "neutral"

    return {
        "emotion": emotion,
        "score": round(score, 4)
    }