# engine/intent_detector.py
# Purpose: Hybrid intent detection — rule-based + ML + Tamil support

import json
import os
import pickle
from utils.text_cleaner import extract_keywords, clean_text
from config import INTENTS_FILE, CONFIDENCE_THRESHOLD
from engine.language_detector import (
    detect_tamil_intent,
    translate_tanglish,
    detect_language
)

MODEL_PATH = os.path.join("engine", "aram_model.pkl")

GREETING_WORDS = [
    "hello", "hi", "hey", "hai", "hii", "helo",
    "namaste", "vanakkam", "vanakam", "vannakam",
    "good morning", "good evening", "good afternoon",
    "good night", "morning", "evening", "afternoon",
    "greetings", "howdy", "vanakkom", "aram"
]


def load_intents() -> dict:
    """Loads intents.json as lookup dictionary."""
    with open(INTENTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {
        intent["intent_id"]: intent
        for intent in data["intents"]
    }


def load_intents_list() -> list:
    """Loads intents.json as list."""
    with open(INTENTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["intents"]


def load_ml_model():
    """Loads trained ML model if available."""
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    return None


def rule_based_detect(user_input: str, intents: list) -> tuple:
    """
    Rule-based detection using keyword matching.
    Returns (intent, score).
    """
    user_keywords = extract_keywords(user_input)
    user_text = clean_text(user_input)
    user_set = set(user_keywords)

    if not user_set:
        return None, 0.0

    best_match = None
    best_score = 0.0

    for intent in intents:
        intent_id = intent["intent_id"]
        if intent_id in ["UNKNOWN001", "GREET001"]:
            continue

        keywords = intent.get("keywords", [])
        if not keywords:
            continue

        intent_set = set(keywords)
        direct_matches = user_set.intersection(intent_set)

        phrase_matches = sum(
            1 for kw in keywords
            if len(kw.split()) > 1 and kw in user_text
        )

        total_matches = len(direct_matches) + phrase_matches

        if total_matches == 0:
            continue

        score = total_matches / len(user_set)

        if score > best_score:
            best_score = score
            best_match = intent

    return best_match, best_score


def ml_based_detect(user_input: str, intents_lookup: dict) -> tuple:
    """
    ML-based detection using trained classifier.
    Returns (intent, normalized_confidence).
    """
    model = load_ml_model()
    if not model:
        return None, 0.0

    try:
        predicted_id = model.predict([user_input])[0]
        decision_scores = model.decision_function([user_input])[0]
        classes = model.classes_

        score_dict = dict(zip(classes, decision_scores))
        confidence = score_dict.get(predicted_id, 0)

        if confidence < 0.3:
            return None, 0.0

        positive_scores = [s for s in decision_scores if s > 0]
        if not positive_scores:
            return None, 0.0

        max_score = max(positive_scores)
        normalized = confidence / max_score if max_score > 0 else 0.0

        print(f"   [ML] Predicted: {predicted_id} | "
              f"Raw: {confidence:.2f} | "
              f"Normalized: {normalized:.2f}")

        intent = intents_lookup.get(predicted_id)
        return intent, normalized

    except Exception as e:
        print(f"   [ML Warning] {e}")
        return None, 0.0


def detect_intent(user_input: str) -> dict:
    """
    Main hybrid detection function.

    Priority order:
    1. Greeting check
    2. Tamil/Tanglish keyword detection
    3. Rule-based detection
    4. ML-based detection
    5. Combined hybrid
    6. Unknown fallback
    """
    intents_list   = load_intents_list()
    intents_lookup = load_intents()
    user_lower     = clean_text(user_input)

    # ── Priority 1: Greeting check ───────────────────
    user_words = user_lower.split()
    if len(user_words) <= 3:
        for word in GREETING_WORDS:
            if word in user_lower:
                return intents_lookup.get("GREET001", {})
    else:
        if user_lower in GREETING_WORDS:
            return intents_lookup.get("GREET001", {})

    # ── Priority 2: Tamil/Tanglish detection ─────────
    language = detect_language(user_input)

    if language == "tamil":
        tamil_intent_id = detect_tamil_intent(user_input)
        if tamil_intent_id:
            print(f"   [Tamil] Matched: {tamil_intent_id}")
            return intents_lookup.get(
                tamil_intent_id,
                intents_lookup.get("UNKNOWN001", {})
            )

    if language == "tanglish":
        converted = translate_tanglish(user_input)
        tamil_intent_id = detect_tamil_intent(user_input)
        if tamil_intent_id:
            print(f"   [Tanglish] Matched: {tamil_intent_id}")
            return intents_lookup.get(
                tamil_intent_id,
                intents_lookup.get("UNKNOWN001", {})
            )
        # Use converted text for further detection
        user_input = converted
        user_lower = clean_text(converted)

    # ── Priority 3: Rule-based detection ────────────
    rule_intent, rule_score = rule_based_detect(
        user_input, intents_list
    )

    if rule_score >= 0.5:
        print(f"   [Rule] Strong: "
              f"{rule_intent.get('intent_id')} "
              f"({rule_score:.2f})")
        return rule_intent

    # ── Priority 4: ML-based detection ──────────────
    ml_intent, ml_confidence = ml_based_detect(
        user_input, intents_lookup
    )

    if ml_confidence >= 0.75:
        print(f"   [ML] Strong: "
              f"{ml_intent.get('intent_id')} "
              f"({ml_confidence:.2f})")
        return ml_intent

    # ── Priority 5: Hybrid combined ──────────────────
    if rule_intent and ml_intent and rule_score >= 0.15:
        if rule_intent.get("intent_id") == ml_intent.get("intent_id"):
            print(f"   [Hybrid] Both agree: "
                  f"{rule_intent.get('intent_id')}")
            return rule_intent

        if rule_score >= 0.2:
            print(f"   [Hybrid] Rule wins: "
                  f"{rule_intent.get('intent_id')}")
            return rule_intent

        if ml_confidence >= 0.6:
            print(f"   [Hybrid] ML wins: "
                  f"{ml_intent.get('intent_id')}")
            return ml_intent

    # ── Priority 6: Weak rule match ──────────────────
    if rule_intent and rule_score >= CONFIDENCE_THRESHOLD:
        print(f"   [Rule] Weak: "
              f"{rule_intent.get('intent_id')} "
              f"({rule_score:.2f})")
        return rule_intent

    # ── Fallback: Unknown ────────────────────────────
    print("   [Fallback] No confident match")
    return intents_lookup.get("UNKNOWN001", {})


if __name__ == "__main__":
    test_inputs = [
        "hello",
        "I never got my refund",
        "someone hacked my account",
        "I was tricked into giving money",
        "they are threatening me",
        "I am being harassed at work",
        "cyber fraud happened to me",
        "my product stopped working",
        "account hack pannittaan",
        "emattu vittaan",
        "panam thirumba kudukala",
        "என் கணக்கு hack ஆனது",
        "what is cricket"
    ]

    print("\n🧪 Hybrid Intent Detector Test")
    print("─" * 50)
    for text in test_inputs:
        result = detect_intent(text)
        print(f"\nInput   : {text}")
        print(f"Matched : {result.get('intent_id')} "
              f"— {result.get('intent_description')}")