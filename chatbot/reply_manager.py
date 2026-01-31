import random
from chatbot.memory_manager import get_memory_hint, get_similar_past_topic, get_recurring_emotion
from signal_mapper import count_signals_in_text

# ======================================================
# GREET / EXIT WORDS
# ======================================================

GREET_WORDS = {
    "hey", "heyy", "heyyy", "hi", "hii", "hello", "helloo"
}

EXIT_WORDS = {
    "bye", "byee", "byeee", "goodbye", "see you", "see ya", "later",
    "gotta go", "gtg", "g2g", "im going", "i'm going", "im leaving",
    "i'm leaving", "im out", "i'm out", "peace out", "peace"
}

EXIT_PHRASES = {
    "im going bye", "i'm going bye", "gonna go bye", "going bye",
    "im going now", "i'm going now", "gotta go now", "gonna go now",
    "im leaving now", "i'm leaving now", "i gotta go", "i gtg",
    "nothing more", "thats all", "that's all", "thats it", "that's it",
    "im done talking", "i'm done talking", "done talking",
    "talk later", "ttyl", "catch u later", "catch you later",
    "im off", "i'm off", "signing off", "logging off"
}

# ======================================================
# REST / BREAK PHRASES
# ======================================================

REST_PHRASES = {
    "wanna rest", "want to rest", "need rest", "need a rest",
    "gonna rest", "going to rest", "gotta rest", "take a rest",
    "take rest", "taking rest", "need a break", "wanna take a break",
    "want to take a break", "gonna take a break", "taking a break",
    "need some rest", "need to rest", "gotta take a break",
    "ima rest", "imma rest", "i need rest", "i need a break",
    "i wanna rest", "i want to rest", "i gotta rest",
    "gonna sleep", "wanna sleep", "need sleep", "need to sleep",
    "going to sleep", "gotta sleep", "ima sleep", "imma sleep",
    "gonna nap", "wanna nap", "need a nap", "taking a nap",
    "brb", "be right back", "gtg rest", "gtg sleep",
    "logging off", "signing off", "gonna disconnect",
    "need some time", "need time alone", "need space",
    "gonna take some time", "stepping away", "taking time off",
    "gonna chill", "need to chill", "wanna chill",
    "gonna relax", "need to relax", "wanna relax"
}

REST_REPLIES = [
    "yess go rest friend 💙 i'll be here when u come back",
    "ofc ofc take all the rest u need!! i'm here whenever 🫶",
    "go get that rest!! u deserve it fr. hmu when ur back 💙",
    "yeahh do it!! rest up and take care of urself okay? i'll be here",
    "totally get it 💙 go rest and come back when ur ready",
    "yess pls rest!! u need it. i'm not going anywhere 🫶",
    "go ahead friend 💙 rest is important. talk when ur back!!",
    "ofc!! take ur time and rest well. i'll be right here waiting 💙",
    "yes go rest rn!! u got this. come back whenever u want 🫶",
    "absolutely!! rest up and recharge. i'm always here for u 💙",
    "go get some sleep friend!! i'll be here when u wake up 🫶",
    "yesss take that break!! u deserve it. hmu later 💙",
    "ofc take ur time!! rest well and don't worry i'm here 🫶",
    "go ahead and rest!! talk to me whenever ur ready 💙",
    "totally!! get some rest friend. i'm here whenever u need 🫶"
]

# ======================================================
# FRUSTRATION WORDS (for light consoling)
# ======================================================

FRUSTRATION_WORDS = {
    "frustrated", "frustrating", "frustration", "annoyed", "annoying",
    "irritated", "irritating", "agitated", "pissed", "pissed off",
    "fed up", "sick of", "tired of", "had enough", "cant take it",
    "losing it", "going crazy", "driving me crazy", "ugh", "ughhh",
    "argh", "gah", "ffs", "smh", "so done", "im done", "i cant"
}

# ======================================================
# SICK / UNWELL PHRASES (for showing concern)
# ======================================================

SICK_PHRASES = {
    "not feeling well", "not feeling good", "dont feel well", "dont feel good",
    "feeling sick", "feel sick", "im sick", "i am sick", "got sick",
    "feeling unwell", "feel unwell", "im unwell", "i am unwell",
    "not well", "im ill", "i am ill", "feeling ill", "fell ill",
    "under the weather", "feeling off", "feel off", "feeling bad",
    "got a cold", "have a cold", "caught a cold", "have flu", "got flu",
    "have fever", "got fever", "running a fever", "have a headache",
    "got a headache", "head hurts", "my head hurts", "stomach hurts",
    "tummy hurts", "body aches", "body hurts", "feeling weak",
    "feel weak", "feeling dizzy", "feel dizzy", "gonna throw up",
    "feel nauseous", "feeling nauseous", "cant eat", "cant sleep",
    "no appetite", "lost appetite", "feeling terrible", "feel terrible",
    "feeling awful", "feel awful", "health issues", "not okay physically"
}

SICK_WORDS = {
    "sick", "ill", "unwell", "fever", "cold", "flu", "headache",
    "nauseous", "vomit", "puke", "dizzy", "weak", "faint",
    "migraine", "cramps", "ache", "pain", "sore", "infection"
}

# ======================================================
# PHYSICAL INJURY / ACCIDENT PHRASES
# ======================================================

PHYSICAL_INJURY_PHRASES = {
    # accidents
    "had an accident", "got in an accident", "was in an accident",
    "car accident", "bike accident", "got into accident",
    "met with an accident", "accident happened",
    # injuries
    "got hurt", "got injured", "im hurt", "i'm hurt", "im injured", "i'm injured",
    "hurt myself", "injured myself", "hurt my leg", "hurt my arm", "hurt my hand",
    "hurt my back", "hurt my head", "hurt my knee", "hurt my ankle", "hurt my wrist",
    # falls
    "fell down", "i fell", "fell and hurt", "slipped and fell",
    "tripped and fell", "took a fall", "had a fall",
    # burns/cuts
    "got burned", "burned myself", "burnt myself", "got a burn",
    "cut myself", "got a cut", "deep cut", "bleeding",
    # sprains/fractures
    "sprained my", "twisted my", "fractured my", "broke my",
    "broken bone", "fracture", "sprain"
}

# ======================================================
# FEELING BETTER / IM FINE PHRASES (follow-up to sickness)
# ======================================================

FEELING_BETTER_PHRASES = {
    # im fine now
    "im fine", "i'm fine", "im fine now", "i'm fine now",
    "im okay", "i'm okay", "im okay now", "i'm okay now",
    "im alright", "i'm alright", "im alright now", "i'm alright now",
    "im good", "i'm good", "im good now", "i'm good now",
    # feeling better
    "feeling better", "feel better", "feeling better now", "feel better now",
    "much better", "much better now", "im better", "i'm better",
    "im better now", "i'm better now", "getting better", "got better",
    # recovered
    "recovered", "im recovered", "i'm recovered", "fully recovered",
    "all good now", "all better", "all better now",
    "doing better", "doing fine", "doing okay"
}

FEELING_BETTER_REPLIES = [
    # relieved + happy to hear
    "omg good to hear 💙 im so glad ur feeling better!!",
    "ahh thats such a relief 💙 glad ur okay now!!",
    "yay 💙 so happy to hear ur better!! take it easy still okay??",
    "aw thats great 💙 glad ur doing okay now!! dont push urself too hard",
    "oh good 💙 im relieved to hear that!! how r u feeling overall??",
    "that makes me happy 💙 glad ur better!! rest up still okay??",
    "yesss 💙 so glad ur okay!! was worried about u",
    "aw good good 💙 happy to hear ur feeling better now!!",
    "thats great news 💙 glad ur doing better!! take care of urself okay??",
    "oh thank goodness 💙 so glad ur okay now!!"
]

# ======================================================
# STILL SICK / NOT BETTER YET PHRASES
# ======================================================

STILL_SICK_PHRASES = {
    # still sick
    "still sick", "still not well", "still unwell", "still not feeling well",
    "still not feeling good", "still ill", "still not okay",
    "not better", "not better yet", "not feeling better",
    "still the same", "no better", "hasnt improved", "hasn't improved",
    "getting worse", "got worse", "worse now", "feeling worse"
}

STILL_SICK_REPLIES = [
    # caring + take care
    "aw no 💙 pls take care of urself okay?? rest up and dont push it",
    "oh no still?? 💙 pls rest and take it easy okay?? ur health comes first",
    "aw friend 💙 pls take care of urself!! dont overdo anything okay??",
    "oh no 💙 pls rest up okay?? hope u feel better soon. take care of u",
    "aw im sorry 💙 pls take care and rest!! ur body needs it",
    "oh no still not better?? 💙 pls rest and drink water okay?? take care",
    "aw 💙 pls take it easy okay?? ur health is important. rest up",
    "oh no 💙 hope u feel better soon!! pls take care of urself okay??",
    "aw friend 💙 rest rest rest okay?? take care of urself pls",
    "oh no 💙 pls dont push urself okay?? rest and get better soon!!"
]

# ======================================================
# NOT LETTING ME REST / PEACE PHRASES
# ======================================================

NO_PEACE_PHRASES = {
    "not letting me rest", "wont let me rest", "dont let me rest",
    "not letting me sleep", "wont let me sleep", "dont let me sleep",
    "not giving me space", "wont give me space", "dont give me space",
    "not leaving me alone", "wont leave me alone", "dont leave me alone",
    "not letting me be", "wont let me be", "cant get any rest",
    "cant get any peace", "cant get peace", "no peace", "no rest",
    "always bothering me", "keep bothering me", "keeps bothering me",
    "always disturbing me", "keep disturbing me", "keeps disturbing me",
    "always nagging", "keep nagging", "keeps nagging", "wont stop nagging",
    "always on my case", "on my back", "on my neck", "breathing down my neck",
    "no break from", "cant catch a break", "never get a break",
    "always something", "its always something", "one thing after another",
    "ppl wont let me", "people wont let me", "they wont let me",
    "everyone keeps", "they keep", "people keep", "ppl keep",
    "cant even rest", "cant even relax", "cant even breathe",
    "no time for myself", "no me time", "zero me time"
}

# ======================================================
# ESCAPE FANTASY / QUIT JOB + RUN AWAY PHRASES
# ======================================================

ESCAPE_FANTASY_PHRASES = {
    "quit and go to", "quit my job and go", "wanna quit and move",
    "want to quit and go", "quit everything and go", "drop everything and go",
    "run away to", "move to the mountains", "go to himalayas", "go to the himalayas",
    "disappear to", "escape to", "leave everything and go", "just wanna disappear",
    "wanna run away", "want to run away", "move to bali", "move to thailand",
    "become a monk", "live in the mountains", "go off grid", "go off the grid",
    "quit and travel", "quit my job and travel", "leave and never come back",
    "start over somewhere", "start fresh somewhere", "move far away"
}

# ======================================================
# WANT TO QUIT / GONNA QUIT (work frustration, not job loss)
# ======================================================

WANNA_QUIT_PHRASES = {
    # gonna quit
    "gonna quit", "going to quit", "im gonna quit", "i'm gonna quit",
    "imma quit", "bout to quit", "about to quit", "ready to quit",
    "gonna quit fs", "gonna quit fr", "gonna quit honestly",
    "gonna quit this job", "gonna quit my job",
    # want to quit
    "wanna quit", "want to quit", "i wanna quit", "i want to quit",
    "wanna quit so bad", "wanna quit fr", "wanna quit fs",
    "really wanna quit", "really want to quit", "lowkey wanna quit",
    "highkey wanna quit", "just wanna quit", "just want to quit",
    # if this continues
    "if this continues", "if this keeps up", "if they keep",
    "if it continues", "if this goes on", "at this rate",
    "cant keep doing this", "can't keep doing this",
    # done with job
    "so done with this job", "done with this place", "over this job",
    "cant do this anymore", "can't do this anymore", "had it with this job",
    "had enough of this job", "sick of this job", "tired of this job",
    # threatening to leave
    "might just quit", "might just leave", "tempted to quit",
    "considering quitting", "thinking about quitting", "thinking of quitting",
    "one more thing and im out", "one more thing and i quit",
    "this close to quitting", "this close to leaving"
}

WANNA_QUIT_REPLIES = [
    # bestie energy (30-40%) + concern (70%) + explicit "why do u wanna quit"
    "nooo bestie 😔💙 i hear u tho... work sounds rough rn. but like why do u wanna quit?? what happened??",
    "ugh wait 💙 before u quit... tell me why?? like what's been going on that got u feeling this way??",
    "omg 😔 okay okay i get it... but like why do u wanna quit tho?? wanna vent about it??",
    "bestie noo 💙 ur feelings are so valid but like... why do u wanna leave?? what did they do??",
    "wait wait 😔 hold up... why do u wanna quit?? like tell me everything what happened",
    "nooo 💙 i feel u tho... but like why tho?? what's making u wanna quit rn??",
    "ugh okay 😔 that sounds rough... but fr why do u wanna quit?? whats going on there??",
    "bestie 💙 ur frustration is SO valid... but like tell me why u wanna leave?? im listening",
    "omg wait 😔 before anything... why do u wanna quit tho?? like what happened??",
    "noo 💙 i hear u... but like why do u wanna go?? tell me whats been happening??",
    # more consoling + explicit why
    "ugh bestie 😔 that wanting to quit feeling is rough... but like why tho?? what pushed u here??",
    "okay okay 💙 i get it... but tell me why do u wanna quit?? whats been going on??",
    "nooo 😔 ur feelings matter so much... but like why u wanna leave?? wanna talk about it??",
    "wait 💙 before u decide anything... why do u wanna quit tho?? like fr what happened??",
    "ugh i hear u bestie 😔 but like... tell me why?? what made u feel like quitting??",
    "omg 💙 okay the frustration is real... but why do u wanna go?? whats the situation??",
    "noo wait 😔 i feel u tho... but like why do u wanna quit?? tell me everything??",
    "bestie 💙 ur wellbeing comes first always... but tell me why u wanna leave?? what happened??",
    "ugh okay 😔 i understand... but fr why do u wanna quit tho?? like whats going on??",
    "nooo 💙 that sounds heavy... but like tell me why?? why do u wanna quit rn??"
]

BESTIE_WANNA_QUIT_NO_QUESTION = [
    "i hear u 💙 ur feelings are so valid. u deserve peace",
    "ugh i feel u 😔 that wanting to quit feeling is overwhelming",
    "ur frustration is valid 💙 u've been dealing with so much",
    "i get it 💙 sometimes u just need to step away",
    "ur wellbeing comes first 💙 always. i hear u",
    "the pressure getting to u is understandable 💙",
    "u deserve to feel valued 💙 ur feelings matter"
]

ESCAPE_FANTASY_REPLIES = [
    # playful + understanding
    "LMAOOO okay i get the quit part but himalayas?? 😭 u fr rn?? tell me what happened at work tho",
    "wait wait wait 💀 quitting i understand but becoming a mountain person?? what did they DO to u omg",
    "no bc i lowkey get it 😭 but like... the himalayas tho?? u gonna meditate ur problems away or what lmaooo",
    "STOPPP 💀 the way u went from quit to himalayas so fast... work really said 📉 huh",
    "okay mood tbh 😭 but like babe the mountains dont have wifi... u sure about this?? what happened tho",
    "LMFAOOO not the escape plan 💀 okay but fr what happened that made u wanna go full monk mode",
    "the himalayas tho?? 😭 that's so dramatic i love it... but like what happened at work bestie",
    "no bc same 💀 but also... u know its cold there right?? anyway what did they do to u",
    "HELP not the mountain escape fantasy 😭 okay but seriously what's going on at work",
    "bro said forget 2 weeks notice im going to the HIMALAYAS 💀 okay but what happened tho",
    # more supportive but still playful
    "okay the himalayas is sending me 😭 but fr i feel u... work got u THAT stressed huh??",
    "LMAOO the escape plan is wild 💀 but like... i get it. what's going on that's making u feel this way??",
    "no bc the urge to disappear is real 😭 but like talk to me first before u pack for the mountains",
    "not the quit and run fantasy 💀 okay but lowkey... what happened that u wanna leave everything behind",
    "the himalayas TOOK ME OUT 😭 but fr tho... that bad at work?? tell me what's happening",
    # understanding the frustration
    "okay okay i hear u 😭 the whole escape thing is a mood... but like what's making u feel this way fr",
    "LMAOOO babe 💀 i love the dramatic exit plan but like... u wanna talk about what's actually stressing u out??",
    "no bc sometimes u just wanna vanish i get it 😭 but what happened that got u planning ur mountain retirement",
    "the way u went straight to himalayas 💀 not a beach, not a city... THE MOUNTAINS. that's how i know its bad. spill.",
    "okay the escape fantasy is valid 😭 but like maybe talk about it first before becoming a hermit?? what happened"
]

# ======================================================
# HUMILIATION / BEING HUMILIATED AT WORK PHRASES
# ======================================================

HUMILIATION_PHRASES = {
    # direct humiliation
    "humiliates me", "humiliated me", "humiliating me", "keeps humiliating",
    "always humiliates", "humiliated in front of", "publicly humiliated",
    "humiliated at work", "my hr humiliates", "boss humiliates", "manager humiliates",
    "they humiliate", "humiliate me", "feel humiliated", "felt humiliated",
    "constantly humiliates", "humiliates me daily", "humiliates me everyday",
    # embarrassment / degradation at work
    "embarrassed me", "embarrassed in front of", "embarrassed at work",
    "degraded me", "degrading me", "treated like trash", "treated like nothing",
    "made me feel small", "made me feel worthless", "made me feel stupid",
    "made a fool of me", "made fool of me", "belittled me", "belittling me",
    "treats me like garbage", "treats me like im nothing", "treats me like dirt",
    "makes me feel like nothing", "makes me feel worthless", "makes me feel dumb",
    # public shaming / disrespect
    "called out in front of", "yelled at in front of", "shouted at in front",
    "scolded in front of", "criticized in front of", "insulted me", "insulting me",
    "disrespected me", "disrespecting me", "talks down to me", "talked down to",
    "treated me like dirt", "treated like dirt", "looked down on me",
    "mocked me", "mocking me", "laughed at me", "laughing at me", "ridiculed me",
    "ridiculing me", "shamed me", "shaming me", "put me down", "puts me down",
    # workplace specific
    "hr treats me badly", "hr is mean", "hr is rude", "hr is harsh",
    "boss treats me badly", "manager treats me badly", "coworkers mock me",
    "everyone laughs at me", "they make fun of me", "making fun of me"
}

HUMILIATION_REPLIES = [
    # validation + concern (subtle question at end)
    "oh no 💙 no one deserves to be humiliated like that... thats not okay at all. wanna talk about what happened??",
    "wait that's actually awful 😔 being humiliated is so painful... ur feelings are completely valid. what did they do??",
    "ugh 💙 that's so degrading and wrong... u dont deserve to be treated like that. wanna tell me more??",
    "im so sorry 😔 humiliation at work is genuinely traumatic... thats really unfair to u. what happened??",
    "no one should make u feel small like that 💙 thats not professional thats just cruel. wanna talk about it??",
    "thats actually terrible 😔 being embarrassed in front of others... thats so hurtful. what did they say??",
    "hey 💙 that's not okay at all... u deserve respect not humiliation. im here if u wanna share more",
    "ugh my heart hurts for u 😔 no one deserves that treatment... thats so wrong. what happened there??",
    "thats genuinely awful 💙 humiliation is such a painful feeling... ur feelings matter. tell me what happened??",
    "im sorry ur going through this 😔 being talked down to is so hurtful... wanna tell me about it??",
    # more empathetic replies
    "wait hold on 💙 they did WHAT to u?? thats so messed up... u deserve so much better. tell me everything",
    "omg no 😔 being treated like that is genuinely traumatic... im so sorry. what happened??",
    "that makes me so angry for u 💙 no one has the right to humiliate u like that. wanna vent about it??",
    "ugh 😔 the way they treat u is NOT okay... ur worth so much more than that. what did they do??",
    "im genuinely upset hearing this 💙 u deserve respect and kindness... not this. tell me what happened",
    "no no no 😔 thats actually cruel... u shouldnt have to deal with that. wanna talk about it??",
    "that breaks my heart 💙 being made to feel small is so painful... im here for u. what happened??",
    "wait thats actually abusive behavior 😔 u dont deserve any of that. im listening... tell me more",
    "ugh i hate that for u so much 💙 no one should ever make u feel worthless. what did they say??",
    "im so sorry 😔 that kind of treatment leaves scars... ur feelings are so valid. wanna share more??"
]

BESTIE_HUMILIATION_NO_QUESTION = [
    "no one deserves to be humiliated like that 💙 thats so wrong",
    "thats actually awful 😔 u deserve so much better treatment",
    "im so sorry 💙 that's not okay at all. ur feelings are valid",
    "ugh that makes me so sad for u 😔 u dont deserve that",
    "thats genuinely terrible 💙 humiliation is so painful",
    "ur feelings matter 💙 being treated like that is not okay",
    "im here for u 😔 that treatment is so unfair and wrong"
]

# ======================================================
# NO ONE UNDERSTANDS / FEELING UNHEARD PHRASES
# ======================================================

NO_ONE_UNDERSTANDS_PHRASES = {
    # not understood
    "no one understands", "nobody understands", "noone understands",
    "no one understands me", "nobody understands me", "no one gets it",
    "nobody gets it", "no one gets me", "nobody gets me", "dont get me",
    "doesnt understand", "doesn't understand", "they dont understand",
    "people dont understand", "no one listens", "nobody listens",
    "no one hears me", "nobody hears me", "feel unheard", "feeling unheard",
    "not being heard", "not being listened to", "talking to a wall",
    "like talking to walls", "feels like no one cares", "no one cares",
    # what i wanna say / trying to explain
    "what i wanna say", "what i want to say", "wt i wanna say", "wat i wanna say",
    "trying to explain", "cant explain", "they wont listen", "wont listen to me",
    "no one pays attention", "nobody pays attention", "ignored", "being ignored",
    "feel invisible", "feeling invisible", "like im invisible", "like i dont exist",
    # alone in this
    "alone in this", "im all alone", "feel so alone", "feeling alone",
    "no support", "no one to talk to", "cant talk to anyone",
    "no one i can talk to", "isolated", "feel isolated",
    "no one by my side", "no one on my side", "all by myself",
    "completely alone", "totally alone", "so lonely", "feel lonely",
    # misunderstood
    "misunderstood", "always misunderstood", "constantly misunderstood",
    "they misunderstand", "people misunderstand", "everyone misunderstands"
}

NO_ONE_UNDERSTANDS_REPLIES = [
    # validation + being there for them (subtle question)
    "i hear u 💙 feeling like no one understands is so isolating... im here and im listening. wanna tell me more??",
    "that loneliness of not being understood 😔 i get it... but im here and i want to understand. what's going on??",
    "ugh 💙 feeling unheard is so frustrating and painful... im listening tho. wanna talk about it??",
    "i see u 😔 and i want to understand... u shouldnt have to feel this alone. tell me what's happening??",
    "hey 💙 i know it feels like no one gets it... but im here trying. wanna help me understand??",
    "that feeling of isolation is so heavy 😔 ur not alone rn tho... im here. what's on ur mind??",
    "being unheard is genuinely painful 💙 i want to listen... tell me what u need me to understand??",
    "i hear u 😔 feeling like ur talking to walls is exhausting... but im listening. whats going on??",
    "ur feelings deserve to be heard 💙 im here for that... wanna share what's been happening??",
    "that 'no one gets me' feeling is so lonely 😔 but im trying to... tell me more??",
    # more empathetic + validating
    "hey 💙 im here and i genuinely want to understand... u matter and ur voice matters. tell me whats on ur heart",
    "that isolation of being misunderstood 😔 its one of the loneliest feelings... but im listening. talk to me",
    "i hate that u feel unheard 💙 u deserve to be listened to and understood. im all ears... whats going on??",
    "feeling invisible is so painful 😔 but i see u... i really do. wanna share whats happening??",
    "no one listening to u is so frustrating 💙 but im here and im paying attention. tell me everything",
    "that feeling of talking and no one caring 😔 its exhausting... but i care. whats been going on??",
    "being constantly misunderstood wears u down 💙 im here to actually listen... help me understand??",
    "i know that lonely feeling too well 😔 but ur not alone rn... im right here. talk to me 💙",
    "ur thoughts and feelings MATTER 💙 even if others dont show it... im here and i want to know. whats up??",
    "that 'no one gets what im trying to say' frustration 😔 i feel u... im listening carefully. tell me"
]

BESTIE_NO_ONE_UNDERSTANDS_NO_QUESTION = [
    "i hear u 💙 ur feelings are valid and u matter",
    "im here and im listening 😔 ur not alone",
    "i see u 💙 and i want to understand",
    "ur feelings deserve to be heard 💙",
    "im here for u 😔 u dont have to feel alone",
    "i get it 💙 and im here",
    "ur not invisible 💙 i see u"
]

# ======================================================
# UNDERPAID / COMPENSATION ISSUES PHRASES
# ======================================================

UNDERPAID_PHRASES = {
    # underpaid / not paid well
    "not paid well", "not paid enough", "underpaid", "poorly paid",
    "pay is terrible", "pay is shit", "pay sucks", "salary sucks",
    "salary is terrible", "salary is shit", "salary is low", "pay is low",
    "not compensated well", "not compensated enough", "compensation sucks",
    "deserve better pay", "deserve more pay", "paid less", "getting paid less",
    "not even paid well", "im not even paid well", "i'm not even paid well",
    "not even paid enough", "dont even pay well", "pay is so bad",
    # overworked + underpaid
    "paid peanuts", "paid nothing", "barely paid", "paid so little",
    "work so much for so little", "do so much for so little",
    "all this work for this pay", "all this for this salary",
    "not worth the pay", "not worth the salary", "deserve a raise",
    "no raise", "havent got a raise", "haven't got a raise",
    "all this effort for nothing", "work so hard for nothing",
    "put in so much get so little", "effort not rewarded",
    # inspite of / despite
    "inspite of all this", "despite all this", "after all i do",
    "after all this work", "even after all this", "inspite of this",
    "despite everything", "after everything i do", "after all my work",
    # comparison / unfairness
    "others get paid more", "they get paid more", "paid more than me",
    "earn less than", "make less than", "my pay is less",
    "not fair pay", "unfair pay", "unfair salary", "unfair compensation"
}

UNDERPAID_REPLIES = [
    # validation + understanding (subtle question)
    "ugh that's so frustrating 💙 doing all that work and not being compensated fairly... u deserve better. wanna vent about it??",
    "being underpaid for ur hard work 😔 that's genuinely disheartening... ur worth more than that. what's the situation like??",
    "the pay not matching the effort 💙 i feel that... thats so demotivating. tell me more about it??",
    "ugh 😔 putting in all that work for unfair pay... thats exhausting. wanna talk about whats happening??",
    "u deserve to be compensated fairly 💙 that sucks so much... whats going on with the pay situation??",
    "not being paid what ur worth 😔 that's frustrating... u deserve better. wanna tell me more??",
    "all that work and still underpaid 💙 thats genuinely unfair... how long has it been like this??",
    "the pay not reflecting ur effort 😔 i get why thats frustrating... ur feelings are valid. whats happening??",
    "u put in so much and get so little 💙 that imbalance is exhausting... wanna share more??",
    "being undervalued financially 😔 thats so demotivating... i hear u. what's the situation??",
    # more empathetic replies
    "wait 💙 u do ALL that and theyre not even paying u properly?? thats so unfair... tell me about it",
    "omg 😔 the amount of work u put in vs what u get paid... thats genuinely messed up. whats going on??",
    "that makes me so frustrated for u 💙 ur work has value and they should recognize that. wanna vent??",
    "ugh 😔 being underpaid while working ur ass off... thats exhausting and unfair. tell me more",
    "ur effort deserves proper compensation 💙 this isnt right. how long has it been like this??",
    "not being paid fairly is such a slap in the face 😔 especially after all u do. whats the situation??",
    "u deserve SO much better than what theyre paying u 💙 ur worth more. wanna talk about it??",
    "the audacity of not paying u well after all ur hard work 😔 thats genuinely infuriating. tell me",
    "being financially undervalued hurts different 💙 u put in the work... u deserve the pay. whats up??",
    "ugh 😔 working so hard and still not being compensated right... that wears u down. im listening"
]

BESTIE_UNDERPAID_NO_QUESTION = [
    "u deserve to be compensated fairly 💙 that sucks",
    "being underpaid for hard work is so frustrating 😔",
    "ur worth more than what they pay u 💙",
    "the pay not matching the effort 😔 i feel that",
    "u deserve better compensation 💙 genuinely",
    "thats so demotivating 😔 ur feelings are valid",
    "not being paid ur worth sucks 💙"
]

# ======================================================
# MENTAL HEALTH COLLAPSING / DETERIORATING PHRASES
# ======================================================

MENTAL_HEALTH_COLLAPSING_PHRASES = {
    # collapsing / deteriorating
    "mental health is collapsing", "my mental health is collapsing",
    "mental health collapsing", "health is collapsing", "im collapsing",
    "mental health is deteriorating", "my mental health is deteriorating",
    "mental health deteriorating", "mentally deteriorating",
    "mental state is deteriorating", "my mental state is deteriorating",
    "mentally collapsing", "emotionally collapsing", "falling apart mentally",
    # getting worse
    "mental health getting worse", "my mental health is getting worse",
    "mental health is worse", "mentally getting worse",
    "mental health going downhill", "my mental health is going downhill",
    "mental health spiraling", "my mental health is spiraling",
    "mentally spiraling", "emotionally spiraling", "spiraling down",
    # ruined / destroyed
    "mental health is ruined", "ruined my mental health", "destroying my mental health",
    "destroyed my mental health", "killing my mental health", "draining my mental health",
    "taking a toll on my mental", "toll on my mental health", "affecting my mental health",
    # at breaking point
    "mental health at breaking point", "mentally at breaking point",
    "about to break mentally", "mentally breaking", "emotionally breaking",
    "cant take it mentally", "mentally cant take it", "mentally exhausted",
    "emotionally exhausted", "mentally drained", "emotionally drained"
}

MENTAL_HEALTH_COLLAPSING_REPLIES = [
    # genuine concern + care (no questions - serious topic)
    "hey 💙 i hear u and im genuinely worried about u... please please take care of urself. ur mental health matters more than anything else",
    "that's really serious 💙 ur mental health is precious and im so sorry its getting this bad. please prioritize urself first",
    "im so worried about u 😔 ur wellbeing is the most important thing. nothing is worth destroying ur mental health over",
    "please take care of urself 💙 ur mental health deteriorating is a sign u need to step back. u matter more than any of this",
    "hey 💙 that's really scary to hear... please be gentle with urself. ur mental health is worth protecting above everything",
    "im here for u 😔 ur mental health collapsing is serious... please dont ignore what ur mind is telling u. u come first",
    "that breaks my heart 💙 please please prioritize urself. nothing is worth sacrificing ur mental wellbeing",
    "i hear u and i care about u 😔 ur mental health matters so much. please take a step back and take care of urself",
    "ur mental health is not something to push through 💙 please be kind to urself. im here if u need someone",
    "that's really concerning 😔 ur wellbeing comes first always. please dont let anything destroy ur peace",
    # more caring + supportive
    "hey hey 💙 stop for a second... ur mental health is MORE important than anything else rn. please take care of u first",
    "this breaks my heart to hear 😔 please please please put urself first. nothing else matters as much as u do",
    "im genuinely so worried about u 💙 ur mind is telling u something important... please listen to it and rest",
    "ur mental health crashing is a serious sign 😔 please step back from everything and take care of urself. i mean it",
    "hey 💙 u matter so much more than any job or stress... please prioritize urself. im here for u always",
    "that's not okay 😔 ur mental health deserves protection... please be gentle with urself. nothing is worth this",
    "im so sorry its gotten this bad 💙 ur wellbeing is precious... please take a step back. u deserve peace",
    "this hurts to hear 😔 please know that u come first ALWAYS. ur mental health > everything else. im here 💙",
    "ur mind is screaming for help 💙 please listen to it... take care of urself. nothing else is worth this pain",
    "i care about u so much 😔 please please prioritize ur mental health... step back and breathe. im here for u 💙"
]

BESTIE_MENTAL_HEALTH_COLLAPSING_NO_QUESTION = [
    "ur mental health matters more than anything 💙",
    "please take care of urself first 💙 nothing is worth this",
    "im genuinely worried about u 😔 please prioritize urself",
    "ur wellbeing > everything else. always 💙",
    "nothing is worth sacrificing ur peace over 💙",
    "please be gentle with urself 😔 u matter",
    "ur mental health is precious 💙 protect it"
]

# ======================================================
# FORCING / COERCION PHRASES (being forced to do things)
# Emotion: distress, anger | Intent: vent_only
# ======================================================

FORCING_COERCION_PHRASES = {
    # direct forcing
    "forcing me", "forced me", "forcing us", "being forced", "theyre forcing",
    "they are forcing", "they're forcing", "made me do", "making me do",
    "have no choice", "had no choice", "no other choice", "no options",
    "not a choice", "dont have a choice", "don't have a choice",
    # pressured
    "pressuring me", "pressured me", "pressured into", "pushed me into",
    "pushed into", "guilted into", "guilt tripped", "guilt tripping",
    "manipulated into", "manipulated me", "coerced into", "coerced me",
    # no say / autonomy
    "no say", "have no say", "had no say", "dont have a say", "don't have a say",
    "no voice", "my opinion doesnt matter", "my opinion doesn't matter",
    "nobody asked me", "no one asked me", "didnt ask me", "didn't ask me",
    "without my consent", "against my will", "against my wishes",
    # demand / order
    "demanded that i", "demanded i do", "ordered me to", "told me i have to",
    "told me i must", "said i have to", "said i must", "said i had to",
    "expected to just", "supposed to just", "must do it", "have to do it",
    # threat / ultimatum
    "threatened me", "threatening me", "gave me an ultimatum", "or else",
    "do it or", "either i do or", "no choice but", "forced to choose"
}

FORCING_COERCION_REPLIES = [
    # validating their lack of autonomy + empathy
    "omg thats so unfair 😤 u shouldnt be forced into anything. ur feelings matter",
    "nooo that's not okay 💙 being forced into something is the worst. im sorry ur dealing with this",
    "wait what?? 😤 nobody should force u to do anything. thats messed up",
    "bestie thats lowkey controlling 💙 u deserve to have a say in ur own life. what happened??",
    "ugh that makes me mad for u 😤 u shouldnt have to do anything against ur will. whats going on??",
    "thats literally not okay 💙 ur autonomy matters. tell me more?? what r they forcing u to do??",
    "nah thats not right 😤 u should have a CHOICE. im so sorry ur going thru this",
    "being forced is the worst feeling 💙 u deserve to be heard. wanna talk about it??",
    "omg no 😤 nobody has the right to force u into anything. what happened??",
    "that's actually so unfair to u 💙 ur voice matters. tell me everything??",
    # more supportive
    "wait being forced?? 😤 thats not okay at all. u deserve better than that",
    "bestie no one should make u do something u dont want 💙 thats wrong. whats going on??",
    "ugh i hate when ppl think they can force others 😤 ur autonomy is important",
    "that sounds really frustrating 💙 u shouldnt be put in that position. im here for u",
    "nooo thats not fair at all 😤 u deserve to have choices. wanna vent about it??",
    "being pressured like that is so stressful 💙 im sorry ur dealing with this",
    "wait they're making u do that?? 😤 thats not okay. u shouldnt have to",
    "ur feelings about this are SO valid 💙 no one should force u into anything",
    "thats literally manipulation 😤 u deserve to make ur own choices. whats happening??",
    "omg im so sorry 💙 being forced into something is awful. im here to listen"
]

BESTIE_FORCING_NO_QUESTION = [
    "thats not okay at all 😤 u shouldnt be forced into anything",
    "ur autonomy matters 💙 no one should make u do anything",
    "being pressured is the worst 😤 ur feelings are valid",
    "thats literally not fair 💙 u deserve choices",
    "ugh i hate that for u 😤 u shouldnt have to deal with this",
    "thats manipulation honestly 💙 u deserve better",
    "nooo u shouldnt be forced 😤 that's not right"
]

# ======================================================
# REGRET / MISTAKE PHRASES (regretting decisions)
# Emotion: distress, sadness | Intent: vent_only
# ======================================================

REGRET_PHRASES = {
    # regret
    "regret this", "i regret", "regretting", "regret taking", "regret joining",
    "regret coming", "regret accepting", "regret saying yes", "regret agreeing",
    "so much regret", "full of regret", "biggest regret", "deeply regret",
    # should have / shouldn't have
    "shouldnt have", "should not have", "shouldn't have", "should have never",
    "never should have", "shouldve never", "should've never",
    "i wish i didnt", "wish i didn't", "wish i hadnt", "wish i hadn't",
    "why did i", "why tf did i", "why the hell did i",
    # biggest mistake
    "biggest mistake", "huge mistake", "terrible mistake", "worst mistake",
    "worst decision", "bad decision", "terrible decision", "stupid decision",
    "dumbest thing", "stupidest thing", "what was i thinking",
    # could have been different
    "if only i didnt", "if only i didn't", "if only i hadnt", "if only i hadn't",
    "coulda shoulda woulda", "hindsight", "looking back", "in retrospect",
    "shouldve known better", "should've known better", "knew better",
    # specific contexts
    "regret this job", "regret this company", "regret this relationship",
    "mistake to join", "mistake to take", "mistake to come"
}

REGRET_REPLIES = [
    # validating regret + empathy
    "ugh that feeling of regret is SO heavy 😔 im sorry ur carrying that. what happened??",
    "hey we all make choices that feel wrong later 💙 dont be too hard on urself. wanna talk about it??",
    "bestie hindsight is literally 20/20 😔 u didnt know then what u know now. its okay",
    "omg that feeling is the worst 💙 regret is so heavy... tell me what happened??",
    "nooo dont beat urself up 😔 we all have things we wish we did differently. whats going on??",
    "hey u made the best decision u could with what u knew then 💙 thats all anyone can do",
    "regret is such a hard feeling to sit with 😔 im here for u. wanna vent??",
    "bestie we've all been there 💙 the important thing is what u do NOW. what happened??",
    "ugh i feel that 😔 that 'what if i didnt' feeling is so painful. tell me everything",
    "u couldnt have known 💙 please be gentle with urself. whats making u feel this way??",
    # more supportive
    "the past is already done 😔 but how ur feeling rn is valid. wanna talk??",
    "hey sometimes things dont work out 💙 that doesnt make u dumb for trying",
    "u were just doing ur best 😔 u didnt have a crystal ball. its okay to feel this tho",
    "bestie regret is a teacher 💙 its showing u what u value now. that matters",
    "i hate that ur feeling this way 😔 u deserve compassion from urself too",
    "we all have those 'why did i do that' moments 💙 ur not alone in this",
    "looking back is painful 😔 but u were doing what felt right at the time",
    "please dont blame urself too much 💙 hindsight makes everything look obvious",
    "that regret feeling is real 😔 but it doesnt define u. wanna talk about it??",
    "hey ur allowed to make mistakes 💙 thats how we learn. im here for u"
]

BESTIE_REGRET_NO_QUESTION = [
    "hindsight is 20/20 😔 u couldnt have known",
    "dont be too hard on urself 💙 u did ur best then",
    "regret is heavy 😔 but u made the best choice u could",
    "we all have things we wish we did differently 💙",
    "ur allowed to make mistakes 😔 thats how we grow",
    "be gentle with urself 💙 u were doing ur best",
    "the past is done 😔 what matters is now 💙"
]

# ======================================================
# SUFFOCATED / TRAPPED PHRASES (feeling stuck/suffocated)
# Emotion: distress, despair | Intent: vent_only
# ======================================================

SUFFOCATED_TRAPPED_PHRASES = {
    # suffocating
    "suffocates me", "this place suffocates", "work suffocates", "job suffocates",
    "feel suffocated", "feeling suffocated", "its suffocating", "it's suffocating",
    "so suffocating", "suffocating here", "suffocating environment",
    "feel so suffocated", "feeling so suffocated", "im suffocated", "i'm suffocated",
    "suffocated here", "literally suffocating", "actually suffocating",
    "cant breathe here", "can't breathe here", "hard to breathe",
    # trapped / stuck
    "feel trapped", "feeling trapped", "im trapped", "i'm trapped",
    "so trapped", "trapped here", "trapped in this", "completely trapped",
    "feel stuck", "feeling stuck", "im stuck", "i'm stuck", "so stuck",
    "stuck here", "stuck in this", "cant get out", "can't get out",
    "no escape", "no way out", "cant escape", "can't escape",
    # caged / imprisoned
    "like a cage", "feels like a cage", "caged", "imprisoned",
    "like a prison", "feels like a prison", "locked in", "boxed in",
    # no freedom
    "no freedom", "have no freedom", "dont have freedom", "don't have freedom",
    "cant leave", "can't leave", "unable to leave", "no exit",
    "walls closing in", "walls are closing", "closing in on me",
    # specific contexts
    "trapped in this job", "trapped in this relationship", "trapped in this life",
    "stuck in this job", "stuck in this situation", "stuck with no options"
}

SUFFOCATED_TRAPPED_REPLIES = [
    # validating the trapped feeling + empathy
    "omg that feeling of being trapped is SO suffocating 😔 im so sorry. what's happening??",
    "bestie that sounds so claustrophobic 💙 like u cant even breathe. tell me about it??",
    "nooo feeling stuck is the worst 😔 u deserve to feel free. whats making u feel this way??",
    "ugh i hate that for u 💙 feeling trapped is so heavy. wanna talk about it??",
    "that sounds so overwhelming 😔 like the walls are closing in. what happened??",
    "being stuck somewhere is EXHAUSTING 💙 u deserve better. tell me everything",
    "omg that trapped feeling is awful 😔 im here for u. whats going on??",
    "nooo u shouldnt have to feel caged like that 💙 what's the situation??",
    "that suffocating feeling is so real 😔 im sorry ur going thru this. im listening",
    "bestie feeling stuck takes such a toll 💙 u deserve freedom. wanna vent??",
    # more supportive
    "feeling trapped is one of the worst feelings 😔 im so sorry",
    "that sounds absolutely suffocating 💙 u deserve to breathe freely",
    "omg no one should feel caged like that 😔 whats keeping u stuck??",
    "that no-way-out feeling is so heavy 💙 im here to listen",
    "ugh feeling stuck is so draining 😔 u deserve options",
    "bestie thats so unfair 💙 u shouldnt feel trapped like this",
    "the walls closing in feeling is scary 😔 im here for u",
    "that suffocating environment sounds awful 💙 u deserve peace",
    "nooo feeling like u cant escape is terrible 😔 im so sorry",
    "u deserve freedom 💙 feeling trapped is not how life should be"
]

BESTIE_SUFFOCATED_NO_QUESTION = [
    "feeling trapped is the worst 😔 im so sorry",
    "u deserve to feel free 💙 this isnt fair",
    "that suffocating feeling is awful 😔 im here",
    "u shouldnt have to feel caged 💙",
    "the stuck feeling is so heavy 😔",
    "u deserve options and freedom 💙",
    "feeling like no way out is so hard 😔 im sorry"
]

# ======================================================
# WANT PEACE / SEEKING ESCAPE PHRASES (yearning for calm)
# Emotion: distress, exhaustion | Intent: vent_only
# ======================================================

WANT_PEACE_PHRASES = {
    # want peace
    "i want peace", "want peace", "need peace", "just want peace",
    "i need peace", "give me peace", "want some peace", "need some peace",
    "peace in my life", "want peace in my life", "need peace in my life",
    "peace of mind", "want peace of mind", "need peace of mind",
    "just want to be at peace", "want to feel at peace", "need to feel at peace",
    # want quiet / silence
    "want quiet", "need quiet", "want silence", "need silence",
    "want to be left alone", "leave me alone", "just leave me alone",
    "need space", "need some space", "give me space", "i need space",
    "need a break", "need to breathe", "cant breathe", "let me breathe",
    # escape / get away
    "need to escape", "want to escape", "wanna escape", "gotta escape",
    "want to run away", "wanna run away", "need to get away",
    "want to get away", "wanna get away", "need to disappear",
    "want to disappear", "just disappear", "want out", "need out",
    # tired of everything
    "tired of everything", "sick of everything", "done with everything",
    "had enough", "had enough of everything", "over everything",
    "need rest", "need to rest", "just wanna rest", "let me rest"
}

WANT_PEACE_REPLIES = [
    # bestie energy (30-40%) + concern (70%) - validating their need for peace
    "nooo bestie 😔💙 u deserve peace so badly... life sounds overwhelming rn. whats been draining u??",
    "ugh i feel u 💙 needing peace is so valid... everything must be so loud rn. wanna talk about it??",
    "omg 😔 the need for peace is real... u deserve calm and quiet. whats been going on??",
    "bestie 💙 ur soul is literally screaming for rest... thats valid. tell me whats overwhelming u??",
    "nooo 😔 u shouldnt have to beg for peace... u deserve it. whats been draining ur energy??",
    "ugh that need for quiet is SO valid 💙 everything must be so much rn. whats happening??",
    "omg bestie 😔 wanting peace means ur spirit is tired... im here. wanna vent about it??",
    "nooo 💙 u deserve peace and calm... like fr. whats been making everything so loud??",
    "ugh 😔 the world is probably being way too much rn... i get it. tell me whats going on??",
    "bestie 💙 needing space to breathe is so valid... u deserve rest. whats overwhelming u??",
    # more supportive + questions
    "omg 😔 when u just want peace... everything feels so heavy. whats been happening??",
    "nooo 💙 u deserve to feel at peace... ur soul needs rest. wanna talk about whats draining u??",
    "ugh bestie 😔 that craving for quiet means things are too much... im listening. whats up??",
    "that need to escape is so real 💙 u deserve peace. whats been making u feel this way??",
    "omg 😔 wanting to just disappear from it all... i get it. whats been overwhelming u??",
    "nooo bestie 💙 peace should be ur default not a wish... whats been going on??",
    "ugh 😔 u shouldnt have to fight for peace... u deserve calm. tell me whats happening??",
    "omg 💙 the exhaustion is real when u just want peace... im here. wanna vent??",
    "bestie 😔 ur need for space is SO valid... everything must be so draining. whats up??",
    "nooo 💙 u deserve rest and quiet... thats not too much to ask. whats been going on??"
]

BESTIE_WANT_PEACE_NO_QUESTION = [
    "u deserve peace 💙 ur feelings are so valid",
    "needing quiet is valid 😔 ur soul needs rest",
    "u shouldnt have to fight for peace 💙",
    "the world is too loud sometimes 😔 i get it",
    "u deserve calm and rest 💙 always",
    "that need to escape is so real 😔",
    "ur spirit is tired 💙 peace is what u deserve"
]

# ======================================================
# SILVER LINING / BRIGHT SIDE PHRASES (finding positives amid chaos)
# ======================================================

SILVER_LINING_PHRASES = {
    "one thing im happy", "one thing i'm happy", "one good thing",
    "at least", "atleast", "the only good thing", "only thing good",
    "bright side", "on the bright side", "good news is", "good part is",
    "one positive", "only positive", "small win", "at least i get",
    "at least ill get", "at least i'll get", "happy about is",
    "glad about is", "thankful for is", "grateful for is", "silver lining",
    "but hey at least", "but atleast", "one thing tho", "but one thing",
    "only thing keeping me going", "one thing keeping me sane"
}

SILVER_LINING_REPLIES = [
    # validating the positive while acknowledging struggle
    "YESS okay hold onto that 💰 like yes the rest is trash but that W is real",
    "no fr tho 💙 thats the energy!! focus on that win even when everything else is chaos",
    "okay YES 💰 see thats the spirit!! one good thing is still ONE GOOD THING u know??",
    "ayeee there we go 😌 finding the bright side even when its rough... i respect that fr",
    "EXACTLY 💙 like yes things are hard but u still got that going for u!! hold onto it",
    "no bc thats how u gotta think sometimes 💰 the bs is temporary but that W is real",
    "yess the silver lining mindset 😌 its not ignoring the problems its just... surviving smart",
    "okay i love that for u tho 💙 like yes things suck BUT at least something good right??",
    "fr fr 💰 thats the one thing keeping u going and thats VALID. take that win bestie",
    "see!! thats the attitude 😌 acknowledging the mess but also seeing the good. proud of u",
    # more supportive
    "no but fr that matters 💙 like everything else can be trash but that one W counts",
    "PERIOD 💰 take that win!! the other stuff is annoying but this is still something",
    "okay yes love the perspective shift 😌 its not much but its honest work u know",
    "thats literally how u survive bad times 💙 find the one good thing and HOLD ON",
    "yesss 💰 like the situation is messy but that right there?? thats ur anchor rn",
    # playful but validating
    "lmaoo the way u found the bright side tho 😌 like yes chaos BUT also a W. valid",
    "okay okay i see u finding the silver lining 💰 the rest is mess but this?? this is good",
    "not u being ur own hype person 💙 'yes this is bad BUT' i love that energy fr",
    "the glass half full moment 💰 like yes its chaos but at least SOMETHING is going right",
    "no bc same energy as 'my life is falling apart but at least ___' 😌 thats how we cope bestie"
]

# ======================================================
# CORPORATE BURNOUT / EXHAUSTION PHRASES
# Emotion: exhaustion, burnout | Intent: vent_only
# ======================================================

CORPORATE_BURNOUT_PHRASES = {
    # Original phrases
    "exhausted and its only", "exhausted and it's only", "only tuesday",
    "draining the life", "burned out", "burnt out", "burnout",
    "running on caffeine", "caffeine and anxiety", "survival mode",
    "dont remember the last time", "don't remember the last time",
    "tired before the day", "feel empty after work", "giving everything",
    "still falling behind", "running on fumes", "completely drained",
    "no energy left", "dead inside", "mentally exhausted", "physically exhausted",
    # New dataset phrases
    "nothing left in the tank", "exhausted beyond words", "aged me 10 years",
    "this week aged me", "mentally done", "surviving not living",
    "so tired it hurts", "taken everything out of me", "dont feel human",
    "don't feel human", "pushing through but barely", "tired of being tired",
    "still expected to perform", "cant keep up this pace", "can't keep up this pace",
    "drowning in work", "constantly catching up", "have nothing left",
    "im drained", "i'm drained", "im exhausted", "i'm exhausted",
    # Corporate burnout - extended
    "bandwidth is zero", "out of bandwidth", "no bandwidth left", "bandwidth maxed",
    "at capacity", "over capacity", "beyond capacity", "past my capacity",
    "hitting a wall", "hit a wall", "crashed and burned", "crash and burn",
    "running on empty", "tank is empty", "completely depleted", "resource depleted",
    "stretched too thin", "stretched thin", "spread too thin", "overextended",
    "burning the candle", "candle at both ends", "working myself to death",
    "chained to my desk", "desk jail", "corporate hamster wheel", "hamster wheel",
    "quarterly review drained me", "performance review exhausted", "fiscal year fatigue",
    "synergy overload", "too many synergies", "alignment fatigue", "pivot fatigue",
    "stakeholder exhaustion", "deliverable burnout", "kpi burnout", "metrics fatigue",
    "zoom fatigue", "meeting fatigue", "slack burnout", "email burnout",
    "agile fatigue", "sprint burnout", "standup fatigue", "retro exhaustion",
    "always on call", "on call 24 7", "never really off", "cant disconnect",
    "work follows me home", "work in my dreams", "dreaming about work",
    "sunday scaries hit hard", "monday dread", "weekend doesnt feel like weekend",
    # HR pressure / forced overtime / no rest
    "hr is pressuring", "hr pressuring", "hr keeps pressuring", "hr always pressuring",
    "pressuring me", "always pressuring", "keeps pressuring", "constantly pressuring",
    "manager pressuring", "boss pressuring", "boss is pressuring", "manager is pressuring",
    "work on sundays", "working on sundays", "no sundays off", "even on sundays",
    "on sundays", "work on weekends", "working weekends", "no weekends", "weekend work",
    "forced to work", "making me work", "have to work extra", "extra hours",
    "overtime every day", "constant overtime", "unpaid overtime", "too much overtime",
    "no day off", "no days off", "no time off", "no breaks", "no rest",
    "work even when sick", "cant take leave", "can't take leave", "leave denied",
    "feel burnout", "i feel burnout", "getting burnout", "so burnout"
}

# Emotion: exhaustion, burnout | Intent: vent_only
CORPORATE_BURNOUT_REPLIES = [
    # validate + subtle invite (supportive, not anti-company)
    "ugh 💙 that exhaustion is so real. i hear u",
    "burnout is SO real 💙 ur feelings are valid. i'm here",
    "the survival mode feeling 😔 u deserve more than that",
    "'mentally done' hits hard 💙 that's real exhaustion",
    "pushing through while running on empty 💙 that takes so much out of u",
    "constantly catching up but never caught up 😔 that's exhausting",
    "ugh i feel that 💙 some weeks just take everything out of u",
    "being expected to perform while drained 😔 that's really tough",
    "the burnout is real 💙 ur not weak for feeling this way",
    "that 'nothing left' feeling 😔 i hear u. i'm here",
    # more supportive replies
    "stretched too thin 💙 that's not sustainable. i'm listening",
    "back to back without rest 😔 that wears anyone down",
    "the pressure is real huh 💙 wanna talk about it??",
    "work taking everything from u 😔 that's so heavy",
    "u deserve rest 💙 ur wellbeing matters",
    "the exhaustion is valid 💙 i'm here for u",
    "that sounds so draining 😔 talk to me",
    "ur body is telling u something 💙 i hear u",
    "being on all the time is exhausting 😔 i feel that",
    "u deserve boundaries 💙 ur time matters"
]

# ======================================================
# CORPORATE FRUSTRATION / IRRITATION PHRASES
# Emotion: frustration, irritation | Intent: vent_only
# ======================================================

CORPORATE_FRUSTRATION_PHRASES = {
    # Original phrases
    "couldve been an email", "could've been an email", "could have been an email",
    "nothing ever gets decided", "changing priorities", "same issues again",
    "zero clarity", "endless pressure", "everything is urgent",
    "trying to stay professional", "sick of this", "so frustrated",
    "makes no sense", "waste of time", "pointless meeting", "no direction",
    "keep going in circles", "same problems", "nobody listens",
    # New dataset phrases
    "makes zero sense", "why is this so complicated", "overengineering everything",
    "no ownership anywhere", "nobody communicates properly", "tired of repeating myself",
    "we keep going in circles", "going in circles", "lack of direction",
    "unnecessarily messy", "everything is last minute", "last minute",
    "annoyed but trying to stay calm", "feels chaotic", "it feels chaotic",
    "this is frustrating", "so annoying", "makes no sense",
    # Corporate frustration - extended
    "scope creep again", "another scope creep", "scope keeps changing",
    "moving the goalposts", "goalposts keep moving", "shifting goalposts",
    "thrown under the bus", "got thrown under", "taking the fall",
    "micromanaged to death", "micromanagement hell", "being micromanaged",
    "red tape everywhere", "bureaucracy nightmare", "corporate red tape",
    "silos everywhere", "siloed teams", "no cross team communication",
    "blame game", "pointing fingers", "finger pointing culture",
    "passive aggressive emails", "cc my manager", "reply all chaos",
    "blocked by dependencies", "waiting on approvals", "approval hell",
    "too many cooks", "decision by committee", "committee decisions",
    "action items that go nowhere", "action items ignored", "follow up ignored",
    "double standards", "rules for thee", "one set of rules",
    "politics everywhere", "office politics", "corporate politics",
    "toxic positivity", "forced positivity", "fake positivity culture",
    "gaslighting at work", "being gaslit", "feels like gaslighting",
    "moving deadlines", "deadline keeps changing", "unrealistic timeline",
    "underpromise overdeliver my ass", "overpromised underdelivered",
    "stakeholder nightmare", "too many stakeholders", "stakeholder hell",
    "requirements keep changing", "spec changed again", "brief changed again",
    "legacy system nightmare", "technical debt", "tech debt hell"
}

# Emotion: frustration, irritation | Intent: vent_only
CORPORATE_FRUSTRATION_REPLIES = [
    # acknowledge frustration + let them vent (validate first)
    "'makes zero sense' is RIGHT 😤 like who designed this process honestly",
    "NOT THE MEETING THAT COULDVE BEEN AN EMAIL 💀 the corporate trauma is real",
    "ugh the endless priority changes 😤 how is anyone supposed to plan anything omg",
    "'no ownership anywhere' is such a specific frustration 💙 everyone passing the buck huh",
    "nobody communicates properly and then everyone acts surprised when things fall apart 😤 the logic??",
    "tired of repeating urself?? 💀 that's exhausting on a whole other level",
    "going in circles is SO frustrating 😤 like can we please just DECIDE something",
    "the lack of direction while expecting results?? 💙 make it make sense fr",
    "'unnecessarily messy' describes corporate life perfectly 😤 why do they do this",
    "everything being last minute is such a vibe killer 💙 no time to breathe",
    "'annoyed but trying to stay calm' 💀 i FEEL that internal screaming energy",
    "the chaos is REAL 😤 and somehow we're supposed to function in it??",
    "overengineering everything while undercommunicating 💙 peak corporate experience",
    "ugh the frustration is valid 😤 vent it out... whats been the most annoying part??",
    "no bc WHY is everything so complicated when it doesnt need to be 💀",
    # Corporate frustration replies - extended
    "scope creep is the BANE of existence 😤 they just keep adding stuff like magic huh",
    "goalposts moving again?? 💀 how r u supposed to win a game with no fixed rules",
    "thrown under the bus for someone elses mess 😤 corporate loyalty is a myth fr",
    "micromanagement hell is so suffocating 💙 like do they not trust anyone??",
    "red tape blocking everything 😤 bureaucracy was invented to torture us i swear",
    "silos everywhere and zero collaboration 💀 companies love to say teamwork then do THIS",
    "the blame game is exhausting 😤 nobody takes accountability and u pay the price",
    "passive aggressive emails with cc to manager 💀 the corporate warfare is real",
    "blocked by dependencies AGAIN 😤 waiting on ppl who dont care about ur deadlines",
    "decision by committee means no decision ever 💙 too many cooks ruin everything",
    "action items from last meeting still ignored 😤 why do we even have meetings then",
    "office politics are DRAINING 💀 just let ppl do their jobs omg",
    "toxic positivity culture is so fake 😤 u cant just positive vibes away real problems",
    "requirements changed AGAIN after u finished 💙 the disrespect is unreal",
    "technical debt piling up while leadership ignores it 😤 then they wonder why things break"
]

# ======================================================
# CORPORATE SAD / DISAPPOINTED PHRASES
# Emotion: sadness, disappointment | Intent: vent_only
# ======================================================

CORPORATE_SAD_PHRASES = {
    # Original phrases
    "dont feel valued", "don't feel valued", "not valued", "feel invisible",
    "expected more", "gave so much", "still wasnt enough", "still wasn't enough",
    "losing motivation", "used to care", "isnt what i imagined", "isn't what i imagined",
    "not what i signed up for", "feel overlooked", "no recognition",
    "work goes unnoticed", "nobody notices", "taken for granted",
    # New dataset phrases
    "feel unappreciated", "i feel unappreciated", "dont feel seen", "don't feel seen",
    "efforts dont seem to matter", "efforts don't seem to matter", "my efforts",
    "im losing motivation", "i'm losing motivation", "isnt fulfilling", "isn't fulfilling",
    "not fulfilling anymore", "i feel stuck", "feel stuck", "disappointed in how this turned out",
    "questioning myself", "i'm questioning myself", "im questioning myself",
    # Corporate sad - extended
    "passed over for promotion", "didnt get the promotion", "promotion went to someone else",
    "career plateau", "stuck in same role", "no growth opportunities", "dead end job",
    "my ideas get ignored", "nobody cares about my input", "input doesnt matter",
    "lost my passion", "passion died", "used to love this job", "dont love it anymore",
    "dream job turned nightmare", "this isnt what i wanted", "not my dream anymore",
    "feel like a cog", "just a number", "feel like just a number", "replaceable",
    "no work life balance", "sacrificed everything", "gave up so much for this",
    "peers got promoted", "everyone moving up except me", "left behind",
    "mentor left the company", "good people leaving", "everyone is leaving",
    "culture changed", "company changed", "not the same company anymore",
    "values dont align", "misaligned values", "dont believe in the mission",
    "golden handcuffs", "trapped by salary", "cant afford to leave",
    "imposter syndrome", "feel like a fraud", "dont belong here",
    "layoffs hit my team", "lost my team", "team got dissolved",
    "project got cancelled", "work meant nothing", "all for nothing",
    "feedback was harsh", "bad performance review", "review crushed me"
}

# Emotion: sadness, disappointment | Intent: vent_only
CORPORATE_SAD_REPLIES = [
    # gentle empathy + reflection (soft tone, no rushing)
    "feeling unappreciated after everything u put in 💙 that quiet hurt is so real",
    "not feeling seen is such a lonely feeling 😔 u deserve to be noticed for ur work",
    "'my efforts dont seem to matter' 💙 that hits hard... bc they DO matter even if no one says it",
    "aw no 💙 losing motivation slowly is rough... when did it start feeling like this??",
    "'this isnt fulfilling anymore' 😔 thats such a sad thing to realize about something u cared about",
    "feeling stuck is one of the hardest feelings 💙 like ur spinning wheels but going nowhere",
    "the disappointment in how things turned out 😔 u had hopes and they didnt land... thats painful",
    "questioning urself when maybe the environment is the problem 💙 thats a heavy place to be",
    "being overlooked when u know ur worth more 😔 that quiet hurt is real and valid",
    "u shouldnt have to prove ur worth every single day 💙 some places just dont see it",
    "the slow motivation drain is heartbreaking 😔 u started with so much hope huh",
    "'feel invisible' at work is so painful 💙 u deserve to be seen and appreciated",
    "gave so much and still not enough 😔 thats not a u problem... thats a them problem",
    "taken for granted after putting in the effort 💙 that disappointment is so valid",
    "the gap between what u expected and what u got 😔 thats a special kind of sad",
    # Corporate sad replies - extended
    "passed over for promotion AGAIN 💙 that rejection stings so deep... u deserved it",
    "career plateau is such a lonely place 😔 feeling like ur going nowhere while putting in work",
    "ur ideas getting ignored hurts different 💙 u have value even if they dont see it",
    "losing ur passion for something u loved 😔 thats grief honestly... mourning what it used to be",
    "dream job becoming a nightmare 💙 the betrayal of ur own expectations is heavy",
    "feeling like just a cog in the machine 😔 u r more than ur output i promise",
    "golden handcuffs trapping u 💙 when the money keeps u in misery... thats so conflicting",
    "watching everyone else get promoted 😔 left behind while putting in the same work... unfair",
    "good people leaving one by one 💙 watching the culture crumble is heartbreaking",
    "the company changed and not for the better 😔 mourning what it used to be is valid",
    "values not aligning anymore 💙 when u cant believe in what u do... thats soul crushing",
    "imposter syndrome is lying to u 😔 u belong there even when ur brain says u dont",
    "losing ur team to layoffs 💙 that grief is real... they were ur work family",
    "project cancelled after all that work 😔 feeling like it was all for nothing is devastating",
    "harsh feedback can break u 💙 especially when u tried ur best... take ur time to process"
]

# ======================================================
# STUCK WHILE OTHERS SUCCEED / COMPARISON PHRASES
# (casual/natural phrasing for career comparison feelings)
# ======================================================

STUCK_COMPARISON_PHRASES = {
    # everyone getting promoted except me
    "everyone around me is getting promoted", "everyone is getting promoted",
    "everyone getting promoted", "everyone got promoted", "everyone else got promoted",
    "everyone moving up", "everyone is moving up", "everyone's moving up",
    "ppl around me getting promoted", "people around me getting promoted",
    "friends are getting promoted", "my friends got promoted",
    "colleagues getting promoted", "coworkers getting promoted",
    # im still stuck / same place
    "im still stuck", "i'm still stuck", "still stuck doing the same",
    "still doing the same thing", "still doing the same stuff",
    "still in the same place", "still in same position", "same position for years",
    "havent moved up", "haven't moved up", "not moving up",
    "going nowhere", "im going nowhere", "i'm going nowhere",
    "stuck in the same role", "same role for so long",
    # not enough / never enough
    "no matter how much i do", "no matter what i do", "nothing is ever enough",
    "its never enough", "it's never enough", "never enough for them",
    "feels like nothing i do matters", "nothing i do is enough",
    "whatever i do its not enough", "whatever i do it's not enough",
    "do so much but", "work so hard but", "try so hard but",
    # left behind / falling behind
    "getting left behind", "im getting left behind", "i'm getting left behind",
    "falling behind everyone", "everyone is ahead of me", "everyone ahead of me",
    "behind everyone else", "feel so behind", "feeling so behind",
    "they're all ahead", "theyre all ahead", "everyone passed me",
    # comparison / watching others
    "watching everyone succeed", "seeing everyone succeed",
    "everyone is succeeding", "everyone succeeding except me",
    "others are doing better", "everyone doing better than me",
    "why not me", "when is it my turn", "whens my turn"
}

STUCK_COMPARISON_REPLIES = [
    # validating + encouraging bestie energy (dont doubt urself, itll be okay)
    "heyy nooo 💙 dont doubt urself okay?? ur time is coming i promise. everyone has their own timeline and urs is valid",
    "aw friend 💙 pls dont feel sad okay?? i know it looks like everyone is ahead but ur doing amazing too. trust the process",
    "nooo stop comparing urself 💙 ur journey is YOURS okay?? their wins dont take away from urs. ur time will come i promise",
    "hey hey 💙 dont let this get u down okay?? u r putting in the work and it WILL pay off. believe in urself pls",
    "aw no dont doubt urself 💙 i know it feels like ur stuck but ur not. good things r coming okay?? i believe in u",
    "heyy 💙 dont be so hard on urself okay?? everyone moves at different speeds and thats totally fine. ur gonna get there",
    "nooo friend pls dont feel bad 💙 ur efforts matter SO much okay?? sometimes it takes time but it'll happen for u too",
    "aw 💙 i get it but pls dont lose hope okay?? ur working hard and thats gonna pay off. dont doubt urself",
    "hey listen 💙 their success doesnt mean u failed okay?? ur time is coming. believe in urself bc i believe in u!!",
    "nooo dont feel down about this 💙 comparing never helps okay?? ur doing great and good things r on the way i promise",
    "aw friend 💙 pls dont doubt urself okay?? i know its frustrating but ur gonna level up too. just keep going",
    "heyy 💙 ur timeline is perfect for YOU okay?? dont let others' success make u feel less. UR time is coming",
    "nooo stop being sad about this 💙 u r enough okay?? more than enough. the right opportunity will find u i promise",
    "hey 💙 dont let this break u okay?? ur putting in work and thats what matters. success is coming ur way",
    "aw no 💙 pls dont doubt urself friend. everyone blooms at different times okay?? urs is coming soon i feel it"
    "i see u 💙 the stuck feeling is so heavy... especially when u watch others move ahead. its not fair"
]

BESTIE_STUCK_COMPARISON_REPLIES = [
    "dont doubt urself okay?? 💙 ur time is coming",
    "heyy ur gonna get there 💙 believe in urself pls",
    "nooo dont feel sad 💙 ur timeline is perfect for u",
    "ur time will come i promise 💙 keep going okay??",
    "dont let this get u down 💙 good things r coming",
    "pls dont doubt urself 💙 u r doing amazing",
    "their success ≠ ur failure okay?? 💙 ur turn is next",
    "stop comparing friend 💙 ur journey is urs"
]

# ======================================================
# CORPORATE DRAMA / BACKSTABBING / FRIEND TURNED ENEMY
# (workplace jealousy, badmouthing, toxic coworkers)
# ======================================================

CORPORATE_DRAMA_PHRASES = {
    # friend turned enemy / betrayal
    "she was my friend", "he was my friend", "we were friends",
    "thought she was my friend", "thought he was my friend",
    "friend until", "was my friend until", "were friends until",
    "friend turned enemy", "turned against me", "she turned on me", "he turned on me",
    "betrayed me", "she betrayed me", "he betrayed me", "felt betrayed",
    "stabbed me in the back", "backstabbed me", "backstabbing",
    # badmouthing / bitching / talking shit
    "badmouthing me", "badmouthing about me", "bad mouthing me",
    "bitching about me", "bitching abt me", "she is bitching", "he is bitching",
    "talking shit about me", "talking shit abt me", "talks shit about me",
    "talking behind my back", "talks behind my back", "said things behind my back",
    "spreading rumors", "spreading rumours", "spreading lies", "lying about me",
    "trash talking me", "trashtalking me", "trash talks me",
    "saying bad things about me", "saying stuff about me",
    # jealousy over success / offer / promotion
    "jealous of my promotion", "jealous i got promoted", "jealous of my offer",
    "jealous i got the offer", "jealous of my success", "jealous of me",
    "since i got the offer", "after i got the offer", "when i got promoted",
    "since i got promoted", "after i got promoted", "ever since my promotion",
    "changed after i got", "different since i got", "acting weird since i got",
    "cant handle my success", "can't handle my success",
    # toxic coworker / office politics
    "toxic coworker", "toxic colleague", "office politics", "workplace drama",
    "coworker is toxic", "colleague is toxic", "drama at work",
    "taking credit for my work", "took credit for my work", "stealing my credit",
    "threw me under the bus", "throwing me under the bus",
    "making me look bad", "trying to make me look bad", "made me look bad",
    "sabotaging me", "sabotaged me", "trying to sabotage",
    "turning people against me", "turned everyone against me",
    # two faced / fake
    "two faced", "two-faced", "so fake", "shes so fake", "hes so fake",
    "fake friend", "fake friends", "pretends to be nice", "nice to my face",
    "acts nice but", "sweet to my face", "different behind my back"
}

CORPORATE_DRAMA_REPLIES = [
    # bestie energy with concern - validating + supportive
    "omg nooo 💙 thats so messed up?? she was ur FRIEND and now shes doing this?? im so sorry ur dealing with this bs",
    "wait WHAT 💙 the audacity to badmouth u after everything?? thats so gross behavior. r u okay?? this must hurt so much",
    "ugh people can be SO fake 💙 im sorry friend. u didnt deserve this backstabbing at all. thats painful fr",
    "nooo thats awful 💙 jealousy makes ppl act so ugly. im sorry shes being like this. u deserve better friends",
    "omg the BETRAYAL 💙 i hate when ppl switch up like that. r u okay?? this kind of stuff hurts so deep",
    "wait shes talking shit about u?? 💙 thats so not okay. im sorry ur going thru this. u dont deserve that at all",
    "ugh workplace drama is the WORST 💙 especially when its someone u trusted. im here for u okay?? this sucks",
    "nooo friend 💙 the fact that they changed after ur success says everything about THEM not u. im sorry tho that hurts",
    "omg thats so toxic 💙 bitching about u behind ur back?? absolutely not okay. r u holding up okay??",
    "ugh the two-faced behavior 💙 nice to ur face but talking shit behind?? thats so gross. im sorry friend",
    "wait she turned on u after u got the offer?? 💙 jealousy is so ugly. u should be CELEBRATED not backstabbed",
    "nooo thats heartbreaking 💙 when someone u trusted becomes like this... im so sorry. u didnt deserve this",
    "omg the nerve to badmouth u 💙 after u thought they were ur friend?? im furious for u. r u okay tho??",
    "ugh people who cant handle others success 💙 thats a THEM problem not a u problem. but i know it still hurts",
    "nooo friend im so sorry 💙 workplace backstabbing is traumatizing fr. u deserve ppl who r genuinely happy for u"
]

BESTIE_CORPORATE_DRAMA_REPLIES = [
    "omg the audacity?? 💙 im so sorry friend",
    "ugh thats so fake and gross 💙 u deserve better",
    "nooo the backstabbing 💙 that hurts so much im sorry",
    "jealousy makes ppl so ugly 💙 this is a them problem",
    "two faced behavior is the worst 💙 im here for u",
    "omg shes badmouthing u?? 💙 absolutely not okay",
    "the betrayal hurts so deep 💙 im sorry friend",
    "ugh workplace drama sucks 💙 u didnt deserve this"
]

# ======================================================
# CORPORATE ANXIETY / JOB FEAR PHRASES
# Emotion: anxiety, fear | Intent: vent_only / unknown
# ======================================================

CORPORATE_ANXIETY_PHRASES = {
    # Original phrases
    "thin ice", "scared i might get fired", "might get fired", "get fired",
    "layoff rumors", "layoffs", "dont know where i stand", "don't know where i stand",
    "feels unstable", "everything unstable", "every mistake feels huge",
    "cant relax", "can't relax", "always worried", "job security",
    "walking on eggshells", "anxious about work", "stressed about job",
    "might lose my job", "scared of losing",
    # New dataset phrases
    "constantly worried about messing up", "worried about messing up", "scared of messing up",
    "feel like im under a microscope", "feel like i'm under a microscope", "under a microscope",
    "dont feel secure here", "don't feel secure here", "dont feel secure", "don't feel secure",
    "scared of being let go", "being let go", "lot of uncertainty", "a lot of uncertainty",
    "feel replaceable", "i feel replaceable", "cant switch my brain off", "can't switch my brain off",
    "switch off my brain", "pressure is intense", "the pressure is intense",
    # Corporate anxiety - extended
    "pip anxiety", "scared of pip", "performance improvement plan", "on a pip",
    "reorganization coming", "reorg anxiety", "restructuring", "team restructure",
    "merger anxiety", "acquisition rumors", "company being acquired", "buyout rumors",
    "budget cuts", "cost cutting", "headcount reduction", "hiring freeze",
    "probation period stress", "still on probation", "probation ending soon",
    "contract ending", "contract renewal anxiety", "might not renew",
    "one mistake away", "cant afford to mess up", "zero room for error",
    "boss is unpredictable", "never know where i stand", "mixed signals from manager",
    "feedback loop anxiety", "waiting for feedback", "dreading feedback",
    "quarterly review anxiety", "annual review stress", "review coming up",
    "presentation anxiety", "big meeting coming", "stakeholder presentation",
    "client escalation", "client complaint", "client might leave",
    "behind on deliverables", "missing deadlines", "deadline anxiety",
    "inbox anxiety", "email dread", "scared to check email",
    "slack notification anxiety", "teams ping anxiety", "message anxiety",
    "return to office anxiety", "rto stress", "hybrid work stress"
}

# Emotion: anxiety, fear | Intent: vent_only / unknown
CORPORATE_ANXIETY_REPLIES = [
    # grounding + reassurance (calming tone, no dismissing)
    "constantly worried about messing up is SO exhausting 💙 ur brain never gets a break huh",
    "feeling under a microscope at work 😔 that hypervigilance takes so much energy",
    "not feeling secure is such an unsettling feeling 💙 u deserve stability not constant worry",
    "the fear of being let go even when ur doing fine 😔 anxiety doesnt care about logic",
    "so much uncertainty makes it hard to plan anything 💙 that limbo is genuinely stressful",
    "feeling replaceable is such a painful thought 😔 but ur more valuable than u think",
    "cant switch ur brain off from work 💙 that constant loop is draining. do u ever get a break??",
    "the pressure being intense rn 😔 i hear u. thats a lot to carry every day",
    "walking on eggshells at work is no way to live 💙 that stress is valid and heavy",
    "hey 💙 i know the anxiety is loud rn... take a breath. ur doing better than u think",
    "layoff rumors mess with ur head so bad 😔 the not knowing is sometimes worse than knowing",
    "the 'where do i stand' spiral is exhausting 💙 u deserve clarity not constant guessing",
    "job instability anxiety is SO real 😔 hard to function when ur future feels uncertain",
    "when work makes u anxious even outside of work 💙 thats a sign its affecting u deep",
    "the fear feels so real even if nothing happened yet 😔 thats how anxiety works and its valid",
    # Corporate anxiety replies - extended
    "pip anxiety is terrifying 💙 that fear of being put on one... i hear u. breathe first okay??",
    "reorg uncertainty is so destabilizing 😔 not knowing if ur role survives is genuine stress",
    "merger rumors make everything feel so unstable 💙 the unknown is the worst part",
    "budget cuts looming over everything 😔 that job insecurity is exhausting to carry",
    "probation period stress is real 💙 feeling like ur constantly being evaluated... heavy",
    "contract ending anxiety hits different 😔 not knowing if ull have income next month... scary",
    "one mistake away from disaster thinking 💙 that perfectionism pressure is crushing",
    "unpredictable boss is so anxiety inducing 😔 never knowing what mood theyll be in",
    "waiting for feedback is torture 💙 the anticipation sometimes worse than the actual feedback",
    "quarterly review coming up 😔 that anxiety buildup is valid... how r u preparing mentally??",
    "presentation anxiety before stakeholders 💙 deep breaths... u know ur stuff even if it doesnt feel like it",
    "client escalation stress is real 😔 when someone elses anger becomes ur problem",
    "deadline anxiety spiraling 💙 behind on deliverables while the clock keeps ticking... breathe",
    "inbox dread is so relatable 😔 scared of what bad news awaits in there",
    "rto anxiety when u were thriving remote 💙 change is hard especially forced change"
]

# ======================================================
# CORPORATE NUMB / DETACHED PHRASES
# Emotion: numbness, apathy | Intent: unknown
# ======================================================

CORPORATE_NUMB_PHRASES = {
    "its fine", "it's fine", "whatever", "dont care anymore", "don't care anymore",
    "same old", "just here for the paycheck", "stopped expecting",
    "it is what it is", "doesnt matter", "doesn't matter", "numb to it",
    "past caring", "checked out", "emotionally checked out", "going through motions",
    # Corporate numb - extended
    "quiet quitting", "doing the bare minimum", "bare minimum", "minimum effort",
    "autopilot mode", "on autopilot", "just going through", "robot mode",
    "disengaged", "mentally checked out", "physically present mentally gone",
    "stopped trying", "why bother", "whats the point", "no point trying",
    "detached from work", "dont feel anything", "feel nothing about it",
    "apathetic about work", "apathy", "zero motivation", "no motivation left",
    "disconnected from team", "dont care about results", "results dont matter",
    "coasting", "just coasting", "coasting through", "phoning it in",
    "lost interest", "interest died", "dont care about growth", "growth doesnt matter",
    "stopped caring about promotions", "promotions dont excite me", "nothing excites me",
    "hollow", "empty at work", "work feels empty", "meaningless job",
    "clock watching", "counting hours", "waiting for 5pm", "living for weekends"
}

CORPORATE_NUMB_REPLIES = [
    # soft check-in, low pressure (don't push)
    "the 'its fine' energy 💙 sometimes thats all we can say huh",
    "whatever mode is valid sometimes 😔 not everything deserves ur energy",
    "just here for the paycheck is a whole mood 💙 no shame in that honestly",
    "stopped expecting anything... 😔 thats a defense mechanism and i get it",
    "it is what it is hits different when u actually mean it 💙",
    "the numbness is real 😔 sometimes feeling nothing is easier than feeling everything",
    "checked out mentally but still showing up 💙 thats a special kind of exhaustion",
    "hey 💙 u dont have to feel anything specific rn... just existing is okay",
    "same old stuff... 😔 the monotony can be numbing fr. u okay tho??",
    "going through the motions is survival 💙 no judgment here",
    # Corporate numb replies - extended
    "quiet quitting is just protecting ur peace honestly 💙 no shame in that",
    "bare minimum when they give u bare minimum back 😔 makes sense to me",
    "autopilot mode is a coping mechanism 💙 sometimes thats all we got",
    "why bother when nothing changes anyway 😔 that learned helplessness is valid",
    "detached from work to protect urself 💙 emotional distance is sometimes necessary",
    "feeling nothing is sometimes the brains way of coping 😔 u okay under there??",
    "coasting through work 💙 when caring hurt too much... numbness is safer huh",
    "lost interest in something u used to care about 😔 thats a quiet kind of grief",
    "clock watching till freedom 💙 living for 5pm is more common than ppl admit",
    "empty at work but still showing up 😔 thats its own kind of strength honestly",
    "physically there mentally elsewhere 💙 dissociating from work is... relatable",
    "nothing exciting about work anymore 😔 when even wins dont feel like wins",
    "the hollow work feeling 💙 going through motions without feeling them... i hear u",
    "stopped caring about promotions 😔 when the carrot stops working... fair enough",
    "living for weekends is survival mode 💙 no judgment... how long has it been like this??"
]

# ======================================================
# CORPORATE SARCASM / DARK HUMOR PHRASES
# Emotion: masked stress | Intent: vent_only
# ======================================================

CORPORATE_SARCASM_PHRASES = {
    "living the dream", "thriving obviously", "thriving", "productive meeting that solved nothing",
    "work life balance never heard of her", "work-life balance", "another late night",
    "unrealistic deadlines", "love unrealistic", "so excited", "cant wait",
    "absolutely love", "totally fine", "everything is fine", "this is fine",
    # Sarcastic escape fantasies
    "marry someone rich", "marry rich", "sugar daddy", "sugar mommy",
    "win the lottery", "lottery ticket", "sell my organs", "become a housewife",
    "become a trophy wife", "be a stay at home", "run away", "move to bali",
    "start an onlyfans", "drop everything", "disappear", "become a farmer",
    "live in the woods", "off the grid", "escape to mountains", "quit and travel",
    # Corporate sarcasm - extended
    "love being looped in last minute", "looped in last minute", "last minute loop",
    "per my last email", "as per my previous email", "as i mentioned",
    "circle back", "lets circle back", "circling back", "touch base",
    "synergy", "love the synergy", "so much synergy", "synergize",
    "leverage", "lets leverage", "leveraging our strengths", "leverage this opportunity",
    "move the needle", "moving the needle", "needle moved", "big needle mover",
    "low hanging fruit", "grab the low hanging fruit", "easy wins",
    "bandwidth", "no bandwidth", "love having no bandwidth", "bandwidth for this",
    "take this offline", "lets take this offline", "offline discussion",
    "align", "lets align", "alignment meeting", "getting aligned",
    "deep dive", "do a deep dive", "deep diving", "another deep dive",
    "unpack this", "lets unpack", "unpacking the issue", "unpacking that",
    "pivot", "time to pivot", "pivoting again", "love a good pivot",
    "lean in", "leaning in", "lean into this", "lean into the discomfort",
    "boil the ocean", "not trying to boil the ocean", "boiling the ocean",
    "open the kimono", "opening the kimono", "full transparency",
    "drink the kool aid", "kool aid drinker", "drank the kool aid",
    "move fast break things", "fail fast", "failing forward",
    "value add", "adding value", "what value does this add", "value added"
}

CORPORATE_SARCASM_REPLIES = [
    # acknowledge humor FIRST, then gently probe
    "LMAOOO 'living the dream' 💀 the sarcasm is strong with this one... but fr tho how r u actually",
    "'thriving obviously' TOOK ME OUT 😭 okay but under the sarcasm... u good??",
    "not the productive meeting that solved nothing 💀 i felt that in my SOUL",
    "'work life balance never heard of her' STOPPP 😭 the accuracy hurts",
    "the 'so excited for another late night' energy 💀 ur coping thru humor but like... u okay??",
    "'absolutely love unrealistic deadlines' 😭 the corporate sarcasm is PEAK",
    "lmaoo the way u said that so casually 💀 but actually tho... whats really going on",
    "'this is fine' while everything burns 😭 i see u. whats happening fr??",
    "the sarcasm is immaculate 💀 but im sensing some real frustration under there huh",
    "okay the humor is coping but 💙 u can drop the sarcasm w me... whats up actually",
    # Escape fantasy sarcasm replies
    "LMAOOO marry rich and escape 💀 bestie the dream... but fr work got u that exhausted huh",
    "'marry someone rich' the way we've ALL been there 😭 work really pushing u to the edge today",
    "the escape fantasy is REAL 💀 should we start a gofundme for ur freedom... but actually what happened",
    "not the 'quit and become a housewife' energy 😭 i feel that in my bones... work is THAT bad huh",
    "STOPPP the marry rich plan 💀 okay but seriously what did work do to u today",
    "the sarcasm is giving 'i cannot do this anymore' 😭 tell me what's going on fr",
    "lmaoo the escape plan is forming 💀 but under all that humor... u good?? whats happening",
    "'i cant do this' mood is TOO real 😭 the job really testing u huh... spill",
    # Corporate sarcasm replies - extended
    "'per my last email' VIOLENCE 💀 who made u send that... spill the tea",
    "LETS CIRCLE BACK said no one who actually wanted to solve anything 😭",
    "'love the synergy' i am DECEASED 💀 corporate buzzwords hitting different today huh",
    "leverage this leverage that 😭 when did we start talking like linkedin posts",
    "'moving the needle' but which needle and where 💀 corporate speak is wild",
    "low hanging fruit they said 😭 as if anything at work is actually easy",
    "'no bandwidth' is corporate for 'leave me alone' 💀 i see u bestie",
    "lets take this offline aka this meeting is a waste 😭 the shade is real",
    "another alignment meeting to get aligned about alignment 💀 make it stop",
    "'deep dive' into what exactly 😭 more meetings about meetings??",
    "pivoting AGAIN 💀 at this point yall just spinning in circles",
    "'lean into the discomfort' LMAOOO 😭 how about no??",
    "fail fast fail often is just failing with extra steps 💀 the corporate gaslighting",
    "'value add' added to my list of phrases that mean nothing 😭",
    "the corporate jargon is giving unhinged 💀 but fr what happened today"
]

# ======================================================
# CORPORATE MEME VENTING / JOKES PHRASES
# Emotion: stress masked as humor | Intent: vent_only
# ======================================================

CORPORATE_MEME_PHRASES = {
    "trauma bonding", "personality is now work stress", "laugh so i dont cry",
    "laugh so i don't cry", "survived today barely", "survived today",
    "career growth means more work", "same pay", "send help",
    "corporate girlies", "corporate life", "adulting", "9 to 5 more like 9 to 9",
    # Corporate meme - extended
    "we are a family", "work family", "family culture", "like a family here",
    "pizza party", "another pizza party", "pizza instead of raise",
    "unlimited pto that nobody takes", "unlimited pto", "pto guilt",
    "hustle culture", "rise and grind", "grindset", "that grind life",
    "eat sleep work repeat", "work work work", "all i do is work",
    "spreadsheet therapy", "powerpoint is my personality", "excel wizard",
    "meetings that couldve been emails", "email that couldve been nothing",
    "slack is my toxic ex", "teams notification ptsd", "email trauma",
    "linkedin influencer energy", "linkedin cringe", "linkedin post vibes",
    "thought leader", "industry disruptor", "passionate about synergy",
    "corporate millennial", "corporate zoomer", "corporate elder",
    "out of office forever", "ooo but not really", "checking email on vacation",
    "reply all apocalypse", "cc everyone", "bcc drama",
    "coffee is a coping mechanism", "caffeine dependent", "coffee IV drip",
    "imposter syndrome era", "fake it till u make it", "faking competence",
    "monday motivation delusional", "hump day energy", "friday brain activated"
}

CORPORATE_MEME_REPLIES = [
    # match the meme energy, then check in
    "'corporate life is trauma bonding' IS SO TRUE THO 💀 we're all just coping together",
    "SEND HELP 😭 okay but like... actually tho whats happening bestie",
    "'my personality is now work stress' STOPPP 💀 thats too real and too sad at the same time",
    "i laugh so i dont cry is literally the corporate anthem 😭",
    "'survived today barely' 💀 the bar is in HELL but hey u made it",
    "career growth = more work same pay is THE scam of our generation 😭",
    "not the 9 to 5 thats actually 9 to 9 💀 labor laws left the chat",
    "the way u made that funny but its actually sad 😭 talk to me tho fr",
    "meme venting is valid 💀 but also... u wanna actually talk about it??",
    "okay the joke landed but 💙 whats really going on under all that humor",
    # Corporate meme replies - extended
    "'we are a family' until u need a raise 💀 then suddenly its business decisions",
    "PIZZA PARTY INSTEAD OF LIVING WAGE 😭 the audacity is astronomical",
    "unlimited pto that u feel guilty using 💀 the scam of the century fr",
    "hustle culture is just exploitation rebranded 😭 but like... u okay tho??",
    "eat sleep work repeat is giving dystopia 💀 when did this become normal",
    "powerpoint is ur personality now 😭 corporate really took everything huh",
    "meetings that couldve been emails that couldve been nothing 💀 PEAK efficiency",
    "slack being a toxic ex is TOO accurate 😭 the notifications never stop",
    "linkedin thought leader energy 💀 HELP why is that so specific and so true",
    "coffee as a coping mechanism 😭 caffeine keeping the corporate world alive fr",
    "imposter syndrome era is rough 💀 but also... most ppl r faking it too",
    "monday motivation is DELUSIONAL 😭 who is actually motivated on mondays??",
    "'we are family' trauma bonding is wild 💀 dysfunctional family maybe",
    "checking email on vacation is a disease 😭 pto stands for 'pretending time off'",
    "friday brain activated 💀 but also... how was ur week actually??"
]

# ======================================================
# CORPORATE POSITIVE / HAPPY PHRASES
# Emotion: happiness, pride | Intent: unknown (celebrate)
# ======================================================

CORPORATE_POSITIVE_PHRASES = {
    "finally got promoted", "got promoted", "promotion", "went well today",
    "manager appreciated", "feel motivated", "looking up", "proud of myself",
    "project excites me", "good day at work", "work was good", "feeling good about work",
    "got recognized", "positive feedback", "good review", "nailed it",
    # Corporate positive - extended
    "landed the job", "got the offer", "offer letter", "new job offer",
    "raise approved", "got a raise", "salary increase", "bonus came through",
    "project shipped", "launched successfully", "release went smooth", "deployment success",
    "client loved it", "stakeholder approved", "green light", "got the green light",
    "team won", "our team won", "award", "team award", "recognition award",
    "mentor praised me", "skip level went well", "1 on 1 was great", "great 1 on 1",
    "learning so much", "growing at work", "skill development", "upskilling",
    "work from home approved", "remote approved", "flexible schedule", "hybrid approved",
    "dream project", "assigned dream project", "working on something cool",
    "great team", "love my team", "team vibes", "team chemistry",
    "manager supports me", "supportive manager", "good leadership", "great boss",
    "boundaries respected", "work life balance achieved", "leaving on time",
    "made a difference", "impact at work", "contribution recognized",
    "interview went well", "crushed the interview", "final round", "got to final round"
}

CORPORATE_POSITIVE_REPLIES = [
    # celebrate + ask for details
    "WAIT U GOT PROMOTED?? 🎉 LETS GOOO!! tell me everything omg",
    "work went WELL?? 😱 in THIS economy?? thats huge!! what happened??",
    "manager appreciation hits different 🥹 u deserve that!! what did they say??",
    "feeling motivated again!! 💛 i love that for u!! whats got u excited??",
    "things looking up?? 🎉 YESS!! tell me the good news!!",
    "proud of urself!! AS U SHOULD BE 💛 what did u accomplish??",
    "a project that excites u?? 😍 thats rare and beautiful!! whats it about??",
    "OKAY GOOD VIBES 🎉 i love this energy!! spill the details!!",
    "not u having a GOOD day at work 💛 we need to document this moment lol whats up??",
    "got recognized for ur work?? 🥹 FINALLY!! tell me more!!",
    # Corporate positive replies - extended
    "LANDED THE JOB?? 🎉 OMG CONGRATS!! tell me about the role!!",
    "RAISE APPROVED!! 💰 u DESERVE that!! how much we celebrating??",
    "project shipped successfully!! 🚀 thats HUGE!! how does it feel??",
    "client loved it?? 🥹 ur hard work paid off!! what did they say??",
    "team won an award?? 🏆 LETS GOOO!! what was it for??",
    "mentor praised u!! 💛 thats so validating!! what happened??",
    "learning and growing at work!! 🌱 i love that for u!! whats new??",
    "remote work approved?? 🏠 THE DREAM!! how r u feeling about it??",
    "dream project assignment?? 😍 OKAY MAIN CHARACTER MOMENT!! tell me more!!",
    "great team vibes?? 💛 thats so rare and precious!! what makes them special??",
    "supportive manager?? 🥹 u hit the jackpot!! what do they do thats great??",
    "work life balance ACHIEVED?? 🎉 in THIS economy?? how did u do it??",
    "making an impact at work!! 💛 thats what its all about!! what happened??",
    "crushed the interview?? 🔥 I KNEW U WOULD!! how did it go??",
    "final round of interviews?? 🎉 so close to the finish line!! u got this!!"
]

# ======================================================
# CORPORATE MIXED EMOTIONS PHRASES
# Emotion: conflicted | Intent: vent_only
# ======================================================

CORPORATE_MIXED_PHRASES = {
    "grateful but exhausted", "good pay bad peace", "like the work hate the environment",
    "okay but tired", "happy but overwhelmed", "dont know how to feel",
    "don't know how to feel", "conflicted", "mixed feelings", "good and bad",
    "love and hate", "blessing and curse", "double edged",
    # Corporate mixed - extended
    "promoted but more stress", "more money more problems", "raise but more work",
    "love the role hate the hours", "great team toxic culture", "good manager bad company",
    "remote but lonely", "flexible but no boundaries", "autonomous but unsupported",
    "challenging but overwhelming", "learning but struggling", "growing but painful",
    "passionate but burning out", "caring but depleted", "invested but exhausted",
    "excited but anxious", "hopeful but scared", "optimistic but cautious",
    "proud but empty", "successful but unfulfilled", "achieving but unhappy",
    "stable but stagnant", "secure but bored", "comfortable but stuck",
    "independent but isolated", "empowered but overwhelmed", "trusted but overloaded",
    "appreciated but underpaid", "recognized but burnt out", "valued but exhausted",
    "dream job but nightmare hours", "perfect role wrong company", "right job wrong time",
    "love what i do hate how i do it", "passion becoming burden", "hobby turned job stress"
}

CORPORATE_MIXED_REPLIES = [
    # acknowledge BOTH sides
    "'grateful but exhausted' is such a real thing 💙 both can be true at the same time",
    "good pay bad peace is THE corporate dilemma 😔 money vs mental health is rough",
    "loving the work but hating the environment?? 💙 thats so conflicting to live with",
    "okay but tired... 😔 the 'fine on paper struggling inside' energy",
    "happy but overwhelmed is valid 💙 success can be exhausting too",
    "not knowing how to feel is a feeling too 😔 u dont have to have it figured out",
    "the mixed emotions are real 💙 life isnt black and white and neither are feelings",
    "when something is both good and bad at the same time 😔 thats genuinely confusing to process",
    "the blessing and curse of a job 💙 u can appreciate it AND be drained by it",
    "its okay to hold two feelings at once 😔 grateful AND exhausted. happy AND overwhelmed. both are real",
    # Corporate mixed replies - extended
    "promoted but more stress 💙 the win comes with a price huh... how r u processing that??",
    "more money more problems is literally real 😔 u thought itd feel better but it doesnt huh",
    "great team but toxic culture 💙 the ppl r good but the system is broken... thats hard",
    "remote work but lonely 😔 the flexibility vs connection tradeoff is real",
    "challenging work but overwhelming pace 💙 u want growth but not like THIS huh",
    "passionate but burning out 😔 when the thing u love starts hurting u... thats painful",
    "excited but anxious about whats next 💙 new opportunities are scary AND exciting",
    "proud of success but feeling empty 😔 achieving goals that dont fulfill u... confusing",
    "stable job but feeling stagnant 💙 security vs growth is such a real dilemma",
    "trusted with responsibility but overloaded 😔 appreciation that comes with exploitation",
    "dream job with nightmare hours 💙 getting what u wanted but not how u wanted it",
    "love what u do hate how u do it 😔 passion becoming a burden is heartbreaking",
    "appreciated but underpaid 💙 words without fair compensation hits different",
    "successful but unfulfilled 😔 winning by everyones standards except ur own",
    "empowered but overwhelmed 💙 autonomy without support is just abandonment with extra steps"
]

NO_PEACE_REPLIES = [
    # empathy + validation
    "ugh that's so annoying fr 😤 u deserve some peace!! who's not letting u rest??",
    "omg that sounds exhausting 😔 u need ur space!! what's going on??",
    "bruh that's not okay 💙 everyone needs rest. who's bothering u??",
    "damn that's frustrating fr 😤 u have every right to rest. tell me what's happening",
    "ugh i hate when ppl don't respect boundaries 😔 what's going on??",
    "yo that's lowkey suffocating 💙 u need ur time. who's not letting u be??",
    "that sounds so draining omg 😤 u deserve a break fr. what happened??",
    "friend that's not fair 💙 u need rest too!! who's doing this??",
    "ugh boundaries are important fr 😔 what's going on?? tell me",
    "damn they need to chill 😤 u deserve peace. what's happening??",
    # more supportive
    "no fr that's exhausting 💙 u can't pour from an empty cup. what's up??",
    "ugh that's so frustrating when ppl don't get it 😔 what happened??",
    "yo u literally need rest to function 😤 who's not letting u??",
    "friend ur wellbeing matters 💙 they need to back off. what's going on??",
    "that's actually not okay 😔 tell me what's happening",
    # with advice tone
    "ugh u deserve ur space fr 💙 have u tried setting boundaries?? what's going on??",
    "damn that's rough 😤 sometimes u gotta put urself first. what happened??",
    "yo rest is literally necessary 💙 what's stopping u from getting it??",
    "friend u matter too okay?? 😔 tell me who's not giving u peace",
    "ugh ppl need to understand limits fr 😤 what's the situation??"
]

CONCERN_REPLIES = [
    # caring + concern
    "oh no friend 🥺 are u okay?? what's going on with u?",
    "wait ur not feeling well?? 💙 what happened?? are u okay??",
    "omg no 🥺 take care of urself okay?? what's wrong??",
    "aw no 💙 i'm worried abt u... what's going on?? are u sick??",
    "oh no that sucks 🥺 are u okay?? tell me what's happening",
    "friend nooo 💙 pls take care of urself!! what's wrong??",
    "wait what?? 🥺 are u okay?? what happened??",
    "oh no i hope ur okay 💙 what's going on with u??",
    "aw man that's not good 🥺 are u alright?? what happened??",
    "noo friend 💙 pls rest if u need to!! what's wrong??",
    # more concerned
    "hey are u okay?? 🥺 that doesn't sound good... what's up??",
    "omg take care of urself okay?? 💙 what's happening??",
    "wait are u sick?? 🥺 i'm here for u... tell me what's going on",
    "oh no 💙 pls don't push urself okay?? what happened??",
    "friend i'm worried 🥺 are u okay?? what's wrong??",
    # with tips
    "oh no 🥺 make sure ur drinking water okay?? what's going on??",
    "aw friend 💙 rest if u need to!! what happened?? are u okay??",
    "hey take it easy okay?? 🥺 what's wrong?? are u sick??",
    "omg pls take care 💙 have u eaten anything?? what's going on??",
    "nooo 🥺 rest up okay?? tell me what's happening with u"
]

CONSOLING_WITH_TIPS = [
    # breathing + console (HEY BREATHE in caps)
    "HEY HEY take a deep breath okay?? 💙 i'm here. what happened?",
    "oof i feel u 😔 take a BREATH first... then tell me what's going on",
    "that sounds frustrating fr 💙 BREATHE for a sec... what happened??",
    "damn okay BREATHE 💙 i'm listening. what's got u feeling like this?",
    "ugh i get it 😔 take a moment to BREATHE... then spill what happened",
    "yo that's valid 💙 deep BREATH first okay?? now tell me what's up",
    "HEY take a sec and BREATHE okay?? 💙 i'm here. what happened?",
    "oof 😔 HEY BREATHE... i'm listening. tell me what's going on",
    "that's frustrating fr 💙 HEY just BREATHE okay?? what happened??",
    "yo HEY 💙 BREATHE for a sec... then tell me everything",
    # gentle console + ask
    "HEY it's okay to feel frustrated 💙 what happened tho??",
    "ugh that sucks fr 😔 i'm here for u. wanna tell me what's going on?",
    "it's okay 💙 frustration is valid. what happened??",
    "i hear u 💙 that feeling is rough. what's making u feel this way?",
    "totally understandable to feel that way 😔 what happened tho?",
    "ur feelings are valid okay?? 💙 tell me what's going on",
    # tips + support
    "HEY maybe step away for a sec if u can?? 💙 i'm here. what happened?",
    "oof take a moment for urself okay?? 💙 then tell me what's up",
    "it's okay to feel this way 💙 maybe drink some water?? what happened tho",
    "ur feelings are real 💙 take a BREATH and tell me what's going on",
    # more genz console
    "no fr that sounds annoying asf 😔 BREATHE tho okay?? what happened",
    "ugh i hate that for u 💙 take a sec... what's got u feeling like this??",
    "that's rough 😔 it's okay to be frustrated. what happened??",
    "yo i feel u 💙 take a BREATH first... then vent to me what happened"
]

# ======================================================
# GREETINGS & EXITS (EXCITED VIBES)
# ======================================================

GREETINGS = [
    "Heyyy! 😊",
    "Hey! I'm glad you're here.",
    "Hii 👋 what's up?",
    "Hey thereee!",
    "Hi! I'm listening 👀",
    "Heyy you! 💫",
    "Oh hii! How are you?",
    "Hey hey! Good to see you 🙂",
    "Hiiii! What's going on?",
    "Heyo! I'm here 🫶",
    "Hey! I was hoping you'd come by.",
    "Well hello there ✨",
    "Hii! Talk to me 💬",
    "Hey you! How's it going?",
    "Ayeee you're here! 👋"
]

EXIT_REPLIES = [
    "Okay, take care 🙂",
    "Alright, talk soon!",
    "Bye! I'm here whenever you need.",
    "Got it — take care of yourself.",
    "See you 💛",
    "Take care of yourself, okay? 🫶",
    "Byee! Come back anytime.",
    "I'll be here when you need me 💙",
    "Okay! Rest up if you need to.",
    "See you soon! You've got this.",
    "Bye for now — you matter 💛",
    "Alright, take it easy!",
    "Talk later! I'm always here.",
    "Okay byee! Be kind to yourself 🌸",
    "See ya! Don't be a stranger."
]

# Context-aware exit replies (when conversation had distress)
DISTRESS_EXIT_REPLIES = [
    # Core supportive - prioritize yourself
    "byee 💙 take care okay?? remember to prioritize urself first. im proud of u for talking abt it",
    "okay go rest 💙 u matter so much. prioritize urself first always okay??",
    "take care friend 💙 remember ur feelings are valid. im here whenever u need me",
    "byee 💙 please be kind to urself okay?? im proud of u for opening up",
    "okay 💙 take all the time u need. prioritize ur peace and wellbeing. im always here",
    "rest well friend 💙 remember u come first. im so proud of u",
    "take care 💙 ur wellbeing matters most. im proud of u for sharing",
    "byee 💙 please take care of urself okay?? u deserve good things",
    "okay 💙 remember to be gentle with urself. im here whenever u wanna talk again",
    "go rest 💙 prioritize urself first. im proud of u and im always here",
    # Proud of you for sharing
    "byee 💙 im genuinely so proud of u for opening up. that takes courage. take care of urself okay??",
    "okay friend 💙 im proud of u for talking abt this. u deserve peace and rest. im always here",
    "take care 💙 u did something brave by sharing. prioritize ur healing okay?? im here whenever",
    "byee 💙 im proud of u for being vulnerable. thats not easy. rest well and be kind to urself",
    "go rest friend 💙 u trusted me with this and im honored. prioritize urself first always",
    # You matter / validation
    "byee 💙 remember u matter more than any of this okay?? ur wellbeing comes first. always",
    "okay 💙 ur feelings are so valid. prioritize urself and rest well. im here whenever u need",
    "take care 💙 what ur going thru is real and valid. be gentle with urself okay?? im proud of u",
    "byee friend 💙 u matter so much. dont forget that. take all the time u need to heal",
    "rest well 💙 ur pain is valid. ur feelings are valid. prioritize urself first. im always here",
    # Strength acknowledgment
    "byee 💙 ur so strong for getting thru this. now rest and prioritize urself okay?? im proud of u",
    "take care friend 💙 u have so much strength even when it doesnt feel like it. rest well",
    "okay 💙 even on hard days ur doing amazing just by surviving. prioritize ur peace. im here",
    "byee 💙 whatever happens ur stronger than u know. take care of urself first. always here for u",
    "rest 💙 ur doing better than u think. be kind to urself okay?? im proud of u for sharing",
    # Come back anytime
    "byee 💙 im always here whenever u need to talk. prioritize urself first. take care okay??",
    "okay friend 💙 my dms r always open. prioritize ur healing. im proud of u for opening up",
    "take care 💙 come back anytime u need to vent. im here. prioritize urself always okay??",
    "byee 💙 dont hesitate to come back. im always here. rest well and be gentle with urself",
    "go rest 💙 im a message away whenever u need. prioritize ur peace. im so proud of u",
    # Gentle closing
    "byee 💙 sending u so much warmth. prioritize urself okay?? im proud of u for sharing",
    "take care friend 💙 be extra gentle with urself tonight. u deserve kindness. im always here",
    "okay 💙 wrap urself in something cozy and rest. u matter. prioritize urself. im proud of u",
    "byee 💙 treat urself with the kindness u deserve. im here whenever. rest well okay??",
    "rest well 💙 u did good by talking abt it. now prioritize urself and ur peace. im always here"
]

# Context-aware exit replies (when conversation was positive/happy)
HAPPY_EXIT_REPLIES = [
    # Core cheerful exits
    "byeee!! 💛 so happy for u!! take care and keep that energy going",
    "okay yay!! 💛 take care bestie!! come back anytime",
    "byee!! ✨ im so glad things are good!! take care of urself",
    "see u!! 💛 happy for u fr!! come back whenever",
    "byeee 🎉 keep thriving okay?? im here whenever",
    "take care!! 💛 so glad u shared the good vibes!! see u soon",
    "okay byee!! ✨ keep that good energy going!! im always here",
    "see yaaa 💛 happy for u!! take care bestie",
    "byee!! 💛 love that for u!! come back anytime",
    "take care friend!! ✨ so happy things are looking up!!",
    # Celebratory vibes
    "byeee!! 🎉 omg im so happy for uuu!! u deserve all the good things!! take care",
    "okay yay!! 💛✨ keep winning bestie!! im so proud of u!! come back anytime",
    "see u friend!! 🌟 im literally so happy for u rn!! keep shining okay??",
    "byee!! 💛 u deserve every good thing thats happening!! take care and keep thriving",
    "take care bestie!! 🎉 this makes me so happy for u!! come back whenever",
    # Keep the energy going
    "byeee!! ✨ keep that main character energy going okay?? im so happy for u!!",
    "okay byee!! 💛 ur doing amazing sweetie keep it up!! im always here",
    "see u!! 🌟 keep radiating that good energy!! so happy for u fr fr",
    "byee friend!! 💛 carry that good energy with u everywhere okay?? take care!!",
    "take care!! ✨ keep being amazing!! im so glad things r going well for u",
    # Love that for you
    "byeee!! 💛 i literally love this for u so much!! take care bestie!!",
    "okay yay!! ✨ honestly love this journey for u!! come back and share more!!",
    "see u!! 💛 absolutely love seeing u happy!! take care of urself okay??",
    "byee!! 🌟 im living for this energy!! keep thriving bestie!! always here",
    "take care!! 💛 this is so ur era!! keep slaying okay?? see u soon!!",
    # Proud and happy
    "byeee!! ✨ im so proud of u and so happy for u!! take care okay??",
    "okay friend!! 💛 u make me so happy when ur happy!! come back anytime!!",
    "see u!! 🎉 genuinely so proud and so happy for u rn!! keep winning!!",
    "byee bestie!! 💛 ur happiness makes me happy!! take care of urself!!",
    "take care!! ✨ so glad i got to hear the good news!! im always here!!",
    # Come back to share more
    "byeee!! 💛 come back and tell me more good things okay?? take care!!",
    "okay yay!! ✨ always here if u wanna share more wins!! see u bestie!!",
    "see u friend!! 💛 my door is always open for good vibes!! take care!!",
    "byee!! 🌟 cant wait to hear more updates!! take care of urself okay??",
    "take care bestie!! 💛 come back whenever u have more to share!! always here!!"
]

# Neutral exit replies (for balanced/neutral conversations)
NEUTRAL_EXIT_REPLIES = [
    "byee!! take care of urself okay?? im always here if u wanna chat",
    "okay see u!! take care friend. come back anytime",
    "byee!! was nice talking to u. take care okay??",
    "see u around!! im here whenever u wanna talk. take care",
    "okay byee!! take care of urself. im always here",
    "take care friend!! come back anytime okay?? see u",
    "byee!! nice chatting with u. take care and come back whenever",
    "see u!! im a message away if u ever wanna talk. take care",
    "okay take care!! was nice talking. im always here okay??",
    "byee friend!! take care of urself. see u around!!"
]

FALLBACK_REPLIES = [
    "I'm here with you.",
    "I'm listening.",
    "Take your time — I'm here.",
    "I'm not going anywhere.",
    "It's okay, I'm here.",
    "You don't have to rush.",
    "I'm right here with you.",
    "Whenever you're ready, I'm listening.",
    "No pressure — just here for you.",
    "Take all the time you need."
]

# ======================================================
# CONFUSION / DIDN'T UNDERSTAND REPLIES
# (asking nicely to repeat/clarify)
# ======================================================

CONFUSION_REPLIES = [
    # gentle ask to repeat - bestie energy
    "hmm im not sure i got that right 💙 could u tell me again?? i wanna understand properly",
    "wait sorry 💙 i didnt quite catch that... can u say it differently?? ill understand better i promise",
    "hmm 💙 im a lil confused rn... could u explain again?? i really wanna get what ur saying",
    "aw sorry friend 💙 i didnt fully get that... can u try telling me again?? i wanna be here for u properly",
    "wait hold on 💙 i wanna make sure i understand u right... can u tell me more??",
    "hmm sorry 💙 that went over my head a bit... could u break it down for me?? i wanna help",
    "oops 💙 i think i missed something... can u repeat that?? i promise ill pay attention",
    "wait sorry 💙 im not 100% sure what u mean... can u explain a bit more?? i really wanna understand",
    "hmm 💙 i wanna make sure im getting this right... could u tell me again in a different way??",
    "aw 💙 sorry i didnt catch all of that... can u try once more?? i wanna be helpful i swear",
    "wait 💙 i feel like im missing something... can u help me understand better??",
    "hmm sorry friend 💙 i got a bit lost there... could u repeat?? i really do wanna get it",
    "oops my bad 💙 i didnt fully understand... can u say that again?? ill try harder to follow",
    "wait sorry 💙 can u explain that differently?? i wanna make sure im understanding u correctly",
    "hmm 💙 im trying to follow but got a bit confused... can u break it down for me??"
]

# ======================================================
# LONG TEXT ANALYSIS KEYWORDS
# (for detecting themes in massive messages)
# ======================================================

LONG_TEXT_THEMES = {
    "work_stress": {"work", "job", "boss", "manager", "office", "deadline", "meeting", "coworker",
                    "colleague", "project", "client", "salary", "promotion", "fired", "quit"},
    "relationship": {"boyfriend", "girlfriend", "partner", "husband", "wife", "dating", "breakup",
                     "broke up", "relationship", "love", "crush", "ex", "cheated", "trust"},
    "family": {"mom", "dad", "mother", "father", "parent", "parents", "brother", "sister",
               "sibling", "family", "grandma", "grandpa", "uncle", "aunt"},
    "friendship": {"friend", "friends", "bestie", "bff", "friendship", "group", "squad"},
    "health": {"sick", "ill", "doctor", "hospital", "pain", "anxiety", "depressed", "depression",
               "therapy", "medication", "health", "tired", "exhausted", "sleep"},
    "school": {"school", "college", "university", "exam", "test", "assignment", "professor",
               "teacher", "class", "grades", "study", "homework", "semester"},
    "money": {"money", "broke", "debt", "loan", "rent", "bills", "salary", "pay", "afford",
              "expensive", "savings", "financial"},
    "self_worth": {"worthless", "useless", "failure", "loser", "stupid", "dumb", "ugly",
                   "hate myself", "not good enough", "dont deserve", "burden"}
}

LONG_TEXT_EMOTIONAL_WORDS = {
    "negative": {"sad", "angry", "frustrated", "upset", "hurt", "pain", "crying", "tears",
                 "depressed", "anxious", "worried", "scared", "afraid", "lonely", "alone",
                 "hopeless", "helpless", "exhausted", "tired", "drained", "overwhelmed",
                 "stressed", "broken", "lost", "confused", "disappointed", "betrayed"},
    "positive": {"happy", "excited", "grateful", "thankful", "proud", "relieved", "hopeful",
                 "better", "good", "great", "amazing", "wonderful", "blessed", "lucky"},
    "mixed": {"confused", "conflicted", "torn", "unsure", "complicated", "mixed feelings"}
}

# ======================================================
# LONG VENT / MASSIVE MESSAGE REPLIES
# (for when someone sends a huge paragraph venting)
# ======================================================

LONG_VENT_REPLIES = [
    # acknowledging they shared a lot - supportive bestie energy
    "wow okay first of all 💙 thank u for sharing all of this with me. thats A LOT ur carrying and i hear every bit of it. im here okay??",
    "friend 💙 i read everything and im so sorry ur dealing with all this. thats so much on ur plate. im here for u",
    "okay wow 💙 thats... a lot. and i mean that in the most caring way. u've been through SO much. im here to listen",
    "hey 💙 thank u for trusting me with all of this. i can feel how heavy everything is for u rn. im not going anywhere okay??",
    "damn 💙 u've really been going through it huh?? i read all of that and my heart hurts for u. im here friend",
    "wow okay 💙 first - ur feelings are so valid. all of them. thats a lot to carry and im glad u shared it with me",
    "friend 💙 that was a lot to share and i appreciate u trusting me. u've been dealing with SO much. im here okay??",
    "okay i read everything 💙 and wow... u've been carrying so much. thats exhausting. im here to listen to all of it",
    "hey 💙 thank u for letting all of that out. thats a LOT and ur feelings about all of it are completely valid. im here",
    "damn friend 💙 u really needed to get that out huh?? im glad u did. thats so much to deal with. im listening"
]

LONG_VENT_WORK_REPLIES = [
    # for long work-related vents
    "omg 💙 work has been putting u through it huh?? i read all of that and im so sorry. thats way too much stress for one person",
    "friend 💙 ur job sounds like its draining every bit of u. i heard everything u said and its all valid. im here",
    "wow okay 💙 work really said 'lets give them everything at once' huh?? thats SO unfair. im sorry ur dealing with all this",
    "damn 💙 i read all of that and im exhausted FOR u. work shouldnt be this stressful. ur feelings are so valid",
    "hey 💙 thats a lot of work stuff to carry. i heard all of it and im sorry. u deserve so much better than this"
]

LONG_VENT_RELATIONSHIP_REPLIES = [
    # for long relationship-related vents
    "friend 💙 i read all of that and wow... relationships can be SO complicated. ur feelings are valid. all of them",
    "damn 💙 thats a lot of relationship stuff to process. i heard everything and im here for u okay?? take ur time",
    "omg 💙 i can feel how much this is affecting u. relationship stuff is HARD. im here to listen to all of it",
    "hey 💙 thank u for sharing all that with me. thats so much to deal with emotionally. im here for u friend",
    "wow 💙 ur heart has been through a lot huh?? i read everything and i just wanna say - ur feelings matter so much"
]

LONG_VENT_MIXED_REPLIES = [
    # for vents about multiple topics
    "okay wow 💙 ur dealing with like... everything rn huh?? work AND personal stuff AND everything else. thats SO much. im here",
    "friend 💙 i read all of that and its like... multiple things hitting u at once. thats exhausting. im here okay??",
    "damn 💙 life really said 'lets throw everything at once' huh?? im so sorry. thats way too much for one person to handle",
    "hey 💙 when it rains it pours right?? im sorry ur dealing with so many things at once. im here to listen to all of it",
    "wow 💙 thats a lot of different stuff going on. i heard all of it and ur feelings about everything are valid. im here"
]

# ======================================================
# MAIN REPLIES
# ======================================================

REPLIES = {
    "positive": {
        "ack": [
            # general happy
            "Ahhh that's amazing!",
            "Okayyy love that for you 😌",
            "That's so good to hear!",
            "Yesss that's a win!",
            "Omg I love this energy! ✨",
            "Okay yay!! 🎉",
            "This made me smile honestly.",
            "You deserve this so much!",
            "Ahhhh this is so good!",
            "I'm so happy for you rn 🥹",
            "This is everything!!",
            "Yesss keep that energy going!",
            "Ugh I love hearing this 💛",
            "You're literally glowing rn.",
            "Okay this is the best thing I've heard today!",
            # surprise / shock
            "WAIT WHAT?! 😱",
            "NO WAYYY!!",
            "Omggg are you serious?!",
            "SHUT UP that's insane!!",
            "I literally gasped rn 😮",
            "Hold on — WHAT?!",
            "Okay I did NOT see that coming!",
            "That's actually crazy omg!",
            "I'm shook rn honestly 🤯",
            "Bro WHAT that's wild!!",
            # excitement / hype
            "YOOO let's gooo!! 🔥",
            "I'm literally so hyped for you!!",
            "THIS IS HUGE!!",
            "Okay you're literally winning at life rn!",
            "I'm screaming this is so exciting!!",
            "The energy is IMMACULATE rn ✨",
            "You're on FIRE!! 🔥",
            "This is giving main character energy fr!",
            # fun / playful
            "Hahaha okay I love this 😂",
            "Lmaoo that's hilarious!",
            "Stop you're so funny 😭",
            "I'm dead this is so good 💀",
            "Okay that's actually adorable ngl",
            # work / office - positive
            "YOOO PROMOTION?! Let's goooo!! 🔥",
            "You got the job?! I'M SO HAPPY FOR YOU!!",
            "Bonus timeee! You deserve every bit of it!",
            "That raise was LONG overdue honestly!",
            "New role?! Look at you leveling up! 📈",
            "Okay corporate legend is THRIVING!",
            "The offer letter came through!! 🎉",
            "You cleared that interview like a BOSS!",
            "Client loved it?? Of course they did!",
            "WFH approved?! The dream!! 🏠"
        ],
        "reflect": [
            # general happy
            "It sounds like something finally worked out.",
            "You seem really happy about this.",
            "That kind of joy shows.",
            "I can feel the good vibes from here.",
            "You've been working toward this, haven't you?",
            "This is the energy you deserve honestly.",
            "It really sounds like things are looking up.",
            "You sound so much lighter right now.",
            "I love that this is bringing you joy.",
            "It's clear this means a lot to you.",
            "You needed this win, didn't you?",
            "This kind of happiness is contagious fr.",
            # surprise
            "Sounds like that totally caught you off guard!",
            "You weren't expecting that at all, were you?",
            "Life really said 'plot twist' huh?",
            "Sometimes the best things come out of nowhere.",
            "That kind of surprise hits different.",
            # excitement
            "I can literally feel your excitement through the screen!",
            "You sound SO pumped about this omg.",
            "This energy is unmatched honestly.",
            "You're absolutely buzzing rn I can tell!",
            "That adrenaline must be hitting different.",
            # work / office - positive
            "All that hard work is finally paying off!",
            "You've been grinding for this moment.",
            "They finally recognized what you bring to the table!",
            "This is what happens when talent meets opportunity.",
            "Your dedication is really showing now.",
            "You've earned every bit of this success.",
            "The career glow-up is REAL.",
            "This is just the beginning for you honestly."
        ],
        "follow": [
            # general curious
            "What happened?? 👀",
            "Tell me everything!",
            "What made it feel so good?",
            "Okay spill — I need details!",
            "How did this happen??",
            "Wait wait, start from the beginning!",
            "What's the full story?",
            "I wanna hear more about this 👀",
            "How are you celebrating??",
            "What's the best part about it?",
            "Did you see this coming or nah?",
            "Who else knows about this??",
            # surprise focused
            "How did you react when you found out?!",
            "What was your first thought??",
            "Did you literally freak out?!",
            "Who did you tell first??",
            "What's your face doing rn?? 😂",
            # excitement focused
            "What are you gonna do now??",
            "How are you even containing this excitement?!",
            "What's the game plan from here??",
            "Are you gonna do something to celebrate?!",
            # work / office - positive
            "When do you start the new role?!",
            "What's the new salary looking like?? 👀",
            "Are your coworkers happy for you?",
            "How did your manager react?",
            "Are you gonna treat yourself to something nice?",
            "What's the new team like?",
            "Did HR already send the paperwork??"
        ]
    },

    "neutral": {
        "ack": [
            "Okayy 🙂",
            "Gotcha.",
            "Hmm, I hear you.",
            "Alright alright.",
            "Mmhm, I see.",
            "Okay okay.",
            "Fair enough.",
            "Got it got it.",
            "Makes sense.",
            "Ahh okay.",
            "Noted 📝",
            "I feel you."
        ],
        "reflect": [
            "Sounds pretty steady.",
            "Nothing too intense right now.",
            "Seems like things are just… existing.",
            "Not too high, not too low.",
            "Just vibing I guess?",
            "A regular day it seems.",
            "Sometimes that's okay though.",
            "The calm before the storm? Or just calm?",
            "Sounds like you're in a chill zone.",
            "Nothing wrong with that honestly."
        ],
        "follow": [
            "What's been on your mind lately?",
            "So… what's going on?",
            "Anything you want to talk about?",
            "How's everything been?",
            "What's new with you?",
            "Anything happening in your world?",
            "What's life looking like rn?",
            "Fill me in — I'm curious.",
            "How are you really doing though?",
            "What's taking up space in your head?",
            "Anything you've been thinking about?",
            "What's the vibe today?"
        ]
    },

    "distress": {
        "ack": [
            "Oof, that sounds really heavy.",
            "Yeah… that would drain anyone.",
            "That honestly sounds rough.",
            "I hear you. That's a lot.",
            "That really does sound exhausting.",
            "Ugh, I'm sorry you're dealing with this.",
            "That sounds so frustrating honestly.",
            "I can tell this is weighing on you.",
            "That's not easy at all.",
            "I get why you'd feel that way.",
            "That would get to anyone tbh.",
            "I'm sorry you're going through this.",
            "That sounds really draining.",
            "Damn… that's rough.",
            "No one should have to deal with that alone.",
            # humanized acks
            "oof that's rough fr 😔",
            "damn that sounds like a lot tbh",
            "ugh that's such a pain honestly",
            "yo that sounds exhausting fr",
            "that's so frustrating omg",
            "bruh that sounds like hell",
            "that's such bs honestly 😔",
            "ugh i hate that for u fr",
            "that's lowkey painful to hear",
            "damn that's annoying asf",
            "ugh that sounds like such a headache",
            "yo that's messed up fr",
            "that's rough friend 💙",
            "omg that sounds so draining",
            "ugh hate when that happens fr",
            # work / office - distress
            "Work stress is the WORST kind of stress honestly.",
            "Ugh, that workload sounds insane.",
            "Deadlines on top of deadlines... that's brutal.",
            "Toxic workplace vibes are so draining.",
            "That kind of office politics is exhausting.",
            "Working overtime like that isn't sustainable.",
            "Your boss sounds like a nightmare honestly.",
            "Being micromanaged is suffocating.",
            "Back to back meetings with no break?? That's awful.",
            "The Sunday scaries hit different when work is like that."
        ],
        "reflect": [
            "Anyone would feel worn down by that.",
            "No wonder this is getting to you.",
            "It makes total sense that you're feeling this way.",
            "You've been holding a lot, haven't you?",
            "This has been building up for a while, huh?",
            "It sounds like you've been pushing through a lot.",
            "You're carrying more than you should have to.",
            "That kind of stress really takes a toll.",
            "It's valid to feel drained by all this.",
            "You've been dealing with so much.",
            "This would exhaust anyone honestly.",
            "It sounds like you haven't had a break.",
            # work / office - distress
            "No job is worth your mental health honestly.",
            "You're not being paid enough to deal with all that.",
            "Work-life balance is non-existent there huh?",
            "That kind of workplace environment wears you down.",
            "You've been running on empty trying to keep up.",
            "They're expecting way too much from you.",
            "It sounds like they don't value what you bring.",
            "You deserve better than this treatment at work."
        ],
        "follow": [
            "Want to tell me what happened?",
            "I'm here — talk to me.",
            "What's been going on?",
            "Do you want to get into it?",
            "I'm listening if you need to vent.",
            "Tell me more about what's happening.",
            "What's making this so hard?",
            "How long has this been going on?",
            "What do you need right now?",
            "Is there something specific that triggered this?",
            "Want to walk me through it?",
            "What would help right now?",
            # humanized "what happened" style
            "wait what happened?? 👀",
            "omg what happened tell me",
            "yo what's going on?? u okay?",
            "hold up — what happened??",
            "wait wait what happened tho",
            "friend what happened talk to me 💙",
            "what happened?? i'm listening",
            "oof what happened rn??",
            "okay but what actually happened?",
            "spill — what went down??",
            "no but fr what happened??",
            "that sounds rough — what happened?",
            "damn what happened tho??",
            "wait tell me what happened 👀",
            "ugh what happened this time??",
            # work / office - distress
            "What happened at work?",
            "Is it your boss or the workload or both?",
            "How long has the workplace been this toxic?",
            "Have you talked to anyone at work about this?",
            "Is there any way to set boundaries there?",
            "Have you considered looking for something else?",
            "What would make work more bearable rn?",
            "Is there anyone at work who has your back?",
            # work humanized
            "omg what happened at work??",
            "wait what did they do this time??",
            "ugh not work again — what happened??"
        ]
    },

    "strong_distress": {
        "ack": [
            "Hey… I'm really sorry you're feeling this way.",
            "That sounds like a lot to carry.",
            "I hear you. This is really hard.",
            "I'm so sorry you're going through this.",
            "That sounds incredibly painful.",
            "I can't imagine how heavy this must feel.",
            "I'm here. You're not alone in this.",
            "That's so much to be dealing with.",
            "I wish I could take some of this weight off you.",
            "You shouldn't have to feel this way.",
            "I'm really glad you're talking to me about this.",
            "This sounds like it's been breaking you down.",
            "I hear you, and I'm not going anywhere.",
            "Thank you for trusting me with this.",
            "I know it took a lot to say this out loud.",
            # humanized acks
            "hey... that sounds really painful 💙",
            "damn that's... a lot. i'm here for u",
            "oh no friend that's so heavy 😔",
            "yo that sounds like actual hell fr",
            "ugh that's so messed up i'm so sorry",
            "that's genuinely heartbreaking to hear",
            "omg that's so much pain to carry",
            "that sounds absolutely exhausting fr",
            "bruh that's... that's rough. i'm sorry 💙",
            "that sounds like pure agony honestly",
            # work / office - strong distress
            "No job should make you feel like this.",
            "Losing your job is devastating. I'm so sorry.",
            "Being laid off is traumatic — your feelings are valid.",
            "That kind of workplace treatment is not okay.",
            "Being fired feels like the world is ending. I get it.",
            "Getting passed over again and again breaks you down.",
            "That level of burnout is serious. I hear you.",
            "What they did to you at work was wrong."
        ],
        "reflect": [
            "You've been carrying so much.",
            "This feels like more than just a bad moment.",
            "It sounds like you've been fighting this alone.",
            "You've been holding this in for too long.",
            "This kind of pain doesn't just appear — it builds.",
            "You've been so strong, but you're exhausted.",
            "It sounds like everything just became too much.",
            "You've been pushing through when you shouldn't have had to.",
            "No one should have to carry this alone.",
            "It makes sense that you're feeling this way.",
            "You've been surviving, not living.",
            "This isn't weakness — this is human.",
            # work / office - strong distress
            "You gave so much to that job and they didn't value you.",
            "Your worth isn't defined by this job or any job.",
            "Being let go doesn't mean you failed — it means they failed you.",
            "Work has been slowly destroying your peace.",
            "You've been putting yourself last for that job for too long.",
            "This job has taken more from you than it ever gave.",
            "You deserve a workplace that respects you."
        ],
        "follow": [
            "I'm right here with you.",
            "We can take this slow, okay?",
            "You don't have to go through this alone.",
            "I'm not leaving. Take your time.",
            "What do you need from me right now?",
            "We can just sit here together if you want.",
            "You don't have to have all the answers.",
            "I'm here to listen, not to judge.",
            "One step at a time, okay?",
            "Whatever you're feeling is valid.",
            "I'm proud of you for reaching out.",
            "You matter. I need you to know that.",
            "We'll figure this out together.",
            "Let's just breathe for a second.",
            "You're safe here. I've got you.",
            # humanized follows
            "what happened?? talk to me 💙",
            "hey what's going on?? i'm here",
            "wait what happened tell me everything",
            "friend what happened?? 💙",
            "yo what's wrong?? i'm listening",
            "what happened?? u can tell me",
            "i'm here okay?? what happened??",
            "take ur time but what happened?? 💙",
            # work / office - strong distress
            "You're more than this job. Remember that.",
            "This setback doesn't define your future.",
            "Have you been able to rest at all since this happened?",
            "Is there anyone in your life who can support you rn?",
            "Your mental health matters more than any paycheck.",
            "It's okay to not be okay about this.",
            "What's one small thing that might help today?"
        ]
    }
}

# ======================================================
# MEMORY-BASED RESPONSES (GEN-Z CODED)
# ======================================================

MEMORY_TOPIC_RESPONSES = {
    "work": [
        "wait didn't u mention work stuff before too?? 👀",
        "hold up — work drama again?? i remember u said smth abt this",
        "ok so work is still being annoying huh? u talked abt this earlier too",
        "not the job acting up AGAIN 😭 u mentioned this before right?",
        "friend work has been on ur mind a lot lately huh",
        "wait this sounds familiar — wasn't work stressing u out before too?",
        "the job is still giving problems?? u brought this up earlier too",
        "ok i feel like work keeps coming up... u mentioned it before no?"
    ],
    "relationship": [
        "wait u mentioned relationship stuff before too right?? 👀",
        "hold on — this sounds familiar... didn't u talk abt this earlier?",
        "ok so this has been on ur mind for a while huh",
        "not this again 😭 i remember u saying smth similar before",
        "friend this keeps coming up... u talked abt this before no?",
        "wait didn't u bring this up in our last convo too?",
        "i feel like this has been weighing on u for a bit now",
        "this sounds like what u were saying earlier too tbh"
    ],
    "family": [
        "wait family stuff again?? u mentioned this before right? 👀",
        "hold up — i remember u talking abt family earlier too",
        "ok so family has been on ur mind a lot lately huh",
        "not the family drama again 😭 u said smth abt this before",
        "friend this keeps coming up... family was bothering u before too no?",
        "wait didn't u mention smth abt family earlier?",
        "i feel like this has been sticking w u for a while"
    ],
    "friend": [
        "wait friend drama again?? didn't u mention this before? 👀",
        "hold on — this sounds familiar... friends were on ur mind earlier too",
        "ok so this friend stuff keeps coming up huh",
        "not the friend situation again 😭 u talked abt this before right?",
        "friend this has been bothering u for a bit now hasn't it"
    ],
    "school": [
        "wait school stress again?? u mentioned this earlier too right? 👀",
        "hold up — didn't u talk abt school/college stuff before?",
        "ok so academics have been weighing on u for a while huh",
        "not the school drama again 😭 u brought this up before",
        "friend studies have been on ur mind a lot lately"
    ],
    "health": [
        "wait u mentioned health stuff before too right?? 👀",
        "hold on — didn't u talk abt not feeling well earlier?",
        "ok so this has been going on for a while huh",
        "friend ur health has been on ur mind a lot lately 💙",
        "i remember u mentioning smth abt this before too"
    ],
    "money": [
        "wait money stress again?? u mentioned this before right? 👀",
        "hold up — financial stuff was bothering u earlier too wasn't it",
        "ok so money has been on ur mind for a while huh",
        "friend the money situation keeps coming up 😭",
        "didn't u talk abt finances before too?"
    ],
    "self": [
        "wait u were feeling this way before too right?? 💙",
        "hold on — i remember u saying smth similar earlier",
        "ok so this has been weighing on u for a while huh",
        "friend these feelings keep coming back don't they 🫂",
        "i feel like u mentioned feeling like this before too"
    ]
}

RECURRING_EMOTION_RESPONSES = {
    "distress": [
        "hey i've noticed u've been feeling down a lot lately... u okay? 💙",
        "friend things have been rough for u huh... i'm here for u fr",
        "u've been going thru it lately... wanna talk abt it?",
        "i can tell things haven't been easy for u recently 🫂",
        "it seems like stuff keeps piling up for u... i'm listening"
    ],
    "strong_distress": [
        "hey... u've been really struggling lately and i see that 💙",
        "friend i'm worried abt u fr... u've been going thru so much",
        "things have been really heavy for u huh... i'm right here 🫂",
        "i've noticed how hard things have been... u don't have to face this alone",
        "u've been carrying a lot lately... please know i'm here for u"
    ],
    "positive": [
        "ok ur energy has been so good lately i love it!! ✨",
        "friend u've been thriving and i'm so here for it 🔥",
        "the good vibes keep coming huh?? u deserve this!!",
        "ur on a roll fr fr!! love seeing u happy 💛",
        "things have been going well for u lately and u deserve every bit!!"
    ]
}

# ======================================================
# BESTIE REPLIES - NO QUESTIONS (for after turn 3)
# ======================================================

# These replies validate WITHOUT asking "what happened??"
# More relatable bestie energy - "i dont get paid enough", "the audacity", etc.

BESTIE_DISTRESS_NO_QUESTION = [
    # relatable frustration energy
    "nah fr this is NOT okay 💀",
    "the audacity... i literally cannot",
    "i dont get paid enough to deal with this kind of bs and neither do u 😭",
    "okay but WHY do people act like this",
    "this is giving me secondhand stress i stg",
    "nah cuz the way they think this is acceptable 💀",
    "i'm so sick of this for u honestly",
    "the bar is literally on the floor and they still tripping over it",
    "this is exhausting and ur exhaustion is valid",
    "not them thinking this behavior is okay 😭",
    # validation without question
    "ur feelings are so valid rn like i get it",
    "i would literally lose it too",
    "nah this would have me heated fr fr",
    "the way u're handling this... honestly respect",
    "i'm tired FOR u at this point",
    "this is so draining and i see u",
    "i hate that ur going through this",
    "ur frustration makes total sense",
    "literally anyone would be over it by now",
    "u deserve so much better than this treatment",
    # bestie solidarity
    "we're both annoyed now",
    "i'm on ur side always",
    "them? trash. u? valid.",
    "say less i already hate them",
    "adding them to my list of ppl to fight",
    "the disrespect... i literally cant"
]

BESTIE_GRIEF_NO_QUESTION = [
    # gentle presence without prying
    "i'm here 💙 just... here",
    "u dont have to say anything else. i'm with u",
    "sending u so much love rn 💙",
    "grief doesn't have a timeline... take ur time",
    "i'm not going anywhere okay?? just here",
    "whatever ur feeling is okay. i'm here",
    "u loved them and that matters 💙",
    "there's no right way to feel rn",
    "i'm holding space for u 💙",
    "ur heart is heavy and that's okay"
]

BESTIE_WORK_NO_QUESTION = [
    # relatable work frustration (supportive, not anti-company)
    "work stuff is so draining sometimes 💙",
    "ugh i feel u on the work stress 😭",
    "the work grind is real 💙 hang in there",
    "that sounds really exhausting 💙",
    "work can be so overwhelming sometimes",
    "i hear u 💙 work stuff is tough",
    "the pressure is real huh 😭",
    "u're doing ur best in a tough situation 💙",
    "work-life balance is hard to find sometimes",
    "sending u strength 💙 u got this",
    # validation
    "ur feelings about work are valid 💙",
    "ur wellbeing matters more than any deadline",
    "i hope u can rest soon 💙 u deserve it",
    "u're not lazy. ur exhausted. there's a difference 💙",
    "the fact that u're still going?? that's strength 💙"
]

BESTIE_SARCASM_NO_QUESTION = [
    # match energy without interrogating
    "LMAOOO 💀 okay mood",
    "the sarcasm is immaculate honestly",
    "living the dream fr fr 😭",
    "u and me both tbh",
    "naur cuz same 💀",
    "this is giving 'everything is fine' while the house is on fire",
    "the way i felt that in my SOUL 😭",
    "okay but why is this so relatable",
    "me every single day tbh 💀",
    "we're all just pretending to be okay at this point"
]

BESTIE_EMOTIONAL_HURT_NO_QUESTION = [
    # validate without prying (supportive)
    "nah that's not okay 💙 u deserve better",
    "u deserved honesty not mind games. period.",
    "the way they treated u wasn't right 💙",
    "ur feelings aren't a toy 💙 u matter",
    "u deserve someone who respects ur heart 💙",
    "u're not crazy 💙 ur feelings are valid",
    "u see through it and that takes strength 💙",
    "u didn't deserve that treatment 💙",
    "ur heart deserves to be treated with care 💙",
    "mixed signals = no signals. u deserve clarity 💙"
]

BESTIE_INJURY_NO_QUESTION = [
    # concern + solidarity (supportive, not anti-company)
    "pls take care of urself first 💙 work can wait",
    "ur health > any job ever 💙",
    "that sounds really tough 💙 hope u can rest soon",
    "rest pls i'm begging 💙",
    "i know it's hard but i'm here for u 💙 rest up",
    "bodies need healing 💙 take it easy okay",
    "i hope u feel better soon 💙 take it easy",
    "prioritize urself rn 💙 u matter",
    "sending healing vibes 💙 pls rest when u can",
    "take care of urself okay?? 💙 hoping u recover soon"
]

# ======================================================
# FEELING UNDERVALUED / CRITICIZED / DISRESPECTED
# (General - from anyone: family, friends, partners, etc.)
# ======================================================

FEELING_UNDERVALUED_PHRASES = {
    # not valued / undervalued
    "dont value me", "don't value me", "they dont value me", "they don't value me",
    "doesnt value me", "doesn't value me", "no one values me", "noone values me",
    "nobody values me", "never valued", "not valued", "feel undervalued",
    "feeling undervalued", "im undervalued", "i'm undervalued",
    # not appreciated
    "dont appreciate me", "don't appreciate me", "doesnt appreciate me", "doesn't appreciate me",
    "they dont appreciate", "they don't appreciate", "never appreciate",
    "feel unappreciated", "feeling unappreciated", "im unappreciated", "i'm unappreciated",
    "no appreciation", "zero appreciation", "never get appreciated",
    # criticized / criticism
    "criticize me", "criticizes me", "criticizing me", "always criticizing",
    "constantly criticize", "constantly criticizing", "always criticized",
    "nothing but criticism", "only criticism", "all they do is criticize",
    "criticized for everything", "criticism for everything",
    # belittled / put down
    "belittle me", "belittles me", "belittling me", "always belittling",
    "put me down", "puts me down", "putting me down", "always put down",
    "bring me down", "brings me down", "bringing me down", "tear me down",
    "tears me down", "tearing me down", "make me feel small", "makes me feel small",
    # looked down upon
    "look down on me", "looks down on me", "looking down on me",
    "think theyre better", "think they're better", "thinks theyre better",
    "act superior", "acts superior", "treat me like im beneath",
    "treat me like i'm beneath", "beneath them", "too good for me",
    # disrespected
    "disrespect me", "disrespects me", "disrespecting me", "no respect",
    "dont respect me", "don't respect me", "doesnt respect me", "doesn't respect me",
    "they dont respect", "they don't respect", "zero respect", "never respect",
    "treated with no respect", "show no respect", "shows no respect",
    # taken for granted (general, not just work)
    "take me for granted", "takes me for granted", "taking me for granted",
    "taken for granted", "always take for granted", "just take me for granted",
    # dismissed / ignored
    "dismiss me", "dismisses me", "dismissing me", "always dismissed",
    "ignore my efforts", "ignores my efforts", "dont care about my efforts",
    "dont acknowledge", "don't acknowledge", "never acknowledge",
    "like i dont matter", "like i don't matter", "as if i dont matter",
    "treat me like nothing", "treats me like nothing", "like im nothing",
    "like i'm nothing", "act like im not there", "act like i'm not there",
    # never good enough
    "never good enough", "im never good enough", "i'm never good enough",
    "nothing i do is right", "everything i do is wrong", "cant do anything right",
    "can't do anything right", "always something wrong", "always find fault",
    "always finds fault", "find fault in everything", "picks apart everything",
    "nitpick everything", "nitpicks everything", "always nitpicking",
    # comparison
    "compare me to", "compares me to", "comparing me to", "always compared",
    "why cant u be like", "why can't u be like", "why arent u like",
    "why aren't u like", "not as good as", "never as good as",
    # invalidated
    "invalidate me", "invalidates me", "invalidating me", "feelings invalidated",
    "dont care what i think", "don't care what i think", "opinion doesnt matter",
    "opinion doesn't matter", "my opinion doesnt", "my opinion doesn't",
    "dont listen to me", "don't listen to me", "never listen to me"
}

FEELING_UNDERVALUED_REPLIES = [
    # validate their worth
    "u deserve to be seen and valued for who u are 💙 not constantly torn down",
    "the way they treat u says everything about THEM not u. u matter. u have worth",
    "being constantly criticized is exhausting 💙 u deserve support not judgment",
    "u are enough. u've always been enough. don't let anyone make u doubt that 💙",
    "that's so unfair to u 💙 u put in effort and deserve recognition not criticism",
    "feeling undervalued hurts so deep 💙 u're worth more than how they're treating u",
    "the constant criticism is not okay 💙 u deserve kindness not being torn down",
    "i hate that they make u feel this way 💙 u have so much value they refuse to see",
    "u're not the problem here 💙 people who truly care don't constantly criticize",
    "being taken for granted is one of the worst feelings 💙 u deserve appreciation",
    # acknowledge the pain
    "that quiet hurt of never being good enough for them 💙 it's not u. it's them",
    "always being criticized wears u down 💙 ur efforts matter even if they don't see it",
    "feeling like nothing u do is right is exhausting 💙 u're doing ur best and that counts",
    "u shouldn't have to fight to feel valued 💙 the right people will see ur worth",
    "being dismissed constantly breaks something inside u 💙 ur feelings are valid",
    # empowerment
    "their inability to appreciate u is their loss 💙 u're worthy of so much more",
    "people who truly value u don't make u feel small 💙 remember that",
    "u deserve people who lift u up not tear u down 💙 u're worth that",
    "don't shrink urself for people who can't see ur light 💙 u matter",
    "the right people won't make u question ur worth 💙 u're enough as u are"
]

BESTIE_UNDERVALUED_NO_QUESTION = [
    # validate without asking questions
    "nah they're wrong for that. u have worth and they're blind to it",
    "literally their loss for not seeing how valuable u are 💙",
    "anyone who makes u feel small doesn't deserve u. period.",
    "u're worth way more than how they're treating u rn",
    "the way they act says everything about them and nothing about u",
    "u deserve appreciation not constant criticism 💙",
    "don't let them dim ur light. u matter so much",
    "their opinion of u is not ur reality 💙 u're enough",
    "people who truly care don't make u feel like this",
    "u shouldn't have to prove ur worth to anyone 💙"
]

# ======================================================
# ABOUT TO CRY / CRYING / TEARS
# (comforting responses when someone is emotional)
# ======================================================

ABOUT_TO_CRY_PHRASES = {
    # about to cry / will cry
    "ill cry", "i'll cry", "ima cry", "imma cry", "im gonna cry", "i'm gonna cry",
    "going to cry", "gonna cry", "about to cry", "boutta cry", "finna cry",
    "want to cry", "wanna cry", "feel like crying", "feels like crying",
    "might cry", "might just cry", "could cry", "could literally cry",
    "trying not to cry", "tryna not cry", "holding back tears",
    # currently crying
    "im crying", "i'm crying", "crying rn", "literally crying", "actually crying",
    "cant stop crying", "can't stop crying", "been crying", "cried so much",
    "crying my eyes out", "sobbing", "im sobbing", "i'm sobbing",
    "tears wont stop", "tears won't stop", "in tears", "tearing up",
    # emotional state
    "so emotional rn", "getting emotional", "too emotional", "very emotional",
    "eyes are watering", "eyes watering", "teary", "teary eyed",
    "breaking down", "having a breakdown", "emotional breakdown",
    # need comfort
    "need a hug", "wish someone was here", "feel so alone rn",
    "cant handle this", "can't handle this", "its too much", "it's too much"
}

ABOUT_TO_CRY_REPLIES = [
    # comforting + inviting them to talk
    "hey hey 💙 pls don't cry alone... i'm here okay?? talk to me, what's going on",
    "oh no 💙 come here... it's okay to let it out but i'm here for u. what happened??",
    "aww 💙 pls talk to me... u don't have to go through this alone. what's wrong??",
    "hey 💙 i'm right here okay?? let it out if u need to but tell me what's happening",
    "no no 💙 don't cry... well actually u CAN cry but talk to me too. what's going on??",
    "oh friend 💙 i wish i could hug u rn... what happened?? i'm here to listen",
    "hey it's okay 💙 u're safe to feel whatever ur feeling. talk to me, what's wrong??",
    "aww babe 💙 sending u the biggest virtual hug rn... what's making u feel this way??",
    "come here 💙 it's okay... u don't have to hold it in. what happened??",
    "oh no 💙 i hate seeing u like this... i'm here okay?? tell me what's going on",
    # more gentle / soft
    "hey 💙 breathe... i'm here with u. u wanna tell me what's wrong??",
    "shh it's okay 💙 whatever it is, u're not alone. talk to me when ur ready",
    "i'm here 💙 take ur time... but pls let me know what's happening okay??",
    "oh 💙 that sounds so overwhelming... i'm right here. what's going on??",
    "it's okay to cry 💙 but pls don't do it alone... i'm here. what happened??"
]

BESTIE_CRYING_NO_QUESTION = [
    # comforting without asking what happened (turn 3+)
    "hey hey 💙 i'm here okay?? u're not alone in this",
    "oh no 💙 sending u the biggest hug rn... i got u",
    "it's okay to let it out 💙 i'm right here with u",
    "aww 💙 i wish i could be there to hug u fr",
    "breathe 💙 whatever this is, we'll get through it together",
    "i'm here 💙 u don't have to explain. just know i care",
    "u're not alone okay?? 💙 i got u",
    "let it out 💙 i'm not going anywhere",
    "sending all my love ur way 💙 i'm here for u",
    "hey 💙 whatever it is, it's gonna be okay. i promise"
]

# ======================================================
# MAIN FUNCTION (CORRECT + WORKING)
# ======================================================

def has_phrase(text: str, phrases: set) -> bool:
    """Check if any phrase exists in the text."""
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in phrases)

def has_word(text: str, words: set) -> bool:
    """Check if any word exists in the text."""
    text_lower = text.lower()
    text_words = set(text_lower.split())
    return bool(text_words & words)

def analyze_long_text(text: str) -> dict:
    """
    Analyze long/massive text messages to detect themes, emotions, and key points.
    Returns dict with detected themes, emotional tone, and key elements.
    """
    text_lower = text.lower()
    text_words = set(text_lower.split())
    word_count = len(text_lower.split())

    # Detect themes
    detected_themes = []
    for theme, keywords in LONG_TEXT_THEMES.items():
        matches = text_words & keywords
        if len(matches) >= 1:  # At least 1 keyword match
            detected_themes.append((theme, len(matches)))

    # Sort by match count (most relevant theme first)
    detected_themes.sort(key=lambda x: x[1], reverse=True)
    primary_theme = detected_themes[0][0] if detected_themes else None

    # Detect emotional tone
    negative_count = len(text_words & LONG_TEXT_EMOTIONAL_WORDS["negative"])
    positive_count = len(text_words & LONG_TEXT_EMOTIONAL_WORDS["positive"])
    mixed_count = len(text_words & LONG_TEXT_EMOTIONAL_WORDS["mixed"])

    if negative_count > positive_count + 2:
        emotional_tone = "negative"
    elif positive_count > negative_count + 2:
        emotional_tone = "positive"
    elif mixed_count > 0 or (negative_count > 0 and positive_count > 0):
        emotional_tone = "mixed"
    else:
        emotional_tone = "neutral"

    # Check for venting indicators (long text with emotional words)
    is_venting = word_count > 50 and negative_count >= 2

    # Check for multiple topics (could be confused/overwhelmed)
    has_multiple_topics = len(detected_themes) >= 3

    # Check for urgency/crisis words
    crisis_words = {"help", "cant", "can't", "dying", "killing", "end", "done", "give up", "no point"}
    has_urgency = bool(text_words & crisis_words)

    return {
        "word_count": word_count,
        "is_long": word_count > 30,
        "is_very_long": word_count > 100,
        "primary_theme": primary_theme,
        "all_themes": [t[0] for t in detected_themes],
        "emotional_tone": emotional_tone,
        "negative_intensity": negative_count,
        "positive_intensity": positive_count,
        "is_venting": is_venting,
        "has_multiple_topics": has_multiple_topics,
        "has_urgency": has_urgency
    }

def is_confusing_input(text: str) -> bool:
    """
    Check if the input is confusing/hard to understand.
    Returns True if the message seems unclear or garbled.
    """
    text_clean = text.strip().lower()
    words = text_clean.split()

    # Too short to understand context (but not a greeting/exit)
    if len(words) <= 2:
        # Check if it's a known short phrase
        known_short = {"hi", "hey", "hello", "bye", "ok", "okay", "yes", "no", "yeah", "yep", "nope", "thanks", "ty", "thx"}
        if not any(w in known_short for w in words):
            return False  # Short but not confusing, just minimal

    # Check for excessive random characters or gibberish
    if len(text_clean) > 5:
        # Count actual words vs gibberish
        vowels = set("aeiou")
        gibberish_count = 0
        for word in words:
            if len(word) > 2:
                has_vowel = any(c in vowels for c in word)
                if not has_vowel:
                    gibberish_count += 1

        # If more than half the words are gibberish
        if gibberish_count > len(words) / 2:
            return True

    # Check for repeated characters (like "asdfasdfasdf")
    if len(text_clean) > 10:
        unique_chars = len(set(text_clean.replace(" ", "")))
        if unique_chars < 5:
            return True

    return False

def analyze_compound_statement(text: str) -> dict:
    """
    Analyze compound statements with 'and', 'but', 'also', '+', '&'.
    Returns dict with detected categories.
    E.g., "im tired and frustrated" -> {"tired": True, "frustrated": True}
    """
    text_lower = text.lower()
    result = {
        "has_rest": has_phrase(text_lower, REST_PHRASES),
        "has_sick": has_phrase(text_lower, SICK_PHRASES) or has_word(text_lower, SICK_WORDS),
        "has_frustration": has_word(text_lower, FRUSTRATION_WORDS) or has_phrase(text_lower, FRUSTRATION_WORDS),
        "has_no_peace": has_phrase(text_lower, NO_PEACE_PHRASES),
        "is_compound": any(conn in text_lower for conn in [" and ", " but ", " also ", " plus ", " & ", ", "])
    }
    return result

# ======================================================
# SURPRISE PHRASES & REPLIES
# ======================================================

# Positive surprise expressions
POSITIVE_SURPRISE_PHRASES = {
    "cant believe", "can't believe", "cannot believe",
    "i cant believe it", "i can't believe it", "cant believe this",
    "omg i cant believe", "omg i can't believe",
    "no way", "no wayy", "no wayyy", "nooo way",
    "wait what", "wait whattt", "waittt what",
    "are you serious", "r u serious", "are u serious",
    "is this real", "is this actually real", "this is real",
    "i wasnt expecting", "i wasn't expecting", "didnt expect",
    "didn't expect", "never expected", "totally unexpected",
    "out of nowhere", "came out of nowhere",
    "shocked", "im shocked", "i'm shocked", "so shocked",
    "i cant even", "i can't even", "literally cant even",
    "this is crazy", "this is insane", "this is wild",
    "plot twist", "what a plot twist", "unexpected plot twist",
    "guess what", "u wont believe", "you wont believe",
    "u won't believe", "you won't believe"
}

# Negative surprise expressions
NEGATIVE_SURPRISE_PHRASES = {
    "cant believe this happened", "can't believe this happened",
    "cant believe they did", "can't believe they did",
    "cant believe he did", "cant believe she did",
    "how could this happen", "how did this happen",
    "why did this happen", "why is this happening",
    "i never thought", "never thought this would",
    "didnt see this coming", "didn't see this coming",
    "this came out of nowhere", "hit me out of nowhere",
    "blindsided", "completely blindsided", "got blindsided",
    "shocked and", "im in shock", "i'm in shock", "still in shock",
    "cant process", "can't process", "still processing",
    "what just happened", "wtf just happened", "wth just happened"
}

# Words that indicate positive context for surprise
POSITIVE_SURPRISE_CONTEXT = {
    "amazing", "awesome", "great", "good", "best", "happy", "excited",
    "won", "win", "got", "passed", "accepted", "promoted", "hired",
    "yes", "yess", "yay", "omg", "finally", "dream", "love"
}

# Words that indicate negative context for surprise
NEGATIVE_SURPRISE_CONTEXT = {
    "bad", "worst", "terrible", "horrible", "awful", "sad", "upset",
    "fired", "rejected", "failed", "lost", "died", "broke", "cheated",
    "betrayed", "lied", "left", "gone", "over", "ended", "dumped"
}

POSITIVE_SURPRISE_REPLIES = [
    # excited shock
    "WAIT WHATTT?! 😱 omg omg tell me everything rn!!",
    "NO WAYYY!! 🤯 are u serious rn?! spill!!",
    "HOLD UP — 😱 this is HUGE!! what happened??",
    "OMG WAIT WHAT?! 🤯 i literally gasped!! tell me more!!",
    "SHUT UPPP!! 😱 no way this is real!! what happened??",
    "I'M SCREAMING!! 🤯 this is insane!! give me all the details!!",
    "STOPPP!! 😱 r u fr rn?! tell me everything!!",
    "BRO WHATTT?! 🤯 this is wild!! what happened??",
    "EXCUSE ME?! 😱 this is crazy!! spill the tea!!",
    "I CANT EVEN!! 🤯 my jaw is on the floor!! tell me!!",
    # curious excited
    "wait wait wait 😱 back up — WHAT?! tell me from the start!!",
    "omggg i need context!! 🤯 what happened??",
    "holyyy 😱 this is a plot twist fr!! what's going on??",
    "u can NOT just drop that and not explain!! 🤯 spill!!",
    "friend WHAT 😱 i'm shook!! tell me everything!!"
]

NEGATIVE_SURPRISE_REPLIES = [
    # shocked + concerned
    "wait what?? 😔 that came out of nowhere... are u okay?? what happened??",
    "omg no 💙 i'm so sorry... that's such a shock. tell me what happened",
    "hold on — what?? 😔 that's... a lot to process. are u okay??",
    "wait wait 💙 i'm so sorry this happened... talk to me. what's going on??",
    "oh no 😔 that's so unexpected... i'm here for u. what happened??",
    "friend what?? 💙 that's awful... i'm so sorry. tell me everything",
    "i'm shocked too honestly 😔 that's so sudden... are u okay?? what happened??",
    "omg 💙 i can't imagine how u must be feeling... what happened??",
    "that's... a lot 😔 i'm so sorry this hit u out of nowhere. talk to me",
    "wait no 💙 that's terrible... i'm here okay?? tell me what's going on",
    # more empathetic
    "i'm so sorry 😔 that kind of shock is the worst... what happened??",
    "omg friend 💙 that's devastating... i'm right here. tell me",
    "no no no 😔 that's so unfair... are u okay?? what happened??",
    "that's heartbreaking 💙 i'm so sorry... i'm listening. what's going on??",
    "ugh that's awful 😔 unexpected things like that hurt so much... what happened??"
]

# ======================================================
# JOB FEAR / ANXIETY PHRASES (fear of getting fired, job insecurity)
# ======================================================

JOB_FEAR_PHRASES = {
    # fear of being fired
    "getting fired", "gonna get fired", "going to get fired",
    "might get fired", "prly get fired", "probably get fired",
    "prly am getting fired", "probably getting fired",
    "think im getting fired", "think i'm getting fired",
    "afraid of getting fired", "scared of getting fired",
    "worried about getting fired", "fear of getting fired",
    "they might fire me", "they gonna fire me", "they will fire me",
    "boss might fire me", "manager might fire me",
    "about to get fired", "gonna be fired", "going to be fired",
    "might be fired", "could get fired", "could be fired",
    "im gonna lose my job", "i'm gonna lose my job",
    "might lose my job", "gonna lose my job", "going to lose my job",
    "afraid of losing my job", "scared of losing my job",
    "worried about losing my job", "fear of losing my job",
    # job insecurity
    "job is not secure", "job isnt secure", "job isn't secure",
    "not sure about my job", "uncertain about my job",
    "job might be gone", "position might be cut",
    "layoffs coming", "layoffs happening", "might be laid off",
    "gonna be laid off", "could be laid off", "about to be laid off",
    "company is downsizing", "my team is getting cut",
    "my position might be eliminated", "role might be cut",
    # performance anxiety
    "think im underperforming", "think i'm underperforming",
    "not performing well", "performance is bad",
    "boss is unhappy with me", "manager is unhappy",
    "got a warning", "got written up", "on thin ice",
    "one more mistake", "messed up at work", "screwed up at work"
}

# ======================================================
# SALARY / BONUS / PAYDAY PHRASES (money excitement)
# ======================================================

SALARY_PHRASES = {
    # salary day
    "salary today", "salary day", "payday", "pay day", "getting paid",
    "got paid", "got my salary", "salary came", "salary credited",
    "money came", "got my pay", "paycheck", "pay check",
    "salary is here", "salary hit", "account credited",
    # getting salary variations
    "get my salary", "get salary", "getting my salary", "getting salary",
    "ill get my salary", "ill get salary", "i'll get my salary", "i'll get salary",
    "gonna get my salary", "gonna get salary", "going to get salary",
    "receive my salary", "receive salary", "receiving salary",
    # bonus
    "got bonus", "got a bonus", "got my bonus", "bonus came",
    "bonus credited", "bonus today", "getting bonus", "received bonus",
    "bonus hit", "bonus is here", "get my bonus", "get bonus",
    "gonna get bonus", "getting my bonus", "ill get bonus", "i'll get bonus",
    # increment / raise
    "got a raise", "got raise", "got increment", "increment came",
    "salary increased", "salary hike", "pay raise", "pay increase",
    "getting a raise", "gonna get a raise", "got promoted",
    # excitement about money
    "finally getting paid", "finally payday", "waiting for salary",
    "excited for salary", "excited for payday", "cant wait for salary",
    "salary coming", "bonus coming", "pay coming",
    "excited about salary", "excited about payday", "happy about salary",
    "excited ill get", "excited i'll get", "excited to get paid"
}

SALARY_REPLIES = [
    # excited celebration
    "YOOO PAYDAY!! 💰🎉 the best day fr!! what are u gonna do with it??",
    "MONEY MONEY MONEY!! 💸 u deserve it!! any plans for it??",
    "ayyy salary day is the BEST day!! 💰 treat urself okay??",
    "omg yess get that bag!! 💸🔥 what's the first thing ur getting??",
    "PAYDAY VIBES!! 💰✨ u worked hard for this!! how are u celebrating??",
    "the account looking HEALTHY rn!! 💸 what are u gonna splurge on??",
    "yesss the grind paid off literally!! 💰 any shopping plans??",
    "LETS GOOO!! 💸🎉 payday hits different fr!! what's the move??",
    "omg that salary notification hits different!! 💰 treating urself??",
    "the bank account is happy today!! 💸 what are u buying first??",
    # bonus specific
    "BONUS?! 💰🔥 u absolutely deserve that!! what are u gonna do with it??",
    "omggg bonus day!! 💸✨ that's amazing!! any plans for the extra cash??",
    "yesss get that bonus!! 💰 ur hard work paid off!! literally!! what's the plan??",
    # more casual
    "ayyy money in the bank!! 💰 love that for u!! what are u gonna get??",
    "payday friend!! 💸 the vibes are immaculate rn!! treating urself??",
    "that direct deposit hittin!! 💰🔥 any fun plans??",
    "salary credited = serotonin boosted!! 💸 what's on the wishlist??",
    "omg yay!! 💰 u worked so hard for this!! enjoy it okay??",
    "money money money!! 💸✨ what's the first purchase gonna be??",
    "the grind is finally paying off!! 💰 literally!! what are u getting??"
]

# ======================================================
# SPENDING MONEY / TREATING SELF PHRASES (follow-up to salary)
# ======================================================

SPENDING_MONEY_PHRASES = {
    # spending it
    "gonna spend", "going to spend", "will spend", "spending it",
    "spend it", "spend it all", "spend it in whole", "spend in whole",
    "gonna spend it all", "spending everything", "spend everything",
    # splurging
    "gonna splurge", "going to splurge", "splurging", "splurge on",
    "gonna blow it", "blowing it all", "blow it on",
    # treating self
    "gonna treat myself", "treating myself", "treat myself",
    "gonna buy", "going to buy", "buying stuff", "gonna get stuff",
    "gonna shop", "going shopping", "shopping spree",
    # saving
    "gonna save", "going to save", "saving it", "save some",
    "put it in savings", "saving up", "gonna save some",
    # general money spending
    "use the money", "use it for", "using it for",
    "got plans for it", "plans for the money"
}

SPENDING_MONEY_REPLIES = [
    # excited supportive
    "YESSS treat urself!! 💰✨ u deserve it fr!! have so much fun spending!!",
    "omg go off!! 💸🔥 spend that bag!! u earned it!!",
    "ayyy that's the spirit!! 💰 enjoy every bit of it!!",
    "yesss live ur best life!! 💸✨ u worked hard for this!! enjoy!!",
    "PERIODT!! 💰🔥 as u should!! have fun!!",
    "omg yess!! 💸 that's the energy!! treat urself!!",
    "ayyy go have fun with it!! 💰✨ u deserve to splurge!!",
    "yesss!! 💸🔥 spend it all friend!! u earned every penny!!",
    "love that for u!! 💰 enjoy ur money!! u deserve it!!",
    "as u should!! 💸✨ have the best time spending it!!",
    # more casual
    "ooooh nice!! 💰 have fun with it!!",
    "yesss get urself smth nice!! 💸 enjoy!!",
    "that's the move!! 💰✨ have fun!!",
    "ayyy go treat urself!! 💸 u deserve it!!",
    "omg yay!! 💰 enjoy spending it!! have fun!!"
]

# ======================================================
# SIMPLE SADNESS PHRASES (im sad, feeling sad, etc.)
# ======================================================

SIMPLE_SAD_PHRASES = {
    "im sad", "i'm sad", "i am sad", "feeling sad", "feel sad",
    "so sad", "im so sad", "i'm so sad", "really sad", "kinda sad",
    "bit sad", "a bit sad", "little sad", "a little sad",
    "feeling down", "feel down", "im down", "i'm down",
    "feeling low", "feel low", "im low", "feeling blue",
    "not happy", "im not happy", "i'm not happy", "unhappy",
    "im unhappy", "i'm unhappy", "feeling unhappy",
    "sad rn", "sad today", "sad lately", "been sad",
    "just sad", "idk im sad", "idk i'm sad"
}

SIMPLE_SAD_REPLIES = [
    # gentle + asking what's wrong
    "aww friend 💙 what happened?? talk to me",
    "oh no 😔 i'm here for u. what's going on??",
    "hey 💙 i'm sorry ur feeling sad. what happened??",
    "aw 😔 that sucks. wanna tell me what's wrong??",
    "friend nooo 💙 what's making u sad?? i'm listening",
    "hey i'm here okay?? 😔 tell me what's going on",
    "aw man 💙 what happened?? talk to me",
    "oh no 😔 i hate that ur feeling this way. what's up??",
    "hey 💙 it's okay to be sad. wanna talk about it??",
    "aw friend 😔 i'm here. what's making u feel this way??",
    # more casual
    "yo what happened?? 💙 i'm listening",
    "hey talk to me 😔 what's going on??",
    "aw no 💙 what's wrong??",
    "friend what happened?? 😔 tell me",
    "hey i got u 💙 what's making u sad??"
]

# ======================================================
# PANIC / ANXIETY ATTACK PHRASES (URGENT - needs grounding)
# ======================================================

PANIC_ATTACK_PHRASES = {
    # anxiety attacks
    "having anxiety attack", "having an anxiety attack", "anxiety attack",
    "having anxiety attacks", "getting anxiety attacks", "got anxiety attack",
    "my anxiety is attacking", "anxiety is attacking me",
    # panic attacks
    "panic attack", "panic attacks", "having a panic attack", "having panic attack",
    "having panic attacks", "getting panic attacks", "got a panic attack",
    "panicking", "im panicking", "i'm panicking", "panicking rn",
    "panicking right now", "cant stop panicking", "can't stop panicking",
    # cant breathe / hyperventilating
    "cant breathe", "can't breathe", "hard to breathe", "struggling to breathe",
    "hyperventilating", "im hyperventilating", "i'm hyperventilating",
    "breathing too fast", "cant catch my breath", "can't catch my breath",
    "chest is tight", "my chest is tight", "chest tightening",
    # freaking out
    "freaking out", "im freaking out", "i'm freaking out",
    "freaking out rn", "freaking out right now",
    # heart racing
    "heart is racing", "my heart is racing", "heart racing",
    "heart pounding", "my heart is pounding", "heart wont stop",
    # shaking
    "im shaking", "i'm shaking", "shaking rn", "cant stop shaking",
    "can't stop shaking", "hands are shaking", "my hands are shaking",
    "trembling", "im trembling", "i'm trembling"
}

PANIC_ATTACK_REPLIES = [
    # URGENT grounding - BREATHE in caps, calming presence
    "HEY HEY 💙 BREATHE for me okay?? im right here. in... and out... u got this. im not going anywhere",
    "HEY 💙 BREATHE. im right here with u okay?? slow breath in... and out... im here im here",
    "hey hey hey 💙 BREATHE for me pls?? im right here. slow down... in... out... im not leaving",
    "HEY 💙 its okay its okay. BREATHE with me okay?? in... hold... out... im right here with u",
    "hey friend 💙 BREATHE. i need u to breathe for me okay?? im here. slow breath... in... out...",
    "HEY HEY 💙 im here im here. BREATHE okay?? just focus on my words. in... and out... ur safe",
    "hey 💙 BREATHE for me okay?? im right here i promise. slow... in... out... ur gonna be okay",
    "HEY 💙 stop everything and BREATHE. im here with u. slow breath in... and out... im not going anywhere",
    "hey hey 💙 its okay. BREATHE for me pls?? im right here. in... hold... out... i got u",
    "HEY 💙 BREATHE okay?? just breathe. im here. in... out... in... out... ur not alone rn",
    "hey friend 💙 HEY. BREATHE with me okay?? im right here. slow down... in... and out... im here",
    "HEY HEY its okay 💙 BREATHE. im not going anywhere. focus on breathing... in... out... i got u",
    "hey 💙 i need u to BREATHE for me okay?? im right here with u. slow... in... out... ur safe",
    "HEY 💙 its okay its okay. BREATHE pls?? im here. just breathe with me... in... out...",
    "hey hey 💙 BREATHE okay?? im right here i promise. slow breath... in... hold... out... ur gonna be okay"
]

BESTIE_PANIC_ATTACK_REPLIES = [
    "HEY 💙 BREATHE for me okay?? im right here",
    "hey hey 💙 BREATHE. im here. in... out...",
    "HEY 💙 its okay. BREATHE with me okay??",
    "hey 💙 BREATHE pls?? im right here with u",
    "HEY HEY 💙 BREATHE. im not going anywhere",
    "hey 💙 slow breath for me okay?? im here"
]

# ======================================================
# MENTAL HEALTH CRISIS PHRASES (strong_distress)
# ======================================================

MENTAL_HEALTH_CRISIS_PHRASES = {
    # affecting mental health (serious but not crisis)
    "affecting my mental health", "affecting my mental", "affects my mental health",
    "taking a toll on my mental", "taking toll on my mental health",
    "ruining my mental health", "destroying my mental health",
    "bad for my mental health", "terrible for my mental health",
    "hurting my mental health", "damaging my mental health",
    "messing with my mental health", "messing up my mental health",
    "impacting my mental health", "killing my mental health",
    "draining my mental health", "my mental health is suffering",
    "mental health is suffering", "mental health cant take this",
    "mental health can't take this", "too much for my mental health",
    # mental health crashing/declining
    "mental health is crashing", "my mental health is crashing",
    "mental health crashing", "mental health is declining",
    "mental health declining", "mental health is bad",
    "mental health is terrible", "mental health is awful",
    "mental health is shit", "mental health is trash",
    "mental health is gone", "mental health is falling apart",
    "losing my mental health", "my mental health is gone",
    # breaking down
    "im breaking down", "i'm breaking down", "breaking down",
    "mentally breaking down", "emotionally breaking down",
    "having a breakdown", "having a mental breakdown",
    "on the verge of breakdown", "about to break down",
    "falling apart", "im falling apart", "i'm falling apart",
    "everything is falling apart", "my life is falling apart",
    # losing it / going crazy
    "losing my mind", "im losing my mind", "i'm losing my mind",
    "going crazy", "im going crazy", "i'm going crazy",
    "going insane", "im going insane", "i'm going insane",
    "losing it", "im losing it", "i'm losing it",
    "cant think straight", "can't think straight",
    "head is a mess", "my head is a mess", "mind is a mess",
    # cant cope / handle
    "cant cope", "can't cope", "cant handle this",
    "can't handle this", "cant handle it", "can't handle it",
    "cant deal", "can't deal", "cant deal with this",
    "cant take it anymore", "can't take it anymore",
    "cant do this anymore", "can't do this anymore",
    "had enough", "ive had enough", "i've had enough",
    # spiraling
    "spiraling", "im spiraling", "i'm spiraling",
    "in a dark place", "im in a dark place", "i'm in a dark place",
    "at my lowest", "im at my lowest", "i'm at my lowest",
    "hit rock bottom", "rock bottom", "at rock bottom",
    # exhausted mentally
    "mentally exhausted", "emotionally exhausted",
    "mentally drained", "emotionally drained",
    "mentally done", "emotionally done",
    "mentally tired", "emotionally tired",
    "brain is fried", "my brain is fried",
    # everything too much
    "everything is too much", "its all too much", "it's all too much",
    "overwhelmed by everything", "drowning in everything",
    "suffocating", "im suffocating", "i'm suffocating",
    "cant breathe", "can't breathe", "feel like im drowning",
    # giving up vibes
    "whats the point", "what's the point", "no point anymore",
    "nothing matters", "nothing matters anymore",
    "dont see the point", "don't see the point",
    "losing hope", "lost all hope", "no hope left",
    # anxiety related
    "anxiety is killing me", "my anxiety is so bad", "anxiety is through the roof",
    "anxiety wont stop", "anxiety won't stop", "cant stop the anxiety",
    "anxiety is too much", "anxiety is overwhelming", "anxiety is crippling",
    "having anxiety attacks", "anxiety attack", "panic attack", "panic attacks",
    "anxious all the time", "constantly anxious", "always anxious",
    "anxiety is eating me", "anxiety is consuming me",
    # done/exhausted by situation
    "im done by", "i'm done by", "done by the end of",
    "im done because of", "i'm done because of", "done because of this",
    "this is making me", "due to this im", "due to this i'm",
    "because of this im", "because of this i'm", "bc of this im",
    "this has me", "this got me", "this is getting to me",
    "im at my limit", "i'm at my limit", "reached my limit",
    "im so done", "i'm so done", "just so done", "literally done",
    "im over it", "i'm over it", "so over it", "completely over it"
}

MENTAL_HEALTH_CRISIS_REPLIES = [
    # caring + concerned (NO questions, just support)
    "hey 💙 ur mental health matters so much. please take care of urself first okay?? nothing is worth sacrificing that",
    "i hear u 💙 that's really serious and i'm genuinely concerned. ur wellbeing comes first, always",
    "friend 💙 i'm so sorry this is affecting u like this. ur mental health is not something to push through. it matters",
    "hey... 💙 please be gentle with urself. when something starts affecting ur mental health, that's ur mind telling u it's too much",
    "i'm really sorry 💙 ur mental health is precious. please don't ignore what ur mind is telling u",
    "that's heavy 💙 and i need u to know - nothing is worth destroying ur peace over. ur health comes first",
    "hey 💙 the fact that it's affecting u this much... please take care of urself. i'm genuinely worried",
    "i hear u and i care about u 💙 ur mental health is not negotiable. please prioritize urself",
    "friend... 💙 i'm so sorry. when things start hurting ur mental health, that's a sign to step back. u matter more than any of this",
    "that breaks my heart 💙 please know ur mental wellbeing is the most important thing. take care of urself first",
    # gentle presence
    "i'm here with u 💙 ur mental health is so important. please be kind to urself",
    "hey 💙 i see u and i hear u. ur mental health matters more than anything else. i'm here",
    "i'm really concerned about u 💙 please know that ur peace of mind is worth protecting",
    "friend 💙 i hate that this is affecting u so much. ur mental health deserves to be protected",
    "i'm so sorry 💙 nothing should have this much power over ur wellbeing. u come first, always"
]

# Bestie version for after turn 3 (no questions, just care)
BESTIE_MENTAL_HEALTH_NO_QUESTION = [
    "ur mental health matters more than any of this 💙",
    "please take care of urself first. nothing is worth this",
    "i'm genuinely worried about u 💙 please prioritize urself",
    "ur wellbeing > everything else. always",
    "nothing is worth sacrificing ur peace over 💙",
    "please be gentle with urself. u matter",
    "ur mental health is not negotiable 💙 take care of u first",
    "i hate that this is affecting u like this 💙",
    "prioritize urself okay?? ur health comes first",
    "nothing should have this much power over u 💙"
]

# ======================================================
# GRIEF / LOSS / DEATH PHRASES
# ======================================================

GRIEF_LOSS_PHRASES = {
    # death of pets
    "my dog died", "my cat died", "my pet died", "dog passed away",
    "cat passed away", "pet passed away", "lost my dog", "lost my cat",
    "lost my pet", "dog passed", "cat passed", "pet passed",
    "had to put down", "put my dog down", "put my cat down",
    "put my pet down", "dog was put down", "cat was put down",
    "my dog is gone", "my cat is gone", "my pet is gone",
    # death of people
    "my mom died", "my dad died", "my mother died", "my father died",
    "my parent died", "mom passed away", "dad passed away",
    "mother passed away", "father passed away", "parent passed away",
    "my grandma died", "my grandpa died", "grandma passed away",
    "grandpa passed away", "grandmother died", "grandfather died",
    "my friend died", "friend passed away", "best friend died",
    "my brother died", "my sister died", "sibling died",
    "brother passed away", "sister passed away", "sibling passed away",
    "my husband died", "my wife died", "spouse died", "partner died",
    "husband passed away", "wife passed away", "spouse passed away",
    "my uncle died", "my aunt died", "uncle passed away", "aunt passed away",
    "my cousin died", "cousin passed away",
    "someone i know died", "someone close died", "someone i love died",
    "lost someone", "lost a loved one", "loved one passed",
    "lost my mom", "lost my dad", "lost my friend", "lost my grandma",
    "lost my grandpa", "lost my brother", "lost my sister",
    # general death/loss phrases
    "passed away", "passed on", "is gone forever", "no longer with us",
    "left this world", "is no more", "died yesterday", "died today",
    "died last week", "died last night", "died this morning",
    "just died", "recently died", "suddenly died", "unexpectedly died",
    "found out they died", "got the news", "got news that",
    # grief expressions
    "i lost", "we lost", "they died", "death in the family",
    "funeral", "going to the funeral", "after the funeral",
    "still grieving", "grieving so hard", "the grief is heavy",
    "miss them so much", "miss her so much", "miss him so much",
    "wish they were here", "wish she was here", "wish he was here",
    "never see them again", "never coming back", "gone forever",
    # breakup/relationship loss (heartbreak)
    "broke up with me", "dumped me", "left me", "ended things",
    "relationship ended", "we broke up", "just got dumped",
    "they left me", "she left me", "he left me", "partner left",
    "marriage ended", "getting divorced", "got divorced", "divorce",
    "heart is broken", "heartbroken", "my heart hurts",
    "lost the love", "love of my life left", "lost my soulmate"
}

# Keywords that indicate workplace callousness during grief
GRIEF_WORK_CALLOUSNESS_KEYWORDS = {
    "no day off", "didnt give me", "didn't give me", "wont let me",
    "won't let me", "no leave", "denied leave", "cant take off",
    "can't take off", "still have to work", "expected to work",
    "no compassion", "no humanity", "heartless", "dont care",
    "don't care", "doesnt care", "doesn't care", "insensitive",
    "made me work", "have to come in", "no time off", "refused leave",
    "not allowed", "wouldnt let me", "wouldn't let me", "no empathy",
    "zero empathy", "no sympathy", "zero sympathy"
}

GRIEF_WORK_CALLOUSNESS_REPLIES = [
    # acknowledges BOTH the loss AND the workplace cruelty
    "i'm so sorry about your loss 💙 and the fact that they won't even give you time to grieve?? that's genuinely cruel. you deserve space to process this",
    "that's heartbreaking on two levels 💙 losing someone you love AND being treated like your grief doesn't matter. that's so wrong",
    "i'm really sorry 💙 first the loss, and then your workplace showing zero humanity... you shouldn't have to deal with both at once",
    "oh no 💙 i'm so sorry for your loss. and them not giving you time off?? that's inhumane. your grief matters more than their deadlines",
    "that's awful 💙 you're dealing with real loss and they can't even show basic compassion?? the lack of humanity is disgusting honestly",
    "i'm so sorry 💙 losing someone is hard enough without your workplace making it worse. they should be ashamed for not supporting you",
    "the fact that you're grieving AND being denied time off is so messed up 💙 you deserve better than that. i'm really sorry",
    "i'm sorry for your loss 💙 and honestly?? a workplace that won't let you grieve is telling you exactly what they think of you as a person. that's not okay",
    "that's two gut punches at once 💙 the loss itself and then being treated like a machine instead of a human. i'm so sorry",
    "losing someone AND having to deal with a heartless workplace 💙 that's too much. you shouldn't have to fight for basic compassion"
]

GRIEF_LOSS_REPLIES = [
    # death responses - gentle, no fixing, no toxic positivity
    "oh no... i'm so so sorry 💙 that kind of loss leaves such a deep emptiness. i'm here with you",
    "i'm really sorry 💙 losing someone you love hurts in a way that's hard to put into words. i'm here",
    "that's heartbreaking 💙 i'm so sorry for your loss. there's no rushing grief... take all the time you need",
    "i'm so sorry 💙 that kind of pain is so heavy. you don't have to go through this alone",
    "oh friend... 💙 i'm so deeply sorry. losing them must feel like losing a part of yourself",
    "that's such a painful loss 💙 i'm here for you. grief doesn't have a timeline... be gentle with yourself",
    "i'm so sorry 💙 there are no words that can make this easier... but i'm here and i'm not going anywhere",
    "my heart hurts for you 💙 that kind of loss changes everything. i'm here to listen whenever you need",
    "i'm so sorry for your loss 💙 the bond you shared was real and that pain is real. i'm here",
    "that's devastating 💙 i'm so sorry. you loved them and that love doesn't just disappear. i'm here with you",
    # pet death specific
    "oh no 💙 losing a pet is losing family. i'm so so sorry. they were lucky to be loved by you",
    "i'm so sorry 💙 pets leave such a huge hole when they go. that grief is real and valid",
    "that's such a painful loss 💙 they weren't just a pet, they were your companion. i'm here for you",
    # breakup/heartbreak responses
    "i'm so sorry 💙 that kind of heartbreak cuts so deep. you don't have to pretend to be okay",
    "that's really painful 💙 having someone leave like that... it's devastating. i'm here for you",
    "oh friend 💙 heartbreak is its own kind of grief. take all the time you need to feel this. i'm here",
    "i'm sorry 💙 losing someone you loved that way leaves such an ache. you don't have to go through this alone"
]

# ======================================================
# INJURY / ILLNESS + FORCED TO WORK (no humanity)
# ======================================================

INJURY_ILLNESS_KEYWORDS = {
    # fractures / breaks
    "fractured", "fracture", "broken bone", "broke my", "sprained",
    "twisted ankle", "twisted my", "fractured ankle", "fractured leg",
    "fractured arm", "fractured wrist", "broken leg", "broken arm",
    "broken wrist", "broken ankle", "on crutches", "in a cast",
    "wearing a cast", "got a cast", "torn ligament", "torn muscle",
    # injuries
    "injured", "injury", "hurt my", "hurting", "in pain",
    "cant walk", "can't walk", "cant move", "can't move",
    "surgery", "had surgery", "post surgery", "recovering from surgery",
    "stitches", "got stitches", "wound", "bleeding",
    # illness
    "high fever", "really sick", "very sick", "so sick",
    "hospitalized", "was hospitalized", "in the hospital",
    "diagnosed with", "got diagnosed", "chronic pain",
    "migraine", "severe headache", "food poisoning",
    "throwing up", "vomiting", "cant keep food down",
    "bedridden", "bed rest", "doctor said rest"
}

INJURY_WORK_CALLOUSNESS_REPLIES = [
    # concern FIRST, then acknowledge callousness, then subtle ask
    "wait wait hold on 💙 you have a FRACTURED ANKLE and they're still making you work?? are you okay?? that's absolutely insane... how did this even happen??",
    "omg 💙 first of all are you okay?? a fracture is serious... and the fact that they're making you work through it?? that's genuinely messed up. what happened??",
    "hold up 💙 you're INJURED and still working?? that's not dedication that's being exploited. are you at least able to rest at all?? how did you get hurt??",
    "wait what 💙 you should be RESTING not working... the fact that they expect you to work through an injury shows zero humanity fr. are you okay?? what happened??",
    "oh no 💙 that sounds really painful... and they won't even let you recover properly?? that's so wrong. how are you holding up?? what happened to you??",
    "friend 💙 you're literally injured and they still want you working?? that's cruel. forget work for a sec - are YOU okay?? how did this happen??",
    "that's awful 💙 your health should come first always. the fact that they're making you work while you're hurt is disgusting. are you okay tho?? tell me what happened",
    "wait 💙 you're working with a fracture?? nah that's not okay at all. how are you even managing?? and more importantly - how did you get hurt??",
    "omg pls take care of yourself 💙 the workplace can wait... your body literally cannot. are you getting proper rest at all?? what happened??",
    "that's genuinely inhumane 💙 expecting someone to work while injured... you deserve to heal. how are you feeling?? what happened to you??"
]

# ======================================================
# EMOTIONAL HURT / PLAYING WITH FEELINGS / MANIPULATION
# ======================================================

EMOTIONAL_HURT_PHRASES = {
    # playing with feelings
    "played with my feelings", "playing with my feelings", "plays with my feelings",
    "played with my heart", "playing with my heart", "plays with my heart",
    "played me", "got played", "being played", "im being played", "i'm being played",
    "toying with me", "toyed with me", "toys with my emotions",
    "messing with my head", "messed with my head", "messing with my feelings",
    "led me on", "leading me on", "leads me on", "strung me along", "stringing me along",
    # manipulation
    "manipulated me", "manipulating me", "being manipulated", "feels like manipulation",
    "gaslighting me", "gaslighted me", "being gaslighted", "gaslit me",
    "made me feel crazy", "making me feel crazy", "makes me doubt myself",
    "twisted my words", "twisting my words", "twists everything i say",
    "blame shifting", "blames me for everything", "always my fault",
    # emotional abuse / cruelty
    "emotionally abusive", "emotional abuse", "emotionally manipulative",
    "uses my feelings", "using my feelings against me", "weaponizes my emotions",
    "hot and cold", "mixed signals", "sends mixed signals", "one minute then",
    "says one thing does another", "words dont match actions", "actions dont match",
    # betrayal of trust
    "trusted them", "i trusted", "broke my trust", "betrayed my trust",
    "took advantage of me", "taking advantage", "used me", "theyre using me", "they're using me", "just using me", "only using me", "been using me",
    "treated me like", "treats me like nothing", "like i dont matter",
    "made me feel worthless", "makes me feel worthless", "feel so stupid",
    "feel like an idiot", "feel like a fool", "made a fool of me",
    # heartbreak from manipulation
    "knew what they were doing", "did it on purpose", "intentionally hurt me",
    "doesnt care about my feelings", "doesn't care how i feel",
    "never cared", "didnt even care", "didn't even care"
}

EMOTIONAL_HURT_REPLIES = [
    # validate the hurt + acknowledge the manipulation
    "that's not love that's cruelty 💙 playing with someone's feelings like that is so messed up. you didn't deserve that",
    "ugh that's so painful 💙 when someone toys with your emotions like that... it messes with your whole sense of trust. i'm sorry",
    "that's emotional manipulation fr 💙 and it's not okay. your feelings are real and they matter. you're not crazy",
    "i'm so sorry 💙 being played with like that is one of the worst feelings. you deserved honesty not mind games",
    "that's genuinely cruel 💙 the hot and cold thing, the mixed signals... it's designed to keep you confused. you're not the problem",
    "nah that's not okay 💙 using someone's feelings against them is manipulative af. you didn't deserve that treatment",
    "god that hurts 💙 when you trust someone and they just... play with that trust. the betrayal is real",
    "that's so unfair to you 💙 you gave them your feelings and they treated it like a game. that's on them not you",
    "the fact that they knew what they were doing makes it worse 💙 you're not stupid for trusting them. they're trash for abusing that",
    "being led on like that is devastating 💙 you wanted something real and they gave you games. i'm so sorry",
    # validation + empowerment
    "you're not crazy okay?? 💙 gaslighting makes you doubt yourself but YOUR feelings are valid. they're the problem",
    "that's textbook manipulation 💙 making you feel like it's your fault when THEY'RE the one messing with your head",
    "i hate this for you 💙 you opened up to someone and they weaponized it. that says everything about them and nothing about you",
    "the mixed signals thing is intentional 💙 it keeps you hooked while they do whatever they want. you deserve clarity not chaos",
    "feeling like a fool doesn't mean you are one 💙 you trusted someone who didn't deserve it. that's on THEM"
]

# ======================================================
# SARCASM / DARK HUMOR / JOKES / SELF-DEPRECATING HUMOR
# ======================================================

SARCASM_PHRASES = {
    # exaggerated sarcasm
    "oh wow", "oh great", "oh fantastic", "oh wonderful", "oh perfect",
    "just great", "just wonderful", "just perfect", "just fantastic",
    "how nice", "how lovely", "how wonderful", "isnt that nice",
    "what a surprise", "shocking", "im shocked", "i'm shocked", "who wouldve thought",
    "totally didnt see that coming", "never saw that coming", "saw that coming",
    "of course", "obviously", "naturally", "as expected", "as always",
    # dismissive/ironic
    "yeah right", "sure sure", "sure thing", "oh sure", "mhm sure",
    "totally", "absolutely", "definitely", "100 percent", "for sure bro",
    "must be nice", "sounds fun", "sounds great", "living the dream",
    "love that for me", "love this for me", "great for me", "lucky me",
    "my favorite thing", "my favorite part", "best part is", "best thing ever",
    # dark humor / self-deprecating
    "im fine", "i'm fine", "this is fine", "everything is fine",
    "no big deal", "totally normal", "very normal", "super normal",
    "just another day", "typical", "just my luck", "story of my life",
    "why am i like this", "classic me", "me being me", "of course its me",
    "cant have anything", "can't have nice things", "this is why",
    # frustration sarcasm
    "thanks i hate it", "wow thanks", "gee thanks", "thanks so much",
    "so helpful", "very helpful", "super helpful", "incredibly helpful",
    "makes total sense", "logic", "the logic", "flawless logic",
    "genius", "brilliant", "amazing idea", "great plan", "wonderful idea",
    # out of this world / exaggeration
    "out of this world", "from another planet", "living in their own world",
    "in their own universe", "main character", "thinks theyre special",
    "god complex", "holier than thou", "better than everyone",
    "too good for", "above everyone", "on another level"
}

SARCASM_FRUSTRATION_REPLIES = [
    # mirror the sarcasm + validate the frustration underneath
    "lmaooo the sarcasm is DRIPPING 💀 but fr that sounds annoying as hell",
    "okay the 'this is fine' energy when it's clearly NOT fine 😭 what happened??",
    "'must be nice' TOOK ME OUT 💀 the passive aggression is earned tho. what did they do",
    "the way u said that 😭 i can FEEL the frustration. spill what happened",
    "LMAOOO not the sarcastic 'oh great' 💀 okay but fr what's going on",
    "'living the dream' when the dream is actually a nightmare 😭 i felt that",
    "the dark humor is a whole mood 💀 but like... u good?? what happened",
    "'love that for me' is sending me 😭 the self-deprecating energy is real. talk to me",
    "okay the sarcasm is 10/10 💀 but i can tell something's actually bothering u",
    "LMAO 'totally normal' sure sure 😭 what's actually going on tho",
    # understanding the real emotion
    "'story of my life' hit different 💀 that frustration is valid fr. what happened this time",
    "the way u said that tells me everything 😭 okay what did they do NOW",
    "'of course' has so much weight behind it 💀 u sound fed up fr. tell me",
    "that sarcasm is masking something real 😭 i'm here if u wanna talk about it",
    "'thanks i hate it' MOOD 💀 what's going on that's got u like this"
]

SARCASM_PLAYFUL_REPLIES = [
    # match the playful energy
    "LMAOOO okay 💀 the humor tho",
    "STOPPP 😭 u did not just say that",
    "the way u said that 💀 i cant with u",
    "LMFAOOO 😭 okay fair enough",
    "not u being dramatic 💀 i love it tho",
    "the sass is immaculate 😭",
    "okay comedian hours 💀 i see u",
    "HELP the way u phrased that 😭",
    "ur sense of humor tho 💀 i cant",
    "LMAOO okay that was actually funny 😭"
]

DARK_HUMOR_SELF_DEPRECATING_REPLIES = [
    # acknowledge the humor but also check in gently
    "LMAOOO 💀 the self-roast... but also u okay tho??",
    "okay the self-deprecating humor is too real 😭 but fr how are u actually doing",
    "'classic me' energy 💀 i laughed but also... u good??",
    "the way u joke about it 😭 i feel like there's more to this tho",
    "LMAO 'why am i like this' is such a mood 💀 but like... wanna talk about it??",
    "the dark humor is immaculate 💀 but i'm lowkey checking in on u rn",
    "'cant have nice things' TOOK ME OUT 😭 but also... what happened",
    "ur humor is 10/10 💀 but i sense some real frustration underneath",
    "LMAOOO 💀 okay but behind the joke... u okay??",
    "the self-deprecating energy 😭 relatable but also... i'm here if u need to vent"
]

JOB_FEAR_REPLIES = [
    # empathetic + validating
    "omg that's so scary 😔 job insecurity is the worst feeling. what's making u think that??",
    "ugh friend that anxiety is so real 💙 what happened?? tell me what's going on",
    "damn that's such a stressful thing to worry about 😔 what's making u feel like this??",
    "that fear is so valid 💙 job stuff is scary. what's been happening??",
    "omg i'm so sorry ur going through that anxiety 😔 what happened?? talk to me",
    "oof that's a heavy thing to carry 💙 what's making u worried about ur job??",
    "that sounds so stressful fr 😔 job insecurity hits different. what's going on??",
    "ugh i hate that for u 💙 that kind of worry is exhausting. tell me what happened",
    "damn friend 😔 that's such a scary feeling. what's making u think that??",
    "that anxiety is so understandable 💙 work stuff can be terrifying. what's up??",
    # more supportive
    "hey i'm here okay?? 💙 that's a really scary thing to deal with. what happened??",
    "omg that must be so stressful 😔 tell me what's going on at work",
    "ugh job fear is the WORST 💙 ur feelings are so valid. what's happening??",
    "damn that's rough 😔 not knowing is so anxiety-inducing. what's been going on??",
    "i'm so sorry ur dealing with that fear 💙 what's making u worried??",
    # with gentle reassurance
    "hey breathe okay?? 💙 let's talk about it. what's making u feel like u might get fired??",
    "that's such a scary thought 😔 but let's not spiral yet. what happened??",
    "oof that worry can eat u up 💙 tell me what's going on so we can think through it",
    "i know that fear is overwhelming 😔 but i'm here. what's been happening at work??",
    "friend that anxiety is so real 💙 let's talk it through. what's going on??"
]

# ======================================================
# WORK EXHAUSTION PHRASES (job burnout / tired from work)
# ======================================================

WORK_EXHAUSTION_PHRASES = {
    "exhausted from work", "exhausted after work", "exhausted from my job",
    "exhausted after my job", "tired from work", "tired after work",
    "tired from my job", "tired after my job", "drained from work",
    "drained after work", "drained from my job", "drained after my job",
    "burnt out from work", "burned out from work", "burnout from work",
    "burnt out from my job", "burned out from my job", "burnout from my job",
    "done with work", "done with my job", "done with this job",
    "done after work", "done after my job", "so done with work",
    "so done with my job", "im done with work", "im done with my job",
    "work is killing me", "my job is killing me", "this job is killing me",
    "work is draining me", "my job is draining me", "job is exhausting",
    "work is exhausting", "my job is exhausting", "hate my job",
    "hate this job", "hate going to work", "cant do this job anymore",
    "cant take this job", "cant take my job", "over this job",
    "over my job", "so over work", "so over my job",
    "exhausted and done", "tired and done", "drained and done"
}

WORK_EXHAUSTION_WORDS = {
    "job", "work", "office", "workplace", "boss", "manager",
    "coworker", "coworkers", "colleague", "colleagues"
}

WORK_EXHAUSTION_REPLIES = [
    # empathy + validation
    "ugh work has been draining u huh 😔 that's so valid. what's been going on??",
    "omg that job sounds exhausting fr 💙 u okay?? tell me what happened",
    "damn work really got u feeling like that 😔 i'm here. what's going on??",
    "oof the job burnout is real 💙 u deserve a break fr. what happened??",
    "friend that sounds so draining 😔 work shouldn't make u feel like this. talk to me",
    "ugh i hate that work is doing this to u 💙 what's been happening??",
    "no fr that job sounds like it's taking everything out of u 😔 what's going on??",
    "damn that's rough 💙 u shouldn't have to feel this way after work. what happened??",
    "work exhaustion is the worst honestly 😔 u okay?? tell me about it",
    "oof that sounds brutal 💙 the job really wearing u down huh?? what's up??",
    # more supportive
    "hey ur feelings are so valid 💙 no job should leave u feeling like this. what's going on??",
    "omg friend 😔 work has been too much huh?? i'm listening. tell me everything",
    "damn that job is really getting to u 💙 u deserve better fr. what happened??",
    "ugh the burnout is hitting hard huh 😔 i'm here for u. what's been going on??",
    "that sounds so exhausting fr 💙 u okay?? spill what's happening at work",
    # with gentle advice tone
    "yo that's not sustainable 😔 u matter more than any job. what's going on??",
    "friend ur wellbeing comes first okay?? 💙 tell me what's happening at work",
    "ugh no job is worth ur mental health fr 😔 what's been draining u??",
    "that sounds like way too much 💙 u need rest. what's going on at work??",
    "damn u shouldn't have to feel this way 😔 what's the job putting u through??"
]

# ======================================================
# COMPOUND STATEMENT REPLIES (multiple issues at once)
# ======================================================

# ======================================================
# HELP REQUEST PHRASES
# ======================================================

HELP_REQUEST_PHRASES = {
    "can u help", "can you help", "could u help", "could you help",
    "will u help", "will you help", "help me", "need help",
    "need ur help", "need your help", "i need help", "pls help",
    "please help", "help pls", "help please", "can i ask",
    "can i ask u", "can i ask you", "i have a question",
    "got a question", "quick question", "need advice",
    "need some advice", "need ur advice", "need your advice",
    "can u advise", "can you advise", "any advice",
    "what should i", "wt should i", "wat should i"
}

HELP_REQUEST_REPLIES = [
    "ofc ofc!! i'm here for u 💙 what's going on?? tell me everything",
    "yess always!! 💙 what do u need?? i'm listening",
    "absolutely friend!! i got u 💙 what's up??",
    "ofc!! i'd love to help 💙 tell me what's happening",
    "yesss of course!! 💙 spill — what's going on??",
    "always here for u!! 💙 what do u need help with??",
    "ofc friend!! 💙 i'm all ears. what's up??",
    "yess!! happy to help 💙 tell me what's on ur mind",
    "absolutely!! 💙 lay it on me — what's going on??",
    "ofc ofc!! 💙 what can i help u with??",
    "yess i got u!! 💙 what's the situation??",
    "always!! 💙 tell me what's happening and i'll do my best",
    "ofc!! that's what i'm here for 💙 what's up??",
    "yesss friend!! 💙 what do u need??"
]

# ======================================================
# "WHAT SHOULD I DO" RESPONSES (subtle indirect advice)
# ======================================================

ADVICE_REQUEST_PHRASES = {
    "what should i do", "wt should i do", "wat should i do",
    "what do i do", "wt do i do", "wat do i do",
    "what would u do", "what would you do", "wt would u do",
    "what do u think", "what do you think", "wt do u think",
    "should i", "do u think i should", "do you think i should",
    "what do u suggest", "what do you suggest", "any suggestions",
    "idk what to do", "i dont know what to do", "dunno what to do",
    "im confused what to do", "not sure what to do", "unsure what to do",
    "help me decide", "cant decide", "can't decide",
    # more variations
    "im not sure what to do", "im not sure wt to do", "im not sure wat to do",
    "i dont know wt to do", "i dont know wat to do",
    "idk wt to do", "idk wat to do", "idek what to do",
    "confused what to do", "confused wt to do", "so confused",
    "dont know what to do", "no idea what to do", "no clue what to do"
}

ADVICE_REPLIES = [
    # subtle "you know best" responses
    "hmm honestly?? 💙 i feel like deep down u already know what feels right... what's ur gut telling u??",
    "that's a tough one 💙 but i think u know urself better than anyone... what does ur heart say??",
    "oof that's hard 💙 but like... what would make YOU feel better?? that's what matters most",
    "i hear u 💙 but honestly?? only u can really know what's best for u... what are u leaning towards??",
    "hmm 💙 i think the answer is already in u somewhere... what feels right when u think about it??",
    # encouraging self-trust
    "honestly?? 💙 trust urself on this one. u know what's best for u. what's ur instinct saying??",
    "i feel like u already know 💙 sometimes we just need someone to tell us it's okay to do what we feel... what do u feel??",
    "that's a big decision 💙 but i believe in u. what does ur gut tell u??",
    "honestly?? 💙 no one knows ur situation better than u do. what are u thinking??",
    "u know urself best 💙 what feels like the right move to u??",
    # gentle redirection
    "hmm let me ask u this 💙 if u didn't have to worry about anyone else... what would u want to do??",
    "here's the thing 💙 whatever u choose... make sure it's what's best for U. what are u feeling??",
    "i think the real question is 💙 what do YOU want?? that matters most here",
    "hey 💙 forget what u 'should' do... what do u WANT to do??",
    "honestly?? 💙 i trust u to make the right call. what's ur heart telling u??",
    # supportive nudge
    "i can't tell u what to do 💙 but i CAN say that whatever u decide... i support u. what are u thinking??",
    "that's something only u can answer 💙 but i'm here no matter what u choose. what feels right??",
    "u got this 💙 trust urself. what do u think is the move??",
    "i believe in ur judgment 💙 what are u leaning towards??",
    "sometimes we just need to sit with it 💙 what does ur gut say??",
    # more emotional/supportive (gender neutral)
    "i know it feels overwhelming rn 💙 but u've got more clarity than u think... what does ur heart say??",
    "hey it's okay to not have all the answers 💙 what feels true to u in this moment??",
    "oof i feel u 💙 but like... if fear wasn't a factor what would u do??",
    "u don't have to figure it all out rn 💙 what's one thing that feels right??",
    "i trust u to know what's best for u 💙 what's ur soul telling u rn??"
]

# ======================================================
# POSITIVE NEUTRAL PHRASES (happy casual / excited plans)
# ======================================================

POSITIVE_NEUTRAL_PHRASES = {
    # going out / plans
    "gonna go out", "going out", "going to go out", "im going out",
    "gonna eat", "going to eat", "gonna grab food", "getting food",
    "gonna shop", "going shopping", "gonna go shopping", "going to shop",
    "gonna hang", "going to hang", "hanging out", "gonna hang out",
    "gonna chill", "going to chill", "chilling", "gonna relax",
    "gonna party", "going to party", "partying", "gonna celebrate",
    "gonna meet", "meeting up", "gonna meet up", "meeting friends",
    "gonna watch", "watching movie", "gonna binge", "binge watching",
    "gonna travel", "going on trip", "vacation", "going on vacation",
    "gonna treat myself", "treating myself", "self care day",
    # excited for something
    "cant wait", "can't wait", "so excited", "super excited",
    "looking forward", "hyped for", "pumped for", "ready for",
    "finally gonna", "finally going to", "finally getting to",
    # positive activities
    "gonna have fun", "having fun", "its gonna be fun", "so fun",
    "gonna be great", "its gonna be great", "will be great",
    "gonna enjoy", "enjoying", "gonna love it", "loving it"
}

POSITIVE_NEUTRAL_REPLIES = [
    # excited for them
    "ooooh fun plans!! 🎉 have the best time!! what are u gonna do first??",
    "yesss go have fun!! ✨ u deserve it!! tell me about it",
    "omg that sounds so fun!! 🎉 enjoy urself okay??",
    "ayyy love that for u!! ✨ have an amazing time!!",
    "oooh exciting!! 🎉 what's on the agenda??",
    "yesss treat urself!! ✨ u deserve some fun!! what are u getting??",
    "omg sounds like a vibe!! 🎉 have so much fun!!",
    "love the energy!! ✨ enjoy every moment okay??",
    "that sounds amazing!! 🎉 have the best day!!",
    "yesss go live ur best life!! ✨ tell me how it goes!!",
    # more casual
    "ooh nice!! 🎉 sounds fun!! what's the plan??",
    "ayy have fun!! ✨ enjoy!!",
    "sounds lit!! 🎉 have a great time!!",
    "oooh exciting stuff!! ✨ enjoy urself!!",
    "nice nice!! 🎉 have fun out there!!"
]

# ======================================================
# COPING / TRYING TO BE OKAY PHRASES
# ======================================================

COPING_PHRASES = {
    "its okay", "it's okay", "its fine", "it's fine",
    "its alright", "it's alright", "ill be okay", "i'll be okay",
    "ill be fine", "i'll be fine", "im okay", "i'm okay",
    "im fine", "i'm fine", "im alright", "i'm alright",
    "i guess its okay", "i guess it's okay", "ig its okay",
    "might get another", "can get another", "will find another",
    "ill find another", "i'll find another", "can find another",
    "its not that bad", "it's not that bad", "could be worse",
    "at least", "on the bright side", "silver lining",
    "trying to stay positive", "trying to be positive",
    "trying not to worry", "trying not to think about it",
    "whatever happens happens", "it is what it is",
    "ill figure it out", "i'll figure it out", "will figure it out",
    "ill manage", "i'll manage", "can manage", "will manage",
    "not the end of the world", "life goes on", "move on"
}

COPING_SUPPORTIVE_REPLIES = [
    # validating their attempt to cope while still being supportive
    "hey i love that ur trying to stay positive 💙 but also... it's okay to not be okay rn. how are u really feeling??",
    "that's a good mindset 💙 but u don't have to pretend everything's fine. how are u actually doing??",
    "i admire that u're trying to look at it positively 😊 but it's okay to feel upset too. how r u really??",
    "ur being so strong about this 💙 but u can be honest with me. how are u actually feeling??",
    "that's a healthy way to think about it 😊 but also... are u okay?? like really??",
    "i love ur resilience 💙 but remember it's okay to feel sad about this too. how r u holding up??",
    "ur handling this so well 😊 but don't bottle it up okay?? how are u really feeling??",
    "that's such a mature outlook 💙 but i wanna make sure ur okay. how r u actually doing??",
    "i hear u trying to be positive 💙 and i'm proud of u for that. but how are u really??",
    "ur being really brave about this 😊 but u can let ur guard down with me. what's going on inside??",
    # more gentle
    "hey it's okay to feel however u feel 💙 u don't have to be okay rn. what's really on ur mind??",
    "i appreciate u trying to stay strong 😊 but i'm here if u need to vent. how r u actually??",
    "that positivity is great 💙 but also valid to feel upset. how are u really holding up??",
    "ur doing amazing 💙 but don't forget it's okay to not be okay sometimes. how r u really??",
    "i see u trying to cope 😊 and that's good. but how are u actually feeling about all this??"
]

# ======================================================
# CONVERSATION CONTEXT REPLIES (follow-up based on emotion flow)
# ======================================================

# When user continues after initial distress message
DISTRESS_FOLLOWUP_REPLIES = [
    # supportive follow-ups
    "i hear u 💙 that sounds really tough. tell me more about what happened",
    "damn that's rough 😔 i'm here for u. keep going, i'm listening",
    "oof 💙 that's a lot to deal with. what else happened??",
    "i'm so sorry ur going through this 😔 u can tell me everything",
    "that makes sense 💙 anyone would feel that way. what happened next??",
    "ugh that sucks fr 😔 i'm right here. tell me more",
    "i feel u 💙 that's really hard. what else is going on??",
    "no wonder u feel this way 😔 keep talking, i'm listening",
    "that's so valid 💙 ur feelings make total sense. what else??",
    "damn friend 😔 that's heavy. i'm here for all of it",
    # more empathetic
    "ur not alone in this okay?? 💙 tell me more",
    "i'm glad ur talking to me about this 😔 what else is on ur mind??",
    "that's really painful to hear 💙 i'm here. keep going",
    "u shouldn't have to deal with this alone 😔 what else happened??",
    "i'm listening to every word 💙 tell me more about it"
]

# When user continues after initial positive message
POSITIVE_FOLLOWUP_REPLIES = [
    # excited follow-ups
    "omg yesss!! 🎉 tell me more!! i wanna hear everything",
    "ahhh i love this for u!! ✨ what else happened??",
    "WAIT there's more?? 🔥 keep going!!",
    "okayy i'm loving this energy!! 💛 spill the rest",
    "yesss friend!! ✨ don't stop now, what else??",
    "omg omg omg!! 🎉 i need all the details",
    "this keeps getting better!! 💛 tell me more!!",
    "ur literally glowing rn!! ✨ what happened next??",
    "i'm so here for this!! 🔥 keep talking!!",
    "the good vibes keep coming!! 💛 what else??",
    # curious excited
    "wait wait i need to know everything!! ✨ go on",
    "ur making MY day rn!! 🎉 tell me more",
    "this is amazing!! 💛 what else is going on??",
    "i'm literally smiling rn!! ✨ keep going",
    "yooo this is so good!! 🔥 don't leave me hanging"
]

# When user continues after neutral message
NEUTRAL_FOLLOWUP_REPLIES = [
    # gentle follow-ups
    "mhm i hear u 🙂 what else is on ur mind??",
    "okay okay 💙 tell me more about that",
    "gotcha 🙂 anything else going on??",
    "i see i see 💙 what else??",
    "alright 🙂 is there more to it??",
    "mmhm 💙 keep going if u want",
    "i'm listening 🙂 what else is up??",
    "okay 💙 tell me more",
    "got it 🙂 anything else??",
    "mhm mhm 💙 go on"
]

# When emotion shifts from distress to positive
EMOTION_SHIFT_DISTRESS_TO_POSITIVE = [
    "wait omg!! 🎉 this is such a turn around!! tell me more!!",
    "hold up — things are looking up now?? ✨ i love that!! what happened??",
    "yesss the energy shift!! 💛 i'm so happy for u!! spill",
    "omg from that to THIS?? 🔥 i'm here for it!! tell me everything",
    "wait wait this is good news now?? ✨ i'm so relieved!! what changed??"
]

# When emotion shifts from positive to distress
EMOTION_SHIFT_POSITIVE_TO_DISTRESS = [
    "oh no wait 😔 what happened?? u were so happy before",
    "hold on — something changed?? 💙 talk to me, what's going on??",
    "wait friend 😔 what happened?? tell me",
    "oh no 💙 things took a turn huh?? i'm here. what happened??",
    "wait what?? 😔 everything seemed good... what's wrong??"
]

# ======================================================
# RANT / VENTING PHRASES (when user is venting about their day)
# ======================================================

RANT_STARTER_PHRASES = {
    # bad day phrases
    "my day was", "today was", "this day was", "the day was",
    "my day has been", "today has been", "this day has been",
    "had such a", "had the worst", "had a terrible", "had a bad",
    "had an awful", "had a rough", "had a shit", "had a shitty",
    # venting starters
    "so basically", "okay so", "ok so", "so like", "so um",
    "let me tell you", "lemme tell u", "let me tell u",
    "u wont believe", "you wont believe", "u won't believe",
    "can i vent", "can i just vent", "need to vent", "gotta vent",
    "i need to rant", "let me rant", "gonna rant", "imma rant",
    # story starters
    "so this happened", "this thing happened", "something happened",
    "so today", "so yesterday", "so like today", "omg so",
    "bruh so", "dude so", "yo so", "bro so",
    # frustration venting
    "im so done with", "im so sick of", "im so tired of",
    "i cant with", "i literally cant", "i just cant",
    "everything went wrong", "nothing went right", "nothing is going right",
    # long form indicators
    "first of all", "and then", "but then", "so then", "after that"
}

RANT_BAD_DAY_PHRASES = {
    # explicit bad day
    "bad day", "terrible day", "awful day", "shit day", "shitty day",
    "worst day", "horrible day", "rough day", "hard day", "tough day",
    "long day", "exhausting day", "tiring day", "draining day",
    "stressful day", "frustrating day", "annoying day",
    # things went wrong
    "day sucked", "day was trash", "day was garbage", "day was hell",
    "everything sucked", "everything was bad", "everything went wrong",
    "one of those days", "just one of those days"
}

RANT_REPLIES = [
    # empathetic listening
    "omg 😔 that sounds like A LOT. i'm here for all of it. keep going, i'm listening",
    "damn 💙 that's rough fr. i'm listening to every word. what else happened??",
    "oof 😔 that's so much to deal with. i'm right here. tell me everything",
    "ugh 💙 that sounds exhausting honestly. i'm listening. keep venting",
    "yo 😔 that's wild. i hear u. what happened next??",
    "omg 💙 no wonder u need to vent. i'm all ears. tell me more",
    "damn that sounds frustrating asf 😔 i'm here. keep going",
    "ugh 💙 that's a lot fr. spill everything, i'm listening",
    "that sounds like such a mess 😔 i'm here for u. what else??",
    "yo 💙 that's rough. i'm listening to all of it. go on",
    # validating the vent
    "omg i would be SO frustrated 😔 u have every right to vent. tell me more",
    "damn 💙 anyone would need to vent after that. i'm here. keep going",
    "ugh that's valid asf 😔 let it all out. i'm listening",
    "no fr 💙 that sounds like hell. vent away, i got u",
    "that's rough 😔 i'm glad ur talking to me about it. what else happened??",
    # encouraging more venting
    "keep going 💙 i wanna hear everything. what happened next??",
    "omg and then what?? 😔 i'm invested now. tell me",
    "damn 💙 don't stop there. what else went down??",
    "ugh 😔 there's more isn't there?? tell me everything",
    "yo 💙 this is wild. keep venting, i'm right here"
]

BAD_DAY_REPLIES = [
    # acknowledging bad day specifically
    "aw man 😔 bad days are the WORST. i'm so sorry. what happened??",
    "ugh 💙 i hate that for u fr. tell me what went down",
    "damn 😔 sounds like today really tested u. what happened??",
    "omg 💙 i'm so sorry it was rough. wanna talk about it??",
    "that sucks fr 😔 bad days hit different. i'm here. tell me everything",
    "aw no 💙 u didn't deserve a bad day. what happened??",
    "ugh 😔 some days are just like that. i'm listening. spill",
    "damn 💙 i'm sorry today was rough. what went wrong??",
    "that's rough 😔 i hope it gets better. wanna vent about it??",
    "omg 💙 bad days are exhausting. i'm here for u. what happened??",
    # more supportive
    "hey 💙 i'm sorry u had a bad day. u can tell me all about it",
    "aw 😔 that sucks. u deserve better days. what happened??",
    "ugh 💙 bad days are so draining. i'm listening. tell me",
    "damn 😔 i'm sorry. let it all out okay?? what went wrong??",
    "yo 💙 bad days happen but they still suck. what happened??"
]

COMPOUND_REPLIES = [
    "damn that's a lot going on at once 😔 i'm here for u. tell me more about what's happening",
    "oof friend that sounds overwhelming fr 💙 one thing at a time okay?? what's bothering u the most rn??",
    "yo that's too much to deal with at once 😔 i hear u. what's the biggest thing on ur mind??",
    "bruh that's so much 💙 u shouldn't have to handle all that. what happened??",
    "omg that sounds exhausting fr 😔 which part is hitting u the hardest rn??",
    "damn friend 💙 that's a lot to carry. wanna break it down for me?? what's going on??",
    "ugh that's rough having all that at once 😔 i'm listening. tell me everything",
    "yo u got a lot on ur plate rn 💙 what's stressing u out the most??",
    "that's way too much to deal with fr 😔 i'm here okay?? what happened??",
    "friend that sounds like a lot 💙 take ur time and tell me what's going on",
    # more specific compound acks
    "wait so all of that is happening at the same time?? 😔 that's rough fr. i'm here",
    "omg friend that's way too much 💙 no wonder u feel this way. what's going on??",
    "yo one thing would be bad enough but all that?? 😔 tell me what happened",
    "ugh that combo sounds terrible fr 💙 u okay?? what's the situation??",
    "damn everything at once huh 😔 breathe okay?? tell me what's up"
]

# ======================================================
# PATTERN-BASED REPLIES (Signal Count Based)
# ======================================================

# Heavy Distress (3+ distress signals detected)
HEAVY_DISTRESS_REPLIES = [
    # grounding + deep support (gender neutral)
    "hey hey hey... 💙 i can hear how much pain ur in rn. i'm right here okay?? u don't have to carry this alone. what happened??",
    "oh no... 💙 that's so much pain all at once. i'm here and i'm not leaving. u matter so much okay?? what's going on??",
    "hey... 💙 i hear u. everything feels like too much rn doesn't it?? i'm right here with u. tell me what happened??",
    "oh no 💙 u're really going through it aren't u?? i'm so sorry. i'm here for all of it. what happened??",
    "hey... 💙 that's a lot of pain to hold. please know that ur feelings are valid and i'm right here. what's going on??",
    "hey 💙 i can feel how heavy this is for u. i'm here okay?? u don't have to be strong rn. tell me what happened",
    "oh 💙 ur hurting so much rn and i see that. i'm not going anywhere okay?? u matter. what happened??",
    "hey... take a moment 💙 that's so much to deal with. i'm here and i care about u. what's going on??",
    "hey 💙 i'm so sorry ur feeling all of this at once. please know u're not alone. what happened??",
    "hey 💙 that sounds incredibly overwhelming. i hear u. i'm here to listen to everything. tell me what's going on??",
    # with gentle grounding
    "hey... 💙 can u take a deep breath for me?? i know everything hurts rn but i'm here. what happened??",
    "oh no 💙 that's so heavy. i'm right here with u. breathe okay?? what's going on??",
    "hey 💙 i'm here. try to take a slow breath... i know it's hard. u don't have to face this alone. what happened??",
    "hey... 💙 i hear all of it. i'm not leaving. i'm here. tell me what's going on??",
    "hey 💙 that's a lot of pain. can u take one breath with me?? in... and out... i'm right here. what happened??"
]

# Work/Job Distress Replies (asks what happened)
WORK_DISTRESS_REPLIES = [
    # empathetic + subtle invite to share
    "ugh 💙 work stuff can be so draining. i'm here if u wanna talk about it",
    "that sounds really overwhelming 💙 i hear u. wanna vent??",
    "omg 💙 the work pressure is real. i'm listening if u wanna share more",
    "oof 💙 that's a lot to carry. i'm here for u",
    "ugh i feel u 💙 work can take so much out of u. talk to me",
    "that's so valid 💙 ur feelings about this matter. i'm here",
    "damn 💙 u shouldn't have to feel this way about work. i got u",
    "ugh 💙 that sounds exhausting fr. wanna talk about it??",
    "hey 💙 i hear u. work stuff is hard. i'm listening",
    "oof 💙 no one deserves to feel this drained from work. i'm here for u",
    "ugh 💙 the pressure is real huh. wanna share what's going on??",
    "that's rough 💙 work stress hits different. i'm here if u need to vent",
    "damn 💙 that's a lot to deal with. u can talk to me about it",
    "omg 💙 i can tell this is weighing on u. i'm listening",
    "ugh 💙 ur wellbeing matters more than any job. talk to me"
]

# Yelled At / Screamed At Replies (specific for being yelled at by boss/manager)
YELLED_AT_KEYWORDS = {"yelled", "yelling", "screamed", "screaming", "shouted", "shouting"}
YELLED_AT_REPLIES = [
    "ugh that sucks. getting yelled at hits hard — it's not just about the work, it messes with ur head and ur confidence too. u didn't deserve that, especially if u were already trying ur best. take a breath for a sec; one bad moment with a boss doesn't define u or ur work 💙",
    "damn 💙 being yelled at is never okay. that's not leadership, that's just someone taking their stress out on u. u didn't deserve that. how r u holding up??",
    "oof 💙 getting screamed at is so degrading... it doesn't matter what happened, no one deserves to be treated like that. ur worth isn't measured by someone else's temper",
    "that's rough 💙 being yelled at stays with u... it's not just embarrassing, it genuinely hurts. i'm sorry u had to go through that. u didn't deserve it",
    "ugh 💙 getting yelled at at work is the worst. it's humiliating and unfair. whatever happened, there's always a better way to handle things than screaming. u ok??",
    "damn that's not okay 💙 no matter what the situation was, yelling is never the answer. that says more about them than it does about u. how r u feeling rn??",
    "hey 💙 i'm sorry that happened. being yelled at can really shake u up... it's normal to feel upset or even question urself after. but remember — their reaction is not ur fault",
    "oof 💙 that's so unfair. getting screamed at is traumatizing honestly. u were just trying to do ur job. take a moment to breathe... u're gonna be okay"
]

# Heavy Positive (3+ positive signals detected)
HEAVY_POSITIVE_REPLIES = [
    # maximum hype + celebration
    "OMGGG WAIT WHAT?! 🎉🔥✨ THIS IS INSANE!! i'm literally SO HAPPY for u rn!! tell me EVERYTHING!!",
    "STOOOP UR KIDDING!! 🤯🎉🔥 this is AMAZING!! i'm screaming!! i need all the details rn!!",
    "YOOOOO!! 🎉✨🔥 BEST NEWS EVER!! i'm so so SO happy for u!! u deserve all of this!! spill everything!!",
    "HOLD UP!! 🤯🎉 this is HUGE!! i'm literally so proud of u!! tell me more i'm LIVING for this!!",
    "WAIT WAIT WAIT!! 🎉🔥✨ ARE U SERIOUS RN?! this is INCREDIBLE!! omg tell me everything!!",
    "AHHHHH!! 🎉🤯✨ I CANT EVEN!! this is SO good!! u're literally winning at life rn!! SPILL!!",
    "YOOO!! 🔥🎉 THIS IS EVERYTHING!! i'm so happy i could cry!! tell me all of it!!",
    "OMG OMG OMG!! 🎉✨🔥 this is the BEST thing i've heard!! u deserve this SO much!! details NOW!!",
    "YESSSSS!! 🎉🔥🤯 I KNEW IT!! i'm SO proud of u!! this is amazing!! tell me everything!!",
    "SHUT UPPP!! 🤯🎉✨ this is INSANE!! the universe is literally on ur side!! i need to know more!!",
    # excited celebration
    "THIS IS SO GOOD!! 🎉🔥 i literally can't stop smiling!! ur energy is IMMACULATE rn!! tell me more!!",
    "OKAYYYY LOOK AT U!! ✨🎉 thriving!! winning!! living ur best life!! i'm so here for it!! what happened??",
    "THE VIBES ARE SO GOOD RN!! 🔥🎉✨ i love this so much for u!! u absolutely deserve it!! spill!!",
    "BESTIE UR GLOWING!! 🎉✨ this is YOUR moment!! i'm so happy!! tell me everything omg!!",
    "THIS ENERGY THO!! 🔥🎉 u're literally radiating happiness and i'm HERE for it!! what's going on??"
]

# Mixed Emotions (both distress and positive signals)
MIXED_EMOTIONS_REPLIES = [
    # acknowledging complexity
    "hey 💙 sounds like there's a lot going on... both good and hard stuff huh?? i'm here for all of it. tell me what's on ur mind",
    "i hear u 💙 it sounds like ur feeling a mix of things rn and that's okay. what's weighing on u the most??",
    "that's... a lot of different feelings huh?? 💙 i get it. sometimes life throws everything at u at once. talk to me",
    "hmm 💙 sounds like there's good stuff but also hard stuff going on?? i'm here. what do u wanna talk about first??",
    "hey 💙 i can tell ur feeling torn between different things rn. that's valid. what's on ur heart??",
    "it sounds complicated 💙 like there's happy things but also stuff that's weighing on u?? i'm listening to all of it",
    "yo 💙 life really be throwing mixed signals at u huh?? i'm here for the good and the hard. what's up??",
    "hey 💙 seems like there's both wins and struggles going on?? i wanna hear about all of it. what's happening??",
    "that's a lot of emotions to hold at once 💙 i get it. sometimes things are complicated. talk to me",
    "friend 💙 sounds like ur dealing with a mix of stuff rn. that's okay. what do u need to get off ur chest??",
    # more supportive
    "hey 💙 it's okay to feel happy and sad at the same time. that's human. what's going on with u??",
    "i hear the complexity in what ur saying 💙 let's unpack it together. what's bothering u the most??",
    "sounds like a rollercoaster of emotions huh?? 💙 i'm here for all the ups and downs. tell me",
    "hey 💙 mixed feelings are valid. u don't have to have it all figured out. what's on ur mind??",
    "that's... complicated isn't it?? 💙 i'm here to listen to all of it. start wherever feels right"
]

# Moderate Distress (2 distress signals)
MODERATE_DISTRESS_REPLIES = [
    "hey 💙 that sounds really hard. i'm here for u okay?? tell me what's going on",
    "oof 💙 that's rough fr. i hear u. wanna talk about what happened??",
    "damn friend 💙 that's a lot to deal with. i'm listening. what's up??",
    "hey 💙 i can tell things aren't great rn. i'm here. talk to me",
    "that sounds draining fr 💙 i'm sorry ur going through this. what happened??",
    "ugh 💙 that's not easy at all. i'm right here. tell me more",
    "hey 💙 seems like stuff has been weighing on u. i'm listening. what's going on??",
    "damn 💙 that sounds frustrating and exhausting. i'm here for u. spill",
    "friend 💙 i hear u. that's tough. wanna vent about it??",
    "oof that's a lot 💙 i'm here okay?? tell me what happened"
]

# Moderate Positive (2 positive signals)
MODERATE_POSITIVE_REPLIES = [
    "omg yesss!! 🎉 things are going good huh?? i love that for u!! tell me more!!",
    "ayyyy 🎉 the good vibes are strong!! i'm so happy for u!! what's happening??",
    "ooh nice!! 🎉 sounds like things are looking up!! tell me about it!!",
    "yesss friend!! 🎉 i love this energy!! what's got u feeling good??",
    "okayy i see u!! 🎉 good things happening huh?? spill the tea!!",
    "oooh 🎉 the positive energy is radiating!! i'm here for it!! what's going on??",
    "yay!! 🎉 sounds like there's good stuff happening!! tell me everything!!",
    "nice nice!! 🎉 i love hearing this!! what's making u happy??",
    "omg 🎉 good vibes only huh?? i'm so here for this!! what happened??",
    "ayy 🎉 things are going well!! that's amazing!! tell me more!!"
]

def _get_context_aware_reply(current_emotion: str, context: dict, text: str) -> str:
    """
    Generate a context-aware reply based on conversation flow.
    Returns None if no special context handling is needed.
    """
    initial_emotion = context.get("initial_emotion")
    turn_count = context.get("turn_count", 1)
    emotion_changed = context.get("emotion_changed", False)

    # FIRST: Check for positive neutral phrases - these should ALWAYS get happy replies
    # regardless of conversation history
    if has_phrase(text, POSITIVE_NEUTRAL_PHRASES):
        return random.choice(POSITIVE_NEUTRAL_REPLIES)

    # Check for coping phrases (when someone is trying to be okay after distress)
    if turn_count >= 2 and initial_emotion in {"distress", "strong_distress"}:
        if has_phrase(text, COPING_PHRASES):
            return random.choice(COPING_SUPPORTIVE_REPLIES)

    # Check for emotion shifts (dramatic changes)
    if emotion_changed and turn_count > 1:
        # Shifted from distress/strong_distress to positive
        if initial_emotion in {"distress", "strong_distress"} and current_emotion == "positive":
            return random.choice(EMOTION_SHIFT_DISTRESS_TO_POSITIVE)

        # Shifted from positive to distress/strong_distress
        if initial_emotion == "positive" and current_emotion in {"distress", "strong_distress"}:
            return random.choice(EMOTION_SHIFT_POSITIVE_TO_DISTRESS)

    # For ongoing conversations (turn 2+), use follow-up style replies
    if turn_count >= 2:
        # Use the INITIAL emotion to maintain conversation tone
        # This keeps the supportive tone even if current message is neutral

        # If started with distress, keep being supportive
        if initial_emotion in {"distress", "strong_distress"}:
            # But if current is now positive, celebrate the shift
            if current_emotion == "positive":
                return random.choice(EMOTION_SHIFT_DISTRESS_TO_POSITIVE)
            # Otherwise keep supportive tone
            return random.choice(DISTRESS_FOLLOWUP_REPLIES)

        # If started with positive, keep celebrating
        if initial_emotion == "positive":
            # But if current is now distress, show concern
            if current_emotion in {"distress", "strong_distress"}:
                return random.choice(EMOTION_SHIFT_POSITIVE_TO_DISTRESS)
            # Otherwise keep excited tone
            return random.choice(POSITIVE_FOLLOWUP_REPLIES)

        # If started neutral but current is now emotional
        if initial_emotion == "neutral":
            if current_emotion in {"distress", "strong_distress"}:
                return random.choice(DISTRESS_FOLLOWUP_REPLIES)
            elif current_emotion == "positive":
                return random.choice(POSITIVE_FOLLOWUP_REPLIES)
            else:
                return random.choice(NEUTRAL_FOLLOWUP_REPLIES)

    # No special context handling needed
    return None


def analyze_conversation_history(history: list) -> dict:
    """
    Analyze past conversation messages to understand patterns and context.
    Returns insights about emotional patterns, recurring topics, and what user has shared.
    History format: [{"text": "message", "emotion": "distress"}, ...]
    """
    if not history:
        return {
            "has_history": False,
            "emotional_pattern": None,
            "is_consistently_distressed": False,
            "is_consistently_positive": False,
            "mentioned_work": False,
            "mentioned_relationship": False,
            "mentioned_health": False,
            "mentioned_family": False,
            "previous_topics": [],
            "distress_count": 0,
            "positive_count": 0,
            "user_messages": []
        }

    # All messages in history are user messages (simplified format)
    user_texts = [msg.get("text", "").lower() for msg in history if msg.get("text")]
    emotions = [msg.get("emotion") for msg in history if msg.get("emotion")]

    # Count emotional patterns
    distress_emotions = {"distress", "strong_distress", "sad", "anxious", "angry"}
    positive_emotions = {"positive", "happy", "excited"}

    distress_count = sum(1 for e in emotions if e in distress_emotions)
    positive_count = sum(1 for e in emotions if e in positive_emotions)

    # Determine pattern
    is_consistently_distressed = distress_count >= 2 and distress_count > positive_count
    is_consistently_positive = positive_count >= 2 and positive_count > distress_count

    # Detect mentioned topics from history
    all_text = " ".join(user_texts)

    work_keywords = {"job", "work", "boss", "manager", "coworker", "office", "salary", "fired", "quit", "deadline", "meeting", "promotion", "hr", "sunday", "sundays", "weekend", "overtime", "pressure", "pressuring", "burnout"}
    relationship_keywords = {"boyfriend", "girlfriend", "partner", "ex", "dating", "relationship", "broke up", "breakup", "crush", "love"}
    health_keywords = {"sick", "tired", "exhausted", "sleep", "doctor", "hospital", "pain", "headache", "anxiety", "depressed", "mental health"}
    family_keywords = {"mom", "dad", "mother", "father", "parents", "sibling", "brother", "sister", "family", "grandma", "grandpa"}

    mentioned_work = any(kw in all_text for kw in work_keywords)
    mentioned_relationship = any(kw in all_text for kw in relationship_keywords)
    mentioned_health = any(kw in all_text for kw in health_keywords)
    mentioned_family = any(kw in all_text for kw in family_keywords)

    # Build topic list
    previous_topics = []
    if mentioned_work:
        previous_topics.append("work")
    if mentioned_relationship:
        previous_topics.append("relationship")
    if mentioned_health:
        previous_topics.append("health")
    if mentioned_family:
        previous_topics.append("family")

    return {
        "has_history": True,
        "emotional_pattern": "distress" if is_consistently_distressed else ("positive" if is_consistently_positive else "mixed"),
        "is_consistently_distressed": is_consistently_distressed,
        "is_consistently_positive": is_consistently_positive,
        "mentioned_work": mentioned_work,
        "mentioned_relationship": mentioned_relationship,
        "mentioned_health": mentioned_health,
        "mentioned_family": mentioned_family,
        "previous_topics": previous_topics,
        "distress_count": distress_count,
        "positive_count": positive_count,
        "user_messages": user_texts
    }


# History-aware reply prefixes (to acknowledge ongoing struggles)
HISTORY_AWARE_DISTRESS_PREFIXES = [
    "i know things have been rough lately 💙 ",
    "u've been going through a lot 💙 ",
    "it sounds like things are still heavy 💙 ",
    "i can tell this has been weighing on u 💙 ",
    "u've been dealing with so much lately 💙 ",
]

HISTORY_AWARE_WORK_PREFIXES = [
    "work is really testing u huh 💙 ",
    "this job stuff sounds exhausting 💙 ",
    "still dealing with work stuff i see 💙 ",
]

HISTORY_AWARE_RELATIONSHIP_PREFIXES = [
    "relationship stuff is so emotionally draining 💙 ",
    "the heart stuff is hard 💙 ",
]

HISTORY_AWARE_HEALTH_PREFIXES = [
    "ur wellbeing matters so much 💙 ",
    "pls take care of urself 💙 ",
]

# Phrases that ask about past conversation
RECALL_QUESTION_PHRASES = {
    "what did i tell you", "what did i tell u", "what i told you", "what i told u",
    "do you remember", "do u remember", "did you forget", "did u forget",
    "remember what i said", "remember what i told", "what did i say",
    "what was i saying", "what were we talking", "what was i talking",
    "did i tell you", "did i tell u", "did i mention", "did i say",
    "you remember", "u remember", "remember earlier", "remember before",
    "what i mentioned", "what i was saying", "what i said before",
    "we were talking about", "i was telling you", "i was telling u"
}


def generate_history_recall_reply(history_analysis: dict, text_clean: str) -> str:
    """
    Generate a reply that recalls what user mentioned in conversation history.
    """
    if not history_analysis["has_history"]:
        return "hmm we just started talking! 💙 what's on ur mind??"

    user_messages = history_analysis["user_messages"]
    topics = history_analysis["previous_topics"]

    # Build a summary of what they mentioned
    mentions = []

    if history_analysis["mentioned_work"]:
        # Find work-related message (including HR, pressure, etc.)
        work_msg = next((m for m in user_messages if any(w in m for w in {"job", "work", "boss", "office", "manager", "hr", "pressure", "sunday", "overtime", "burnout"})), None)
        if work_msg:
            mentions.append(f"the work stuff - \"{work_msg[:45]}{'...' if len(work_msg) > 45 else ''}\"")
        else:
            mentions.append("the work stuff")

    if history_analysis["mentioned_relationship"]:
        rel_msg = next((m for m in user_messages if any(w in m for w in {"boyfriend", "girlfriend", "ex", "relationship", "partner"})), None)
        if rel_msg:
            mentions.append(f"the relationship stuff")
        else:
            mentions.append("relationship things")

    if history_analysis["mentioned_health"]:
        health_msg = next((m for m in user_messages if any(w in m for w in {"sick", "tired", "health", "sleep", "anxiety", "exhausted"})), None)
        if health_msg:
            mentions.append(f"how u've been feeling")
        else:
            mentions.append("how u've been feeling")

    if history_analysis["mentioned_family"]:
        mentions.append("the family stuff")

    # Build natural response (subtle, not system-like)
    if mentions:
        if len(mentions) == 1:
            natural_replies = [
                f"yeah i remember 💙 {mentions[0]}. still on ur mind??",
                f"mhm 💙 u mentioned {mentions[0]}. i'm still here",
                f"yeah 💙 that's the same thing u were dealing with. i'm here with u",
                f"i remember 💙 {mentions[0]}. wanna talk more about it??",
                f"yeah ofc 💙 u told me about {mentions[0]}. i'm listening"
            ]
            return random.choice(natural_replies)
        else:
            return f"yeah i remember 💙 u've been dealing with a lot. i'm here with u"
    else:
        # No specific topics detected but we have messages
        if user_messages:
            return "yeah 💙 i'm still here. wanna keep talking about it??"
        else:
            return "i'm here 💙 what's on ur mind??"


def generate_reply(anon_id: str, emotion: str, decision: dict, text: str, conversation_context: dict = None, conversation_history: list = None, timestamp: str = None):
    try:
        # 🔑 USE USER INPUT — NOT MEMORY
        text_clean = text.strip().lower()

        # ---- ANALYZE CONVERSATION HISTORY ----
        history_analysis = analyze_conversation_history(conversation_history or [])

        # ---- CONFUSING INPUT CHECK ----
        # If the input is garbled/unclear, ask nicely to repeat
        if is_confusing_input(text_clean):
            return random.choice(CONFUSION_REPLIES)

        # ---- LONG TEXT ANALYSIS ----
        # For massive messages, analyze themes and emotions
        long_text_analysis = analyze_long_text(text_clean)

        # ---- RECALL QUESTION HANDLING (PRIORITY) ----
        # If user asks "what did I tell you" or similar, recall from history
        if has_phrase(text_clean, RECALL_QUESTION_PHRASES):
            return generate_history_recall_reply(history_analysis, text_clean)

        # ---- TURN AWARENESS ----
        # After turn 3, switch to bestie mode - no interrogating "what happened??"
        turn_count = 1
        if conversation_context:
            turn_count = conversation_context.get("turn_count", 1)

        # If we have history, adjust turn count based on history length
        if history_analysis["has_history"]:
            # Count user messages in history to get true turn count
            history_turns = len(history_analysis["user_messages"])
            turn_count = max(turn_count, history_turns + 1)

        # After turn 3, we switch to bestie mode (half bestie energy, no prying)
        # Turn 1: usually greet, Turn 2-3: ask what happened, Turn 4+: bestie mode
        bestie_mode = turn_count >= 4

        # Subtle question suffixes for turn 1-3 (soft, not interrogating)
        QUESTION_SUFFIXES = [
            " wanna talk about it??",
            " i'm here if u wanna vent 💙",
            " i'm listening 💙",
            " u can tell me anything 💙",
            " i'm here for u 💙",
            " wanna share more??",
            " i got u 💙",
            " talk to me 💙",
            " u okay??",
            " what's been going on??"
        ]

        def ensure_question(reply: str, force: bool = False) -> str:
            """Add a subtle question/invite to the reply if we're in turn 1-3."""
            if bestie_mode and not force:
                return reply  # No questions in bestie mode
            # Check if reply already has a question or invite
            question_indicators = ["??", "wanna", "want to", "tell me", "i'm here", "i'm listening", "talk to me"]
            reply_lower = reply.lower()
            has_question = any(q in reply_lower for q in question_indicators)
            if has_question:
                return reply
            # Add a subtle suffix
            return reply.rstrip(".!") + random.choice(QUESTION_SUFFIXES)

        # Smart question logic - only ask "what happened" if actually needed
        # Needed when: turn 1-2 AND message is vague/short AND no clear context yet
        def needs_question():
            if bestie_mode:
                return False  # Never ask after turn 3
            # Check if message gives enough context already
            word_count = len(text_clean.split())
            has_enough_context = word_count >= 8  # Longer msgs have context
            # If they're already explaining something, don't ask
            explaining_words = {"because", "since", "so", "like", "when", "after", "before"}
            is_explaining = any(w in text_clean for w in explaining_words)
            return not has_enough_context and not is_explaining

        # ---- GREET HANDLING ----
        if text_clean in GREET_WORDS:
            return random.choice(GREETINGS)

        # ---- EXIT HANDLING (context-aware) ----
        if text_clean in EXIT_WORDS or has_phrase(text_clean, EXIT_PHRASES):
            # If the conversation had distress emotions, give caring exit
            if emotion in {"distress", "strong_distress"}:
                return random.choice(DISTRESS_EXIT_REPLIES)
            # If the conversation was positive/happy, give cheerful exit
            elif emotion == "positive":
                return random.choice(HAPPY_EXIT_REPLIES)
            # If the conversation was neutral, give balanced exit
            elif emotion == "neutral":
                return random.choice(NEUTRAL_EXIT_REPLIES)
            # Default fallback exit
            return random.choice(EXIT_REPLIES)

        # ---- LONG TEXT / MASSIVE MESSAGE HANDLING ----
        # When someone sends a huge paragraph, acknowledge and respond appropriately
        if long_text_analysis["is_very_long"] and long_text_analysis["is_venting"]:
            # Check primary theme for more specific response
            primary_theme = long_text_analysis["primary_theme"]
            if primary_theme == "work_stress":
                return random.choice(LONG_VENT_WORK_REPLIES)
            elif primary_theme == "relationship":
                return random.choice(LONG_VENT_RELATIONSHIP_REPLIES)
            elif long_text_analysis["has_multiple_topics"]:
                return random.choice(LONG_VENT_MIXED_REPLIES)
            else:
                return random.choice(LONG_VENT_REPLIES)

        # ---- GRIEF / LOSS / DEATH HANDLING (PRIORITY) ----
        # Must be checked early - grief should NEVER be classified as neutral
        has_grief = has_phrase(text_clean, GRIEF_LOSS_PHRASES)
        has_work_callousness = any(kw in text_clean for kw in GRIEF_WORK_CALLOUSNESS_KEYWORDS)

        # Compound case: grief + workplace callousness (e.g., "grandfather died, they won't give me a day off")
        if has_grief and has_work_callousness:
            if bestie_mode:
                return random.choice(BESTIE_GRIEF_NO_QUESTION + BESTIE_WORK_NO_QUESTION)
            return random.choice(GRIEF_WORK_CALLOUSNESS_REPLIES)

        # Regular grief/loss
        if has_grief:
            if bestie_mode:
                return random.choice(BESTIE_GRIEF_NO_QUESTION)
            return random.choice(GRIEF_LOSS_REPLIES)

        # ---- INJURY / ILLNESS + FORCED TO WORK (PRIORITY) ----
        # Someone injured/sick but still working - show concern first
        has_injury = any(kw in text_clean for kw in INJURY_ILLNESS_KEYWORDS)
        has_work_context = any(word in text_clean for word in {
            "work", "working", "job", "office", "still working",
            "have to work", "made me work", "no humanity", "no leave",
            "no day off", "wont let me", "won't let me", "expected to"
        })

        if has_injury and has_work_context:
            if bestie_mode:
                return random.choice(BESTIE_INJURY_NO_QUESTION)
            return random.choice(INJURY_WORK_CALLOUSNESS_REPLIES)

        # ---- EMOTIONAL HURT / MANIPULATION HANDLING ----
        if has_phrase(text_clean, EMOTIONAL_HURT_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_EMOTIONAL_HURT_NO_QUESTION)
            return ensure_question(random.choice(EMOTIONAL_HURT_REPLIES))

        # ---- FEELING UNDERVALUED / CRITICIZED / DISRESPECTED HANDLING ----
        if has_phrase(text_clean, FEELING_UNDERVALUED_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_UNDERVALUED_NO_QUESTION)
            return ensure_question(random.choice(FEELING_UNDERVALUED_REPLIES))

        # ---- ABOUT TO CRY / CRYING / EMOTIONAL HANDLING ----
        if has_phrase(text_clean, ABOUT_TO_CRY_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_CRYING_NO_QUESTION)
            return random.choice(ABOUT_TO_CRY_REPLIES)

        # ---- SARCASM / JOKES / DARK HUMOR HANDLING ----
        if has_phrase(text_clean, SARCASM_PHRASES):
            # After turn 3, just match energy without asking questions
            if bestie_mode:
                return random.choice(BESTIE_SARCASM_NO_QUESTION)

            # Determine if it's frustrated sarcasm or playful
            # Check for distress signals underneath
            signal_check = count_signals_in_text(text_clean)
            if signal_check["distress_count"] >= 1:
                # Sarcasm masking frustration
                return random.choice(SARCASM_FRUSTRATION_REPLIES)
            elif any(word in text_clean for word in {"lol", "lmao", "haha", "jk", "kidding", "joking"}):
                # Playful sarcasm
                return random.choice(SARCASM_PLAYFUL_REPLIES)
            elif any(phrase in text_clean for phrase in {"why am i like this", "classic me", "story of my life", "cant have nice things", "can't have nice things"}):
                # Self-deprecating humor - check in gently
                return random.choice(DARK_HUMOR_SELF_DEPRECATING_REPLIES)
            else:
                # Default to frustration sarcasm (safer)
                return random.choice(SARCASM_FRUSTRATION_REPLIES)

        # ---- PATTERN-BASED SIGNAL DETECTION ----
        # Count signals in text to determine response mode
        signal_analysis = count_signals_in_text(text_clean)
        distress_count = signal_analysis["distress_count"]
        positive_count = signal_analysis["positive_count"]
        dominant = signal_analysis["dominant"]

        # ---- WANNA QUIT / GONNA QUIT DETECTION ----
        # Work frustration where they want to quit (NOT job loss)
        if has_phrase(text_clean, WANNA_QUIT_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_WANNA_QUIT_NO_QUESTION)
            return random.choice(WANNA_QUIT_REPLIES)

        # ---- ESCAPE FANTASY DETECTION (quit job + run away) ----
        # Check BEFORE work distress to catch the specific funny combo
        if has_phrase(text_clean, ESCAPE_FANTASY_PHRASES):
            return random.choice(ESCAPE_FANTASY_REPLIES)

        # ---- HUMILIATION DETECTION ----
        # Being humiliated at work - high impact emotional distress
        if has_phrase(text_clean, HUMILIATION_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_HUMILIATION_NO_QUESTION)
            return random.choice(HUMILIATION_REPLIES)

        # ---- NO ONE UNDERSTANDS / FEELING UNHEARD DETECTION ----
        # Isolation and feeling misunderstood
        if has_phrase(text_clean, NO_ONE_UNDERSTANDS_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_NO_ONE_UNDERSTANDS_NO_QUESTION)
            return random.choice(NO_ONE_UNDERSTANDS_REPLIES)

        # ---- UNDERPAID / COMPENSATION ISSUES DETECTION ----
        # Not being paid fairly for their work
        if has_phrase(text_clean, UNDERPAID_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_UNDERPAID_NO_QUESTION)
            return random.choice(UNDERPAID_REPLIES)

        # ---- MENTAL HEALTH COLLAPSING / DETERIORATING DETECTION ----
        # Serious mental health decline - priority handling
        if has_phrase(text_clean, MENTAL_HEALTH_COLLAPSING_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_MENTAL_HEALTH_COLLAPSING_NO_QUESTION)
            return random.choice(MENTAL_HEALTH_COLLAPSING_REPLIES)

        # ---- FORCING / COERCION DETECTION ----
        # Being forced into things - validate their autonomy
        if has_phrase(text_clean, FORCING_COERCION_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_FORCING_NO_QUESTION)
            return random.choice(FORCING_COERCION_REPLIES)

        # ---- REGRET / MISTAKE DETECTION ----
        # Regretting decisions - be compassionate
        if has_phrase(text_clean, REGRET_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_REGRET_NO_QUESTION)
            return random.choice(REGRET_REPLIES)

        # ---- SUFFOCATED / TRAPPED DETECTION ----
        # Feeling stuck or suffocated - show empathy
        if has_phrase(text_clean, SUFFOCATED_TRAPPED_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_SUFFOCATED_NO_QUESTION)
            return random.choice(SUFFOCATED_TRAPPED_REPLIES)

        # ---- SILVER LINING DETECTION (finding bright side amid chaos) ----
        # When user finds something positive despite the mess
        if has_phrase(text_clean, SILVER_LINING_PHRASES):
            return random.choice(SILVER_LINING_REPLIES)

        # ---- CORPORATE VENTING DETECTION ----
        # Specific corporate/work-related emotional categories

        # Corporate Burnout (exhausted from work overload)
        if has_phrase(text_clean, CORPORATE_BURNOUT_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_WORK_NO_QUESTION)
            return ensure_question(random.choice(CORPORATE_BURNOUT_REPLIES))

        # Corporate Frustration (annoyed at meetings, coworkers, processes)
        if has_phrase(text_clean, CORPORATE_FRUSTRATION_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_WORK_NO_QUESTION)
            return ensure_question(random.choice(CORPORATE_FRUSTRATION_REPLIES))

        # Stuck while others succeed (comparison / left behind feeling)
        if has_phrase(text_clean, STUCK_COMPARISON_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_STUCK_COMPARISON_REPLIES)
            return random.choice(STUCK_COMPARISON_REPLIES)

        # Corporate Drama / Backstabbing (friend turned enemy, badmouthing, jealousy)
        if has_phrase(text_clean, CORPORATE_DRAMA_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_CORPORATE_DRAMA_REPLIES)
            return random.choice(CORPORATE_DRAMA_REPLIES)

        # Corporate Sadness (feeling undervalued, stuck, overlooked)
        if has_phrase(text_clean, CORPORATE_SAD_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_WORK_NO_QUESTION)
            return ensure_question(random.choice(CORPORATE_SAD_REPLIES))

        # Corporate Anxiety (fear of layoffs, performance pressure)
        if has_phrase(text_clean, CORPORATE_ANXIETY_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_WORK_NO_QUESTION)
            return ensure_question(random.choice(CORPORATE_ANXIETY_REPLIES))

        # Corporate Numbness (emotionally detached, going through motions)
        if has_phrase(text_clean, CORPORATE_NUMB_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_WORK_NO_QUESTION)
            return ensure_question(random.choice(CORPORATE_NUMB_REPLIES))

        # Corporate Sarcasm (dark humor about work life)
        if has_phrase(text_clean, CORPORATE_SARCASM_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_SARCASM_NO_QUESTION)
            return random.choice(CORPORATE_SARCASM_REPLIES)

        # Corporate Meme Venting (internet culture work jokes)
        if has_phrase(text_clean, CORPORATE_MEME_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_SARCASM_NO_QUESTION)
            return random.choice(CORPORATE_MEME_REPLIES)

        # Corporate Positive (small wins, good moments at work)
        if has_phrase(text_clean, CORPORATE_POSITIVE_PHRASES):
            return random.choice(CORPORATE_POSITIVE_REPLIES)

        # Corporate Mixed (torn between staying and leaving, conflicted)
        if has_phrase(text_clean, CORPORATE_MIXED_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_WORK_NO_QUESTION)
            return random.choice(CORPORATE_MIXED_REPLIES)

        # ---- YELLED AT / SCREAMED AT DETECTION ----
        # Specific handling for being yelled at (high-impact workplace distress)
        if any(word in text_clean for word in YELLED_AT_KEYWORDS):
            if bestie_mode:
                return random.choice(BESTIE_DISTRESS_NO_QUESTION)
            return random.choice(YELLED_AT_REPLIES)

        # ---- SALARY / PAYDAY / BONUS HANDLING (CHECK BEFORE WORK DISTRESS) ----
        # Must check BEFORE work distress since "salary" could trigger work context
        if has_phrase(text_clean, SALARY_PHRASES):
            reply = random.choice(SALARY_REPLIES)
            if not bestie_mode:
                reply = ensure_question(reply)
            return reply

        # ---- WORK/JOB DISTRESS DETECTION ----
        # Check for work-related keywords and give work-specific reply
        # Note: "salary" removed - handled above with positive salary detection
        work_keywords = {"job", "work", "boss", "manager", "coworker", "coworkers",
                        "office", "workplace", "company", "fired", "quit",
                        "promotion", "deadline", "meeting", "colleague", "colleagues"}
        has_work_context_local = any(word in text_clean for word in work_keywords)

        if has_work_context_local and distress_count >= 1:
            if bestie_mode:
                return random.choice(BESTIE_WORK_NO_QUESTION)
            return ensure_question(random.choice(WORK_DISTRESS_REPLIES))

        # Heavy Distress Pattern (3+ distress signals)
        if distress_count >= 3 or dominant == "distress_heavy":
            if bestie_mode:
                return random.choice(BESTIE_DISTRESS_NO_QUESTION)
            return ensure_question(random.choice(HEAVY_DISTRESS_REPLIES))

        # Heavy Positive Pattern (3+ positive signals)
        if positive_count >= 3 or dominant == "positive_heavy":
            return random.choice(HEAVY_POSITIVE_REPLIES)

        # Mixed Emotions Pattern (both distress and positive)
        if dominant == "mixed" or (distress_count >= 2 and positive_count >= 2):
            if bestie_mode:
                return random.choice(BESTIE_DISTRESS_NO_QUESTION)
            return ensure_question(random.choice(MIXED_EMOTIONS_REPLIES))

        # Moderate Distress Pattern (2 distress signals, more than positive)
        if dominant == "distress_moderate" or (distress_count >= 2 and distress_count > positive_count):
            if bestie_mode:
                return random.choice(BESTIE_DISTRESS_NO_QUESTION)
            return ensure_question(random.choice(MODERATE_DISTRESS_REPLIES))

        # Moderate Positive Pattern (2 positive signals, more than distress)
        if dominant == "positive_moderate" or (positive_count >= 2 and positive_count > distress_count):
            return random.choice(MODERATE_POSITIVE_REPLIES)

        # ---- POSITIVE NEUTRAL / FUN PLANS HANDLING ----
        if has_phrase(text_clean, POSITIVE_NEUTRAL_PHRASES):
            return random.choice(POSITIVE_NEUTRAL_REPLIES)

        # ---- SPENDING MONEY / TREATING SELF HANDLING ----
        if has_phrase(text_clean, SPENDING_MONEY_PHRASES):
            return random.choice(SPENDING_MONEY_REPLIES)

        # ---- SIMPLE SADNESS HANDLING ----
        if has_phrase(text_clean, SIMPLE_SAD_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_DISTRESS_NO_QUESTION)
            return ensure_question(random.choice(SIMPLE_SAD_REPLIES))

        # ---- PANIC / ANXIETY ATTACK HANDLING (URGENT - grounding first) ----
        if has_phrase(text_clean, PANIC_ATTACK_PHRASES):
            # Panic attacks need IMMEDIATE grounding - BREATHE response
            if bestie_mode:
                return random.choice(BESTIE_PANIC_ATTACK_REPLIES)
            return random.choice(PANIC_ATTACK_REPLIES)

        # ---- MENTAL HEALTH HANDLING (always treat with utmost concern) ----
        if has_phrase(text_clean, MENTAL_HEALTH_CRISIS_PHRASES):
            # Mental health ALWAYS gets caring response, no questions
            if bestie_mode:
                return random.choice(BESTIE_MENTAL_HEALTH_NO_QUESTION)
            return random.choice(MENTAL_HEALTH_CRISIS_REPLIES)

        # ---- JOB FEAR / ANXIETY HANDLING ----
        if has_phrase(text_clean, JOB_FEAR_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_WORK_NO_QUESTION)
            return random.choice(JOB_FEAR_REPLIES)

        # ---- RANT / VENTING / BAD DAY HANDLING ----
        # For long text (rants), check if it's a bad day vent
        is_long_text = len(text_clean) > 100 or len(text_clean.split()) > 20

        # Check for bad day phrases
        if has_phrase(text_clean, RANT_BAD_DAY_PHRASES):
            if bestie_mode:
                return random.choice(BESTIE_DISTRESS_NO_QUESTION)
            return random.choice(BAD_DAY_REPLIES)

        # Check for rant starters with negative emotion
        has_rant_starter = has_phrase(text_clean, RANT_STARTER_PHRASES)
        if has_rant_starter and emotion in {"distress", "strong_distress"}:
            if bestie_mode:
                return random.choice(BESTIE_DISTRESS_NO_QUESTION)
            return random.choice(RANT_REPLIES)

        # For long emotional text that seems like venting
        if is_long_text and emotion in {"distress", "strong_distress"}:
            if bestie_mode:
                return random.choice(BESTIE_DISTRESS_NO_QUESTION)
            return random.choice(RANT_REPLIES)

        # ---- SURPRISE HANDLING ----
        # Check for positive surprise
        has_pos_surprise = has_phrase(text_clean, POSITIVE_SURPRISE_PHRASES)
        has_neg_surprise = has_phrase(text_clean, NEGATIVE_SURPRISE_PHRASES)

        # Determine surprise type by context words
        has_pos_context = any(word in text_clean for word in POSITIVE_SURPRISE_CONTEXT)
        has_neg_context = any(word in text_clean for word in NEGATIVE_SURPRISE_CONTEXT)

        if has_pos_surprise or has_neg_surprise:
            # If explicitly negative surprise phrase or negative context
            if has_neg_surprise or (has_neg_context and not has_pos_context):
                return random.choice(NEGATIVE_SURPRISE_REPLIES)
            # If positive context or general surprise with positive emotion
            elif has_pos_context or emotion == "positive":
                return random.choice(POSITIVE_SURPRISE_REPLIES)
            # Default: check emotion to decide
            elif emotion in {"distress", "strong_distress"}:
                return random.choice(NEGATIVE_SURPRISE_REPLIES)
            else:
                return random.choice(POSITIVE_SURPRISE_REPLIES)

        # ---- CONVERSATION CONTEXT HANDLING ----
        # If this is NOT the first message, use context-aware replies
        if conversation_context and conversation_context.get("turn_count", 1) > 1:
            context_reply = _get_context_aware_reply(emotion, conversation_context, text_clean)
            if context_reply:
                return context_reply

        # ---- HELP REQUEST HANDLING ----
        if has_phrase(text_clean, HELP_REQUEST_PHRASES):
            return random.choice(HELP_REQUEST_REPLIES)

        # ---- ADVICE / "WHAT SHOULD I DO" HANDLING ----
        if has_phrase(text_clean, ADVICE_REQUEST_PHRASES):
            return random.choice(ADVICE_REPLIES)

        # ---- ANALYZE FOR COMPOUND STATEMENTS ----
        analysis = analyze_compound_statement(text_clean)

        # ---- NO PEACE / NOT LETTING ME REST HANDLING ----
        if analysis["has_no_peace"] or has_phrase(text_clean, NO_PEACE_PHRASES):
            return random.choice(NO_PEACE_REPLIES)

        # ---- COMPOUND STATEMENT HANDLING (multiple issues) ----
        # Count how many categories are triggered
        triggered_count = sum([
            analysis["has_rest"],
            analysis["has_sick"],
            analysis["has_frustration"]
        ])

        if analysis["is_compound"] and triggered_count >= 2:
            # Multiple issues mentioned together
            return random.choice(COMPOUND_REPLIES)

        # ---- REST / BREAK HANDLING ----
        if analysis["has_rest"] or has_phrase(text_clean, REST_PHRASES):
            return random.choice(REST_REPLIES)

        # ---- FEELING BETTER HANDLING (follow-up to sickness) ----
        if has_phrase(text_clean, FEELING_BETTER_PHRASES):
            # They said they're feeling better - show relief
            return random.choice(FEELING_BETTER_REPLIES)

        # ---- STILL SICK HANDLING (follow-up to sickness) ----
        if has_phrase(text_clean, STILL_SICK_PHRASES):
            # They said they're still sick - show care
            return random.choice(STILL_SICK_REPLIES)

        # ---- PHYSICAL INJURY / ACCIDENT HANDLING ----
        if has_phrase(text_clean, PHYSICAL_INJURY_PHRASES):
            # show concern for injuries/accidents
            return random.choice(CONCERN_REPLIES)

        # ---- SICK / UNWELL HANDLING (with concern) ----
        if analysis["has_sick"]:
            # show concern when they say they're not feeling well
            return random.choice(CONCERN_REPLIES)

        # ---- FRUSTRATION HANDLING (with light consoling + tips) ----
        if analysis["has_frustration"]:
            # for frustration, give consoling response with breathing tips
            return random.choice(CONSOLING_WITH_TIPS)

        # ---- WORK EXHAUSTION HANDLING ----
        if has_phrase(text_clean, WORK_EXHAUSTION_PHRASES):
            return random.choice(WORK_EXHAUSTION_REPLIES)

        # Check for exhaustion words + work words combo (e.g., "exhausted and done after my job")
        exhaustion_words = {"exhausted", "tired", "drained", "burnt", "burned", "burnout", "done", "over"}
        has_exhaustion = any(word in text_clean for word in exhaustion_words)
        has_work_context = any(word in text_clean for word in WORK_EXHAUSTION_WORDS)
        if has_exhaustion and has_work_context:
            return random.choice(WORK_EXHAUSTION_REPLIES)

        blocks = REPLIES.get(emotion)
        if not blocks:
            # If we couldn't match emotion and message seems unclear, ask to clarify
            if len(text_clean.split()) < 5 and not any(w in text_clean for w in {"sad", "happy", "angry", "tired", "work", "friend", "family"}):
                return random.choice(CONFUSION_REPLIES)
            return random.choice(FALLBACK_REPLIES)

        ack = random.choice(blocks["ack"])
        reflect = random.choice(blocks["reflect"])
        follow = random.choice(blocks["follow"])

        # ---- CHECK FOR SIMILAR PAST TOPIC ----
        past_topic = get_similar_past_topic(anon_id, text)
        if past_topic and past_topic["topic"] in MEMORY_TOPIC_RESPONSES:
            # use memory-based response instead of generic reflect
            reflect = random.choice(MEMORY_TOPIC_RESPONSES[past_topic["topic"]])

        # ---- CHECK FOR RECURRING EMOTION ----
        emotion_count = get_recurring_emotion(anon_id, emotion)
        if emotion_count >= 2 and emotion in RECURRING_EMOTION_RESPONSES:
            # user has been feeling same way multiple times
            if random.random() < 0.4:  # 40% chance to mention it
                reflect = random.choice(RECURRING_EMOTION_RESPONSES[emotion])

        # ---- FALLBACK MEMORY CHECK (old behavior) ----
        if not past_topic:
            memory_hint = get_memory_hint(anon_id)
            if memory_hint == emotion and emotion in {"distress", "strong_distress"}:
                reflect = (
                    "You mentioned feeling this way earlier too — "
                    "it sounds like it's been sticking with you."
                )

        # ---- HISTORY-AWARE REPLY ENHANCEMENT ----
        # If user has been consistently distressed across conversation history,
        # acknowledge that with a caring prefix
        final_reply = f"{ack} {reflect} {follow}"

        if history_analysis["has_history"] and history_analysis["is_consistently_distressed"]:
            # User has been struggling - add empathetic prefix
            if history_analysis["mentioned_work"] and any(w in text_clean for w in {"job", "work", "boss", "office"}):
                prefix = random.choice(HISTORY_AWARE_WORK_PREFIXES)
                final_reply = prefix + final_reply.lower()
            elif history_analysis["mentioned_relationship"] and any(w in text_clean for w in {"boyfriend", "girlfriend", "ex", "relationship", "partner"}):
                prefix = random.choice(HISTORY_AWARE_RELATIONSHIP_PREFIXES)
                final_reply = prefix + final_reply.lower()
            elif history_analysis["mentioned_health"] and any(w in text_clean for w in {"sick", "tired", "health", "sleep", "anxiety"}):
                prefix = random.choice(HISTORY_AWARE_HEALTH_PREFIXES)
                final_reply = prefix + final_reply.lower()
            elif turn_count >= 3:
                # General ongoing distress acknowledgment (only if turn 3+)
                prefix = random.choice(HISTORY_AWARE_DISTRESS_PREFIXES)
                final_reply = prefix + final_reply.lower()

        # ---- ONE LINE ONLY ----
        if decision.get("pace") == "slow":
            return f"{ack} {follow}"

        return final_reply

    except Exception:
        return random.choice(FALLBACK_REPLIES)

