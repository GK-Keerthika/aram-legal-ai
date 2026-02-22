 #engine/log_manager.py
# Purpose: Save logs to BOTH MongoDB and local JSON
# MongoDB = permanent cloud storage
# Local JSON = backup fallback

import json
import os
from datetime import datetime

LOGS_FILE = os.path.join("logs", "conversations.json")


def save_log(
    user_input: str,
    intent: str,
    response: str
):
    """
    Save to MongoDB first.
    Always save to local JSON as backup.
    """
    # Try MongoDB first
    try:
        from engine.mongo_logger import save_to_mongo
        save_to_mongo(user_input, intent, response)
    except Exception as e:
        print(f"⚠️  Mongo log failed: {e}")

    # Always save locally as backup
    _save_local(user_input, intent, response)


def _save_local(
    user_input: str,
    intent: str,
    response: str
):
    """Save conversation to local JSON file."""
    try:
        os.makedirs("logs", exist_ok=True)

        # Load existing logs
        logs = []
        if os.path.exists(LOGS_FILE):
            try:
                with open(LOGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    logs = data
                elif isinstance(data, dict):
                    for key in ["conversations", "logs", "data"]:
                        if key in data:
                            logs = data[key]
                            break
            except Exception:
                logs = []

        # Add new entry
        logs.append({
            "timestamp": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "user_input": user_input,
            "detected_intent": intent,
            "response_given": response[:100],
            "feedback": None
        })

        # Save back
        with open(LOGS_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"⚠️  Local log failed: {e}")


def get_log_summary() -> dict:
    """Returns summary — prefers MongoDB, falls back to local."""
    try:
        from engine.mongo_logger import (
            get_mongo_stats,
            is_connected
        )
        if is_connected():
            return {
                "source": "MongoDB Atlas",
                "stats": get_mongo_stats()
            }
    except Exception:
        pass

    # Fallback to local
    try:
        if os.path.exists(LOGS_FILE):
            with open(LOGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            logs = data if isinstance(data, list) else []
            return {
                "source": "Local JSON",
                "total": len(logs)
            }
    except Exception:
        pass

    return {"source": "none", "total": 0}