from typing import Dict, Any
from services.llm_service import LLMService
import json
import re

llm = LLMService()

VALID_INTENTS = {
    "booking",
    "pricing",
    "support",
    "analyze",
    "automate"
}

LOW_CONFIDENCE_DEFAULT = 0.5


# 🎯 MAIN FUNCTION
async def classify_intent(message: str) -> Dict[str, Any]:
    """
    AI-powered intent classification with:
    - LLM classification
    - fallback heuristics
    - robust parsing
    """

    cleaned_message = message.strip()

    # ⚡ STEP 1 — FAST HEURISTIC (performance boost)
    heuristic = _quick_intent_guess(cleaned_message)
    if heuristic:
        return heuristic

    # 🧠 STEP 2 — LLM classification
    messages = [
        {
            "role": "system",
            "content": _system_prompt()
        },
        {
            "role": "user",
            "content": cleaned_message
        }
    ]

    response = await llm.generate(messages)

    parsed = _safe_parse_json(response.get("content", ""))

    intent = parsed.get("intent", "support")
    confidence = parsed.get("confidence", LOW_CONFIDENCE_DEFAULT)

    # 🔒 STEP 3 — sanitize
    intent = _sanitize_intent(intent)
    confidence = _sanitize_confidence(confidence)

    print(f"[INTENT] {intent} ({confidence:.2f}) → {cleaned_message[:60]}")

    # 🧨 STEP 4 — fallback if weird
    if intent not in VALID_INTENTS:
        return _fallback_intent(cleaned_message)

    return {
        "intent": intent,
        "confidence": confidence
    }


# 🧠 SYSTEM PROMPT
def _system_prompt() -> str:
    return """
You are an intent classifier for a business AI system.

Classify the message into ONE intent:

- booking → scheduling, availability, appointments
- pricing → price, cost, offers
- support → general questions
- analyze → analysis of business or website
- automate → extracting tasks or processing text

Return ONLY JSON:

{
  "intent": "...",
  "confidence": 0.0-1.0
}

Rules:
- no explanation
- choose best match
- if unsure → support
"""


# ⚡ FAST HEURISTIC (important)
def _quick_intent_guess(message: str) -> Dict[str, Any] | None:
    msg = message.lower()

    if any(k in msg for k in ["book", "appointment", "schedule", "available"]):
        return {"intent": "booking", "confidence": 0.85}

    if any(k in msg for k in ["price", "cost", "how much", "discount"]):
        return {"intent": "pricing", "confidence": 0.85}

    if "analyze" in msg or "analysis" in msg:
        return {"intent": "analyze", "confidence": 0.9}

    if any(k in msg for k in ["summarize", "extract", "tasks", "process"]):
        return {"intent": "automate", "confidence": 0.9}

    return None


# 🧨 FALLBACK
def _fallback_intent(message: str) -> Dict[str, Any]:
    print("[INTENT FALLBACK] using heuristic fallback")

    guess = _quick_intent_guess(message)
    if guess:
        return guess

    return {
        "intent": "support",
        "confidence": LOW_CONFIDENCE_DEFAULT
    }


# 🔒 SANITIZE
def _sanitize_intent(intent: Any) -> str:
    if isinstance(intent, str):
        intent = intent.lower().strip()
        if intent in VALID_INTENTS:
            return intent
    return "support"


def _sanitize_confidence(value: Any) -> float:
    try:
        value = float(value)
        return max(0.0, min(1.0, value))
    except Exception:
        return LOW_CONFIDENCE_DEFAULT


# 🛡️ SAFE JSON PARSER
def _safe_parse_json(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        pass

    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass

    return {}