from typing import Dict, Any

from services.intent_service import classify_intent
from services.memory_service import get_context, save_conversation
from services.llm_service import LLMService

from agents.assistant_agent import handle_assistant
from agents.analyzer_agent import handle_analyzer
from agents.automator_agent import handle_automator

# 🔧 INIT
llm = LLMService()

# 🔥 CONFIG
LOW_CONFIDENCE_THRESHOLD = 0.6


# 🎯 MAIN ENTRYPOINT
async def run_agent(session_id: str, message: str, user_id: str) -> Dict[str, Any]:
    """
    Main orchestration layer:
    - loads context (user-aware)
    - classifies intent
    - routes to agent
    - fallback if needed
    - saves conversation
    - returns structured response
    """

    try:
        # 🧠 STEP 1 — LOAD CONTEXT (user-scoped!)
        history = get_context(session_id, user_id)

        # 🧠 STEP 2 — CLASSIFY INTENT
        intent_data = await classify_intent(message)
        intent = intent_data.get("intent", "support")
        confidence = intent_data.get("confidence", 0.5)

        print(f"[AGENT] user={user_id} intent={intent} conf={confidence:.2f}")

        # ⚠️ STEP 3 — LOW CONFIDENCE → FALLBACK
        if confidence < LOW_CONFIDENCE_THRESHOLD:
            result = await _fallback_response(message, history)
            intent = "support"

        else:
            # 🧠 STEP 4 — ROUTING
            result = await _route_intent(intent, message, history)

        # 🧠 STEP 5 — SAVE MEMORY (pair-based, safe)
        _save_conversation(session_id, user_id, message, result)

        # 🧠 STEP 6 — RESPONSE
        return _build_response(intent, confidence, result)

    except Exception as e:
        print(f"[AGENT ERROR] {e}")

        fallback = await _fallback_response(message, [])

        return _build_response(
            intent="support",
            confidence=0.0,
            content=fallback,
            error=str(e)
        )


# =========================
# 🧠 ROUTER
# =========================
async def _route_intent(intent: str, message: str, history):
    if intent == "analyze":
        return await handle_analyzer(message)

    if intent == "automate":
        return await handle_automator(message)

    return await handle_assistant(
        message=message,
        history=history,
        intent=intent
    )


# =========================
# 🧠 FALLBACK
# =========================
async def _fallback_response(message: str, history) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are a helpful business assistant. Be concise and practical."
        },
        *history[-5:],
        {
            "role": "user",
            "content": message
        }
    ]

    response = await llm.generate(messages)
    return response.get("content", "I'm here to help. Could you clarify?")


# =========================
# 💾 MEMORY
# =========================
def _save_conversation(session_id: str, user_id: str, user_message: str, ai_response: Any):
    try:
        # 🔥 normalizacja response
        if isinstance(ai_response, dict):
            ai_text = str(ai_response)
        else:
            ai_text = str(ai_response)

        # 🔥 zapis jako para (ważne!)
        save_conversation(
            session_id=session_id,
            user_id=user_id,
            user_message=user_message,
            ai_response=ai_text
        )

    except Exception as e:
        print(f"[MEMORY ERROR] {e}")


# =========================
# 🧱 RESPONSE BUILDER
# =========================
def _build_response(intent: str, confidence: float, content: Any, error: str = None) -> Dict[str, Any]:
    return {
        "type": intent,
        "content": content,
        "meta": {
            "intent": intent,
            "confidence": round(confidence, 2),
            "error": error
        }
    }