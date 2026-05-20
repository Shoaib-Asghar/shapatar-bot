# Shapatar Bot

Shapatar Bot is a simple, rule-based Python chatbot that chats in Karachi-style Roman Urdu slang. Its personality is inspired by a friend (fictionalized for fun). Instead of fancy AI or machine learning, it uses regex pattern matching, proximity checks, and a simple state machine to respond with a distinct, moody flair.

Just a fun little project, unsurprisingly the results of such a hardcoded bot are modest compared to modern AI bots.

## Technical Capabilities

- **Pattern & Regex Matching**: Uses hardcoded trigger lists and compiled regular expressions to catch root words, allowing it to handle common morphological variations in informal Roman Urdu texting.
- **Proximity-Based Negation**: Rather than looking for exact strings, it checks for negations (like "nahi" or "nai") within a 4-word lookbehind window of a recognized trigger, flipping the detected intent.
- **State Machine (Mood Tracking)**: Uses a Finite State Machine for tracking a `stress` counter. The bot transitions between structural states (`normal`, `tense`, `sulking`, `exploding`) based on aggressive inputs, and auto-recovers after a set number of calm conversation turns.
- **Turn Context**: Retains the `last_intent` variable across the chat loop to handle simple conversational follow-ups without losing track of the subject.

## Architecture & File Structure

The project strictly decouples the rules engine from the vocabulary representation:

- `brain.py` - The logic engine. It handles text normalization, runs the `detect_intent` pipeline (trigger matching, negation checking, regex fallbacks), manages the mood FSM (Finite State Machine), and selects responses.
- `data.py` - The data layer. Contains arrays of Roman Urdu string triggers, compiled regex roots, and nested dictionary pools of responses categorized by mood and intent.
- `main.py` - The terminal entry point and primary `while` loop keeping the chat alive.

## Getting Started

No special libraries or external APIs are required. Just run it with standard library Python 3:

```bash
python main.py
```
