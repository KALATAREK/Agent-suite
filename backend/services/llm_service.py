import os
import json
import time
from typing import List, Dict, Optional, Any
from openai import OpenAI

# 🔧 CONFIG
MODEL_DEFAULT = os.getenv("LLM_MODEL", "gpt-4o-mini")
MAX_RETRIES = 3
TIMEOUT_SECONDS = 30

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# 🧠 CORE CLASS
class LLMService:

    def __init__(self, model: str = MODEL_DEFAULT):
        self.model = model

    # 🔥 MAIN CALL
    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        response_format: Optional[Dict] = None,
        tools: Optional[List[Dict]] = None,
        stream: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        for attempt in range(MAX_RETRIES):
            try:
                start_time = time.time()

                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format=response_format,
                    tools=tools,
                    stream=stream,
                    timeout=TIMEOUT_SECONDS
                )

                duration = round(time.time() - start_time, 2)

                result = {
                    "content": self._extract_content(response),
                    "raw": response,
                    "usage": getattr(response, "usage", None),
                    "model": self.model,
                    "duration": duration,
                    "metadata": metadata or {}
                }

                self._log_success(messages, result)

                return result

            except Exception as e:
                self._log_error(e, attempt)

                if attempt == MAX_RETRIES - 1:
                    return {
                        "content": "",
                        "error": str(e),
                        "model": self.model
                    }

                # 🔥 exponential backoff
                time.sleep(1.5 ** (attempt + 1))

    # 🧠 JSON MODE (bardziej odporny)
    async def generate_json(
        self,
        messages: List[Dict[str, str]],
        schema: Dict
    ) -> Dict[str, Any]:

        response = await self.generate(
            messages=messages,
            response_format={"type": "json_object"}
        )

        content = response.get("content", "")

        try:
            return json.loads(content)
        except Exception:
            parsed = self._safe_parse_json(content)
            if parsed:
                return parsed

            return {
                "error": "Invalid JSON from model",
                "raw": content
            }

    # ⚡ TOOL CALLING (bardziej realne)
    async def generate_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict]
    ) -> Dict[str, Any]:

        response = await self.generate(
            messages=messages,
            tools=tools
        )

        return {
            "content": response.get("content"),
            "tool_calls": self._extract_tool_calls(response.get("raw"))
        }

    # 📡 STREAM (lepsze)
    async def generate_stream(
        self,
        messages: List[Dict[str, str]]
    ):
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            timeout=TIMEOUT_SECONDS
        )

        for chunk in response:
            try:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    yield delta.content
            except Exception:
                continue

    # 🧹 EXTRACT CONTENT
    def _extract_content(self, response) -> str:
        try:
            return response.choices[0].message.content or ""
        except Exception:
            return ""

    # 🧠 TOOL CALL PARSER
    def _extract_tool_calls(self, response) -> Optional[List[Dict[str, Any]]]:
        try:
            calls = response.choices[0].message.tool_calls
            if not calls:
                return None

            return [
                {
                    "name": call.function.name,
                    "arguments": call.function.arguments
                }
                for call in calls
            ]
        except Exception:
            return None

    # 🛡️ SAFE JSON PARSER
    def _safe_parse_json(self, text: str) -> Optional[Dict[str, Any]]:
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(text[start:end])
        except Exception:
            return None

    # 🪵 LOGGING (czytelniejsze)
    def _log_success(self, messages, result):
        preview = messages[-1]["content"][:60].replace("\n", " ")

        print(
            f"[LLM SUCCESS] model={result['model']} "
            f"time={result['duration']}s "
            f"msg='{preview}...'"
        )

    def _log_error(self, error, attempt):
        print(f"[LLM ERROR] attempt={attempt + 1} error={error}")