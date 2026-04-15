from typing import Dict, Any

from agents.analyzer_agent import handle_analyzer


# 🎯 MAIN SERVICE ENTRYPOINT
async def analyze_business(input_data: str) -> Dict[str, Any]:
    """
    High-level analysis service.

    Responsibilities:
    - validate input
    - preprocess data
    - call analyzer agent
    - normalize output
    - prepare final response
    """

    cleaned_input = _validate_input(input_data)

    # 🧠 STEP 1 — enrichment (future-ready)
    enriched_input = await _enrich_input(cleaned_input)

    # 🧠 STEP 2 — run analyzer
    result = await handle_analyzer(enriched_input)

    # 🧠 STEP 3 — normalize final output
    return _build_response(result)


# 🧠 INPUT VALIDATION
def _validate_input(input_data: str) -> str:
    if not input_data or not isinstance(input_data, str):
        raise ValueError("Invalid input for analysis")

    cleaned = input_data.strip()

    if len(cleaned) < 3:
        raise ValueError("Input too short")

    return cleaned


# 🧠 ENRICHMENT LAYER (hook pod przyszłość)
async def _enrich_input(input_data: str) -> str:
    """
    Future:
    - scraping website content
    - extracting meta tags
    - adding business context

    For now:
    - just pass through
    """

    if input_data.startswith("http"):
        return f"Website URL:\n{input_data}"

    return f"Business description:\n{input_data}"


# 🧱 RESPONSE BUILDER
def _build_response(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensures consistent API structure
    """

    return {
        "type": "analysis",
        "content": result.get("data", {}),
        "meta": result.get("meta", {})
    }