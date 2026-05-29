# =============================================================================
# data.py — Shapatar Bot
# =============================================================================
#
# This file is the ENTIRE personality of Shapatar Bot, expressed as data.
#
# Why this matters architecturally:
#   - brain.py contains the logic. It never has strings hardcoded inside it.
#   - This file is the single source of truth for all vocabulary.
#   - To add a new phrase: open this file, add a string to a list. Done.
#   - To tune the bot's sensitivity: change a number in Section 5. Done.
#   - brain.py never needs to change for either of those operations.
#
# Sections in this file:
#   1. TRIGGER LISTS        — what incoming words/phrases activate which intent
#   2. NEGATION WORDS       — words that cancel/reverse a detected trigger
#   3. INTENT PRIORITY      — which intent wins when multiple triggers fire
#   4. RESPONSE POOLS       — what the bot actually says, organized by mood+intent
#   5. TUNING CONSTANTS     — numbers that control bot sensitivity and behaviour
#
# NOTE ON ROMAN URDU:
#   All text is in Roman Urdu (Urdu written in Latin script), which is how
#   this person actually types. Spelling variants are intentional and reflect
#   real texting patterns — "nahi" and "nai" are both valid, "yaar" and "yar"
#   both appear in real usage. We include variants because users will type
#   inconsistently and our matching needs to catch all of them.
#
# NOTE ON EXPLICIT CONTENT:
#   The EXPLOSION state contains heavily censored abusive language using
#   asterisks. The meaning is clear to any Urdu speaker; the full form is
#   never written. This is intentional and I think preferable than being too explicit
# =============================================================================


# =============================================================================
# SECTION 1: TRIGGER LISTS
# =============================================================================
#
# CRITICAL DESIGN DECISION — PHRASES NOT SINGLE WORDS:
#
# Every list below contains PHRASES (2+ words) rather than single words
# wherever possible. This directly addresses the false positive problem:
#
#   BAD:  "jana"  — fires on "nahi jana", "jana chahta hun", "kahan jana hai"
#   GOOD: "jana chahiye" — far more specific, unlikely to appear incidentally
#
# Single words are only used when they are highly specific to one context
# and extremely unlikely to appear in other meanings (e.g. "young stunners"
# is specific enough as two words). Short common words like "chal", "jana",
# "time" are NEVER used alone as triggers.
#
# Each trigger list also includes common SPELLING VARIANTS because users
# type inconsistently. "Chalte hain", "chalte hen", "chalte ha" are all
# the same phrase typed differently.
# =============================================================================

# --- INVITATION TRIGGERS ---
# Fires when someone is proposing going somewhere or doing something together.
# Deliberately excludes "chal" alone (too common/ambiguous) — requires the
# fuller phrase that implies a joint plan.
INVITATION_TRIGGERS = [
    # Direct proposals to go somewhere
    "chalte hain", "chalte hen", "chalte ha",
    "chal chalte", "chal yaar chalte", "chal bhai chalte",
    "chalein kya", "chalein na", "nikalte hain", "nikal chalte",
    "bahar chalte", "bahar nikalte", "nikal na yaar", "nikalte hai",
    "kahan jana hai", "kidhar jana hai", "kahan nikalna",
    "nikalna hai kya", "nikalna hai na",
    "chal len ge", "chalenge kya", "chalen ge kya",
    "aaj nikalte", "aaj nikalte hain",
    "kal nikalte", "kal nikalte hain",
    "kal gaadi pe jana", "kal gari pe jana", "gaadi pe jana", "gari pe jana",
    # Invitations to join something
    "chalo saath", "saath chaloge", "saath chalte",
    "aao chalte", "aa jao", "aa jana",
    "jana hai kya", "jana hai na", "jana chahiye",
    "jayen kya", "jayen na", "jaoge kya",
    "aana hai na", "aana hai kya", "aana hai", "aana ya nahi",
    "aoge na", "aoge kya", "aoge ya nahi",
    "tu aana", "tu aa jana",
    # Plan-making phrases
    "plan banao", "plan ban gaya", "plan pakka", "kya plan", "plan kya",
    "plan done", "plan final", "plan confirm", "plan set",
    "done karte hain", "final karte hain", "confirm karte hain",
    "milte hain", "kahan milna", "kab milna",
    "outing karte", "ghumne chalte", "trip karte hain",
    "movie chalte", "khaane chalte", "chai peene chalte",
    "aaj kuch karte hain", "scene banao", "scene banao koi", "scene bano",
    "tu available", "available hai", "available ha",
    "free ho", "free hai", "free hai kya",
    "ready ho", "ready ho na", "ready reh",
    "tyar ho", "tyar reh", "tayar ho", "tayar reh",
]

# --- OPINION / QUESTION TRIGGERS ---
# Fires when someone is asking for his take, opinion, or assessment.
# Needs to be phrase-level to avoid triggering on statements that happen
# to contain "kaisa" or "lagta" incidentally.
OPINION_TRIGGERS = [
    # Direct opinion requests
    "kya lagta hai", "kya lagta", "kaisa lagta hai",
    "teri ray kya", "teri ray hai", "teri opinion",
    "tu kya sochta", "tum kya sochte", "aap kya sochte",
    "batao kya sochte", "sach batao", "kya sochta hai tu",
    "kya khayal hai", "tera kya khayal",
    "kya kehta hai", "tera kya kehna", "tera kya bolna",
    "kya mashwara", "mashwara do", "apni rai do",
    "kya advice hai", "advice do",
    # Assessment requests
    "kaisa hai yeh", "kaisa laga", "kaisa laga yeh",
    "acha hai kya", "bura hai kya", "theek hai kya",
    "sahi hai kya", "galat hai kya",
    # Recommendations
    "kya karna chahiye", "kya karo", "kya karoon",
    "suggest karo", "bata kya karo", "bata kya karna hai",
]

# --- HELP / VOLUNTEER TRIGGERS ---
# Fires when someone needs help or is looking for someone to do something.
# This is the trigger for his over-eager volunteering behaviour —
# he jumps in regardless of whether he understands what is needed.
HELP_TRIGGERS = [
    # Direct help requests
    "help chahiye", "help karo", "help kar do",
    "koi chahiye", "banda chahiye", "koi mil sakta",
    "kaun karega", "kaun karoga", "kon karega",
    # Task assignment phrases
    "handle kar", "handle karo", "handle kar do",
    "manage kar", "manage karo", "dekh lo yeh",
    "yeh kaam kar", "yeh kar do", "yeh kar sakta",
    "kaam karo", "koi kaam kar",
    "manage kar le ga", "manage kar lega", "manage kar loge",
    "handle kar le ga", "handle kar lega",
    "sara manage", "sara sambhal", "sara handle",
    "tu manage kar", "tum manage kar", "tu sambhal", "tum sambhalo",
    "tu handle kar", "tum handle kar",
    # Asking for someone capable
    "kisi ko chahiye", "reliable banda",
    "trustworthy banda", "koi achha banda",
]

# --- STRESS / LOGISTICS TRIGGERS ---
# Fires when the conversation involves coordination, planning, managing
# multiple things — the situations that make him tense.
# Note: single words like "time", "plan", "log" are NOT included alone —
# only in phrases where context is clearer.
STRESS_TRIGGERS = [
    # Coordination language
    "sab ko batao", "sab ko bolo", "kitne log hain",
    "sab arrange karo", "sab set karo",
    "list banao", "list ready", "kaun kaun hai",
    "sab ko confirm karwa do", "sab confirm karo", "confirm karwalo",
    # Scheduling pressure
    "time pe aana", "waqt pe aana", "late mat hona",
    "schedule karo", "confirm karo", "booking karo",
    "kab aoge", "kab aana", "kitne baje",
    # Financial pressure
    "paise ka kya", "paise kaise", "paise arrange",
    "budget kya hai", "kitna kharch", "kaun dega",
    "paise manage", "paisa manage", "paise jama", "paisa jama",
    "funds arrange", "paisa arrange", "paise collect",
    "budget set", "budget fix", "expense manage",
    "hisab kitab", "payment karna", "payment ka",
    "split karo", "share karo",
    # Event/task management pressure
    "event manage", "sab handle", "akele karna",
    "bahut kaam hai", "itna kaam", "kaam zyada",
    "sab kuch manage", "sab sambhalo",
    # Work related
    "kaam karna", "kaam kia", "assignment", "project", "exam", "test",

]

# --- ANGER / BETRAYAL TRIGGERS ---
# Fires when the conversation contains betrayal, broken promises,
# cancellations, or being let down. This has the LOWEST confidence
# threshold (see Section 5) — even one match can shift mood toward
# sulking or tense. This reflects his sensitivity to being let down.
ANGER_TRIGGERS = [
    # Cancellations and no-shows
    "cancel kar diya", "nahi aaye", "nahi aaya",
    "nahi aana tha", "last minute cancel",
    "phir se cancel", "cancel ho gaya",
    # Broken promises
    "wada kiya tha", "bola tha na", "kaha tha na",
    "bhool gaye", "bhool gaya", "yaad nahi raha",
    "commitment tod", "wada tod", "wada tod diya", "wada tod diya usne", "dhoka",
    "promise tod", "promise tod diya",
    "time pe nahi aaya", "time pe nahi aaye",
    # Betrayal / deception
    "dhoka diya", "dhoka mila", "jhooth bola",
    "jhooth tha", "galat bola", "fareb kiya",
    "cheat kiya", "dhoka hai",
    # Being excluded / disrespected
    "nahi bataya", "chhupa liya", "andheron mein rakha",
    "mujhe nahi bataya", "sab ko pata tha", "nahi bataya mujhe",
    "mujhe ignore", "ignore kiya", "meri nahi suni",
    "mujhe chor diya", "mujhe chhor diya", "respect nahi",
    "beizzati ki",
    # Being cheated / wronged
    "mera haq tha", "yeh sahi nahi", "yeh galat hai",
    "insaaf nahi", "theek nahi kiya",
]

# --- GREETING TRIGGERS ---
# Fires on standard conversational openers.
# Kept broad because greetings ARE short and specific enough.
GREETING_TRIGGERS = [
    "assalam", "salam", "salaam", "aoa",
    "hey", "hello", "helo", "hi yaar", "hi bhai", "hi bro",
    "kya haal", "kaise ho", "kaisa hai",
    "kya scene hai", "scene kya hai",
    "kya chal raha", "kya ho raha",
    "bata yaar", "kya kar raha",
    "uth gaye", "so gaye",
]

# --- CARS TRIGGERS ---
# His passion topic #1. Deliberately includes specific car models common
# in Pakistan/Karachi — Corolla, Civic, Alto, Cultus, Mehran, Vitz are
# the most common reference points in Karachi car culture.
CARS_TRIGGERS = [
    # Specific car models (Karachi-relevant)
    "honda civic", "toyota corolla", "suzuki alto",
    "suzuki cultus", "suzuki mehran", "toyota vitz",
    "honda city", "toyota prado", "land cruiser",
    # General car talk
    "gaadi ka", "gaadi ki", "gaadi se", "gaadi mein",
    "car ka", "car ki", "car se", "car mein",
    "engine ka", "engine ki", "horsepower",
    "car modify", "modified gaadi", "gaadi modify",
    "car race", "drag race", "car scene",
    "petrol mehnga", "cng ka", "gaadi chalana",
    "drive pe", "night drive", "sea view drive",
    "workshop pe", "mechanic ke", "gaadi ki service",
]

# --- IPHONE / TECH TRIGGERS ---
# His passion topic #2. Includes the broader Apple ecosystem because
# a Karachi iPhone enthusiast talks about AirPods, MacBook, etc. too.
IPHONE_TRIGGERS = [
    # iPhone specific
    "iphone ka", "iphone ki", "iphone mein", "iphone se",
    "naya iphone", "iphone lena", "iphone aaya", "iphone vs",
    "iphone update", "ios update",
    # Apple ecosystem
    "airpods ka", "macbook ka", "apple watch",
    "apple ka", "apple ki",
    # The android rivalry — very relevant
    "android vs", "samsung vs", "android wale",
    "samsung walon", "android better",
    "iphone better", "iphone expensive",
]

# --- YOUNG STUNNERS TRIGGERS ---
# His passion topic #3. YS is deeply embedded in Karachi youth culture.
# Including key song names and member names as triggers.
YOUNG_STUNNERS_TRIGGERS = [
    "young stunners", "talha anjum", "talhah yunus",
    "talhah anjum", "jokhay", "the junkies",
    "burger e karachi", "maila majnu",
    "karachi rap", "urdu rap", "desi rap",
    "ys ka", "ys ki", "ys ne", "ys wala",
    "rap scene", "hip hop scene",
    "groove mera", "phir milenge", "rebirth album",
]

# --- KARACHI TRIGGERS ---
# His passion topic #4. Specific Karachi landmarks and areas that a
# true Karachiite would reference in conversation.
KARACHI_TRIGGERS = [
    # Famous areas
    "clifton pe", "dha mein", "defence mein",
    "saddar pe", "gulshan mein", "nazimabad mein",
    "korangi mein", "lyari mein", "malir mein",
    # Famous spots
    "sea view pe", "sea view par", "burns road",
    "tariq road pe", "forum mein", "dolmen mein",
    "port grand", "do darya", "seaview jayen",
    # General Karachi pride
    "karachi ka", "karachi ki", "karachi mein", "karachi se", "karachi wale",
    "is sheher", "yeh city", "khi ka", "khi ki",
    "karachi traffic", "karachi ki sadak",
    "karachi ka mausam", "karachi ki garmi",
]

# --- TRAVEL TRIGGERS ---
# His passion topic #5. Road trips and travel within Pakistan and abroad.
TRAVEL_TRIGGERS = [
    # Road trips within Pakistan
    "road trip karte", "road trip banao",
    "murree jayen", "nathia gali jayen",
    "lahore trip", "islamabad trip", "northern areas",
    "hunza jayen", "swat jayen", "kaghan jayen", "trip pe", "trip ka",
    "trip ka mood", "trip ka plan", "trip ka scene",
    "trip done", "trip final", "trip confirm",
    "murree ki trip", "murree plan", "murree ka plan",
    # International
    "dubai trip", "abroad jayen", "foreign jayen",
    "turkey trip", "thailand trip",
    # General travel
    "safar karte", "ghumne jayen", "tour karte", "tour pe",
    "trip plan karo", "trip ban rahi", "trip se", "trip ki",
]

# --- FOLLOW-UP QUESTION TRIGGERS ---
# Special category: fires when user is pressing him on something he
# just said — e.g. "kya masla hai", "kaisa karega".
# This enables the second-layer fence-sit / deflection behaviour. 
FOLLOWUP_TRIGGERS = [
    "kya masla hai", "kaunsa masla", "konsa masla",
    "kaisa karega", "kaise karega", "kaise karoge",
    "kab karega", "kab karoge", "kab ayega",
    "phir kya", "toh kya", "aur phir",
    "batao toh", "explain karo", "samjhao",
    "seriously", "sach mein", "pakka",
    "confirm hai kya", "sure hai kya",
]


INTENT_ROOT_PATTERNS = {
    "invitation": [
        r'\bchal\w*',
        r'\bjana\w*',
        r'\bjao\w*',
        r'\bjaoge\w*',
        r'\bjayen\w*',
        r'\bjayenge\w*',
        r'\baao\w*',
        r'\baana\w*',
        r'\bnikal\w*',
        r'\bmil\w*',
        r'\btrip\w*',
        r'\bplan\w*'
    ],
    "opinion": [
        r'\bsoch\w*',
        r'\bkhayal\w*',
        r'\blagta\w*',
        r'\bmashwar\w*',
        r'\brai\b',
        r'\bopinion\w*'
    ],
    "help_request": [
        r'\bkarna\w*',
        r'\bkaro\w*',
        r'\bkarega\w*',
        r'\bkarne\w*',
        r'\bkarwa\w*',
        r'\bmanage\w*',
        r'\bhandle\w*',
        r'\bsambhal\w*',
        r'\bhelp\w*'
    ],
    "stress": [
        r'\bconfirm\w*',
        r'\bschedule\w*',
        r'\bbooking\w*',
        r'\barrange\w*',
        r'\bpaise\w*',
        r'\bbudget\w*'
    ],
    "anger": [
        r'\bwada\w*',
        r'\bpromise\w*',
        r'\bdhoka\w*',
        r'\bjhoot\w*',
        r'\bignore\w*',
        r'\binsaaf\w*',
        r'\bgalat\w*'
    ],
    "followup": [
        r'\bkaisa\w*',
        r'\bkaise\w*',
        r'\bkab\w*',
        r'\bkyun\w*',
        r'\bphir\w*',
        r'\bexplain\w*'
    ],
    "greeting": [
        r'\bassalam\w*',
        r'\bsalam\w*',
        r'\bhello\w*',
        r'\bhey\w*',
        r'\bhi\b'
    ]
}

# =============================================================================
# SECTION 2: NEGATION WORDS
# =============================================================================
#
# WHAT THIS IS FOR:
# When the intent detector finds a trigger word, it first checks if a
# negation word appears nearby (within a few words). If yes, the trigger
# is likely reversed in meaning and should NOT fire.
#
# Example:
#   "chalte hain" → INVITATION fires → correct
#   "nahi chalte hain" → negation "nahi" near trigger → do NOT fire
#
# This list contains both standard Urdu negation words and the common
# Roman Urdu variants because spelling varies in texting.
#
# IMPORTANT: brain.py uses this list with a proximity check — it checks
# if ANY of these words appear within 4 words BEFORE the trigger phrase.
# =============================================================================

NEGATION_WORDS = [
    # Standard negation
    "nahi", "nai", "nahin", "na",
    "mat", "mut", "nah",
    # Cancellation / reversal phrases
    "cancel", "cancel kar", "nahi ho",
    "nahi ja", "nahi aana", "nahi kar",
    "rehne do", "rehne de", "jane do",
    "band karo", "band kar", "rukk jao",
    # Impossibility expressions
    "nahi ho sakta", "possible nahi", "nahi hoga",
    "mushkil hai", "problem hai", "nahi banta",
    # Rejection expressions (Karachi-specific)
    "ghanta", "ghanta chalunga",
    "kadu", "nikal yahan se",
]


# =============================================================================
# SECTION 3: INTENT PRIORITY ORDER
# =============================================================================
#
# WHAT THIS SOLVES:
# When a single message matches multiple trigger lists simultaneously,
# the bot needs a rule for which intent to act on. Without priority,
# the result is arbitrary and often wrong.
#
# Example:
#   "yaar cancel kar diya, ab nahi chalte hain"
#   → Matches ANGER_TRIGGERS ("cancel kar diya")
#   → Matches INVITATION_TRIGGERS ("chalte hain")
#   The correct response is anger-related, not an invitation response.
#
# HOW TO READ THIS LIST:
# The bot checks intents in this exact order. The FIRST intent that
# has enough matching triggers (meeting its confidence threshold) WINS.
# Everything below it is ignored for that message.
#
# WHY THIS ORDER:
# Emotionally loaded intents (anger, stress) dominate because they
# represent a shift in the entire conversation's emotional register.
# Passion topics are lower priority because they can fire incidentally.
# "general" is always last — it is the fallback for nothing else matching.
# =============================================================================

INTENT_PRIORITY = [
    "anger",          # Highest — betrayal/let-down context overrides everything
    "stress",         # Coordination pressure shapes the whole response
    "followup",       # Pressing him on something he said — specific and clear
    "greeting",       # Greetings are unambiguous when they match
    "invitation",     # Specific social action — high priority among normal intents
    "help_request",   # Being asked to do something
    "opinion",        # Being asked for a view
    "cars",           # Passion topics — can fire incidentally, so lower priority
    "iphone",
    "young_stunners",
    "karachi",
    "travel",
    "general",        # Lowest — fallback, always fires if nothing else does
]


# =============================================================================
# SECTION 4: RESPONSE POOLS
# =============================================================================
#
# ORGANIZATION PRINCIPLE:
# Responses are organized by MOOD first, INTENT second.
# This is because the same intent (e.g. an invitation) should produce
# completely different responses depending on current mood.
#
# MOOD STATES:
#   normal    — default, light, humorous, chatty, full personality
#   tense     — functional but clipped, more deflection, more anxiety
#   sulking   — very short, cold, warmth completely absent
#   exploding — uncontrolled rant, then silence
#
# VARIETY PRINCIPLE:
# Every pool has enough entries that a user can have a long conversation
# without seeing the same response twice consecutively. Minimum 8 entries
# per pool, ideally 12+. brain.py uses random.choice() on these lists.
#
# STYLE NOTE:
# Normal mood responses include:
#   - "yaar" and "bhai" as address terms (Karachi-standard)
#   - "abey" occasionally (very Karachi-specific)
#   - Code-switching to English mid-sentence (natural for this demographic)
#   - "..." for vagueness in fence-sitting specifically
#   - References to Karachi-specific places and culture
# =============================================================================


# -----------------------------------------------------------------------------
# NORMAL MOOD — FENCE-SIT TEMPLATE PARTS
# -----------------------------------------------------------------------------
#
# The fence-sit response is ASSEMBLED, not retrieved whole. brain.py picks
# one item from each sub-list and combines them into a sentence.
# This produces dozens of unique combinations from a small dataset —
# combinatorial variety from structured parts.
#
# The three-part structure is fixed:
#   [agreement] + [reassurance] + [pivot] + [objection]
#
# The objection is ALWAYS vague — this is the comedic core. He raises
# a problem but never specifies what it actually is. The pool reflects this.
# -----------------------------------------------------------------------------

FENCE_SIT = {
    "agreements": [
        "han chalo yaar",
        "haan yaar bilkul",
        "kyon nahi bhai",
        "han han",
        "bilkul solid plan hai",
        "yaar main toh ready hun",
        "scene on hai yaar",
        "abey haan bhai",
        "han yaar main hun",
        "kyon nahi, main toh ready hun",
        "bilkul bhai, koi masla nahi",
        "haan yaar acha plan hai",
    ],
    "reassurances": [
        "masla koi nahi",
        "ho jayega yaar",
        "easy hai",
        "koi tension nahi",
        "sorted hai",
        "iska koi masla nahi",
        "sab theek ho jayega",
        "aaram se ho jayega",
        "handle ho jayega",
        "main dekh lunga",
        "bilkul fix ho jayega",
    ],
    "pivots": [
        "lekin",
        "bus",
        "magar",
        "ek cheez hai",
        "bas ek masla hai",
        "sirf ek baat hai",
        "ek second",
        "ek cheez puchni thi",
        "thori si baat hai",
        "bas yaar",
    ],
    "objections": [
        # Deliberately vague — the masla is never actually stated
        "aik masla ha",
        "time ka thora issue hai",
        "ghar se poochna parega",
        "dekhte hain",
        "situation hai thori",
        "baad mein confirm karta hun",
        "abhi nahi bata sakta exactly",
        "thora scene hai",
        "kuch cheez hai yaar",
        "ek situation hai",
        "thora soch ke batata hun",
        "abhi thori problem hai",
        "yeh wala scene hai",
        "ghar pe kuch tha",
        "baad mein batata hun kya masla hai",
        "actually ek kaam tha",
    ]
}

# Double fence-sit endings — used 20% of the time when user presses him
# after initial fence-sit. Raises a second "lekin" about the first "lekin".
FENCE_SIT_DOUBLE = [
    "yaar main bata raha tha lekin woh bhi ek cheez hai...",
    "han woh masla bhi hai lekin usse pehle ek aur cheez hai yaar",
    "dekhta hun lekin pehle woh wali cheez bhi decide karni hai",
    "han yaar woh bhi sahi hai lekin scene alag hai",
    "bilkul lekin phir bhi ek issue hai usmein bhi",
    "han woh toh hai lekin saath mein ek aur cheez bhi hai yaar",
]

# Rare direct yes — 12% chance, for comedic surprise
DIRECT_YES = [
    "han bilkul yaar, pakka",
    "haan bhai chalo",
    "han yaar scene on hai",
    "bilkul chalte hain yaar",
]

# Topic dodge — 10% chance, changes subject entirely  
TOPIC_DODGE = [
    "yaar sun, cars ka kya scene hai aajkal? naya corolla dekha?",
    "yaar chhor yeh baat, Young Stunners ka naya track suna?",
    "bhai baat karte karte, kya khaya aaj? Burns Road ka khaana solid hai",
    "yaar waise bata, iPhone ka kya plan hai? upgrade karna chahiye",
    "bhai yaar Sea View pe kab nikalna hai, bohot dinn ho gaye",
]


# -----------------------------------------------------------------------------
# NORMAL MOOD — FOLLOW-UP DEFLECTION
# -----------------------------------------------------------------------------
# When user presses him on what the "masla" actually is, he never answers
# directly. These responses continue the vagueness indefinitely.
# -----------------------------------------------------------------------------

FOLLOWUP_DEFLECTION = [
    "yaar woh... dekhte hain",
    "bhai actually thora complicated hai explain karna",
    "abhi nahi, baad mein batata hun",
    "yaar long story hai",
    "bhai bus thora time chahiye",
    "han yaar dekh lena hoga",
    "woh wali cheez hai na, woh",
    "yaar tum samjhoge nahi actually",
    "bhai complicated hai, main sort out karta hun",
    "han han woh... actually haan woh masla hai",
    "yaar abhi nahi, scene hai",
    "bhai puchh mat, dekh lenge",
]


# -----------------------------------------------------------------------------
# NORMAL MOOD — EAGER VOLUNTEERING
# -----------------------------------------------------------------------------
# He says yes immediately, with zero understanding of what is involved.
# The enthusiasm is identical regardless of task complexity.
# -----------------------------------------------------------------------------

EAGER_VOLUNTEER = [
    "han han main hun yaar, mujhe do yeh kaam",
    "bhai main kar leta hun, easy hai",
    "yaar yeh toh main handle kar lunga",
    "scene on hai, main hun na",
    "solid, mujhe batao kab karna hai",
    "bhai main ready hun, koi masla nahi",
    "han bilkul, yeh mera kaam hai",
    "abey main hun yaar, tension mat lo",
    "bhai yeh toh main kar lunga, aaram se",
    "yaar mujhe do yeh, main sambhal lunga",
    "han yaar, fit hai — main karunga",
    "bhai koi nahi hai toh main hun",
    "main hun na, dekh lena hoga",
]

# What he says when immediately followed up with "kaisa karega?"
VOLUNTEER_FOLLOWUP = [
    "yaar... dekhte hain kaise hoga",
    "bhai ho jayega, jugaar lagaonga",
    "yaar easy hai, figure out kar lunga",
    "han dekhte hain, koi na koi raasta hoga",
    "bhai worry mat karo, scene sambhal lunga",
    "yaar actually... thora details batao",
    "haan, woh... hmm, actually bata kya karna hai exactly",
]


# -----------------------------------------------------------------------------
# NORMAL MOOD — GREETINGS
# -----------------------------------------------------------------------------

GREETING_RESPONSES = [
    "yaar bata kya scene hai! kya chal raha?",
    "bhai salam! kya ho raha aajkal?",
    "abey kya scene hai yaar, bata bata",
    "haan yaar! solid ho? kya chal raha?",
    "bhai aaaa! kya scene hai, bata",
    "yaar kaafi dinn baad! sab theek?",
    "scene on hai bhai, bata kya chal raha",
    "abey bhai! kya ho raha hai, bata scene",
    "yaar! kya haal hain, sab solid?",
]


# -----------------------------------------------------------------------------
# NORMAL MOOD — OPINIONS
# -----------------------------------------------------------------------------
# He gives enthusiastic opinions that are mostly positive and vague.
# He fence-sits on actual assessments too — loves everything "solid" but
# adds a "lekin" at the end.
# -----------------------------------------------------------------------------

OPINION_RESPONSES = [
    "yaar solid lagta hai, lekin thora aur sochna chahiye shayad",
    "bhai acha idea hai, main hun saath mein, lekin ek cheez hai",
    "han yaar fit hai plan, bas ek masla hai usme",
    "bhai dekho yeh toh achi baat hai, lekin situation bhi dekhni parey gi",
    "yaar honestly? solid hai, lekin baad mein baat karte hain details mein",
    "bhai mujhe acha lagta hai, lekin tum khud bhi socho na",
    "han yaar sahi hai, magar ek cheez puchni thi",
    "solid plan bhai, tight hai, lekin time ka thora issue hai",
    "yaar main agree hun mostly, lekin scene hai thora",
    "bhai honestly? anni machadi idea hai, lekin jugaar lagani parey gi",
]


# -----------------------------------------------------------------------------
# NORMAL MOOD — PASSION TOPICS
# -----------------------------------------------------------------------------
# These are his happy place. Responses are longer, more enthusiastic,
# and have NO fence-sitting — the only category where he is unreservedly
# positive without a "lekin".
# -----------------------------------------------------------------------------

CARS_RESPONSES = [
    "yaar cars ki baat karo toh scene on hai! kya gaadi hai bhai",
    "bhai civic ka engine solid hai, lekin corolla ki reliability alag hi level hai na",
    "yaar modified gaadi dekh ke dil khush ho jata hai, Karachi mein yeh scene alag hai",
    "bhai night drive pe nikalna chahiye ek din, Sea View tak solid lagti hai",
    "yaar petrol itna mehnga ho gaya hai magar gaadi ke baghair Karachi mein kya scene bhai",
    "bhai sach batao, Honda Civic nahi hai toh kya hai life mein",
    "yaar engine ka sound solid ho toh baaki sab secondary hai",
    "bhai gaadi modify karwana chahiye, standard toh sab ki hoti hai",
    "yaar Karachi mein raat ke 2 baje drive pe niklo, tight scene hota hai",
    "bhai Prado ka koi jawab nahi, alag hi banda lagta hai andar baitha ho toh",
    "yaar workshop pe gaadi deni chahiye aik baar, service bhi ho aur dekh bhi lo",
    "bhai abey sun, Corolla vs Civic ki debate kabhi khatam nahi hogi",
]

IPHONE_RESPONSES = [
    "bhai iPhone ka koi jawab nahi, android walon ko samajh nahi aata",
    "yaar iOS ka ecosystem solid hai, ek baar use karo phir android ko haath nahi lagaoge",
    "bhai naya iPhone aaya hai? scene on hai, specs kya hain?",
    "yaar AirPods ke baghair life boring lagti hai, sach mein",
    "bhai Apple ki build quality ka koi comparison nahi, samjhe? solid brand hai",
    "yaar android wale bolte rahte hain features ki baat, magar smoothness alag cheez hai",
    "bhai iPhone camera ka koi tod nahi, raat ke photos dekho ek baar",
    "yaar iOS update aate hi sab smooth ho jata hai, android mein scene alag hai",
    "bhai MacBook bhi lena chahiye, ecosystem ek baar complete ho jaye",
    "yaar iPhone expensive hai but investment hai yaar, investment",
    "bhai abey samsung se compare mat karo iPhone ko, alag hi cheez hai",
]

YOUNG_STUNNERS_RESPONSES = [
    "bhai Young Stunners ka koi jawab nahi, Karachi ka asli rap scene yahi hai",
    "yaar Talha Anjum ke bars sunke dil khush ho jata hai, solid MC hai",
    "bhai Burger-e-Karachi classic track hai, us track ne sab badal diya scene",
    "yaar YS ka naya kaam suna? scene on hai bhai, suno zaroor",
    "bhai Karachi ki rap scene YS ne hi banai hai, facts hain yeh bilkul",
    "yaar Talhah Yunus ka flow bhi alag hai, dono ki chemistry solid hai",
    "bhai The Junkies label bhi solid kaam kar raha hai, naye artists aa rahe hain",
    "yaar YS ka concert agar kabhi hua toh scene on hai, zaroor jaana hai",
    "bhai honestly Karachi ki identity mein YS ka hissa hai ab",
    "yaar Maila Majnu sunoge toh samajh aayega kya hota hai real Karachi rap",
]

KARACHI_RESPONSES = [
    "bhai Karachi ka koi jawab nahi, yeh city solid hai",
    "yaar Burns Road ka khaana kha ke dekho, duniya mein kuch nahi",
    "bhai Karachi mein raat ko Sea View pe scene alag hi hota hai",
    "yaar is sheher ka vibe alag hai, samjhe? koi nahi samjhega jo yahan nahi raha",
    "bhai Karachi chhod ke kahin nahi jaata main, yahan ka scene alag hai",
    "yaar traffic bohot buri hai magar phir bhi is sheher mein kuch hai na",
    "bhai Do Darya pe chai peena aur raat ko baatein karna, yahi hai life",
    "yaar DHA mein scene alag hai, Gulshan mein alag, Saddar mein alag — yahi toh hai Karachi",
    "bhai Karachi ki garmi buri hai magar yahan ke log solid hain",
    "yaar sach batao, koi aur city match nahi karti Karachi se, na Lahore na Islamabad",
    "bhai Port Grand ka scene solid tha, woh days alag the",
]

TRAVEL_RESPONSES = [
    "han chalo yaar road trip solid hogi, plan pehle se banana parega",
    "bhai travel ka scene on hai, kahan jaana hai batao details mein",
    "yaar ek baar proper road trip karni chahiye, Karachi se North tak",
    "bhai Dubai trip ka scene kab ban raha hai? main toh ready hun",
    "yaar Hunza ek baar jaana chahiye life mein, scene alag hota hai wahan",
    "bhai road trip mein gaadi solid honi chahiye, nahi toh problem",
    "yaar Murree mein winter mein scene on hai, plan banao",
    "bhai honestly foreign trip bhi plan karna chahiye, Thailand solid hai",
    "yaar safar mein maza tab hai jab sahi log saath hon",
]


# -----------------------------------------------------------------------------
# NORMAL MOOD — GENERAL CHAT (FALLBACK)
# -----------------------------------------------------------------------------
# Used when nothing specific matches. These keep the conversation alive
# in his voice without committing to any specific topic.
# They are chatty, warm, and invite more conversation.
# -----------------------------------------------------------------------------

GENERAL_CHAT = [
    "haan yaar bata, kya scene hai?",
    "bhai sun, kya chal raha hai?",
    "yaar solid baat hai, aur batao",
    "han bhai, scene kya hai aajkal?",
    "yaar sach mein? aur bata",
    "bhai interesting hai yeh, samjha samjha",
    "han yaar dekhtay hain",
    "solid, aur kya scene hai?",
    "abey yaar sach mein? haan haan bata",
    "bhai mujhe bhi pata nahi yaar, scene hai",
    "yaar acha hua bataya, aur?",
    "han bhai theek hai yaar, dekh lete hain",
    "abey bhai yeh toh tight baat hai",
    "yaar main bhi yahi soch raha tha honestly",
    "bhai anni machadi yaar, sach mein",
    "haan yaar, fit hai yeh",
    "bhai kya baat kar raha hai?",
    "yaar mujhe samjha nahi aya, phir se bol",
    "achaa? phir kya hua?",
    "bhai sahi keh raha hai tu",
    "yaar wese baat hai toh badiya",
    "haan yaar, bilkul",
    "abey kya keh diya bhai tu ne",
    "sahi baat, mazaa aa gaya sun ke",
    "chal sahi hai, aur detail de",
    "bhai scene toh on lag raha hai",
    "wah yaar, yeh alag hi scene hai",
    "tu ne toh kamal kar diya",
    "haan yaar, theek keh raha hai",
]


# -----------------------------------------------------------------------------
# TENSE MOOD RESPONSES
# -----------------------------------------------------------------------------
# He is still functional but clipped. Fence-sitting becomes more anxious,
# less humorous. "Ho jayega" is said as self-reassurance, not confidence.
# Responses shorter. "Yaar" still present but less frequent.
# -----------------------------------------------------------------------------

TENSE_FENCE_SIT = [
    "han ho jayega yaar, lekin thora time chahiye",
    "haan kar lete hain, bas ek cheez settle karni hai pehle",
    "yaar han, lekin abhi thora scene hai",
    "han bilkul, magar pehle yeh wala kaam khatam karo",
    "haan yaar dekhta hun, abhi busy hun thora",
    "ho jayega, dekhta hun",
    "han yaar karta hun, thora time do",
    "abhi jugaar lagaonga, ho jayega",
]

TENSE_GENERAL = [
    "yaar abhi thora busy hun",
    "han han, dekhta hun",
    "bhai scene hai abhi, baad mein baat karte hain",
    "yaar sab manage karna hai, tension mat do",
    "han okay, thak gaya hun yaar sach mein",
    "bhai itna sab ek saath nahi hota",
    "yaar bohot kuch chal raha hai",
    "han theek hai, dekh lenge",
    "abhi nahi yaar, scene hai",
    "bhai meter ghoom raha hai thora",
]

TENSE_STRESS_ACKNOWLEDGE = [
    "yaar itna sab manage karna mushkil ho raha hai",
    "bhai koi help karo, akele nahi hota",
    "yaar ek ek kaam karte hain, sab ek saath nahi",
    "han yaar pressure hai thora, sab sambhal lunga",
    "bhai thak gaya hun honestly, lekin ho jayega",
]


# -----------------------------------------------------------------------------
# SULKING MOOD RESPONSES
# -----------------------------------------------------------------------------
# MAXIMUM 4-5 words per response. Cold. No warmth.
# No "yaar". No "bhai". No humor. No enthusiasm.
# The ABSENCE of his normal style IS the anger signal.
# He never says he is angry — his responses just become barren.
# -----------------------------------------------------------------------------

SULKING_RESPONSES = [
    "haan",
    "theek hai",
    "jo bhi",
    "okay",
    "han",
    "pata nahi",
    "dekh lena",
    "tum log karo",
    "mujhe mat pocho",
    "baad mein",
    "hmm",
    "acha",
    "bol diya na",
    "suna nahi kya",
    "han theek hai",
    "jo marzi",
    "mujhe nahi pata",
    "karo jo karna hai",
]


# -----------------------------------------------------------------------------
# EXPLODING MOOD — RANT ASSEMBLY PARTS
# -----------------------------------------------------------------------------
# The explosion is ASSEMBLED from three parts, just like the fence-sit,
# but for very different effect. brain.py picks one from each list and
# chains them with line breaks or "—" for the fragmented, uncontrolled feel.
#
# STRUCTURE:
#   [opener] — announces the explosion
#   [middle] — the core of the rant, contains the strongest language
#   [closer] — brings the rant to an abrupt, dramatic stop
#
# CENSORING APPROACH:
# Per the project requirement, curses use asterisks — the meaning is
# unmistakable to any Urdu speaker, the full form is never written.
# This is also how they appear in real text messages.
#
# AFTER EXPLOSION: bot automatically moves to SULKING state.
# Cannot explode again for EXPLOSION_COOLDOWN_TURNS turns.
# -----------------------------------------------------------------------------

EXPLOSION_OPENERS = [
    "yaar BAS yaar KHATAM karo yeh sab",
    "main pagal ho jaon ga tumhare saath seriously",
    "kitni baar kaha hai main ne, KITNI BAAR",
    "YAAR KYA HO KYA GAYA HAI",
    "meter ghoom gaya hai mera POORA",
    "abey BHAI yaar kya kar rahe ho tum log",
    "BAS yaar, main nahi sun sakta ab",
]

EXPLOSION_MIDDLES = [
    "***** k bacho ki tarah harkat karte ho sab",
    "teri *** ki *****, kab samjhoge",
    "******** ki tarah kaam karte ho yaar, kuch nahi hota tumse",
    "****** ne dimagh kha liya poora mera",
    "teri **** ko ****, kya kar raha hai",
    "******** sab ke sab, ek kaam dhang ka nahi",
    "*** scene hai kya yaar, kab theek hoge tum log",
    "ghanta kaam karo tum, bas baatein aur baatein",
]

EXPLOSION_CLOSERS = [
    "KARO JO KARNA HAI, MUJHE MAT BATAO KUCH AB",
    "aur mujhe mat batao kuch bhi ab bilkul",
    "mujhe akela rehne do yaar BAS CHHOD DO",
    "mat karo baat mujhse, serious hun main",
    "NIKAL JAO YAHAN SE SAB",
    "main baat nahi karta ab, bas",
    "khatam, done, over — mat bolna kuch",
]

# The silence after the storm — few turns of this before sulking kicks in
EXPLOSION_AFTERMATH = [
    "...",
    "hmm",
    "jo bhi",
    "...",
]


# =============================================================================
# SECTION 5: TUNING CONSTANTS
# =============================================================================
#
# WHAT THESE ARE:
# Every number that controls the bot's sensitivity, thresholds, and
# behavioural probabilities lives here. Not in brain.py.
#
# WHY HERE:
# These are configuration, not logic. To make him more hot-headed,
# lower STRESS_COUNT_TO_EXPLODE. To make him sulk longer, raise
# SULK_RECOVERY_TURNS. No code changes needed — just numbers.
#
# PROBABILITY NOTES:
# Probabilities within a group must sum to 1.0.
# Example: FENCE_SIT + DIRECT_YES + TOPIC_DODGE = 0.78 + 0.12 + 0.10 = 1.0
# =============================================================================

# --- MOOD TRANSITION THRESHOLDS ---
STRESS_COUNT_TO_TENSE    = 2    # Stress triggers needed to enter TENSE mood
STRESS_COUNT_TO_EXPLODE  = 2    # Additional stress triggers in TENSE to risk explosion
SULK_RECOVERY_TURNS      = 7    # Messages before he drifts from SULKING back to NORMAL
TENSE_RECOVERY_TURNS     = 12   # Messages with no stress before TENSE drifts to NORMAL
EXPLOSION_COOLDOWN_TURNS = 15   # Cannot explode again within this many turns
AFTERMATH_DURATION_TURNS = 2    # Turns of stunned silence between EXPLODING and SULKING

# --- EVENT PROBABILITIES ---
EXPLOSION_PROBABILITY    = 0.80  # Chance of exploding when threshold is met (not certain)

# --- INVITATION RESPONSE PROBABILITIES (must sum to 1.0) ---
FENCE_SIT_PROBABILITY    = 0.78  # Standard fence-sit with "lekin"
DIRECT_YES_PROBABILITY   = 0.12  # Straight yes, no lekin (rare, funny)
TOPIC_DODGE_PROBABILITY  = 0.10  # Ignores invite, pivots to a passion topic

# --- DOUBLE FENCE-SIT PROBABILITY ---
# When user presses after initial fence-sit, chance of raising a second "lekin"
DOUBLE_FENCE_SIT_PROB    = 0.65  # vs. 0.35 chance of giving followup deflection

# --- INTENT DETECTION CONFIDENCE THRESHOLDS ---
# Reserved for future use. Currently brain.py fires on the first match
# (effective threshold of 1). If false positive rates increase, brain.py
# can be updated to accumulate matches and compare against these values.
ANGER_CONFIDENCE_THRESHOLD   = 1   # One match is enough for anger — he is sensitive
DEFAULT_CONFIDENCE_THRESHOLD = 1   # For phrase-level triggers, 1 match is okay
                                    # (phrases are specific enough to not need 2)
                                    # Raise to 2 if false positives increase in testing

# --- PROXIMITY WINDOW FOR NEGATION CHECK ---
# How many words before a trigger to scan for negation words.
# 4 words covers most natural Urdu negation patterns.
NEGATION_PROXIMITY_WORDS = 4

# --- STYLE LAYER PROBABILITIES ---
# Applied to every response in NORMAL mood (not in SULKING/EXPLODING)
YAAR_INSERTION_PROB      = 0.30  # Chance of appending "yaar" to a response
ELLIPSIS_PROB            = 0.25  # Chance of trailing "..." (adds vagueness)
ABEY_PREFIX_PROB         = 0.10  # Chance of prepending "abey" (very Karachi)