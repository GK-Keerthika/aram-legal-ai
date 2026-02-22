# app.py
# ARAM v3.0 — Complete Flask Application
# Security: Rate limiting, input sanitization,
#           security headers, integrity check

from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import re
import hashlib
import os

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

# ── Rate Limiter ──────────────────────────────────────
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# ── File Integrity Check ──────────────────────────────
LAW_FILES = [
    "laws/consumer_protection.md",
    "laws/it_act.md",
    "laws/bns.md"
]

def calculate_hash(filepath: str) -> str:
    """Calculate SHA256 hash of a file."""
    try:
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return ""

def build_integrity_map() -> dict:
    """Build hash map of all law files at startup."""
    return {
        filepath: calculate_hash(filepath)
        for filepath in LAW_FILES
    }

# Calculate hashes when app starts
INTEGRITY_MAP = build_integrity_map()
print("✅ File integrity map built:")
for filepath, hash_val in INTEGRITY_MAP.items():
    print(f"   {filepath}: {hash_val[:16]}...")

def verify_integrity() -> bool:
    """
    Check if law files have been tampered.
    Returns True if all files are intact.
    """
    for filepath, original_hash in INTEGRITY_MAP.items():
        current_hash = calculate_hash(filepath)
        if current_hash != original_hash:
            print(f"⚠️  INTEGRITY WARNING: {filepath} has been modified!")
            save_log(
                f"INTEGRITY_CHECK",
                "SECURITY_ALERT",
                f"File tampered: {filepath}"
            )
            return False
    return True

# ── Input Sanitization ────────────────────────────────
def sanitize_input(text: str) -> str:
    """
    Clean user input before processing.
    Removes dangerous characters and limits length.
    """
    if not text:
        return ""

    # Limit length — prevent huge inputs
    text = text[:500]

    # Remove HTML tags — prevent XSS
    text = re.sub(r'<[^>]+>', '', text)

    # Remove dangerous script-related words
    text = re.sub(
        r'(javascript:|vbscript:|onload=|onerror=|onclick=)',
        '',
        text,
        flags=re.IGNORECASE
    )

    # Remove null bytes
    text = text.replace('\x00', '')

    # Normalize whitespace
    text = ' '.join(text.split())

    return text.strip()

def validate_response(response: str) -> str:
    """
    Validate response contains required disclaimer.
    If missing, append it automatically.
    """
    disclaimer = "⚖️  Disclaimer: This is legal awareness guidance only"

    # Only check legal responses — not general chat
    legal_keywords = [
        "APPLICABLE LAW",
        "YOUR NEXT STEPS",
        "Consumer Protection",
        "IT Act",
        "BNS"
    ]

    is_legal_response = any(
        kw in response for kw in legal_keywords
    )

    if is_legal_response and disclaimer not in response:
        response += f"\n\n{disclaimer}, not legal advice."

    return response

# ── Security Headers ──────────────────────────────────
@app.after_request
def add_security_headers(response):
    """Add security headers to every response."""

    # Prevent clickjacking — no iframes allowed
    response.headers['X-Frame-Options'] = 'DENY'

    # Prevent MIME sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'

    # Force HTTPS
    response.headers['Strict-Transport-Security'] = (
        'max-age=31536000; includeSubDomains'
    )

    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:;"
    )

    # Prevent XSS in older browsers
    response.headers['X-XSS-Protection'] = '1; mode=block'

    return response


# ── Routes ─────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")


@limiter.limit("15 per minute")
@app.route("/chat", methods=["POST"])
def chat():

    # ── Get and sanitize input ────────────────────────
    raw_message = request.json.get("message", "")
    user_message = sanitize_input(raw_message)

    if not user_message:
        return jsonify({
            "response": "Please type something so I can help you."
        })

    # ── Integrity check ───────────────────────────────
    if not verify_integrity():
        return jsonify({
            "response": (
                "⚠️ System integrity check failed. "
                "Please try again later or contact support."
            )
        })

    # ── Step 1: Offensive filter ──────────────────────
    if is_offensive(user_message):
        response = get_offensive_response()
        save_log(user_message, "OFFENSIVE", response)
        return jsonify({"response": response})

    # ── Step 2: General conversation ──────────────────
    conv_type = is_general_conversation(user_message)
    if conv_type:
        response = get_general_response(conv_type)
        save_log(user_message, "GENERAL", response)
        return jsonify({"response": response})

    # ── Step 2b: "in tamil" request ───────────────────
    if user_message.lower().strip() in [
        "in tamil", "tamil la",
        "tamil la sollu", "tamil la solu"
    ]:
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
        response = validate_response(response)
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

    # ── Step 10: Validate response ────────────────────
    response = validate_response(response)

    # ── Step 11: Log conversation ─────────────────────
    save_log(user_message, intent_id, response)

    return jsonify({"response": response})


@app.route("/logs/summary")
def log_summary():
    from engine.log_manager import get_log_summary
    return jsonify(get_log_summary())


@app.route("/health")
def health():
    integrity_ok = verify_integrity()
    return jsonify({
        "status": "running",
        "app": "ARAM Legal Awareness Assistant",
        "version": "3.0",
        "ml_accuracy": "78%",
        "languages": ["English", "Tamil", "Tanglish"],
        "integrity": "✅ OK" if integrity_ok else "⚠️ WARNING"
    })


if __name__ == "__main__":
    app.run(debug=True)