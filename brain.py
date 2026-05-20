# =============================================================================
# brain.py — Shapatar Bot
# =============================================================================
#
# This file contains ALL the logic of the bot.
# It imports data from data.py and uses it to process messages.
# It knows nothing about Discord, Telegram, or any platform.
# It only knows: take a string, do work, return a string.
#
# Functions in this file (built one step at a time):
#   preprocess(text)          → clean raw input for matching
#   detect_intent(text)       → classify cleaned input into a category
#   check_mood_transition()   → decide if mood should change
#   generate_response()       → pick/assemble a response
#   apply_style()             → add personality-wide style touches
#   process_message()         → master function that runs the full pipeline
# =============================================================================

import re 
import random

# Import all our data from data.py.
from data import (
    # Trigger lists
    INVITATION_TRIGGERS, OPINION_TRIGGERS, HELP_TRIGGERS,
    STRESS_TRIGGERS, ANGER_TRIGGERS, GREETING_TRIGGERS,
    CARS_TRIGGERS, IPHONE_TRIGGERS, YOUNG_STUNNERS_TRIGGERS,
    KARACHI_TRIGGERS, TRAVEL_TRIGGERS, FOLLOWUP_TRIGGERS,

    # Negation and intent routing
    NEGATION_WORDS,
    INTENT_PRIORITY,

    # Response pools
    FENCE_SIT, FENCE_SIT_DOUBLE, DIRECT_YES, TOPIC_DODGE,
    FOLLOWUP_DEFLECTION, EAGER_VOLUNTEER, VOLUNTEER_FOLLOWUP,
    GREETING_RESPONSES, OPINION_RESPONSES,
    CARS_RESPONSES, IPHONE_RESPONSES, YOUNG_STUNNERS_RESPONSES,
    KARACHI_RESPONSES, TRAVEL_RESPONSES,
    GENERAL_CHAT,
    TENSE_FENCE_SIT, TENSE_GENERAL, TENSE_STRESS_ACKNOWLEDGE,
    SULKING_RESPONSES,
    EXPLOSION_OPENERS, EXPLOSION_MIDDLES, EXPLOSION_CLOSERS,
    EXPLOSION_AFTERMATH,

    # Tuning constants
    STRESS_COUNT_TO_TENSE, STRESS_COUNT_TO_EXPLODE,
    SULK_RECOVERY_TURNS, TENSE_RECOVERY_TURNS,
    EXPLOSION_COOLDOWN_TURNS, EXPLOSION_PROBABILITY,
    FENCE_SIT_PROBABILITY, DIRECT_YES_PROBABILITY, TOPIC_DODGE_PROBABILITY,
    DOUBLE_FENCE_SIT_PROB,
    ANGER_CONFIDENCE_THRESHOLD, DEFAULT_CONFIDENCE_THRESHOLD,
    NEGATION_PROXIMITY_WORDS,
    YAAR_INSERTION_PROB, ELLIPSIS_PROB, ABEY_PREFIX_PROB,
)


# =============================================================================
# THE PUNCTUATION PATTERN — defined once, reused in preprocess()
# =============================================================================
#
# This is a compiled regex pattern. Two concepts here:
#
# 1. CHARACTER CLASS [...]:
#    In regex, square brackets define a "character class" — match ANY ONE
#    character listed inside. [!?.,] matches exactly one of: !, ?, ., or comma.
#
# 2. re.compile():
#    You can either write re.sub(pattern, ...) inline every time, or compile
#    the pattern once into a Pattern object and reuse it. Compiling is faster
#    when the same pattern is used repeatedly — the regex engine parses the
#    pattern string once and stores the result. For a bot receiving many
#    messages, this matters.
#
# WHAT THIS PATTERN MATCHES:
#   [!؟?.,،۔]   — common punctuation in both English and Urdu Roman text
#   +            — one or more of them in a row
#   ("yaar!!!" → "yaar", "hain..." → "hain")
# =============================================================================

PUNCTUATION_PATTERN = re.compile(r'[!؟?.,،۔]+')


def preprocess(text: str) -> str:
    """
    Clean raw user input into a normalised form suitable for pattern matching.

    The transformations applied, in order:
    1. Lowercase    — so trigger matching is case-insensitive
    2. Strip edges  — remove leading/trailing whitespace
    3. Remove punctuation — so "hain!" matches trigger "hain"
    4. Collapse spaces — so "chal  chalte" matches trigger "chal chalte"

    Args:
        text: The raw string received from the user.

    Returns:
        A cleaned string, ready for intent detection.
    """

    # Step 1: Lowercase
    text = text.lower()

    # Step 2: Strip leading and trailing whitespace
    text = text.strip()

    # Step 3: Remove punctuation
    # PUNCTUATION_PATTERN.sub(replacement, string) works exactly like
    # re.sub() but uses the pre-compiled pattern for efficiency.
    # We replace matched punctuation with a space (not empty string)
    # because "yaar,chal" (comma between words) should become
    # "yaar chal" (space between words), not "yaarchal" (merged).
    text = PUNCTUATION_PATTERN.sub(' ', text)

    # Step 4: Collapse multiple spaces into one
    # After Step 3, we might have introduced extra spaces where punctuation
    # was. This step collapses any sequence of whitespace into exactly
    # one space, then strips edges again (step 3 might have added edge spaces).
    text = re.sub(r'\s+', ' ', text).strip()

    return text


# =============================================================================
# INTENT DETECTION
# =============================================================================
#
# This section answers: "what category does this message belong to?"
#
# The output is a string label — one of the keys in INTENT_PRIORITY.
# This label is the ONLY thing passed forward to response generation.
# Detection and response generation are completely separate concerns.
#
# TWO FUNCTIONS:
#   _check_triggers()   — helper, does one trigger list check with negation
#   detect_intent()     — main function, runs all checks in priority order
#
# The underscore prefix on _check_triggers is a Python convention meaning
# "this is an internal helper, not intended to be called from outside
# this module." It is not enforced — just a signal to other developers.
# =============================================================================


# Map each intent name to its corresponding trigger list from data.py.
# This dictionary is defined at module level so detect_intent() can look
# up any intent's triggers by name without a long chain of if/elif.
# Adding a new intent later means adding one line here and one in INTENT_PRIORITY.
INTENT_TRIGGER_MAP = {
    "anger":          ANGER_TRIGGERS,
    "stress":         STRESS_TRIGGERS,
    "followup":       FOLLOWUP_TRIGGERS,
    "greeting":       GREETING_TRIGGERS,
    "invitation":     INVITATION_TRIGGERS,
    "help_request":   HELP_TRIGGERS,
    "opinion":        OPINION_TRIGGERS,
    "cars":           CARS_TRIGGERS,
    "iphone":         IPHONE_TRIGGERS,
    "young_stunners": YOUNG_STUNNERS_TRIGGERS,
    "karachi":        KARACHI_TRIGGERS,
    "travel":         TRAVEL_TRIGGERS,
    # "general" has no triggers — it is the fallback, always fires last
}


def _check_triggers(cleaned_text: str, trigger_list: list) -> tuple:
    """
    Check whether any phrase in trigger_list appears in cleaned_text,
    and if so, whether that match is negated by a nearby negation word.

    This is a HELPER FUNCTION — it is called by detect_intent() for
    each intent in priority order. It encapsulates the matching + negation
    logic so detect_intent() stays clean and readable.

    HOW NEGATION DETECTION WORKS:
        1. Tokenise cleaned_text into a word list
        2. For each trigger phrase, find if it appears in the text
        3. If it does, find the position of the trigger's first word
           in the token list
        4. Look at the N words before that position (N = NEGATION_PROXIMITY_WORDS)
        5. If any negation word appears in that window, mark as negated

    Args:
        cleaned_text:  The preprocessed message string.
        trigger_list:  One of the trigger lists from data.py.

    Returns:
        (matched: bool, negated: bool)
        matched=True means at least one trigger phrase was found.
        negated=True means the match was preceded by a negation word.
        If matched=False, negated is always False.
    """

    # Tokenise once — we reuse this list for the negation proximity check.
    # .split() splits on whitespace, returns a list of word strings.
    words = cleaned_text.split()

    for trigger_phrase in trigger_list:

        # STEP 1: Fast check first.
        # Before doing any expensive positional work, check if the phrase
        # even appears in the text at all. The `in` operator on strings
        # is a simple substring search — very fast. If this fails,
        # there is nothing to do for this trigger.
        if trigger_phrase not in cleaned_text:
            continue  # Move to next trigger phrase in the list

        # STEP 2: Phrase found. Now check for negation.
        # We need the position (index) of the trigger's first word
        # in the token list, so we can look backwards from it.
        trigger_first_word = trigger_phrase.split()[0]

        # Find the index of the trigger's first word in the word list.
        # We use a try/except because .index() raises ValueError if not found.
        # This should rarely happen (we already confirmed the phrase is in
        # the text), but defensive programming anticipates edge cases.
        try:
            trigger_position = words.index(trigger_first_word)
        except ValueError:
            # Could not find the word in token list — edge case, treat as match
            return True, False

        # STEP 3: Define the negation window.
        # We look at the slice of words from (trigger_position - N) to
        # trigger_position. This is the window of words just before the trigger.
        #
        # max(0, ...) prevents negative indices — if the trigger is the
        # first word, there are no words before it to check.
        window_start = max(0, trigger_position - NEGATION_PROXIMITY_WORDS)
        preceding_words = words[window_start:trigger_position]

        # STEP 4: Check if any negation word appears in the window.
        # We use Python's built-in any() function with a generator expression.
        #
        # any(condition for item in iterable) returns True if condition
        # is True for at least one item. It short-circuits — stops as soon
        # as it finds the first True. This is more Pythonic and slightly
        # faster than a manual for loop with a break.
        is_negated = any(neg in preceding_words for neg in NEGATION_WORDS)

        # STEP 5: Return the result.
        # We found a match. Whether it is negated determines what the
        # caller does with it — but we always report the match itself.
        return True, is_negated

    # Looped through all triggers, none matched.
    return False, False


def detect_intent(cleaned_text: str, last_intent: str = None) -> tuple:
    """
    Classify the cleaned input message into an intent category.

    Checks each intent in INTENT_PRIORITY order. The first intent whose
    triggers match (and are not negated) is returned. If nothing matches,
    returns "general" as the fallback.

    The `last_intent` parameter enables context-awareness for the followup
    detection — if the bot's previous response was an invitation fence-sit,
    and the user is now asking "kya masla hai?", we want to detect "followup"
    even if the followup triggers are somewhat ambiguous.

    Args:
        cleaned_text:  Preprocessed message from preprocess().
        last_intent:   The intent of the previous bot turn (optional).
                       Used to inform followup detection.

    Returns:
        (intent: str, negated: bool)
        intent is one of the keys in INTENT_PRIORITY, or "general".
        negated indicates whether the detected trigger was negated —
        useful context for the response generator.
    """

    # Special case: empty or very short messages.
    # A message of 1-2 characters cannot meaningfully match any phrase trigger.
    # Return "general" immediately rather than running all checks for nothing.
    if len(cleaned_text.strip()) <= 2:
        return "general", False

    # Walk through INTENT_PRIORITY in order.
    # This is the entire priority mechanism — the list order IS the priority.
    # The first intent that matches wins; everything else is ignored.
    for intent_name in INTENT_PRIORITY:

        # "general" has no trigger list — it is the fallback.
        # Skip it here; it is returned at the bottom if nothing else matches.
        if intent_name == "general":
            continue

        # Look up this intent's trigger list from the map we defined above.
        trigger_list = INTENT_TRIGGER_MAP.get(intent_name, [])

        # Run the trigger check with negation detection.
        matched, negated = _check_triggers(cleaned_text, trigger_list)

        if matched:
            # Special handling: negated anger or invitation is still informative.
            # A negated invitation ("nahi chalte hain") might signal stress
            # or disappointment — but for now, we skip negated matches and
            # continue to the next intent. This keeps the logic simple.
            # A future improvement could handle negated intents specifically.
            if negated:
                continue

            # Non-negated match found — this intent wins.
            return intent_name, negated

    # Nothing matched across all intents. Return the fallback.
    # negated=False because there was no match to negate.
    return "general", False


# =============================================================================
# STATE MACHINE — MOOD MANAGEMENT
# =============================================================================
#
# Two functions:
#   create_context()          → initialise a fresh conversation context
#   update_mood()             → take context + intent, return updated context
#
# The context dictionary is the bot's memory. It is created once at the
# start of a conversation and passed through every turn.
# =============================================================================


def create_context() -> dict:
    """
    Create and return a fresh conversation context dictionary.

    This is called once at the start of a conversation — in main.py, before the conversation loop begins. 
    The returned dictionary is then passed into process_message() on every turn.

    Returns:
        A dictionary representing the initial state of a conversation.
    """
    return {
        # --- MOOD STATE MACHINE ---
        "mood": "normal",          # Current mood: normal/tense/sulking/exploding

        # --- COUNTERS ---
        # These drive the automatic mood transitions.
        "stress_count": 0,         # Stress triggers accumulated in current mood
        "turns_in_mood": 0,        # How many turns spent in the current mood
        "explosion_cooldown": 0,   # Turns remaining before explosion is possible again
        "total_turns": 0,          # Total turns in the conversation (for debugging)

        # --- CONVERSATIONAL CONTEXT ---
        # Minimal memory of what just happened — enables followup detection
        # and prevents the same response appearing twice in a row.
        "last_intent": None,       # Intent detected in the previous turn
        "last_response": None,     # Response sent in the previous turn
    }


def update_mood(context: dict, intent: str) -> dict:
    """
    Apply FSM transition logic: given current context and detected intent,return updated context reflecting any mood change.

    This function does NOT generate a response. It only updates state.

    Args:
        context:  The current conversation context dict.
        intent:   The intent string returned by detect_intent().

    Returns:
        Updated context dictionary. The original is not modified, we work on a copy.
    """

    ctx = context.copy()

    # Increment total turns and the in-mood counter on every call.
    ctx["total_turns"] += 1
    ctx["turns_in_mood"] += 1

    # Decrement explosion cooldown if active.
    # max(0, ...) prevents it going negative — once at zero, it stays at zero.
    ctx["explosion_cooldown"] = max(0, ctx["explosion_cooldown"] - 1)

    # Store the intent for next turn's context awareness.
    ctx["last_intent"] = intent

    # -------------------------------------------------------------------------
    # TRANSITION LOGIC — organised by current mood
    # -------------------------------------------------------------------------

    current_mood = ctx["mood"]

    # ---- TRANSITIONS FROM: normal ----------------------------------------
    if current_mood == "normal":

        if intent == "anger":
            # Betrayal/let-down immediately triggers sulking.
            # No intermediate state — this is a direct transition.
            ctx = _transition_to(ctx, "sulking")

        elif intent == "stress":
            ctx["stress_count"] += 1
            if ctx["stress_count"] >= STRESS_COUNT_TO_TENSE:
                # Enough stress accumulated — go tense.
                ctx = _transition_to(ctx, "tense")
                # Reset stress counter — now counting toward explosion from tense
                ctx["stress_count"] = 0

        else:
            # Non-stress, non-anger intent in normal mood.
            # Gradually reduce stress_count so it decays naturally if the conversation stays light.
            # Prevents ghost tension from a single stress message long ago.
            ctx["stress_count"] = max(0, ctx["stress_count"] - 1)

    # ---- TRANSITIONS FROM: tense -----------------------------------------
    elif current_mood == "tense":

        if intent == "anger":
            # Betrayal while already tense — goes to sulking directly.
            ctx = _transition_to(ctx, "sulking")

        elif intent == "stress":
            ctx["stress_count"] += 1

            if ctx["stress_count"] >= STRESS_COUNT_TO_EXPLODE:
                # Threshold reached, but explosion is not certain.
                # Roll the dice using the probability from data.py.
                if (ctx["explosion_cooldown"] == 0 and
                        random.random() < EXPLOSION_PROBABILITY):
                    ctx = _transition_to(ctx, "exploding")
                    ctx["explosion_cooldown"] = EXPLOSION_COOLDOWN_TURNS
                else:
                    # Threshold met but did not explode, stays tense,
                    # reset counter so the pressure can build again.
                    ctx["stress_count"] = 0

        else:
            # Non-stress turn while tense, start counting toward recovery.
            # After enough calm turns, drift back to normal.
            if ctx["turns_in_mood"] >= TENSE_RECOVERY_TURNS:
                ctx = _transition_to(ctx, "normal")

    # ---- TRANSITIONS FROM: sulking ---------------------------------------
    elif current_mood == "sulking":

        # While sulking, no input changes mood — only time passing does. This reflects the behaviour: he does not snap out of sulking
        # because of what is said, he just eventually cools down.
        if ctx["turns_in_mood"] >= SULK_RECOVERY_TURNS:
            ctx = _transition_to(ctx, "normal")

        # Anger trigger while sulking deepens/resets the sulk timer —
        # if you remind him of what made him sulk, he sulks longer.
        if intent == "anger":
            ctx["turns_in_mood"] = 0  # Reset the timer — sulk restarts

    # ---- TRANSITIONS FROM: exploding -------------------------------------
    elif current_mood == "exploding":
        # Explosion is a single-turn state. It fires, then immediately transitions to sulking. 
        # The explosion itself is the response for that turn. After it, he goes quiet.
        ctx = _transition_to(ctx, "sulking")

    return ctx


def _transition_to(ctx: dict, new_mood: str) -> dict:
    """
    Helper: perform a mood transition, resetting relevant counters.

    Args:
        ctx:       Current context dictionary (already a copy).
        new_mood:  The mood state to transition into.

    Returns:
        Updated context with new mood and reset counters.
    """
    ctx["mood"] = new_mood
    ctx["turns_in_mood"] = 0    # Always reset when entering a new mood
    ctx["stress_count"] = 0     # Reset stress accumulation on any transition
    return ctx

    