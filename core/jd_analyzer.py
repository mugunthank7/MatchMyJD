"""
core/jd_analyzer.py
-------------------
Hybrid JD Analyzer

Pipeline:
1) Deterministic preprocessing of raw JD text
2) LLM (Gemini) extraction into STRICT schema-compliant JSON

Purpose:
Convert a Job Description into structured metadata
used downstream by matchers and scorers.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

from config.settings import (
    GEMINI_MODEL_JD,
    MAX_TOKENS_JD,
    debug_log
)
from core.jd_preprocessor import preprocess_jd
from utils.json_extractor import extract_json_from_text


# ---------------------------------------------------------
# GEMINI CLIENT CONFIG
# ---------------------------------------------------------

def configure_gemini():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("❌ Missing GEMINI_API_KEY in environment")

    genai.configure(api_key=api_key)
    debug_log("Gemini client configured successfully.")


# ---------------------------------------------------------
# PROMPT CONSTRUCTION (SCHEMA-STRICT)
# ---------------------------------------------------------

def build_jd_prompt(cleaned_jd: str) -> str:
    return f"""
You are an expert technical recruiter and ATS parser.

You will be given a CLEANED job description.
Extract information strictly and conservatively.

Rules:
- Return ONLY valid JSON
- Do NOT hallucinate skills
- Do NOT include eligibility, visa, or degree requirements
- Skills must be concise (1–3 words)
- If unsure, leave the list empty

Return JSON in EXACTLY this structure:

{{
  "must_have_skills": [],
  "nice_to_have_skills": [],
  "responsibilities": [],
  "seniority": "entry | mid | senior"
}}

Guidelines:
- must_have_skills → explicitly required technical skills
- nice_to_have_skills → preferred or optional technical skills
- responsibilities → short action phrases (not full sentences)
- seniority → infer conservatively from language

CLEANED JOB DESCRIPTION:
{cleaned_jd}
"""


# ---------------------------------------------------------
# MAIN ANALYSIS FUNCTION
# ---------------------------------------------------------

def analyze_jd(raw_jd_text: str) -> dict:
    """
    Full JD analysis pipeline:
    1) Preprocess raw JD
    2) Configure Gemini
    3) Send prompt to Gemini
    4) Extract and return validated JSON
    Retries once if LLM output is truncated.
    """
    debug_log("Starting JD analysis...")

    cleaned_jd = preprocess_jd(raw_jd_text)
    debug_log(f"Preprocessed JD (truncated): {cleaned_jd[:300]}")

    configure_gemini()

    prompt = build_jd_prompt(cleaned_jd)
    model = genai.GenerativeModel(GEMINI_MODEL_JD)

    for attempt in range(2):  # retry once
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": MAX_TOKENS_JD,
                "temperature": 0.2
            }
        )

        try:
            raw_text = response.text
        except AttributeError:
            raw_text = response.candidates[0].content.parts[0].text

        debug_log(f"Raw Gemini response (truncated): {raw_text[:200]}")

        try:
            parsed_json = extract_json_from_text(raw_text)
            debug_log("JD analysis completed successfully.")
            return parsed_json
        except Exception:
            debug_log(f"⚠️ JSON parse failed (attempt {attempt + 1}), retrying...")

    raise RuntimeError("❌ Failed to extract valid JSON from JD after retries")


# ---------------------------------------------------------
# LOCAL DEBUG RUNNER
# ---------------------------------------------------------

def _load_sample_jd(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    """
    Local test:
    python -m core.jd_analyzer
    """
    from pprint import pprint

    sample_path = "data/samples/sample_jd.txt"
    raw_jd = _load_sample_jd(sample_path)

    result = analyze_jd(raw_jd)
    pprint(result)
