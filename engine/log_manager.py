# engine/log_manager.py
# Purpose: Log every conversation for future training improvement

import json
import os
from datetime import datetime

LOG_FILE = os.path.join("logs", "conversations.json")


def load_logs() -> dict:
    """Loads existing conversation logs."""
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"conversations": []}


def save_log(user_input: str, detected_intent: str, response: str):
    """
    Saves each conversation turn to logs/conversations.json.
    This data is used later to improve training.
    """
    try:
        logs = load_logs()

        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_input": user_input,
            "detected_intent": detected_intent,
            "response_given": response[:100],  # Save first 100 chars
            "feedback": None  # Will be filled later by user rating
        }

        logs["conversations"].append(entry)

        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

    except Exception as e:
        print(f"[Log Warning] Could not save log: {e}")


def get_log_summary() -> dict:
    """
    Returns a summary of conversation logs.
    Useful for understanding what users are asking most.
    """
    logs = load_logs()
    conversations = logs.get("conversations", [])

    if not conversations:
        return {"total": 0, "intents": {}}

    intent_counts = {}
    for entry in conversations:
        intent = entry.get("detected_intent", "UNKNOWN")
        intent_counts[intent] = intent_counts.get(intent, 0) + 1

    return {
        "total": len(conversations),
        "intents": intent_counts
    }


if __name__ == "__main__":
    # Test logging
    save_log(
        user_input="I need a refund",
        detected_intent="CP001",
        response="It sounds like you haven't received your refund..."
    )
    print("✅ Log saved successfully!")
    print("📊 Summary:", get_log_summary())