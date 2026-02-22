# config.py
# Purpose: Central configuration for ARAM application

import os

# ── Paths ──────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
INTENTS_FILE = os.path.join(DATA_DIR, "intents.json")

# ── App Settings ───────────────────────────────────
APP_NAME = "ARAM"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Legal Awareness Assistant for Indian Citizens"

# ── Intent Detection Settings ──────────────────────
MIN_KEYWORD_MATCH = 1        # Minimum keywords to match an intent
CONFIDENCE_THRESHOLD = 0.15   # Match confidence threshold (0 to 1)

# ── Severity Levels ────────────────────────────────
SEVERITY_LEVELS = {
    "low": "This situation can likely be resolved through communication.",
    "medium": "This situation may require formal complaint filing.",
    "high": "This situation needs prompt attention and official reporting.",
    "none": ""
}

# ── Display Settings ───────────────────────────────
SEPARATOR = "─" * 60
DISCLAIMER = (
    "\n⚖️  Disclaimer: This is legal awareness guidance only, "
    "not legal advice.\n"
    "   For legal representation, please consult a qualified lawyer."
)