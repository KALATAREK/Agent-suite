from typing import List, Dict
from services.llm_service import LLMService
from prompts.assistant_prompts import (
    BASE_SYSTEM_PROMPT,
    BOOKING_PROMPT,
    PRICING_PROMPT,
    SUPPORT_PROMPT
)

llm = LLMService()

MAX_HISTORY = 8


# 🎯 MAIN AGENT
async def handle_assistant(
    message: str,
    history: List[Dict[str, str]],
    intent: str
) -> str:
    """
    AI business assistant with:
    - intent-aware behavior
    - structured prompting
    - memory handling
    - lightweight business logic
    """

    system_prompt = _build_system_prompt(intent)
    context = _prepare_context(history)

    messages = [
        {"role": "system", "content": system_prompt},
        *context,
        {"role": "user", "content": message}
    ]

    response = await llm.generate(
        messages=messages,
        temperature=_select_temperature(intent)
    )

    raw_text = response.get("content", "")

    return _postprocess_response(raw_text, intent, message)


# 🧠 PROMPT BUILDER (ważniejsze niż się wydaje)
def _build_system_prompt(intent: str) -> str:
    base = BASE_SYSTEM_PROMPT.strip()

    if intent == "booking":
        extra = BOOKING_PROMPT
    elif intent == "pricing":
        extra = PRICING_PROMPT
    else:
        extra = SUPPORT_PROMPT

    return f"{base}\n\n{extra}\n\n{_behavior_rules()}"


def _behavior_rules() -> str:
    return """
Behavior rules:
- Always guide user toward action (booking or decision)
- Keep responses concise but useful
- Avoid long paragraphs
- If missing info → ask a follow-up question
- Be confident, not robotic
"""


# 🧠 CONTEXT MANAGEMENT
def _prepare_context(history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    if not history:
        return []

    # ostatnie wiadomości → lepszy signal
    return history[-MAX_HISTORY:]


# 🎯 TEMPERATURE CONTROL
def _select_temperature(intent: str) -> float:
    if intent == "booking":
        return 0.4  # bardziej precyzyjne

    if intent == "pricing":
        return 0.5  # balans

    return 0.7  # bardziej naturalne


# 🧠 POSTPROCESS (tu robimy UX + sprzedaż)
def _postprocess_response(text: str, intent: str, user_message: str) -> str:

    if not text:
        return "I'm here to help — could you clarify your request?"

    text = text.strip()

    # 🔥 pricing enhancement
    if intent == "pricing":
        text = _enhance_pricing(text)

    # 🔥 booking CTA boost
    if intent == "booking":
        text = _enhance_booking(text)

    # 🔥 natural tone cleanup
    text = _cleanup(text)

    return text


# 💰 PRICING LOGIC (mini business layer)
def _enhance_pricing(text: str) -> str:
    if "PLN" not in text:
        text += "\n\nTypical price range: 40–100 PLN depending on service."

    if "book" not in text.lower():
        text += "\nWould you like me to book an appointment for you?"

    return text


# 📅 BOOKING BOOST
def _enhance_booking(text: str) -> str:
    if "available" not in text.lower():
        text += "\n\nWe have availability this week — what time works for you?"

    return text


# 🧹 CLEANUP
def _cleanup(text: str) -> str:
    # usuwamy śmieciowe powtórzenia i whitespace
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)