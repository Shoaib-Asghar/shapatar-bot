# =============================================================================
# main.py — Shapatar Bot Terminal Interface
# =============================================================================
#
# This file is the terminal-based conversation interface.
# Its only responsibilities are:
#   - Start a conversation (initialise context)
#   - Run the input/output loop
#   - Pass input to the brain, receive output, display it
#   - Handle errors and exit cleanly
#
# This file knows nothing about the bot's personality, mood logic,
# or response generation. It is a thin shell around brain.py.
#
# To run: python main.py
# To exit: type 'quit' or 'exit', or press Ctrl+C
# =============================================================================

from brain import create_context, process_message


# Visual constants — centralised so changing the look means editing one place
SEPARATOR    = "─" * 50          # Horizontal rule between turns
BOT_NAME     = "Shapatar Bot"    # Displayed in the header and prompt
USER_LABEL   = "You"
BOT_LABEL    = "Bot"


def print_header():
    print()
    print("=" * 50)
    print(f"   {BOT_NAME}")
    print(f"   Type 'quit' or 'exit' to end the conversation.")
    print(f"   Press Ctrl+C at any time to force quit.")
    print("=" * 50)
    print()


def print_turn(user_text: str, bot_response: str, mood: str):
    """
    Print one complete conversation turn with consistent formatting..

    Args:
        user_text:    What the user typed.
        bot_response: What the bot replied.
        mood:         Current mood after this turn (for debug visibility).
    """
    print(SEPARATOR)
    print(f"{USER_LABEL}: {user_text}")
    print()
    print(f"{BOT_LABEL}: {bot_response}")
    print(f"[Mood: {mood}]")
    print()


def run():
    """
    The main conversation loop.

    Initialises context once, then loops indefinitely:
      1. Get input from user
      2. Handle edge cases (empty input, quit command)
      3. Pass to brain, get response and updated context
      4. Display the turn
      5. Repeat
    """

    print_header()

    # Initialise context once at the start of the conversation. This is the bot's memory, it persists for the entire session.
    # Every call to process_message() will update and return it.
    context = create_context()

    print(f"{BOT_NAME} is ready. Say something.\n")

    try:
        while True:
            # Get raw input from the user. input() blocks execution, the program pauses here 
            # and waits until the user presses Enter. This is synchronous I/O.
            try:
                user_text = input(f"{USER_LABEL}: ")
            except EOFError:
                # will be raised if the input stream is closed (e.g. on windows, Ctrl+Z then Enter). Exit gracefully instead of crashing.
                print("\n[End of input stream. Goodbye.]")
                break

            # Edge case: empty input, user pressed Enter with nothing typed.
            # Strip whitespace first so "   " is also treated as empty.
            if not user_text.strip():
                print("[Helo..]\n")
                continue  # Skip to next loop iteration, do not call brain

            # Quit command, recognised before passing to the brain.
            if user_text.lower().strip() in ("quit", "exit", "bye"):
                print(f"\n{BOT_NAME}: theek hai yaar. Allah hafiz.\n")
                break

            # Pass to the brain pipeline.
            # process_message() runs all five stages and returns:
            #   response       — the final string to display
            #   updated_context — the new context for the next turn
            #
            # We reassign context here — this is how the bot's memory persists across turns. 
            # The updated context from this turn becomes the input context for the next turn.
            try:
                response, context = process_message(user_text, context)
            except Exception as e:
                # Something went wrong inside the brain pipeline. We catch it here, print a debug message, and keep running.
                print(f"[Brain error: {e}]")
                print("[Shapatar Bot had a moment. Try again.]\n")
                continue

            # Display the full turn with formatting
            print_turn(user_text, response, context["mood"])

    except KeyboardInterrupt:
        # User pressed Ctrl+C, exit gracefully with a message
        # instead of the default ugly traceback.
        print(f"\n\n{BOT_NAME}: abey bhai, kya hua? theek hai, Allah hafiz yaar.\n")


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    run()