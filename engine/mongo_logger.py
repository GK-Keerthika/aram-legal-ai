# engine/mongo_logger.py
# Purpose: Save conversation logs to MongoDB Atlas
# Fallback to local JSON if MongoDB unavailable

import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

# Try to connect to MongoDB
mongo_available = False
collection = None

try:
    from pymongo.mongo_client import MongoClient
    from pymongo.server_api import ServerApi

    if MONGODB_URI:
        client = MongoClient(
    MONGODB_URI,
    server_api=ServerApi('1'),
    serverSelectionTimeoutMS=5000,
    tlsCAFile=certifi.where()
)
        # Test connection
        client.admin.command('ping')
        db = client["aram_database"]
        collection = db["conversations"]
        mongo_available = True
        print("✅ MongoDB Atlas connected!")
    else:
        print("⚠️  No MongoDB URI found — using local logs")

except Exception as e:
    print(f"⚠️  MongoDB unavailable — using local logs: {e}")
    mongo_available = False


def save_to_mongo(
    user_input: str,
    intent: str,
    response: str
) -> bool:
    """
    Save conversation to MongoDB.
    Returns True if saved, False if failed.
    """
    if not mongo_available or collection is None:
        return False

    try:
        doc = {
            "timestamp": datetime.now(),
            "timestamp_str": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "user_input": user_input,
            "detected_intent": intent,
            "response_given": response[:100],
            "feedback": None
        }
        collection.insert_one(doc)
        return True

    except Exception as e:
        print(f"⚠️  MongoDB save failed: {e}")
        return False


def get_mongo_stats() -> dict:
    """Returns conversation statistics from MongoDB."""
    if not mongo_available or collection is None:
        return {"error": "MongoDB not available"}

    try:
        total = collection.count_documents({})
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        today_count = collection.count_documents({
            "timestamp": {"$gte": today}
        })

        # Intent distribution
        pipeline = [
            {"$group": {
                "_id": "$detected_intent",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        intent_dist = list(collection.aggregate(pipeline))

        return {
            "total": total,
            "today": today_count,
            "intents": {
                item["_id"]: item["count"]
                for item in intent_dist
            }
        }

    except Exception as e:
        return {"error": str(e)}


def is_connected() -> bool:
    """Check if MongoDB is connected."""
    return mongo_available