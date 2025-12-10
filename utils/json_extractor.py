"""
utils/json_extractor.py
-----------------------
Utility helpers to safely extract JSON from LLM responses.
Used by both jd_analyzer and resume_analyzer.
"""

import json
import re
from config.settings import debug_log


def extract_json_from_text(text: str) -> dict:
    """
    Robust JSON extractor:
    - Strips markdown fences
    - Finds first {...} JSON object
    - Raises helpful errors on failure
    """
    if not text or not text.strip():
        raise ValueError("LLM returned empty response text; cannot parse JSON.")

    debug_log(f"Raw LLM response text (truncated): {text[:200]}...")

    # Remove ```json ... ``` and ``` fencing
    cleaned = text.replace("```json", "").replace("```", "").strip()

    # Find first JSON object
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        raise ValueError(f"Could not find JSON object in LLM response:\n{text}")

    json_str = match.group(0)

    try:
        parsed = json.loads(json_str)
        return parsed
    except json.JSONDecodeError as e:
        debug_log(f"JSON decode error: {e}")
        raise ValueError(f"LLM returned invalid JSON:\n\n{json_str}") from e
