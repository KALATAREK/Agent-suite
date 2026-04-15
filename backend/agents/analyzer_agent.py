from typing import Dict, Any
from services.llm_service import LLMService
from prompts.analyzer_prompts import ANALYZER_SYSTEM_PROMPT

llm = LLMService()


# 🎯 MAIN ENTRYPOINT
async def handle_analyzer(input_data: str) -> Dict[str, Any]:
    """
    Analyzer agent.

    Input:
    - URL or business description

    Output:
    - structured analysis + metadata
    """

    cleaned_input = _prepare_input(input_data)

    messages = [
        {
            "role": "system",
            "content": ANALYZER_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": cleaned_input
        }
    ]

    # 🧠 STEP 1 — try structured JSON
    result = await llm.generate_json(messages, schema={})

    # 🧨 STEP 2 — fallback if model fails JSON
    if not result or "error" in result:
        print("[ANALYZER] JSON failed, retrying with standard generation")

        fallback = await llm.generate(messages)
        result = _force_parse(fallback.get("content", ""))

    # 🧠 STEP 3 — normalize
    processed = _postprocess_analysis(result)

    # 🧠 STEP 4 — attach metadata
    return {
        "data": processed,
        "meta": {
            "input_type": _detect_input_type(input_data),
            "quality": _estimate_quality(processed)
        }
    }


# 🧠 INPUT PREPARATION
def _prepare_input(input_data: str) -> str:
    input_data = input_data.strip()

    if input_data.startswith("http"):
        return f"Analyze this website: {input_data}"

    return f"Analyze this business description:\n{input_data}"


def _detect_input_type(input_data: str) -> str:
    return "url" if input_data.startswith("http") else "text"


# 🧠 POSTPROCESS
def _postprocess_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "seo": _ensure_list(data.get("seo")),
        "ux": _ensure_list(data.get("ux")),
        "conversion": _ensure_list(data.get("conversion")),
        "recommendations": _ensure_list(data.get("recommendations")),
        "score": _normalize_score(data.get("score", 5))
    }


# 🔧 HELPERS

def _ensure_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [value]
    return []


def _normalize_score(score: Any) -> int:
    try:
        score = int(score)
        return max(1, min(10, score))
    except Exception:
        return 5


# 🧠 QUALITY ESTIMATION (pro detail)
def _estimate_quality(data: Dict[str, Any]) -> str:
    total_items = sum(len(data.get(k, [])) for k in ["seo", "ux", "conversion", "recommendations"])

    if total_items >= 10:
        return "high"
    if total_items >= 5:
        return "medium"
    return "low"


# 🧨 FORCE PARSE (fallback parsing)
def _force_parse(text: str) -> Dict[str, Any]:
    """
    Tries to recover structure from messy LLM output
    """

    result = {
        "seo": [],
        "ux": [],
        "conversion": [],
        "recommendations": [],
        "score": 5
    }

    lines = text.split("\n")

    current_section = None

    for line in lines:
        line = line.strip("-• ").strip()

        if not line:
            continue

        lower = line.lower()

        if "seo" in lower:
            current_section = "seo"
            continue
        elif "ux" in lower:
            current_section = "ux"
            continue
        elif "conversion" in lower:
            current_section = "conversion"
            continue
        elif "recommend" in lower:
            current_section = "recommendations"
            continue

        if current_section:
            result[current_section].append(line)

    return result