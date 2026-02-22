# utils/text_cleaner.py
# Purpose: Clean and normalize user input before processing

import re
import string

def clean_text(text: str) -> str:
    """
    Cleans raw user input for intent detection.
    Steps:
    1. Lowercase everything
    2. Remove extra spaces
    3. Remove special characters
    4. Strip leading/trailing whitespace
    """

    if not text or not isinstance(text, str):
        return ""

    # Step 1: Lowercase
    text = text.lower()

    # Step 2: Remove punctuation except apostrophes
    text = re.sub(r"[^\w\s']", " ", text)

    # Step 3: Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    # Step 4: Strip
    text = text.strip()

    return text


def extract_keywords(text: str) -> list:
    """
    Splits cleaned text into individual words (tokens).
    Used by intent detector to match against dataset keywords.
    """
    cleaned = clean_text(text)
    return cleaned.split()


# Quick test — only runs when this file is run directly
if __name__ == "__main__":
    sample = "  Hello!! I was CHEATED online... help me?? "
    print("Original :", sample)
    print("Cleaned  :", clean_text(sample))
    print("Keywords :", extract_keywords(sample))