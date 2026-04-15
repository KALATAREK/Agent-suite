from typing import Dict, Any, List
from services.llm_service import LLMService
from prompts.automator_prompts import AUTOMATOR_SYSTEM_PROMPT

llm = LLMService()


# 🎯 MAIN ENTRYPOINT
async def handle_automator(input_text: str) -> Dict[str, Any]:
    """
    Automator agent.

    Input:
    - unstructured text (email, client message, brief)

    Output:
    - structured workflow + metadata
    """

    cleaned_input = _prepare_input(input_text)

    messages = [
        {
            "role": "system",
            "content": AUTOMATOR_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": cleaned_input
        }
    ]

    # 🧠 STEP 1 — structured generation
    result = await llm.generate_json(messages, schema={})

    # 🧨 STEP 2 — fallback if JSON breaks
    if not result or "error" in result:
        print("[AUTOMATOR] JSON failed, fallback parsing")

        fallback = await llm.generate(messages)
        result = _force_parse(fallback.get("content", ""))

    # 🧠 STEP 3 — normalize & enhance
    processed = _postprocess(result)

    # 🧠 STEP 4 — metadata
    return {
        "data": processed,
        "meta": {
            "input_type": _detect_input_type(input_text),
            "task_count": len(processed["tasks"]),
            "quality": _estimate_quality(processed)
        }
    }


# 🧠 INPUT PREP
def _prepare_input(text: str) -> str:
    text = text.strip()

    if len(text) < 10:
        return f"Short message:\n{text}"

    return f"Process this client request:\n{text}"


def _detect_input_type(text: str) -> str:
    if "@" in text or "Subject:" in text:
        return "email"
    if len(text) > 200:
        return "brief"
    return "message"


# 🧠 POSTPROCESS (tu jest dużo logiki)
def _postprocess(data: Dict[str, Any]) -> Dict[str, Any]:

    tasks = _deduplicate_tasks(_ensure_list(data.get("tasks")))

    return {
        "summary": data.get("summary", "").strip(),
        "tasks": tasks,
        "priority": _normalize_priority(data.get("priority"), tasks),
        "reply": _normalize_reply(data.get("reply", "")),
        "client_type": _normalize_client_type(data.get("client_type"), tasks)
    }


# 🔧 HELPERS

def _ensure_list(value) -> List[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if v]
    if isinstance(value, str):
        return [value.strip()]
    return []


def _deduplicate_tasks(tasks: List[str]) -> List[str]:
    seen = set()
    result = []

    for t in tasks:
        key = t.lower()
        if key not in seen:
            seen.add(key)
            result.append(t)

    return result


# 🎯 PRIORITY LOGIC (lepsze niż LLM-only)
def _normalize_priority(value, tasks: List[str]) -> str:
    valid = {"low", "medium", "high"}

    if isinstance(value, str) and value.lower() in valid:
        return value.lower()

    # fallback logic
    joined = " ".join(tasks).lower()

    if any(k in joined for k in ["urgent", "asap", "today"]):
        return "high"

    if len(tasks) >= 3:
        return "medium"

    return "low"


# 💬 REPLY CLEANUP
def _normalize_reply(text: str) -> str:
    text = text.strip()

    if not text:
        return "Hi! Thanks for your message — I’ll get back to you shortly."

    # skracamy przesadnie długie odpowiedzi
    return text[:500]


# 🧠 CLIENT TYPE LOGIC
def _normalize_client_type(value, tasks: List[str]) -> str:
    valid = {"vip", "normal", "low_value"}

    if isinstance(value, str) and value.lower() in valid:
        return value.lower()

    joined = " ".join(tasks).lower()

    if any(k in joined for k in ["premium", "package", "multiple"]):
        return "vip"

    if any(k in joined for k in ["discount", "cheap"]):
        return "low_value"

    return "normal"


# 🧠 QUALITY ESTIMATION
def _estimate_quality(data: Dict[str, Any]) -> str:
    score = 0

    if data.get("summary"):
        score += 1
    if len(data.get("tasks", [])) >= 2:
        score += 1
    if data.get("reply"):
        score += 1

    if score == 3:
        return "high"
    if score == 2:
        return "medium"
    return "low"


# 🧨 FORCE PARSE (fallback parser)
def _force_parse(text: str) -> Dict[str, Any]:
    lines = text.split("\n")

    return {
        "summary": lines[0] if lines else "",
        "tasks": [l for l in lines if l.startswith("-")],
        "priority": "medium",
        "reply": text[:300],
        "client_type": "normal"
    }