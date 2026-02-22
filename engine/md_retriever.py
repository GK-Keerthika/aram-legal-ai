# engine/md_retriever.py
# Purpose: Retrieve relevant law content from .md files
# RAG-lite implementation

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAWS_DIR = os.path.join(BASE_DIR, "laws")

INTENT_TO_LAW_FILE = {
    "CP001": "consumer_protection.md",
    "CP002": "consumer_protection.md",
    "CP003": "consumer_protection.md",
    "CP004": "consumer_protection.md",
    "IT001": "it_act.md",
    "IT002": "it_act.md",
    "IT003": "it_act.md",
    "IT004": "it_act.md",
    "BNS001": "bns.md",
    "BNS002": "bns.md",
    "BNS003": "bns.md",
    "GUIDE001": None,
    "GREET001": None,
    "UNKNOWN001": None
}

INTENT_TO_SECTION = {
    "CP001": "Refund Not Received",
    "CP002": "Defective Product",
    "CP003": "Online Shopping Issues",
    "CP004": "Service Deficiency",
    "IT001": "Cyber Fraud",
    "IT002": "Identity Theft",
    "IT003": "Online Harassment",
    "IT004": "Hacking",
    "BNS001": "Cheating",
    "BNS002": "Criminal Intimidation",
    "BNS003": "Harassment"
}

COMPLAINT_SECTION_MAP = {
    "CP001": "Where to File Complaint",
    "CP002": "Where to File Complaint",
    "CP003": "Where to File Complaint",
    "CP004": "Where to File Complaint",
    "IT001": "Where to Report",
    "IT002": "Where to Report",
    "IT003": "Where to Report",
    "IT004": "Where to Report",
    "BNS001": "Where to File Complaint",
    "BNS002": "Where to File Complaint",
    "BNS003": "Where to File Complaint"
}


def read_law_file(filename: str) -> str:
    """Reads full content of a law .md file."""
    filepath = os.path.join(LAWS_DIR, filename)
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def extract_section(content: str, section_name: str) -> str:
    """Extracts specific section from md content."""
    lines = content.split("\n")
    capturing = False
    section_lines = []

    for line in lines:
        if f"### {section_name}" in line:
            capturing = True
            continue
        if capturing:
            if line.startswith("###") or line.startswith("## "):
                break
            section_lines.append(line)

    return "\n".join(section_lines).strip()


def get_law_context(intent_id: str) -> str:
    """Returns relevant law context for a given intent."""
    law_file = INTENT_TO_LAW_FILE.get(intent_id)
    if not law_file:
        return ""
    content = read_law_file(law_file)
    if not content:
        return ""
    section_name = INTENT_TO_SECTION.get(intent_id, "")
    if section_name:
        section = extract_section(content, section_name)
        if section:
            return section
    return ""


def get_complaint_channels(intent_id: str) -> str:
    """Returns complaint filing information."""
    law_file = INTENT_TO_LAW_FILE.get(intent_id)
    if not law_file:
        return ""
    content = read_law_file(law_file)
    if not content:
        return ""
    section_name = COMPLAINT_SECTION_MAP.get(intent_id, "")
    if section_name:
        return extract_section(content, section_name)
    return ""


if __name__ == "__main__":
    test_intents = ["CP001", "IT001", "BNS002"]
    for intent_id in test_intents:
        print(f"\n{'─'*50}")
        print(f"Intent: {intent_id}")
        print(f"\n📖 Law Context:")
        print(get_law_context(intent_id))
        print(f"\n🏛️ Complaint Channels:")
        print(get_complaint_channels(intent_id))