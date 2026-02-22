# app.py
# ARAM v3.0 — Complete Flask Application

from flask import Flask, render_template, request, jsonify
from engine.intent_detector import detect_intent
from engine.response_generator import generate_response
from engine.log_manager import save_log
from engine.md_retriever import get_law_context, get_complaint_channels
from engine.language_detector import (
    detect_language,
    translate_tanglish,
    get_tamil_response,
    is_offensive,
    is_irrelevant,
    is_general_conversation,
    get_general_response,
    get_offensive_response,
    get_irrelevant_response,
    detect_tamil_intent
)

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip()

    if not user_message:
        return jsonify({
            "response": "Please type something so I can help you."
        })

    # ── Step 1: Offensive filter ─────────────────────
    if is_offensive(user_message):
        response = get_offensive_response()
        save_log(user_message, "OFFENSIVE", response)
        return jsonify({"response": response})

    # ── Step 2: General conversation ─────────────────
    conv_type = is_general_conversation(user_message)
    if conv_type:
        response = get_general_response(conv_type)
        save_log(user_message, "GENERAL", response)
        return jsonify({"response": response})

    # ── Step 2b: "in tamil" request ──────────────────
    if user_message.lower().strip() in ["in tamil", "tamil la", "tamil la sollu", "tamil la solu"]:
        response = "நான் தமிழிலும் பேசுவேன்! உங்கள் கேள்வியை தமிழில் கேளுங்கள். 😊"
        save_log(user_message, "GENERAL", response)
        return jsonify({"response": response})
    
    # ── Step 3: Irrelevant topics ─────────────────────
    if is_irrelevant(user_message):
        response = get_irrelevant_response()
        save_log(user_message, "IRRELEVANT", response)
        return jsonify({"response": response})

    # ── Step 4: Detect language ───────────────────────
    language = detect_language(user_message)

    # ── Step 5: Tamil script ──────────────────────────
    if language == "tamil":
        tamil_intent_id = detect_tamil_intent(user_message)
        if tamil_intent_id:
            response = get_tamil_response(tamil_intent_id)
        else:
            intent = detect_intent(user_message)
            intent_id = intent.get("intent_id", "UNKNOWN001")
            response = get_tamil_response(intent_id)
        save_log(user_message, tamil_intent_id or "UNKNOWN001", response)
        return jsonify({"response": response})

    # ── Step 6: Tanglish ──────────────────────────────
    if language == "tanglish":
        converted = translate_tanglish(user_message)
        intent = detect_intent(converted)
    else:
        # ── Step 7: English ───────────────────────────
        intent = detect_intent(user_message)

    intent_id = intent.get("intent_id", "UNKNOWN001")

    # ── Step 8: Enrich with MD content ───────────────
    if intent_id not in ["GREET001", "UNKNOWN001"]:
        law_context = get_law_context(intent_id)
        complaint_channels = get_complaint_channels(intent_id)
        if law_context:
            intent["md_context"] = law_context
        if complaint_channels:
            intent["complaint_channels"] = complaint_channels

    # ── Step 9: Generate response ─────────────────────
    response = generate_response(intent)

    # ── Step 10: Log conversation ─────────────────────
    save_log(user_message, intent_id, response)

    return jsonify({"response": response})


@app.route("/logs/summary")
def log_summary():
    from engine.log_manager import get_log_summary
    return jsonify(get_log_summary())


@app.route("/health")
def health():
    return jsonify({
        "status": "running",
        "app": "ARAM Legal Awareness Assistant",
        "version": "3.0",
        "ml_accuracy": "78%",
        "languages": ["English", "Tamil", "Tanglish"]
    })


if __name__ == "__main__":
    app.run(debug=True)