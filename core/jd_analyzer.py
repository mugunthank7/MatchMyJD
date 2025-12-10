"""
core/jd_analyzer.py
-------------------
Hybrid JD Analyzer:
1) Deterministic preprocessing of raw JD text
2) LLM (Gemini) extraction into structured JSON

This is the main entry point for converting a JD into
machine-usable metadata for matching.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

from config.settings import GEMINI_MODEL_JD, MAX_TOKENS, debug_log
from core.jd_preprocessor import preprocess_jd
from utils.json_extractor import extract_json_from_text


# ---------------------------------------------------------
# GEMINI CLIENT CONFIG
# ---------------------------------------------------------

def configure_gemini():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY in .env")

    genai.configure(api_key=api_key)
    debug_log("Configured Gemini client with provided API key.")


# ---------------------------------------------------------
# PROMPT CONSTRUCTION (HYBRID: uses preprocessed JD)
# ---------------------------------------------------------

def build_jd_prompt(cleaned_jd: str) -> str:
    """
    Build a STRICT prompt for JD analysis.
    The JD has already been cleaned by jd_preprocessor.
    """
    return f"""
You are an expert ATS job description parser.

You will be given a CLEANED job description.
Extract ONLY the following fields and return STRICT JSON.

Rules:
- DO NOT include company fluff, perks, benefits, mission statements.
- DO NOT include degree/visa/eligibility requirements as skills.
- DO NOT include full sentences as skills.
- DO NOT hallucinate skills not present in the JD.
- Only extract what is explicitly or very clearly implied.

Fields to extract:

- role_title              → Main role name (e.g., 'Software Engineer Intern')
- seniority_level         → 'Intern', 'Junior', 'Mid', 'Senior', 'Lead', etc.
- hard_skills             → Core technical competencies (e.g., Data Structures, Algorithms)
- tools_and_frameworks    → Concrete tools/frameworks/languages (e.g., Python, Java, Git, Docker)
- domains                 → Technical domains (e.g., Software Engineering, Distributed Systems)
- soft_skills             → Interpersonal skills (e.g., communication, teamwork)
- key_responsibility_phrases → Short phrases describing what the intern/engineer does
- must_have_keywords      → REQUIRED technical skills (NOT eligibility conditions)
- nice_to_have_keywords   → Nice-to-have or preferred technical skills

Return JSON ONLY in this exact structure:

{{
  "role_title": "",
  "seniority_level": "",
  "hard_skills": [],
  "tools_and_frameworks": [],
  "domains": [],
  "soft_skills": [],
  "key_responsibility_phrases": [],
  "must_have_keywords": [],
  "nice_to_have_keywords": []
}}

NO extra keys.
NO explanations.
NO markdown.

CLEANED JOB DESCRIPTION:
{cleaned_jd}
"""


# ---------------------------------------------------------
# MAIN ANALYSIS FUNCTION
# ---------------------------------------------------------

def analyze_jd(raw_jd_text: str) -> dict:
    """
    Full hybrid JD analysis:
    1) Preprocess JD text
    2) Send to Gemini
    3) Parse JSON output
    """
    debug_log("Starting JD analysis pipeline...")

    cleaned = preprocess_jd(raw_jd_text)
    debug_log(f"Preprocessed JD (truncated): {cleaned[:300]}...")

    prompt = build_jd_prompt(cleaned)

    model = genai.GenerativeModel(GEMINI_MODEL_JD)

    response = model.generate_content(
        prompt,
        generation_config={
            "max_output_tokens": MAX_TOKENS,
            "temperature": 0.2,  # more deterministic
        },
    )

    # Try to get text from response
    try:
        text = response.text
    except AttributeError:
        # Older SDK fallback
        text = response.candidates[0].content.parts[0].text

    debug_log(f"Raw JD LLM response (truncated): {text[:200]}...")
    result = extract_json_from_text(text)
    debug_log("JD analysis pipeline complete.")
    return result


# ---------------------------------------------------------
# Local test runner
# ---------------------------------------------------------

def _load_sample_jd(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    """
    Local debug run:
    python3 -m core.jd_analyzer
    """
    configure_gemini()
    sample_path = "data/samples/sample_jd.txt"
    raw_jd = _load_sample_jd(sample_path)
    parsed = analyze_jd(raw_jd)
    from pprint import pprint
    pprint(parsed)
