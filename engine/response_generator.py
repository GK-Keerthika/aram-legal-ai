# engine/response_generator.py
# Purpose: Generate structured, calm, varied responses

import random
from config import SEVERITY_LEVELS, SEPARATOR, DISCLAIMER


def get_template(intent: dict) -> str:
    """
    Picks a random response template.
    Supports both string and list formats.
    """
    template = intent.get("response_template", "")
    if isinstance(template, list):
        return random.choice(template)
    return template


def generate_response(intent: dict) -> str:
    """
    Main response generator.
    Routes to correct formatter based on intent type.
    """
    if not intent:
        return (
            "I'm sorry, I could not process your request. "
            "Please try again."
        )

    intent_id = intent.get("intent_id", "")

    if intent_id == "GREET001":
        return format_greeting(intent)

    if intent_id == "UNKNOWN001":
        return format_unknown(intent)

    return format_legal_response(intent)


def format_greeting(intent: dict) -> str:
    """Formats warm varied greeting."""

    greetings = [
        "Hello! I am ARAM, your legal awareness assistant. "
        "How can I help you today?",

        "Hi there! I'm ARAM — here to help you understand "
        "your legal rights calmly and clearly. "
        "What's on your mind?",

        "Welcome! I'm ARAM, your legal awareness guide. "
        "Please describe your situation and "
        "I'll do my best to help.",

        "Hello! Great to have you here. I'm ARAM — "
        "I help Indian citizens understand their legal rights. "
        "How can I assist you?",

        "Hi! I'm ARAM, your legal awareness companion. "
        "I'm here to guide you through consumer issues, "
        "cyber concerns, and general legal matters. "
        "What would you like to know?"
    ]

    response = f"""
{SEPARATOR}
👋  {random.choice(greetings)}

    I can help you with:
    • Consumer complaints (refunds, defective products, online shopping)
    • Cyber issues (fraud, hacking, harassment, identity theft)
    • General legal concerns (cheating, threats, harassment)
    • Complaint guidance (where and how to file)

    Supported languages: English | Tamil | Tanglish
{SEPARATOR}
"""
    return response


def format_unknown(intent: dict) -> str:
    """Formats polite redirect for unknown queries."""

    responses = [
        "I'm not sure I understood that. "
        "Could you describe your situation in a little more detail?",

        "I want to help but need a bit more context. "
        "Could you tell me more about what happened?",

        "I didn't quite catch that. Please describe your situation "
        "and I'll guide you to the right information.",

        "Could you explain your situation a little differently? "
        "I want to make sure I give you the right guidance.",

        "I'm here to help with legal awareness. "
        "Could you share more details about your concern?"
    ]

    response = f"""
{SEPARATOR}
🤔  {random.choice(responses)}

    I can currently help you with:
    • Consumer complaints (refunds, defective products, online shopping)
    • Cyber issues (fraud, hacking, harassment, identity theft)
    • General legal concerns (cheating, threats, harassment)
    • Complaint filing guidance

    💡 Tip: Describe what happened to you and I'll find
    the right legal information for your situation.
{SEPARATOR}
"""
    return response


def format_legal_response(intent: dict) -> str:
    """
    Formats complete structured legal awareness response.
    Includes md file content when available.
    """

    description   = intent.get("intent_description", "")
    mapped_law    = intent.get("mapped_law", "")
    severity      = intent.get("severity_level", "low")
    explanation   = intent.get("simplified_explanation", "")
    steps         = intent.get("recommended_steps", [])
    severity_note = SEVERITY_LEVELS.get(severity, "")
    template      = get_template(intent)
    md_context    = intent.get("md_context", "")
    complaint_ch  = intent.get("complaint_channels", "")

    # Format numbered steps
    formatted_steps = ""
    for i, step in enumerate(steps, 1):
        formatted_steps += f"    {i}. {step}\n"

    # Severity emoji
    severity_emoji = {
        "low":    "🟡",
        "medium": "🟠",
        "high":   "🔴"
    }.get(severity, "🟡")

    # Build md context section
    md_section = ""
    if md_context:
        md_section = f"""
📖  LEGAL DETAILS
    {md_context}
"""

    # Build complaint channels section
    complaint_section = ""
    if complaint_ch:
        complaint_section = f"""
🏛️  WHERE TO FILE COMPLAINT
    {complaint_ch}
"""

    # Build full response
    response = f"""
{SEPARATOR}
📋  SITUATION UNDERSTOOD
    {template}

⚖️  APPLICABLE LAW
    {mapped_law}

{severity_emoji}  SEVERITY: {severity.upper()}
    {severity_note}

💡  WHAT THIS MEANS FOR YOU
    {explanation}
{md_section}
✅  YOUR NEXT STEPS
{formatted_steps}{complaint_section}
{DISCLAIMER}
{SEPARATOR}
"""
    return response


if __name__ == "__main__":
    from engine.intent_detector import detect_intent

    test_inputs = [
        "hello",
        "I need a refund",
        "someone hacked my account",
        "I was cheated",
        "what is cricket"
    ]

    print("\n🧪 Response Generator Test")
    print("─" * 50)
    for text in test_inputs:
        print(f"\n🔍 Input: {text}")
        intent = detect_intent(text)
        response = generate_response(intent)
        print(response)