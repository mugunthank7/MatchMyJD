"""
utils/json_extractor.py
-----------------------
Robust JSON extractor for LLM outputs.

Handles:
- ```json fences
- Trailing text
- Missing closing braces
- Partial truncation (best-effort recovery)
"""

import json
import re
from config.settings import debug_log


def extract_json_from_text(text: str) -> dict:
    if not text or not isinstance(text, str):
        raise ValueError("Empty or invalid LLM response")

    # 1️⃣ Remove markdown fences
    cleaned = re.sub(r"```json|```", "", text).strip()

    # 2️⃣ Extract from first { to last }
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1:
        raise ValueError("No JSON object start found")

    if end == -1:
        debug_log("⚠️ Missing closing brace, attempting recovery")
        cleaned = cleaned + "}"

    json_str = cleaned[start:end + 1]

    # 3️⃣ Balance braces if truncated
    open_braces = json_str.count("{")
    close_braces = json_str.count("}")

    if open_braces > close_braces:
        json_str += "}" * (open_braces - close_braces)

    # 4️⃣ Final parse attempt
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        debug_log("❌ JSON parsing failed")
        debug_log(f"Error: {e}")
        debug_log("Extracted JSON string:")
        debug_log(json_str)
        raise
