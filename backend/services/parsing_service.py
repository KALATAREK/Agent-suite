import re
from typing import Dict, List, Optional


# 🎯 MAIN ENTRYPOINT
def parse_input(text: str) -> Dict:
    """
    High-level parsing function.

    Returns:
    - cleaned text
    - detected type
    - extracted features
    """

    cleaned = clean_text(text)

    return {
        "raw": text,
        "cleaned": cleaned,
        "type": detect_input_type(cleaned),
        "emails": extract_emails(cleaned),
        "urls": extract_urls(cleaned),
        "tasks": extract_tasks(cleaned)
    }


# 🧹 CLEANING
def clean_text(text: str) -> str:
    if not text:
        return ""

    text = str(text).strip()

    # usuń wielokrotne spacje
    text = re.sub(r"\s+", " ", text)

    return text


# 🧠 TYPE DETECTION
def detect_input_type(text: str) -> str:
    text_lower = text.lower()

    if "@" in text or "subject:" in text_lower:
        return "email"

    if text.startswith("http"):
        return "url"

    if len(text) > 200:
        return "brief"

    return "message"


# 📧 EMAIL EXTRACTION
def extract_emails(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)


# 🌐 URL EXTRACTION
def extract_urls(text: str) -> List[str]:
    return re.findall(r"https?://[^\s]+", text)


# 🧠 TASK EXTRACTION (fallback logic)
def extract_tasks(text: str) -> List[str]:
    """
    Extract bullet-like tasks from raw text.
    Works when LLM fails.
    """

    lines = text.split("\n")

    tasks = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line.startswith("-") or line.startswith("•"):
            tasks.append(line.strip("-• ").strip())

    return tasks