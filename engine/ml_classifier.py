# engine/ml_classifier.py
# Purpose: Load trained ML model and classify user input

import json
import pickle
import os
import numpy as np
from config import INTENTS_FILE

MODEL_PATH = os.path.join("engine", "aram_model.pkl")

GREETING_WORDS = [
    "hello", "hi", "hey", "hai", "hii", "helo",
    "namaste", "vanakkam", "vanakam", "vannakam",
    "good morning", "good evening", "good afternoon",
    "good night", "morning", "evening", "afternoon",
    "greetings", "howdy", "vanakkom"
]


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "ML model not found. Please run model_trainer.py first."
        )
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


def load_intents() -> dict:
    with open(INTENTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {
        intent["intent_id"]: intent
        for intent in data["intents"]
    }


def ml_detect_intent(user_input: str) -> dict:
    """
    Uses trained ML model to classify user input.
    Returns matched intent dictionary.
    """
    intents_lookup = load_intents()
    user_lower = user_input.lower().strip()

    # Handle greetings directly
    for word in GREETING_WORDS:
        if word in user_lower:
            return intents_lookup.get("GREET001", {})

    # Load model
    model = load_model()

    # Predict
    predicted_id = model.predict([user_input])[0]

    # Get confidence using decision function
    decision_scores = model.decision_function([user_input])[0]
    classes = model.classes_
    score_dict = dict(zip(classes, decision_scores))
    confidence = score_dict.get(predicted_id, 0)

    print(f"   [ML] Predicted: {predicted_id} | Confidence: {confidence:.2f}")

    # Normalize confidence — LinearSVC scores vary widely
    # Accept if it's the highest score (model is confident)
    max_score = max(decision_scores)
    min_score = min(decision_scores)

    # Normalize to 0-1 range
    if max_score != min_score:
        normalized = (confidence - min_score) / (max_score - min_score)
    else:
        normalized = 1.0

    print(f"   [ML] Normalized confidence: {normalized:.2f}")

    # Accept if normalized confidence is above 0.6
    if normalized >= 0.6:
        return intents_lookup.get(predicted_id,
               intents_lookup.get("UNKNOWN001", {}))

    return intents_lookup.get("UNKNOWN001", {})


if __name__ == "__main__":
    test_inputs = [
        "hello",
        "I never got my refund",
        "someone broke into my account",
        "I was tricked into giving money",
        "they are threatening me",
        "my product is damaged",
        "cyber fraud happened to me",
        "someone is harassing me",
        "what is cricket"
    ]

    print("\n🧪 ML Classifier Test")
    print("─" * 50)
    for text in test_inputs:
        result = ml_detect_intent(text)
        print(f"Input   : {text}")
        print(f"Matched : {result.get('intent_id')} — {result.get('intent_description')}")
        print()